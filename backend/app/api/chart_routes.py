"""
Chart Data Routes formatted for TradingView Lightweight Charts.
"""

from typing import Optional
import math
import pandas as pd
from fastapi import APIRouter, HTTPException
from backend.app.core.data_engine import data_engine
from backend.app.core.indicator_engine import compute_all_indicators
from backend.app.strategies import STRATEGY_REGISTRY

router = APIRouter(prefix="/api/chart", tags=["Chart"])


@router.get("/{ticker}")
def get_chart_data(
    ticker: str,
    period: str = "1y",
    strategy_id: Optional[str] = "trend_pullback"
):
    """
    Returns candlestick series, indicator series, and setup overlays for a given ticker.
    """
    df = data_engine.fetch_ticker_data(ticker, period=period, interval="1d")
    if df is None or len(df) < 15:
        raise HTTPException(status_code=404, detail=f"No price data available for ticker '{ticker}'")

    # Clean, deduplicate and sort
    df = df[~df.index.duplicated(keep='first')].sort_index()
    data = compute_all_indicators(df)

    candles = []
    volumes = []
    ema20_series = []
    ema50_series = []
    ema200_series = []
    bb_upper_series = []
    bb_lower_series = []
    rsi_series = []

    seen_dates = set()

    for i in range(len(data)):
        bar = data.iloc[i]
        date_str = data.index[i].strftime("%Y-%m-%d") if hasattr(data.index[i], "strftime") else str(data.index[i])[:10]
        if date_str in seen_dates:
            continue
        seen_dates.add(date_str)

        open_p = float(bar['Open'])
        close_p = float(bar['Close'])
        high_p = float(bar['High'])
        low_p = float(bar['Low'])
        vol = float(bar['Volume'])

        if math.isnan(open_p) or math.isnan(close_p) or math.isnan(high_p) or math.isnan(low_p):
            continue

        candles.append({
            "time": date_str,
            "open": round(open_p, 2),
            "high": round(high_p, 2),
            "low": round(low_p, 2),
            "close": round(close_p, 2)
        })

        is_green = close_p >= open_p
        volumes.append({
            "time": date_str,
            "value": 0 if math.isnan(vol) else vol,
            "color": "rgba(34, 197, 94, 0.4)" if is_green else "rgba(239, 68, 68, 0.4)"
        })

        if not pd.isna(bar.get('EMA_20')) and not math.isnan(float(bar['EMA_20'])):
            ema20_series.append({"time": date_str, "value": round(float(bar['EMA_20']), 2)})
        if not pd.isna(bar.get('EMA_50')) and not math.isnan(float(bar['EMA_50'])):
            ema50_series.append({"time": date_str, "value": round(float(bar['EMA_50']), 2)})
        if not pd.isna(bar.get('EMA_200')) and not math.isnan(float(bar['EMA_200'])):
            ema200_series.append({"time": date_str, "value": round(float(bar['EMA_200']), 2)})

        if not pd.isna(bar.get('BB_Upper')) and not math.isnan(float(bar['BB_Upper'])):
            bb_upper_series.append({"time": date_str, "value": round(float(bar['BB_Upper']), 2)})
        if not pd.isna(bar.get('BB_Lower')) and not math.isnan(float(bar['BB_Lower'])):
            bb_lower_series.append({"time": date_str, "value": round(float(bar['BB_Lower']), 2)})

        if not pd.isna(bar.get('RSI_14')) and not math.isnan(float(bar['RSI_14'])):
            rsi_series.append({"time": date_str, "value": round(float(bar['RSI_14']), 1)})

    # Evaluate if there is an active setup right now
    active_setup = None
    if strategy_id and strategy_id in STRATEGY_REGISTRY:
        strat = STRATEGY_REGISTRY[strategy_id]
        active_setup = strat.evaluate_setup(df, ticker)

    latest_bar = data.iloc[-1]
    latest_close = round(float(latest_bar['Close']), 2)
    prev_close = round(float(data.iloc[-2]['Close']), 2) if len(data) >= 2 else latest_close
    change_pct = round(((latest_close - prev_close) / prev_close) * 100.0, 2) if prev_close != 0 else 0.0

    return {
        "ticker": ticker,
        "latest_close": latest_close,
        "change_pct": change_pct,
        "candles": candles,
        "volume": volumes,
        "ema20": ema20_series,
        "ema50": ema50_series,
        "ema200": ema200_series,
        "bb_upper": bb_upper_series,
        "bb_lower": bb_lower_series,
        "rsi": rsi_series,
        "active_setup": active_setup
    }
