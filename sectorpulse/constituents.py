"""
Sector Constituents and Relative Strength Leader Ranker.
Maps sector indices to their heavyweight liquid constituent stocks,
computes technical metrics, trend stages, and active setups, and ranks them by merit.
"""

from typing import List, Dict, Any, Optional
import numpy as np
import pandas as pd
import logging

from backend.app.core.data_engine import data_engine
from backend.app.core.indicator_engine import compute_all_indicators
from backend.app.strategies import STRATEGY_REGISTRY

logger = logging.getLogger("SectorPulse.Constituents")

SECTOR_CONSTITUENTS_MAP: Dict[str, List[Dict[str, str]]] = {
    # NSE Sectors
    "^NSEBANK": [
        {"symbol": "HDFCBANK.NS", "name": "HDFC Bank", "weight": "28%"},
        {"symbol": "ICICIBANK.NS", "name": "ICICI Bank", "weight": "24%"},
        {"symbol": "SBIN.NS", "name": "State Bank of India", "weight": "12%"},
        {"symbol": "KOTAKBANK.NS", "name": "Kotak Mahindra Bank", "weight": "11%"},
        {"symbol": "AXISBANK.NS", "name": "Axis Bank", "weight": "10%"},
        {"symbol": "INDUSINDBK.NS", "name": "IndusInd Bank", "weight": "5%"}
    ],
    "^CNXIT": [
        {"symbol": "TCS.NS", "name": "TCS", "weight": "25%"},
        {"symbol": "INFY.NS", "name": "Infosys", "weight": "25%"},
        {"symbol": "HCLTECH.NS", "name": "HCL Tech", "weight": "14%"},
        {"symbol": "WIPRO.NS", "name": "Wipro", "weight": "8%"},
        {"symbol": "TECHM.NS", "name": "Tech Mahindra", "weight": "6%"}
    ],
    "^CNXAUTO": [
        {"symbol": "M&M.NS", "name": "Mahindra & Mahindra", "weight": "20%"},
        {"symbol": "MARUTI.NS", "name": "Maruti Suzuki", "weight": "18%"},
        {"symbol": "TATAMOTORS.NS", "name": "Tata Motors", "weight": "17%"},
        {"symbol": "BAJAJ-AUTO.NS", "name": "Bajaj Auto", "weight": "10%"},
        {"symbol": "EICHERMOT.NS", "name": "Eicher Motors", "weight": "8%"},
        {"symbol": "TVSMOTOR.NS", "name": "TVS Motor", "weight": "6%"}
    ],
    "^CNXPHARMA": [
        {"symbol": "SUNPHARMA.NS", "name": "Sun Pharma", "weight": "23%"},
        {"symbol": "CIPLA.NS", "name": "Cipla", "weight": "13%"},
        {"symbol": "DRREDDY.NS", "name": "Dr. Reddy's Labs", "weight": "12%"},
        {"symbol": "DIVISLAB.NS", "name": "Divi's Laboratories", "weight": "10%"},
        {"symbol": "TORNTPHARM.NS", "name": "Torrent Pharma", "weight": "8%"},
        {"symbol": "APOLLOHOSP.NS", "name": "Apollo Hospitals", "weight": "8%"}
    ],
    "^CNXFMCG": [
        {"symbol": "ITC.NS", "name": "ITC Ltd", "weight": "32%"},
        {"symbol": "HINDUNILVR.NS", "name": "Hindustan Unilever", "weight": "22%"},
        {"symbol": "NESTLEIND.NS", "name": "Nestle India", "weight": "9%"},
        {"symbol": "BRITANNIA.NS", "name": "Britannia Industries", "weight": "7%"},
        {"symbol": "TATACONSUM.NS", "name": "Tata Consumer", "weight": "6%"},
        {"symbol": "VBL.NS", "name": "Varun Beverages", "weight": "5%"}
    ],
    "^CNXMETAL": [
        {"symbol": "TATASTEEL.NS", "name": "Tata Steel", "weight": "24%"},
        {"symbol": "JSWSTEEL.NS", "name": "JSW Steel", "weight": "20%"},
        {"symbol": "HINDALCO.NS", "name": "Hindalco Industries", "weight": "16%"},
        {"symbol": "VEDL.NS", "name": "Vedanta Ltd", "weight": "12%"},
        {"symbol": "JINDALSTEL.NS", "name": "Jindal Steel & Power", "weight": "10%"},
        {"symbol": "COALINDIA.NS", "name": "Coal India", "weight": "8%"}
    ],
    "^CNXREALTY": [
        {"symbol": "DLF.NS", "name": "DLF Ltd", "weight": "32%"},
        {"symbol": "GODREJPROP.NS", "name": "Godrej Properties", "weight": "18%"},
        {"symbol": "OBEROIRLTY.NS", "name": "Oberoi Realty", "weight": "14%"},
        {"symbol": "PHOENIXLTD.NS", "name": "Phoenix Mills", "weight": "12%"},
        {"symbol": "PRESTIGE.NS", "name": "Prestige Estates", "weight": "10%"},
        {"symbol": "BRIGADE.NS", "name": "Brigade Enterprises", "weight": "6%"}
    ],
    "^CNXENERGY": [
        {"symbol": "RELIANCE.NS", "name": "Reliance Industries", "weight": "33%"},
        {"symbol": "NTPC.NS", "name": "NTPC Ltd", "weight": "15%"},
        {"symbol": "ONGC.NS", "name": "Oil & Natural Gas Corp", "weight": "12%"},
        {"symbol": "POWERGRID.NS", "name": "Power Grid Corp", "weight": "11%"},
        {"symbol": "BPCL.NS", "name": "Bharat Petroleum", "weight": "7%"},
        {"symbol": "IOC.NS", "name": "Indian Oil Corp", "weight": "6%"}
    ],
    "^CNXINFRA": [
        {"symbol": "LT.NS", "name": "Larsen & Toubro", "weight": "25%"},
        {"symbol": "ADANIPORTS.NS", "name": "Adani Ports & SEZ", "weight": "15%"},
        {"symbol": "ULTRACEMCO.NS", "name": "UltraTech Cement", "weight": "12%"},
        {"symbol": "BHARTIARTL.NS", "name": "Bharti Airtel", "weight": "12%"},
        {"symbol": "GRASIM.NS", "name": "Grasim Industries", "weight": "8%"},
        {"symbol": "BEL.NS", "name": "Bharat Electronics", "weight": "8%"}
    ],
    "^CNXPSUBANK": [
        {"symbol": "SBIN.NS", "name": "State Bank of India", "weight": "35%"},
        {"symbol": "BANKBARODA.NS", "name": "Bank of Baroda", "weight": "20%"},
        {"symbol": "PNB.NS", "name": "Punjab National Bank", "weight": "15%"},
        {"symbol": "CANBK.NS", "name": "Canara Bank", "weight": "12%"},
        {"symbol": "UNIONBANK.NS", "name": "Union Bank of India", "weight": "8%"}
    ],
    "^CNXMEDIA": [
        {"symbol": "ZEEL.NS", "name": "Zee Entertainment", "weight": "35%"},
        {"symbol": "SUNTV.NS", "name": "Sun TV Network", "weight": "25%"},
        {"symbol": "PVRINOX.NS", "name": "PVR INOX", "weight": "22%"},
        {"symbol": "NAZARA.NS", "name": "Nazara Technologies", "weight": "10%"},
        {"symbol": "NETWORK18.NS", "name": "Network18 Media", "weight": "8%"}
    ],
    # US Sectors
    "XLK": [
        {"symbol": "AAPL", "name": "Apple Inc", "weight": "22%"},
        {"symbol": "MSFT", "name": "Microsoft Corp", "weight": "21%"},
        {"symbol": "NVDA", "name": "NVIDIA Corp", "weight": "18%"},
        {"symbol": "AVGO", "name": "Broadcom Inc", "weight": "5%"},
        {"symbol": "AMD", "name": "Advanced Micro Devices", "weight": "4%"}
    ],
    "XLF": [
        {"symbol": "BRK-B", "name": "Berkshire Hathaway", "weight": "13%"},
        {"symbol": "JPM", "name": "JPMorgan Chase", "weight": "10%"},
        {"symbol": "V", "name": "Visa Inc", "weight": "8%"},
        {"symbol": "MA", "name": "Mastercard Inc", "weight": "7%"},
        {"symbol": "BAC", "name": "Bank of America", "weight": "4%"}
    ],
    "XLE": [
        {"symbol": "XOM", "name": "Exxon Mobil", "weight": "23%"},
        {"symbol": "CVX", "name": "Chevron Corp", "weight": "16%"},
        {"symbol": "EOG", "name": "EOG Resources", "weight": "5%"},
        {"symbol": "COP", "name": "ConocoPhillips", "weight": "8%"},
        {"symbol": "SLB", "name": "Schlumberger", "weight": "5%"}
    ],
    "XLV": [
        {"symbol": "LLY", "name": "Eli Lilly", "weight": "12%"},
        {"symbol": "UNH", "name": "UnitedHealth Group", "weight": "9%"},
        {"symbol": "JNJ", "name": "Johnson & Johnson", "weight": "7%"},
        {"symbol": "ABBV", "name": "AbbVie Inc", "weight": "6%"},
        {"symbol": "MRK", "name": "Merck & Co", "weight": "5%"}
    ],
    "XLY": [
        {"symbol": "AMZN", "name": "Amazon.com", "weight": "24%"},
        {"symbol": "TSLA", "name": "Tesla Inc", "weight": "14%"},
        {"symbol": "HD", "name": "Home Depot", "weight": "9%"},
        {"symbol": "MCD", "name": "McDonald's Corp", "weight": "5%"},
        {"symbol": "NKE", "name": "Nike Inc", "weight": "3%"}
    ],
    "XLC": [
        {"symbol": "META", "name": "Meta Platforms", "weight": "24%"},
        {"symbol": "GOOGL", "name": "Alphabet Class A", "weight": "12%"},
        {"symbol": "GOOG", "name": "Alphabet Class C", "weight": "11%"},
        {"symbol": "NFLX", "name": "Netflix Inc", "weight": "6%"},
        {"symbol": "DIS", "name": "Walt Disney", "weight": "4%"}
    ]
}


