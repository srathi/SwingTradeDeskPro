"""
Unit tests for GMMA Weekly Breakout Strategy and Guppy Ribbon indicators.
"""

import pytest
import numpy as np
import pandas as pd
from backend.app.core.indicator_engine import gmma_ribbons, resample_weekly
from backend.app.strategies.gmma_breakout import GMMABreakoutStrategy
from backend.app.strategies import STRATEGY_REGISTRY


def generate_synthetic_trending_ohlcv(bars: int = 250) -> pd.DataFrame:
    """Generates synthetic trending equity time series."""
    dates = pd.date_range(start="2023-01-01", periods=bars, freq="B")
    np.random.seed(42)
    returns = np.random.normal(0.0015, 0.015, size=bars)
    prices = 1000.0 * np.exp(np.cumsum(returns))

    df = pd.DataFrame({
        "Open": prices * 0.995,
        "High": prices * 1.015,
        "Low": prices * 0.985,
        "Close": prices,
        "Volume": np.random.randint(500_000, 2_000_000, size=bars)
    }, index=dates)
    return df


def test_gmma_ribbon_structure():
    prices = pd.Series(np.linspace(100, 200, 100))
    fast_ribbon, slow_ribbon = gmma_ribbons(prices)

    assert len(fast_ribbon) == 6, "Fast ribbon must contain 6 EMAs (3, 5, 8, 10, 12, 15)"
    assert len(slow_ribbon) == 6, "Slow ribbon must contain 6 EMAs (30, 35, 40, 45, 50, 60)"
    assert "EMA_3" in fast_ribbon and "EMA_15" in fast_ribbon
    assert "EMA_30" in slow_ribbon and "EMA_60" in slow_ribbon


def test_gmma_strategy_registration():
    assert "gmma_breakout" in STRATEGY_REGISTRY, "gmma_breakout must be registered in STRATEGY_REGISTRY"
    strat = STRATEGY_REGISTRY["gmma_breakout"]
    assert isinstance(strat, GMMABreakoutStrategy)
    assert strat.strategy_id == "gmma_breakout"


def test_gmma_evaluate_setup_math():
    df = generate_synthetic_trending_ohlcv(300)
    strat = GMMABreakoutStrategy()
    setup = strat.evaluate_setup(df, "TEST.NS")

    if setup:
        assert setup["close"] > 0
        assert setup["stop_loss"] < setup["close"], "Stop Loss must be strictly below Entry on Longs"
        assert setup["target_1"] > setup["close"], "Target 1 must be strictly above Entry"
        assert setup["target_2"] > setup["target_1"], "Target 2 must be strictly above Target 1"
        assert 0 <= setup["score"] <= 100, "Score must be bounded between 0 and 100"
        assert setup["r_multiple_t1"] >= 2.0, "Target 1 must provide at least 2:1 R:R"


def test_gmma_generate_signals_backtest():
    df = generate_synthetic_trending_ohlcv(200)
    strat = GMMABreakoutStrategy()
    signals_df = strat.generate_signals(df)

    assert "Signal" in signals_df.columns
    assert "Stop_Loss" in signals_df.columns
    assert "Target_1" in signals_df.columns
    assert "Target_2" in signals_df.columns
