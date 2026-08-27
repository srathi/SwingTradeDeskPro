"""
Data Engine with Yahoo Finance Ingestion, Intelligent Fuzzy Name Resolution, and SQLite Disk Caching.
Provides fast, rate-limited, and cached OHLCV market data for Indian and global equities.
"""

import os
import io
import sqlite3
import datetime
import pandas as pd
import yfinance as yf
from typing import List, Dict, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data_cache", "market_cache.db")


class DataEngine:
    def __init__(self, db_path: str = DB_PATH, cache_ttl_hours: int = 4):
        self.db_path = db_path
        self.cache_ttl_hours = cache_ttl_hours
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS ohlcv_cache (
                    ticker TEXT,
                    period TEXT,
                    interval TEXT,
                    data_json TEXT,
                    updated_at TIMESTAMP,
                    PRIMARY KEY (ticker, period, interval)
                )
            """)
            conn.commit()

    def _get_from_cache(self, ticker: str, period: str, interval: str) -> Optional[pd.DataFrame]:
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT data_json, updated_at FROM ohlcv_cache WHERE ticker=? AND period=? AND interval=?",
                    (ticker, period, interval)
                )
                row = cursor.fetchone()
                if row:
                    data_json, updated_at_str = row
                    updated_at = datetime.datetime.fromisoformat(updated_at_str)
                    age_hours = (datetime.datetime.utcnow() - updated_at).total_seconds() / 3600.0
                    if age_hours < self.cache_ttl_hours:
                        df = pd.read_json(io.StringIO(data_json))
                        if not df.empty:
                            df.index = pd.to_datetime(df.index)
                            df = df[~df.index.duplicated(keep='first')].sort_index()
                            return df
        except Exception:
            pass
        return None

    def _save_to_cache(self, ticker: str, period: str, interval: str, df: pd.DataFrame):
        try:
            data_json = df.to_json()
            now_str = datetime.datetime.utcnow().isoformat()
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO ohlcv_cache (ticker, period, interval, data_json, updated_at)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (ticker, period, interval, data_json, now_str)
                )
                conn.commit()
        except Exception:
            pass

    def _download_yf(self, symbol: str, period: str, interval: str) -> Optional[pd.DataFrame]:
        try:
            # Skip invalid multi-token symbols in raw yf.download
            if " " in symbol:
                return None

            df = yf.download(
                symbol,
                period=period,
                interval=interval,
                auto_adjust=False,
                progress=False
            )
            if df.empty or len(df) < 15:
                return None

            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            required_cols = ["Open", "High", "Low", "Close", "Volume"]
            for col in required_cols:
                if col not in df.columns:
                    return None

            df = df[required_cols].copy()
            for col in required_cols:
                df[col] = pd.to_numeric(df[col], errors='coerce')

            df = df.dropna()
            df = df[~df.index.duplicated(keep='first')].sort_index()
            if len(df) < 15:
                return None

            return df
        except Exception:
            return None

    def resolve_symbol(self, query: str) -> List[str]:
        """
        Resolves natural company names and un-suffixed tickers to candidate stock symbols.
        """
        q = query.strip()
        if not q:
            return []

        # If index symbol with caret prefix, preserve exact ticker without fuzzy stock search
        if q.startswith("^"):
            clean = q.replace("^", "")
            return [q, f"{clean}.NS", f"{clean}.BO", clean]

        candidates = []
        # If already formatted with suffix
        if q.upper().endswith(('.NS', '.BO')):
            candidates.append(q.upper())

        # Standard suffixes fallback (only if not already suffixed)
        q_upper = q.upper().replace(" ", "")
        if not q_upper.endswith(('.NS', '.BO')):
            for fallback in [f"{q_upper}.NS", f"{q_upper}.BO", q_upper]:
                if fallback not in candidates:
                    candidates.append(fallback)

        # Query SearchEngine for fuzzy company/ticker matches
        from backend.app.core.search_engine import SearchEngine
        matches = SearchEngine.search(q, limit=5)
        for m in matches:
            sym = m["symbol"]
            if sym not in candidates:
                candidates.append(sym)

        return candidates

    def fetch_ticker_data_with_resolved_sym(
        self,
        ticker: str,
        period: str = "1y",
        interval: str = "1d",
        use_cache: bool = True
    ) -> Tuple[Optional[str], Optional[pd.DataFrame]]:
        """
        Fetches OHLCV dataframe and returns both the resolved official ticker symbol and dataframe.
        """
        candidates = self.resolve_symbol(ticker)
        for sym in candidates:
            if use_cache:
                cached_df = self._get_from_cache(sym, period, interval)
                if cached_df is not None and len(cached_df) >= 20:
                    return sym, cached_df

            df = self._download_yf(sym, period, interval)
            if df is not None:
                if use_cache:
                    self._save_to_cache(sym, period, interval, df)
                return sym, df

        return None, None

    def fetch_ticker_data(
        self,
        ticker: str,
        period: str = "1y",
        interval: str = "1d",
        use_cache: bool = True
    ) -> Optional[pd.DataFrame]:
        """
        Fetches OHLCV dataframe for a single ticker with intelligent symbol resolution and disk caching.
        """
        _, df = self.fetch_ticker_data_with_resolved_sym(ticker, period, interval, use_cache)
        return df

    def fetch_batch_data(
        self,
        tickers: List[str],
        period: str = "1y",
        interval: str = "1d",
        max_workers: int = 15,
        use_cache: bool = True
    ) -> Dict[str, pd.DataFrame]:
        """
        Fetches OHLCV data concurrently for a list of tickers.
        """
        results = {}
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_ticker = {
                executor.submit(self.fetch_ticker_data, t, period, interval, use_cache): t
                for t in tickers
            }
            for future in as_completed(future_to_ticker):
                t = future_to_ticker[future]
                try:
                    df = future.result()
                    if df is not None and not df.empty:
                        results[t] = df
                except Exception:
                    pass
        return results


# Global singleton instance
data_engine = DataEngine()