def get_sector_top_constituents(sector_ticker: str, limit: int = 5) -> List[Dict[str, Any]]:
    """
    Ranks top constituents of a sector by merit, momentum, technical stage, and active swing setups.
    """
    constituents = SECTOR_CONSTITUENTS_MAP.get(sector_ticker, [])
    if not constituents:
        return []

    ranked = []
    for c in constituents:
        sym = c["symbol"]
        try:
            df = data_engine.fetch_ticker_data(sym, period="1y", interval="1d")
            if df is not None and len(df) >= 30:
                data = compute_all_indicators(df)
                latest = data.iloc[-1]
                prev = data.iloc[-2] if len(data) >= 2 else latest
                
                close = float(latest["Close"])
                prev_c = float(prev["Close"])
                chg_pct = round(((close - prev_c) / prev_c) * 100.0, 2) if prev_c > 0 else 0.0
                
                ema20 = float(latest.get("EMA_20", close))
                ema50 = float(latest.get("EMA_50", close))
                ema200 = float(latest.get("EMA_200", ema50))
                rsi_val = round(float(latest.get("RSI_14", 50.0)), 1)
                
                # Technical Stage Identification
                if close > ema50 and ema50 > ema200:
                    stage = "Stage 2 Bull"
                    stage_type = "bull"
                    merit_base = 75.0
                elif close > ema50:
                    stage = "Early Trend"
                    stage_type = "early"
                    merit_base = 60.0
                elif close < ema50 and ema50 < ema200:
                    stage = "Stage 4 Bear"
                    stage_type = "bear"
                    merit_base = 30.0
                else:
                    stage = "Consolidation"
                    stage_type = "neutral"
                    merit_base = 45.0
                
                # Momentum adjustment
                rsi_boost = (rsi_val - 50.0) * 0.4
                trend_dist = min(15.0, max(-15.0, ((close - ema50) / ema50) * 100.0))
                merit_score = merit_base + rsi_boost + trend_dist
                
                # Check for active setups in strategy registry
                active_setup = None
                setup_score = 0
                for s_id in ["trend_pullback", "vcp_breakout", "relative_strength_leader", "mean_reversion"]:
                    st = STRATEGY_REGISTRY.get(s_id)
                    if st:
                        setup = st.evaluate_setup(df, sym)
                        if setup:
                            active_setup = setup.get("strategy")
                            setup_score = setup.get("score", 70)
                            merit_score += 15.0
                            break

                ranked.append({
                    "symbol": sym,
                    "name": c["name"],
                    "weight": c["weight"],
                    "close": round(close, 2),
                    "change_pct": chg_pct,
                    "rsi": rsi_val,
                    "stage": stage,
                    "stage_type": stage_type,
                    "active_setup": active_setup,
                    "setup_score": setup_score,
                    "merit_score": round(max(10.0, min(99.0, merit_score)), 1)
                })
        except Exception as e:
            logger.debug(f"Could not compute constituent metrics for {sym}: {e}")
            continue

    # Sort descending by Merit Score (highest quality / strongest momentum first)
    ranked.sort(key=lambda x: x["merit_score"], reverse=True)
    return ranked[:limit]
