"""
Data Ingestion Module for SectorPulse.
High-performance fetching, cleaning, date-alignment, and SQLite disk-cached time-series ingestion.
Uses dedicated per-sector candidate resolvers to ensure 100% unique, isolated sector data feeds.
"""

from typing import Dict, List, Optional, Tuple
import logging
import pandas as pd

from backend.app.core.data_engine import DataEngine

logger = logging.getLogger("SectorPulse.DataIngestion")

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

# Dedicated isolated fallback chains per sector to prevent any cross-contamination
SECTOR_CANDIDATE_MAP = {
    "^NSEI": ["^NSEI", "NIFTYBEES.NS"],
    "^NSEBANK": ["^NSEBANK", "BANKBEES.NS", "HDFCBANK.NS", "ICICIBANK.NS"],
    "^CNXIT": ["^CNXIT", "ITBEES.NS", "INFY.NS", "TCS.NS"],
    "^CNXAUTO": ["^CNXAUTO", "AUTOBEES.NS", "MARUTI.NS", "M&M.NS"],
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
    Backed by persistent SQLite disk cache and isolated per-sector candidate resolvers.
    """

    def __init__(self, cache_ttl_hours: int = 4):
        self.data_engine = DataEngine(cache_ttl_hours=cache_ttl_hours)

    def fetch_ticker_ohlcv(self, ticker: str, period: str = "2y", interval: str = "1d") -> Optional[pd.DataFrame]:
        """
        Fetches and standardizes single OHLCV ticker DataFrame trying only that sector's dedicated candidates.
        """
        candidates = SECTOR_CANDIDATE_MAP.get(ticker, [ticker])
        req_cols = ["Open", "High", "Low", "Close", "Volume"]

        for cand in candidates:
            try:
                # 1. Check disk cache
                cached_df = self.data_engine._get_from_cache(cand, period, interval)
                if cached_df is not None and len(cached_df) >= 20:
                    cached_df.columns = [c.capitalize() for c in cached_df.columns]
                    for col in req_cols:
                        if col not in cached_df.columns:
                            cached_df[col] = cached_df["Close"] if col != "Volume" else 1_000_000.0
                    if cached_df.index.tz is not None:
                        cached_df.index = cached_df.index.tz_convert(None)
                    return cached_df[req_cols].dropna(subset=["Close"]).copy()

                # 2. Download directly with exact candidate symbol
                df = self.data_engine._download_yf(cand, period, interval)
                if df is not None and len(df) >= 20:
                    self.data_engine._save_to_cache(cand, period, interval, df)
                    df.columns = [c.capitalize() for c in df.columns]
                    for col in req_cols:
                        if col not in df.columns:
                            df[col] = df["Close"] if col != "Volume" else 1_000_000.0
                    if df.index.tz is not None:
                        df.index = df.index.tz_convert(None)
                    return df[req_cols].dropna(subset=["Close"]).copy()
            except Exception as e:
                logger.debug(f"Candidate {cand} for {ticker} failed: {e}")
                continue

        logger.warning(f"Could not resolve any candidate for sector: {ticker}")
        return None

    def ingest_sector_universe(
        self,
        benchmark_ticker: str = DEFAULT_NSE_BENCHMARK,
        sector_tickers: Optional[List[str]] = None,
        period: str = "2y"
    ) -> Tuple[pd.DataFrame, Dict[str, pd.DataFrame]]:
        """
        Fetches and cross-aligns benchmark data and all sector series with forward-fill.
        """
        if sector_tickers is None or len(sector_tickers) == 0:
            sector_tickers = list(DEFAULT_NSE_SECTORS.keys())

        # 1. Fetch benchmark
        bench_df = self.fetch_ticker_ohlcv(benchmark_ticker, period=period)
        if bench_df is None or len(bench_df) < 30:
            raise ValueError(f"Failed to fetch sufficient benchmark data for '{benchmark_ticker}'")

        # 2. Fetch all sector dataframes
        sector_dfs: Dict[str, pd.DataFrame] = {}
        for sec in sector_tickers:
            sec_df = self.fetch_ticker_ohlcv(sec, period=period)
            if sec_df is not None and len(sec_df) >= 20:
                aligned_df = sec_df.reindex(bench_df.index).ffill().bfill()
                sector_dfs[sec] = aligned_df
            else:
                logger.warning(f"Could not resolve data for sector: {sec}")

        return bench_df, sector_dfs
