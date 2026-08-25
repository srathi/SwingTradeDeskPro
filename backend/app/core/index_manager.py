"""
Index Universe Manager for Indian and Global Equities.
Fetches up-to-date index constituents from official exchange feeds with robust fallback caches.
"""

import io
import requests
import pandas as pd
from typing import List, Dict, Optional

# Fallback top liquid stocks for Indian & US Markets
FALLBACK_NIFTY50 = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "INFY.NS",
    "BHARTIARTL.NS", "SBIN.NS", "LICI.NS", "ITC.NS", "HINDUNILVR.NS",
    "LT.NS", "HCLTECH.NS", "BAJFINANCE.NS", "SUNPHARMA.NS", "MARUTI.NS",
    "KOTAKBANK.NS", "TITAN.NS", "TATAMOTORS.NS", "AXISBANK.NS", "NTPC.NS",
    "ONGC.NS", "ADANIENT.NS", "ADANIPORTS.NS", "POWERGRID.NS", "COALINDIA.NS",
    "TATASTEEL.NS", "M&M.NS", "BAJAJFINSV.NS", "ASIANPAINT.NS", "SIEMENS.NS",
    "ULTRACEMCO.NS", "JSWSTEEL.NS", "INDUSINDBK.NS", "TECHM.NS", "NESTLEIND.NS",
    "WIPRO.NS", "GRASIM.NS", "HINDALCO.NS", "DRREDDY.NS", "CIPLA.NS",
    "SBILIFE.NS", "HDFCLIFE.NS", "BRITANNIA.NS", "TATACONSUM.NS", "EICHERMOT.NS",
    "APOLLOHOSP.NS", "DIVISLAB.NS", "HEROMOTOCO.NS", "BPCL.NS", "SHRIRAMFIN.NS"
]

FALLBACK_NIFTY_NEXT50 = [
    "BEL.NS", "HAL.NS", "IOC.NS", "PFC.NS", "RECLTD.NS", "TRENT.NS",
    "ZOMATO.NS", "JIOFIN.NS", "VBL.NS", "CHOLAFIN.NS", "DLF.NS", "VEDL.NS",
    "GAIL.NS", "ABB.NS", "TVSMOTOR.NS", "PIDILITIND.NS", "HAVELLS.NS",
    "BANKBARODA.NS", "CANBK.NS", "PNB.NS", "SRF.NS", "MOTHERSON.NS",
    "POLYCAB.NS", "AMBUJACEM.NS", "INDIGO.NS", "TORNTPHARM.NS", "LTIM.NS"
]

FALLBACK_BSE_SENSEX = [
    "RELIANCE.BO", "TCS.BO", "HDFCBANK.BO", "ICICIBANK.BO", "INFY.BO",
    "BHARTIARTL.BO", "SBIN.BO", "ITC.BO", "HINDUNILVR.BO", "LT.BO",
    "HCLTECH.BO", "BAJFINANCE.BO", "SUNPHARMA.BO", "MARUTI.BO", "KOTAKBANK.BO",
    "TITAN.BO", "TATAMOTORS.BO", "AXISBANK.BO", "NTPC.BO", "POWERGRID.BO",
    "TATASTEEL.BO", "M&M.BO", "BAJAJFINSV.BO", "ASIANPAINT.BO", "ULTRACEMCO.BO",
    "JSWSTEEL.BO", "INDUSINDBK.BO", "TECHM.BO", "NESTLEIND.BO", "WIPRO.BO"
]

FALLBACK_US_MEGA = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "AMD",
    "NFLX", "JPM", "V", "MA", "UNH", "XOM", "JNJ", "PG", "HD", "COST"
]

