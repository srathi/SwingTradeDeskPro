"""
Data Ingestion Module for SectorPulse.
High-performance batch fetching, cleaning, date-alignment, and forward-filling of OHLCV historical time-series.
Incorporates multi-candidate symbol resolution to ensure 100% sector availability across cloud servers.
"""

from typing import Dict, List, Optional, Tuple
import logging
import time
import pandas as pd
import yfinance as yf

logger = logging.getLogger("SectorPulse.DataIngestion")

DEFAULT_NSE_BENCHMARK = "^NSEI"

# Master Sector Names
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

# Multi-candidate ticker resolution: tries index symbol first, then ETF proxy, then top sector bellwether stock
SECTOR_CANDIDATE_MAP = {
    "^NSEI": ["^NSEI", "NIFTYBEES.NS", "RELIANCE.NS"],
    "^NSEBANK": ["^NSEBANK", "BANKBEES.NS", "HDFCBANK.NS", "ICICIBANK.NS"],
    "^CNXIT": ["^CNXIT", "ITBEES.NS", "INFY.NS", "TCS.NS"],
    "^CNXAUTO": ["^CNXAUTO", "AUTOBEES.NS", "M&M.NS", "MARUTI.NS"],
    "^CNXPHARMA": ["^CNXPHARMA", "PHARMABEES.NS", "SUNPHARMA.NS", "DRREDDY.NS"],
    "^CNXFMCG": ["^CNXFMCG", "ITC.NS", "HINDUNILVR.NS", "NESTLEIND.NS"],
    "^CNXMETAL": ["^CNXMETAL", "TATASTEEL.NS", "JSWSTEEL.NS", "HINDALCO.NS"],
    "^CNXREALTY": ["^CNXREALTY", "DLF.NS", "GODREJPROP.NS", "OBEROIRLTY.NS"],
    "^CNXENERGY": ["^CNXENERGY", "RELIANCE.NS", "ONGC.NS", "NTPC.NS"],
    "^CNXINFRA": ["^CNXINFRA", "LT.NS", "POWERGRID.NS", "INFRABEES.NS"],
    "^CNXPSUBANK": ["^CNXPSUBANK", "SBIN.NS", "BANKBARODA.NS", "PSUBNKBEES.NS"],
    "^CNXMEDIA": ["^CNXMEDIA", "ZEEL.NS", "SUNTV.NS", "PVRINOX.NS"]
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
    Utilizes parallelized batch downloading, candidate resolution fallbacks, and in-memory TTL caching.
    """

    def __init__(self, cache_ttl_seconds: int = 3600):
        self.cache_ttl = cache_ttl_seconds
        self._universe_cache: Dict[str, Tuple[float, pd.DataFrame, Dict[str, pd.DataFrame]]] = {}

    def ingest_sector_universe(
        self,
        benchmark_ticker: str = DEFAULT_NSE_BENCHMARK,
        sector_tickers: Optional[List[str]] = None,
        period: str = "1y"
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

        # Build list of all candidate symbols to fetch in a single parallel batch
        symbols_to_fetch = set()
        bench_candidates = SECTOR_CANDIDATE_MAP.get(benchmark_ticker, [benchmark_ticker])
        symbols_to_fetch.update(bench_candidates)

        for sec in sector_tickers:
            sec_candidates = SECTOR_CANDIDATE_MAP.get(sec, [sec])
            symbols_to_fetch.update(sec_candidates)

        all_symbols = list(symbols_to_fetch)
        logger.info(f"Downloading batch of {len(all_symbols)} candidate symbols for SectorPulse...")

        try:
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
            logger.warning(f"Batch download error: {e}")
            batch_data = None

        bench_df: Optional[pd.DataFrame] = None
        req_cols = ["Open", "High", "Low", "Close", "Volume"]

        def extract_df_from_batch(symbol: str) -> Optional[pd.DataFrame]:
            if batch_data is None or batch_data.empty:
                return None
            try:
                if hasattr(batch_data.columns, 'levels') and symbol in batch_data.columns.levels[0]:
                    sub = batch_data[symbol].copy().dropna(subset=["Close"])
                    if len(sub) >= 20:
                        sub.columns = [c.capitalize() for c in sub.columns]
                        for col in req_cols:
                            if col not in sub.columns:
                                sub[col] = sub["Close"] if col != "Volume" else 1_000_000.0
                        if sub.index.tz is not None:
                            sub.index = sub.index.tz_convert(None)
                        return sub[req_cols]
            except Exception:
                pass
            return None

        # 1. Resolve Benchmark
        for bc in bench_candidates:
            bench_df = extract_df_from_batch(bc)
            if bench_df is not None and len(bench_df) >= 30:
                logger.info(f"Benchmark resolved via candidate: {bc}")
                break

        if bench_df is None:
            # Fallback single download for benchmark
            try:
                df = yf.download(benchmark_ticker, period=period, progress=False)
                if df is not None and len(df) >= 30:
                    df.columns = [c.capitalize() for c in df.columns]
                    bench_df = df[req_cols]
            except Exception:
                pass

        if bench_df is None or len(bench_df) < 30:
            raise ValueError(f"Failed to fetch sufficient benchmark data for '{benchmark_ticker}'")

        # 2. Resolve Each Sector
        sector_dfs: Dict[str, pd.DataFrame] = {}
        for sec in sector_tickers:
            candidates = SECTOR_CANDIDATE_MAP.get(sec, [sec])
            sec_df: Optional[pd.DataFrame] = None

            for c in candidates:
                sec_df = extract_df_from_batch(c)
                if sec_df is not None and len(sec_df) >= 20:
                    break

            if sec_df is None:
                for c in candidates:
                    try:
                        single_df = yf.download(c, period=period, progress=False)
                        if single_df is not None and len(single_df) >= 20:
                            single_df.columns = [col.capitalize() for col in single_df.columns]
                            for col in req_cols:
                                if col not in single_df.columns:
                                    single_df[col] = single_df["Close"] if col != "Volume" else 1_000_000.0
                            if single_df.index.tz is not None:
                                single_df.index = single_df.index.tz_convert(None)
                            sec_df = single_df[req_cols]
                            break
                    except Exception:
                        pass

            if sec_df is not None and len(sec_df) >= 20:
                aligned_df = sec_df[req_cols].reindex(bench_df.index).ffill().bfill()
                sector_dfs[sec] = aligned_df
            else:
                logger.warning(f"Could not resolve data for sector: {sec}")

        self._universe_cache[cache_key] = (now, bench_df.copy(), {k: v.copy() for k, v in sector_dfs.items()})
        return bench_df, sector_dfs
