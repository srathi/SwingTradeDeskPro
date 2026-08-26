"""
Data Ingestion Module for SectorPulse.
High-performance batch fetching, cleaning, date-alignment, and forward-filling of OHLCV historical time-series.
"""

from typing import Dict, List, Optional, Tuple
import logging
import time
import pandas as pd
import yfinance as yf

logger = logging.getLogger("SectorPulse.DataIngestion")

# Standard Indian Sector Indices & US Sector ETF defaults
DEFAULT_NSE_BENCHMARK = "^NSEI"
DEFAULT_NSE_SECTORS = {
    "^NSEBANK": "Nifty Bank",
    "^CNXIT": "Nifty IT",
    "^CNXAUTO": "Nifty Auto",
    "^CNXPHARMA": "Nifty Pharma",
    "^CNXFMCG": "Nifty FMCG",
    "^CNXMETAL": "Nifty Metal",
    "^CNXREALTY": "Nifty Realty",
    "^CNXENERGY": "Nifty Energy",
    "^CNXINFRA": "Nifty Infrastructure",
    "^CNXPSUBANK": "Nifty PSU Bank",
    "^CNXMEDIA": "Nifty Media"
}

# Proxy mapping for cloud datacenter environments if carets are rate-limited
NSE_ETF_FALLBACKS = {
    "^NSEI": "NIFTYBEES.NS",
    "^NSEBANK": "BANKBEES.NS",
    "^CNXIT": "ITBEES.NS",
    "^CNXAUTO": "AUTOBEES.NS",
    "^CNXPHARMA": "PHARMABEES.NS",
    "^CNXPSUBANK": "PSUBNKBEES.NS",
    "^CNXINFRA": "INFRABEES.NS",
}

DEFAULT_US_BENCHMARK = "SPY"
DEFAULT_US_SECTORS = {
    "XLK": "Technology Select Sector SPDR",
    "XLF": "Financial Select Sector SPDR",
    "XLE": "Energy Select Sector SPDR",
    "XLV": "Health Care Select Sector SPDR",
    "XLI": "Industrial Select Sector SPDR",
    "XLY": "Consumer Discretionary SPDR",
    "XLP": "Consumer Staples SPDR",
    "XLU": "Utilities Select Sector SPDR",
    "XLRE": "Real Estate Select Sector SPDR",
    "XLC": "Communication Services SPDR",
    "XLB": "Materials Select Sector SPDR"
}


