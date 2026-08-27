"""
Unit and integration tests for Kronos Financial Foundation Model AI Engine and API routes.
"""

import pytest
import numpy as np
import pandas as pd
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.ai_engine.kronos_engine import kronos_engine


@pytest.fixture
def sample_ohlcv_df():
    """Generate 200 bars of synthetic OHLCV data."""
    np.random.seed(42)
    dates = pd.date_range(start="2025-01-01", periods=200, freq="B")
    close = 1000.0 + np.cumsum(np.random.normal(1.0, 15.0, size=200))
    close = np.maximum(close, 50.0)
    open_p = close + np.random.normal(0, 3.0, size=200)
    high = np.maximum(open_p, close) + np.abs(np.random.normal(5.0, 2.0, size=200))
    low = np.minimum(open_p, close) - np.abs(np.random.normal(5.0, 2.0, size=200))
    volume = np.random.randint(100000, 2000000, size=200)

    df = pd.DataFrame({
        "Open": open_p,
        "High": high,
        "Low": low,
        "Close": close,
        "Volume": volume
    }, index=dates)
    return df


def test_kronos_engine_status():
    status = kronos_engine.get_status()
    assert isinstance(status, dict)
    assert "device" in status
    assert "model_name" in status
    assert "cached_entries" in status


def test_kronos_engine_forecast(sample_ohlcv_df):
    pred_len = 15
    n_paths = 20
    res = kronos_engine.forecast(
        df=sample_ohlcv_df,
        ticker="TEST.NS",
        pred_len=pred_len,
        n_paths=n_paths,
        model_type="mini"
    )

    assert isinstance(res, dict)
    assert res["ticker"] == "TEST.NS"
    assert res["pred_len"] == pred_len
    assert res["n_paths"] == n_paths
    assert 0.0 <= res["upside_prob"] <= 100.0
    assert 0.0 <= res["upside_prob_raw"] <= 1.0
    assert "expected_close" in res
    assert "p10_close" in res
    assert "p90_close" in res
    assert res["p10_close"] <= res["p90_close"]
    assert "volatility_amplification" in res
    assert "confluence_badge" in res
    assert len(res["forecast_candles"]) == pred_len
    
    first_candle = res["forecast_candles"][0]
    assert "open" in first_candle
    assert "high" in first_candle
    assert "low" in first_candle
    assert "close" in first_candle
    assert "band_low" in first_candle
    assert "band_high" in first_candle


def test_ai_forecast_api_endpoints():
    client = TestClient(app)

    # 1. Model status endpoint
    status_resp = client.get("/api/ai/model-status")
    assert status_resp.status_code == 200
    status_data = status_resp.json()
    assert "device" in status_data

    # 2. Live Forecast endpoint with known large-cap
    forecast_resp = client.post("/api/ai/forecast", json={
        "ticker": "RELIANCE.NS",
        "pred_len": 15,
        "n_paths": 10,
        "model_type": "mini"
    })
    assert forecast_resp.status_code == 200
    data = forecast_resp.json()
    assert data["ticker"] == "RELIANCE.NS"
    assert len(data["forecast_candles"]) == 15
    assert data["upside_prob"] >= 0