UNIVERSE_METADATA = {
    "NIFTY_50": {
        "name": "Nifty 50 (NSE Large-Cap)",
        "exchange": "NSE",
        "url": "https://archives.nseindia.com/content/indices/ind_nifty50list.csv",
        "fallback": FALLBACK_NIFTY50,
        "default_suffix": ".NS"
    },
    "NIFTY_NEXT_50": {
        "name": "Nifty Next 50 (NSE Junior)",
        "exchange": "NSE",
        "url": "https://archives.nseindia.com/content/indices/ind_niftynext50list.csv",
        "fallback": FALLBACK_NIFTY_NEXT50,
        "default_suffix": ".NS"
    },
    "NIFTY_100": {
        "name": "Nifty 100 (Top 100 Large-Cap)",
        "exchange": "NSE",
        "url": "https://archives.nseindia.com/content/indices/ind_nifty100list.csv",
        "fallback": FALLBACK_NIFTY50 + FALLBACK_NIFTY_NEXT50,
        "default_suffix": ".NS"
    },
    "NIFTY_MIDCAP_100": {
        "name": "Nifty Midcap 100",
        "exchange": "NSE",
        "url": "https://archives.nseindia.com/content/indices/ind_niftymidcap100list.csv",
        "fallback": FALLBACK_NIFTY_NEXT50,
        "default_suffix": ".NS"
    },
    "NIFTY_MIDCAP_150": {
        "name": "Nifty Midcap 150",
        "exchange": "NSE",
        "url": "https://archives.nseindia.com/content/indices/ind_niftymidcap150list.csv",
        "fallback": FALLBACK_NIFTY_NEXT50,
        "default_suffix": ".NS"
    },
    "NIFTY_SMALLCAP_100": {
        "name": "Nifty Smallcap 100",
        "exchange": "NSE",
        "url": "https://archives.nseindia.com/content/indices/ind_niftysmallcap100list.csv",
        "fallback": [],
        "default_suffix": ".NS"
    },
    "NIFTY_SMALLCAP_250": {
        "name": "Nifty Smallcap 250",
        "exchange": "NSE",
        "url": "https://archives.nseindia.com/content/indices/ind_niftysmallcap250list.csv",
        "fallback": [],
        "default_suffix": ".NS"
    },
    "NIFTY_500": {
        "name": "Nifty 500 (Broad Market)",
        "exchange": "NSE",
        "url": "https://archives.nseindia.com/content/indices/ind_nifty500list.csv",
        "fallback": FALLBACK_NIFTY50 + FALLBACK_NIFTY_NEXT50,
        "default_suffix": ".NS"
    },
    "BSE_SENSEX": {
        "name": "BSE Sensex 30",
        "exchange": "BSE",
        "url": None,
        "fallback": FALLBACK_BSE_SENSEX,
        "default_suffix": ".BO"
    },
    "US_MEGA": {
        "name": "US Megacap Top Equities",
        "exchange": "US",
        "url": None,
        "fallback": FALLBACK_US_MEGA,
        "default_suffix": ""
    }
}


class IndexManager:
    _cache: Dict[str, List[str]] = {}

    @classmethod
    def get_universes(cls) -> List[Dict]:
        return [
            {
                "id": k,
                "name": v["name"],
                "exchange": v["exchange"],
                "count": len(v["fallback"]) if k not in cls._cache else len(cls._cache[k])
            }
            for k, v in UNIVERSE_METADATA.items()
        ]

    @classmethod
    def get_tickers(cls, universe_id: str = "NIFTY_50") -> List[str]:
        universe_id = universe_id.upper()
        if universe_id in cls._cache:
            return cls._cache[universe_id]

        meta = UNIVERSE_METADATA.get(universe_id, UNIVERSE_METADATA["NIFTY_50"])
        url = meta.get("url")
        suffix = meta.get("default_suffix", ".NS")

        if url:
            try:
                headers = {
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                }
                resp = requests.get(url, headers=headers, timeout=8)
                if resp.status_code == 200:
                    df = pd.read_csv(io.StringIO(resp.text))
                    col_name = "Symbol" if "Symbol" in df.columns else df.columns[2]
                    tickers = [f"{sym.strip()}{suffix}" for sym in df[col_name] if isinstance(sym, str)]
                    if tickers:
                        cls._cache[universe_id] = tickers
                        return tickers
            except Exception as e:
                print(f"[IndexManager] Notice: Error downloading {universe_id} list: {e}. Using fallback universe.")

        fallback = meta.get("fallback", FALLBACK_NIFTY50)
        cls._cache[universe_id] = fallback
        return fallback
