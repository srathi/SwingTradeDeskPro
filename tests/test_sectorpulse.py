"""
Unit Tests for SectorPulse Package.
Validates Mansfield RS, Hurst Exponent, Markov Duration, and JSON Contract Schema Conformity.
"""

import pytest
import numpy as np
import pandas as pd
from datetime import datetime

from sectorpulse.indicators import calculate_mansfield_rs, compute_adx, compute_atr, compute_sector_indicators
from sectorpulse.persistence import calculate_hurst_exponent, compute_markov_regime_duration
from sectorpulse.foundation_forecaster import ChronosForecaster
from sectorpulse.engine import SectorPulseEngine


@pytest.fixture
def synthetic_market_data():
    """
    Generates 200 trading bars for benchmark and an outperforming sector.
    """
    dates = pd.date_range(start="2025-01-01", periods=200, freq="B")
    np.random.seed(42)

    # Benchmark: Steady 10% drift
    bench_returns = np.random.normal(0.0005, 0.01, size=200)
    bench_close = 20000.0 * np.cumprod(1 + bench_returns)
    bench_df = pd.DataFrame({
        "Open": bench_close * 0.998,
        "High": bench_close * 1.005,
        "Low": bench_close * 0.995,
        "Close": bench_close,
        "Volume": 10_000_000
    }, index=dates)

    # Outperforming Sector: 25% drift (Strong Stage 2 Markup)
    sec_returns = np.random.normal(0.0012, 0.012, size=200)
    sec_close = 5000.0 * np.cumprod(1 + sec_returns)
    sec_df = pd.DataFrame({
        "Open": sec_close * 0.997,
        "High": sec_close * 1.008,
        "Low": sec_close * 0.994,
        "Close": sec_close,
        "Volume": 5_000_000
    }, index=dates)

    return bench_df, sec_df


def test_mansfield_rs_calculation(synthetic_market_data):
    bench_df, sec_df = synthetic_market_data
    mrs = calculate_mansfield_rs(sec_df["Close"], bench_df["Close"], lookback_period=50)

    assert isinstance(mrs, pd.Series)
    assert len(mrs) == len(sec_df)
    assert not mrs.isna().any()
    # Outperforming sector should have positive Mansfield RS towards end of series
    assert mrs.iloc[-1] > 0.0


def test_hurst_exponent_trending():
    np.random.seed(42)
    # Autocorrelated momentum series
    shocks = np.random.normal(0.001, 0.01, 500)
    for i in range(1, 500):
        shocks[i] += 0.55 * shocks[i - 1]
    trending_series = pd.Series(100.0 * np.exp(np.cumsum(shocks)))
    h_trend = calculate_hurst_exponent(trending_series)
    assert h_trend > 0.50, f"Expected H > 0.50 for trending series, got {h_trend}"


def test_markov_regime_duration():
    # Test steady uptrend states
    mrs = pd.Series([1.0, 2.0, 3.5, 4.0, 4.5, 5.0] * 10)
    ma_hier = pd.Series([3] * 60)

    res = compute_markov_regime_duration(mrs, ma_hier)
    assert res["current_state"] == "UPTREND"
    assert res["expected_total_duration_days"] >= 10
    assert res["estimated_remaining_days"] >= 1


def test_chronos_forecaster_fallback():
    forecaster = ChronosForecaster(prediction_length=30, num_samples=50)
    mrs_series = pd.Series(np.linspace(0, 10, 100))
    res = forecaster.forecast_relative_strength(mrs_series)

    assert res.median_peak_horizon_days >= 1
    assert 0.0 <= res.exhaustion_probability <= 1.0
    assert len(res.forecast_trajectories) == 3


def test_strict_json_contract_conformity(synthetic_market_data):
    bench_df, sec_df = synthetic_market_data
    engine = SectorPulseEngine()
    result = engine.analyze_sector("^TESTSEC", sec_df, bench_df, sector_name="Test Sector")

    # Verify top-level contract keys
    assert "timestamp" in result
    assert "sector" in result
    assert "regime" in result
    assert "duration_forecast" in result
    assert "risk_parameters" in result
    assert "trade_recommendation" in result

    # Verify regime block
    regime = result["regime"]
    assert regime["trend_classification"] in [
        "STRONG_UPTREND", "EARLY_UPTREND", "NEUTRAL_RANGE", "EARLY_DOWNTREND", "STRONG_DOWNTREND"
    ]
    assert isinstance(regime["mrs_score"], float)
    assert isinstance(regime["mrs_slope_5d"], float)
    assert isinstance(regime["adx_14"], float)
    assert isinstance(regime["hurst_exponent"], float)

    # Verify duration forecast block
    df_block = result["duration_forecast"]
    assert isinstance(df_block["current_regime_age_days"], int)
    assert isinstance(df_block["expected_total_duration_days"], int)
    assert isinstance(df_block["estimated_remaining_days"], int)
    assert isinstance(df_block["chronos_median_peak_horizon_days"], int)
    assert isinstance(df_block["exhaustion_probability"], float)

    # Verify risk parameters block
    risk = result["risk_parameters"]
    assert isinstance(risk["atr_14"], float)
    assert isinstance(risk["trailing_stop_level"], float)
    assert isinstance(risk["overextension_flag"], bool)

    # Verify trade recommendation block
    trade = result["trade_recommendation"]
    assert isinstance(trade["action"], str)
    assert isinstance(trade["sector_weight_multiplier"], float)
