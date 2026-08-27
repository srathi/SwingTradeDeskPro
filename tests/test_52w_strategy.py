"""
Unit tests for 52-Week High Breakout Strategy (George & Hwang 2004 / Minervini SEPA).
"""

import pytest
import numpy as np
import pandas as pd
from backend.app.strategies.high_52w_breakout import High52WBreakoutStrategy
from backend.app.strategies import STRATEGY_REGISTRY


def generate_synthetic_breakout_ohlcv(bars: int = 300) -> pd.DataFrame:
    """Generates synthetic equity time series breaking to new 52-week high."""
    dates = pd.date_range(start="2023-01-01", periods=bars, freq="B")
    np.random.seed(42)
    # Steady uptrend reaching all-time high on latest bar
    returns = np.random.normal(0.002, 0.012, size=bars)
    prices = 500.0 * np.exp(np.cumsum(returns))
    
    # Ensure latest bar breaks out with strong volume
    prices[-1] = prices[:-1].max() * 1.02

    volumes = np.random.randint(500_000, 1_500_000, size=bars)
    volumes[-1] = 3_000_000 # 2x volume surge

    df = pd.DataFrame({
        "Open": prices * 0.995,
        "High": prices * 1.01,
        "Low": prices * 0.99,
        "Close": prices,
        "Volume": volumes
    }, index=dates)
    return df


def test_52w_strategy_registration():
    assert "high_52w_breakout" in STRATEGY_REGISTRY, "high_52w_breakout must be in STRATEGY_REGISTRY"
    strat = STRATEGY_REGISTRY["high_52w_breakout"]
    assert isinstance(strat, High52WBreakoutStrategy)
    assert strat.strategy_id == "high_52w_breakout"


def test_52w_evaluate_setup_math():
    df = generate_synthetic_breakout_ohlcv(300)
    strat = High52WBreakoutStrategy()
    setup = strat.evaluate_setup(df, "TEST_LEADER.NS")

    assert setup is not None, "Breakout setup should be triggered on synthetic 52W high breakout"
    assert setup["close"] > 0
    assert setup["stop_loss"] < setup["close"], "Stop Loss must be strictly below Entry"
    assert setup["target_1"] > setup["close"], "Target 1 must be strictly above Entry"
    assert setup["target_2"] > setup["target_1"], "Target 2 must be strictly above Target 1"
    assert 60 <= setup["score"] <= 100, "Score must be bounded between 60 and 100"
    assert setup["r_multiple_t1"] >= 2.0, "Target 1 must provide at least 2:1 R:R"


def test_52w_generate_signals_backtest():
    df = generate_synthetic_breakout_ohlcv(300)
    strat = High52WBreakoutStrategy()
    signals_df = strat.generate_signals(df)

    assert "Signal" in signals_df.columns
    assert "Stop_Loss" in signals_df.columns
    assert "Target_1" in signals_df.columns
    assert "Target_2" in signals_df.columns
    assert signals_df["Signal"].sum() >= 1, "Should generate at least one historical breakout signal"
