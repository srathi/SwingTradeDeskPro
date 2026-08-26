"""
Data Ingestion Module for SectorPulse.
Fetches, cleans, aligns, and forward-fills OHLCV historical time-series for benchmark and sector indices.
"""

from typing import Dict, List, Optional, Tuple
import logging
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
    """

    def __init__(self, cache_ttl_seconds: int = 3600):
        self.cache_ttl = cache_ttl_seconds
        self._cache: Dict[str, pd.DataFrame] = {}

    def fetch_ticker_ohlcv(self, ticker: str, period: str = "2y", interval: str = "1d") -> Optional[pd.DataFrame]:
        """
        Fetches and standardizes single OHLCV ticker DataFrame.
        """
        cache_key = f"{ticker}_{period}_{interval}"
        if cache_key in self._cache:
            return self._cache[cache_key].copy()

        try:
            t = yf.Ticker(ticker)
            df = t.history(period=period, interval=interval)
            if df is None or df.empty or len(df) < 30:
                # Fallback for Indian indices that might lack caret prefix or alternate symbology
                clean_sym = ticker.replace("^", "") + ".NS" if not ticker.endswith(".NS") and "^" in ticker else ticker
                t_alt = yf.Ticker(clean_sym)
                df = t_alt.history(period=period, interval=interval)

            if df is None or df.empty:
                logger.warning(f"No OHLCV data found for symbol: {ticker}")
                return None

            # Standardize column names
            df.columns = [c.capitalize() for c in df.columns]
            req_cols = ["Open", "High", "Low", "Close", "Volume"]
            for col in req_cols:
                if col not in df.columns:
                    if col == "Volume":
                        df["Volume"] = 1_000_000.0
                    else:
                        df[col] = df["Close"] if "Close" in df.columns else 100.0

            # Convert timezone-aware index to naive UTC dates
            if df.index.tz is not None:
                df.index = df.index.tz_convert(None)

            df = df[req_cols].dropna(subset=["Close"])
            self._cache[cache_key] = df
            return df.copy()

        except Exception as e:
            logger.error(f"Error fetching data for {ticker}: {e}")
            return None

    def ingest_sector_universe(
        self,
        benchmark_ticker: str = DEFAULT_NSE_BENCHMARK,
        sector_tickers: Optional[List[str]] = None,
        period: str = "2y"
    ) -> Tuple[pd.DataFrame, Dict[str, pd.DataFrame]]:
        """
        Fetches and cross-aligns benchmark data and all sector series.
        Missing trading dates are forward-filled.
        """
        if sector_tickers is None or len(sector_tickers) == 0:
            sector_tickers = list(DEFAULT_NSE_SECTORS.keys())

        # 1. Fetch benchmark
        bench_df = self.fetch_ticker_ohlcv(benchmark_ticker, period=period)
        if bench_df is None or len(bench_df) < 50:
            # Fallback benchmark
            if benchmark_ticker.startswith("^"):
                bench_df = self.fetch_ticker_ohlcv(benchmark_ticker.replace("^", "") + ".NS", period=period)
            if bench_df is None or len(bench_df) < 50:
                raise ValueError(f"Failed to fetch sufficient benchmark data for '{benchmark_ticker}'")

        # 2. Fetch all sector dataframes
        sector_dfs: Dict[str, pd.DataFrame] = {}
        for sec in sector_tickers:
            sec_df = self.fetch_ticker_ohlcv(sec, period=period)
            if sec_df is not None and len(sec_df) >= 40:
                # Align on benchmark index
                aligned_df = sec_df.reindex(bench_df.index).ffill().bfill()
                sector_dfs[sec] = aligned_df
            else:
                logger.warning(f"Skipping sector {sec} due to insufficient historical bars.")

        return bench_df, sector_dfs
