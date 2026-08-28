"""
Dynamic Risk-Adaptive Exit Modeling & Fractional Kelly Position Sizing.
Academic Foundation: Chuck LeBeau (Chandelier Exits), Ed Thorp (The Kelly Criterion), Marcos Lopez de Prado (Triple Barrier Method).
"""

from typing import Dict, Any, Optional
import math
import numpy as np
import pandas as pd


def compute_chandelier_exit(
    df: pd.DataFrame,
    lookback: int = 22,
    atr_multiplier: float = 3.0
) -> Dict[str, Any]:
    """
    Computes Chuck LeBeau Chandelier Trailing Stop.
    Trails the highest high of the last N bars minus k * ATR(14).
    """
    if df is None or len(df) < lookback + 14:
        return {"current_stop": 0.0, "highest_high": 0.0, "atr_14": 0.0}

    from backend.app.core.indicator_engine import atr
    atr_series = atr(df['High'], df['Low'], df['Close'], 14)
    highest_high = float(df['High'].iloc[-lookback:].max())
    latest_atr = float(atr_series.iloc[-1])
    latest_close = float(df['Close'].iloc[-1])

    stop_price = round(highest_high - (atr_multiplier * latest_atr), 2)
    dist_pct = round(((latest_close - stop_price) / latest_close) * 100.0, 2)

    return {
        "chandelier_stop": stop_price,
        "highest_high_period": round(highest_high, 2),
        "atr_14": round(latest_atr, 2),
        "dist_to_stop_pct": dist_pct,
        "lookback_bars": lookback,
        "multiplier": atr_multiplier,
        "is_breached": latest_close < stop_price
    }


def compute_fractional_kelly_sizing(
    win_rate: float = 0.58,
    payoff_ratio: float = 2.0,
    total_capital: float = 500000.0,
    risk_per_trade_pct: float = 1.0,
    entry_price: float = 100.0,
    stop_loss_price: float = 95.0
) -> Dict[str, Any]:
    """
    Computes conservative Half-Kelly position sizing and triple barrier risk metrics.
    """
    w = max(0.01, min(0.99, win_rate))
    b = max(0.1, payoff_ratio)
    
    # Full Kelly: (w * (b + 1) - 1) / b
    full_kelly = (w * (b + 1.0) - 1.0) / b
    
    # Half-Kelly with safety bounds [5%, 25%] of portfolio
    if full_kelly > 0:
        half_kelly = full_kelly * 0.5
        recommended_allocation_pct = round(max(5.0, min(25.0, half_kelly * 100.0)), 1)
    else:
        recommended_allocation_pct = 5.0

    risk_per_share = max(0.01, entry_price - stop_loss_price)
    capital_by_risk = (total_capital * (risk_per_trade_pct / 100.0)) / risk_per_share
    capital_by_kelly = (total_capital * (recommended_allocation_pct / 100.0)) / entry_price
    
    # Conservative minimum of fixed fractional risk and half-kelly allocation
    shares = int(min(capital_by_risk, capital_by_kelly))
    shares = max(1, shares)

    capital_required = round(shares * entry_price, 2)
    actual_allocation_pct = round((capital_required / total_capital) * 100.0, 1)
    actual_risk_amount = round(shares * risk_per_share, 2)

    return {
        "full_kelly_pct": round(full_kelly * 100.0, 1),
        "half_kelly_pct": round(max(0, full_kelly * 50.0), 1),
        "recommended_portfolio_allocation_pct": recommended_allocation_pct,
        "shares": shares,
        "capital_required": capital_required,
        "actual_portfolio_allocation_pct": actual_allocation_pct,
        "total_risk_amount": actual_risk_amount,
        "risk_per_share": round(risk_per_share, 2),
        "triple_barriers": {
            "upper_target_1": round(entry_price + (1.5 * risk_per_share), 2),
            "upper_target_2": round(entry_price + (2.5 * risk_per_share), 2),
            "lower_stop_loss": round(stop_loss_price, 2),
            "time_expiration_sessions": 15,
            "time_barrier_rule": "Exit or reallocate if price fails to reach Target 1 within 15 trading sessions."
        }
    }