class SectorDataIngestion:
    """
    Ingests and aligns time-series OHLCV data for multiple sector indices against a benchmark.
    Utilizes parallelized batch downloading and in-memory TTL caching.
    """

    def __init__(self, cache_ttl_seconds: int = 3600):
        self.cache_ttl = cache_ttl_seconds
        self._cache: Dict[str, Tuple[float, pd.DataFrame]] = {}
        self._universe_cache: Dict[str, Tuple[float, pd.DataFrame, Dict[str, pd.DataFrame]]] = {}

    def fetch_ticker_ohlcv(self, ticker: str, period: str = "2y", interval: str = "1d") -> Optional[pd.DataFrame]:
        """
        Fetches and standardizes single OHLCV ticker DataFrame with caching.
        """
        cache_key = f"{ticker}_{period}_{interval}"
        now = time.time()
        if cache_key in self._cache:
            ts, df = self._cache[cache_key]
            if now - ts < self.cache_ttl:
                return df.copy()

        try:
            df = yf.download(ticker, period=period, interval=interval, progress=False, auto_adjust=False)
            if df is None or df.empty or len(df) < 20:
                # Try fallback symbol if exists
                if ticker in NSE_ETF_FALLBACKS:
                    fb = NSE_ETF_FALLBACKS[ticker]
                    df = yf.download(fb, period=period, interval=interval, progress=False, auto_adjust=False)

            if df is None or df.empty:
                logger.warning(f"No OHLCV data found for symbol: {ticker}")
                return None

            # Flatten multiindex columns if present
            if isinstance(df.columns, pd.MultiIndex):
                df = df.xs(ticker, level=1, axis=1) if ticker in df.columns.levels[1] else df.droplevel(1, axis=1)

            df.columns = [c.capitalize() for c in df.columns]
            req_cols = ["Open", "High", "Low", "Close", "Volume"]
            for col in req_cols:
                if col not in df.columns:
                    if col == "Volume":
                        df["Volume"] = 1_000_000.0
                    else:
                        df[col] = df["Close"] if "Close" in df.columns else 100.0

            if df.index.tz is not None:
                df.index = df.index.tz_convert(None)

            df = df[req_cols].dropna(subset=["Close"])
            self._cache[cache_key] = (now, df.copy())
            return df.copy()

        except Exception as e:
            logger.error(f"Error fetching single data for {ticker}: {e}")
            return None

    def ingest_sector_universe(
        self,
        benchmark_ticker: str = DEFAULT_NSE_BENCHMARK,
        sector_tickers: Optional[List[str]] = None,
        period: str = "2y"
    ) -> Tuple[pd.DataFrame, Dict[str, pd.DataFrame]]:
        """
        Fetches and cross-aligns benchmark data and all sector series using fast batch download.
        Missing trading dates are forward-filled.
        """
        if sector_tickers is None or len(sector_tickers) == 0:
            sector_tickers = list(DEFAULT_NSE_SECTORS.keys())

        cache_key = f"{benchmark_ticker}_{','.join(sorted(sector_tickers))}_{period}"
        now = time.time()
        if cache_key in self._universe_cache:
            ts, b_df, s_dfs = self._universe_cache[cache_key]
            if now - ts < self.cache_ttl:
                return b_df.copy(), {k: v.copy() for k, v in s_dfs.items()}

        all_symbols = list(set([benchmark_ticker] + sector_tickers))

        try:
            # Batch download in a single parallelized request
            batch_data = yf.download(
                all_symbols,
                period=period,
                interval="1d",
                progress=False,
                group_by="ticker",
                auto_adjust=False,
                threads=True
            )
        except Exception as e:
            logger.warning(f"Batch download failed, falling back to individual: {e}")
            batch_data = None

        bench_df: Optional[pd.DataFrame] = None
        sector_dfs: Dict[str, pd.DataFrame] = {}

        # 1. Process Benchmark
        if batch_data is not None and not batch_data.empty and hasattr(batch_data.columns, 'levels') and benchmark_ticker in batch_data.columns.levels[0]:
            try:
                sub = batch_data[benchmark_ticker].copy().dropna(subset=["Close"])
                sub.columns = [c.capitalize() for c in sub.columns]
                if len(sub) >= 40:
                    bench_df = sub
            except Exception as e:
                logger.warning(f"Failed extracting benchmark from batch: {e}")

        if bench_df is None:
            bench_df = self.fetch_ticker_ohlcv(benchmark_ticker, period=period)
            if bench_df is None or len(bench_df) < 40:
                if benchmark_ticker in NSE_ETF_FALLBACKS:
                    bench_df = self.fetch_ticker_ohlcv(NSE_ETF_FALLBACKS[benchmark_ticker], period=period)
                if bench_df is None or len(bench_df) < 40:
                    raise ValueError(f"Failed to fetch sufficient benchmark data for '{benchmark_ticker}'")

        if bench_df.index.tz is not None:
            bench_df.index = bench_df.index.tz_convert(None)

        req_cols = ["Open", "High", "Low", "Close", "Volume"]
        for col in req_cols:
            if col not in bench_df.columns:
                bench_df[col] = bench_df["Close"] if col != "Volume" else 1_000_000.0
        bench_df = bench_df[req_cols]

        # 2. Process Sectors
        for sec in sector_tickers:
            sec_df: Optional[pd.DataFrame] = None
            if batch_data is not None and hasattr(batch_data.columns, 'levels') and sec in batch_data.columns.levels[0]:
                try:
                    sub = batch_data[sec].copy().dropna(subset=["Close"])
                    sub.columns = [c.capitalize() for c in sub.columns]
                    if len(sub) >= 40:
                        sec_df = sub
                except Exception:
                    pass

            if sec_df is None:
                sec_df = self.fetch_ticker_ohlcv(sec, period=period)

            if sec_df is not None and len(sec_df) >= 30:
                if sec_df.index.tz is not None:
                    sec_df.index = sec_df.index.tz_convert(None)
                for col in req_cols:
                    if col not in sec_df.columns:
                        sec_df[col] = sec_df["Close"] if col != "Volume" else 1_000_000.0
                
                # Cross-align on benchmark dates with forward/backward fill
                aligned_df = sec_df[req_cols].reindex(bench_df.index).ffill().bfill()
                sector_dfs[sec] = aligned_df
            else:
                logger.warning(f"Skipping sector {sec} due to insufficient historical bars.")

        self._universe_cache[cache_key] = (now, bench_df.copy(), {k: v.copy() for k, v in sector_dfs.items()})
        return bench_df, sector_dfs
