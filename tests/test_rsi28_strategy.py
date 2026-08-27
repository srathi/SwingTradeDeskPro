"""
Unit tests for RSI(28) Momentum Divergence Strategy.
"""

import pytest
import numpy as np
import pandas as pd
from backend.app.strategies.rsi28_divergence import RSI28DivergenceStrategy, find_swing_lows
from backend.app.strategies import STRATEGY_REGISTRY


def generate_synthetic_divergence_ohlcv(bars: int = 150) -> pd.DataFrame:
    """Generates synthetic equity time series with a clear bullish divergence."""
    dates = pd.date_range(start="2023-01-01", periods=bars, freq="B")
    
    # Create price pattern: High -> Low 1 (bar 100) -> Bounce -> Lower Low 2 (bar 130) -> Bullish candle
    prices = np.ones(bars) * 1000.0
    for i in range(100):
        prices[i] = 1000.0 - (i * 2.0) # downtrend to 800
    for i in range(100, 115):
        prices[i] = 800.0 + ((i - 100) * 3.0) # bounce to 845
    for i in range(115, 140):
        prices[i] = 845.0 - ((i - 115) * 3.0) # drift to lower low 770
    for i in range(140, bars):
        prices[i] = 770.0 + ((i - 140) * 4.0) # sharp reversal bounce

    df = pd.DataFrame({
        "Open": prices * 0.995,
        "High": prices * 1.01,
        "Low": prices * 0.985,
        "Close": prices,
        "Volume": np.random.randint(500_000, 1_500_000, size=bars)
    }, index=dates)
    return df


def test_rsi28_strategy_registration():
    assert "rsi28_divergence" in STRATEGY_REGISTRY, "rsi28_divergence must be registered in STRATEGY_REGISTRY"
    strat = STRATEGY_REGISTRY["rsi28_divergence"]
    assert isinstance(strat, RSI28DivergenceStrategy)
    assert strat.strategy_id == "rsi28_divergence"


def test_rsi28_swing_lows_helper():
    lows = np.array([100, 90, 80, 70, 60, 70, 80, 90, 100, 85, 75, 50, 65, 80, 95])
    rsi_vals = np.array([50, 45, 40, 35, 30, 35, 40, 45, 50, 42, 38, 32, 36, 42, 48])
    pivots = find_swing_lows(lows, rsi_vals, k=2)
    assert len(pivots) >= 2, "Should identify at least 2 swing low pivot troughs"


def test_rsi28_generate_signals_backtest():
    df = generate_synthetic_divergence_ohlcv(150)
    strat = RSI28DivergenceStrategy()
    signals_df = strat.generate_signals(df)

    assert "Signal" in signals_df.columns
    assert "Stop_Loss" in signals_df.columns
    assert "Target_1" in signals_df.columns
    assert "Target_2" in signals_df.columns
