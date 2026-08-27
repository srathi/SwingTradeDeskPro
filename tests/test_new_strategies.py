import pytest
import numpy as np
import pandas as pd
from backend.app.strategies import STRATEGY_REGISTRY
from backend.app.strategies.pocket_pivot import PocketPivotStrategy
from backend.app.strategies.wyckoff_spring import WyckoffSpringStrategy
from backend.app.strategies.nr7_expansion import NR7ExpansionStrategy


def generate_synthetic_ohlcv(n: int = 150) -> pd.DataFrame:
    np.random.seed(42)
    dates = pd.date_range("2025-01-01", periods=n, freq="D")
    base = 100.0 + np.cumsum(np.random.randn(n) * 0.8)
    
    df = pd.DataFrame({
        "Open": base + np.random.randn(n) * 0.2,
        "High": base + np.abs(np.random.randn(n) * 1.5) + 0.5,
        "Low": base - np.abs(np.random.randn(n) * 1.5) - 0.5,
        "Close": base + np.random.randn(n) * 0.4,
        "Volume": np.random.randint(150_000, 800_000, size=n)
    }, index=dates)
    
    df["High"] = df[["Open", "Close", "High"]].max(axis=1) + 0.2
    df["Low"] = df[["Open", "Close", "Low"]].min(axis=1) - 0.2
    return df


def test_strategy_registrations():
    assert "pocket_pivot" in STRATEGY_REGISTRY
    assert "wyckoff_spring" in STRATEGY_REGISTRY
    assert "nr7_expansion" in STRATEGY_REGISTRY
    
    assert isinstance(STRATEGY_REGISTRY["pocket_pivot"], PocketPivotStrategy)
    assert isinstance(STRATEGY_REGISTRY["wyckoff_spring"], WyckoffSpringStrategy)
    assert isinstance(STRATEGY_REGISTRY["nr7_expansion"], NR7ExpansionStrategy)


def test_pocket_pivot_signals_backtest():
    strat = PocketPivotStrategy()
    df = generate_synthetic_ohlcv(120)
    res = strat.generate_signals(df)
    
    assert "Signal" in res.columns
    assert "Stop_Loss" in res.columns
    assert "Target_1" in res.columns
    assert "Target_2" in res.columns


def test_wyckoff_spring_signals_backtest():
    strat = WyckoffSpringStrategy()
    df = generate_synthetic_ohlcv(120)
    res = strat.generate_signals(df)
    
    assert "Signal" in res.columns
    assert "Stop_Loss" in res.columns
    assert "Target_1" in res.columns
    assert "Target_2" in res.columns


def test_nr7_expansion_signals_backtest():
    strat = NR7ExpansionStrategy()
    df = generate_synthetic_ohlcv(120)
    res = strat.generate_signals(df)
    
    assert "Signal" in res.columns
    assert "Stop_Loss" in res.columns
    assert "Target_1" in res.columns
    assert "Target_2" in res.columns
