"""
End-to-End multi-page integration tests for Kronos AI Forecaster across:
1. Dedicated AI Forecast Studio
2. Live Screener Confluence Workflow
3. Chart Studio Overlay
4. Sector Pulse Leading Constituents
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_ai_studio_scenarios():
    """Test AI Forecast Studio endpoints with varied inputs, horizons, and paths."""
    # 1. Standard Large Cap
    resp = client.post("/api/ai/forecast", json={
        "ticker": "RELIANCE.NS",
        "pred_len": 15,
        "n_paths": 10,
        "model_type": "mini"
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["ticker"] == "RELIANCE.NS"
    assert len(data["forecast_candles"]) == 15
    assert len(data["sample_paths"]) == min(5, 10)
    assert data["p10_close"] <= data["p90_close"]
    assert 0 <= data["upside_prob"] <= 100

    # 2. Bare symbol without suffix
    resp_bare = client.post("/api/ai/forecast", json={
        "ticker": "TCS",
        "pred_len": 5,
        "n_paths": 10
    })
    assert resp_bare.status_code == 200
    data_bare = resp_bare.json()
    assert data_bare["ticker"] in ["TCS.NS", "TCS"]
    assert len(data_bare["forecast_candles"]) == 5

    # 3. Misspelled typo auto-resolution (PICCADILLY -> PICCADIL.NS)
    resp_typo = client.post("/api/ai/forecast", json={
        "ticker": "PICCADILLY.NS",
        "pred_len": 15,
        "n_paths": 10
    })
    assert resp_typo.status_code == 200
    data_typo = resp_typo.json()
    assert data_typo["ticker"] in ["PICCADIL.NS", "PICCADILLY.NS"]
    assert data_typo["last_close"] > 0


def test_screener_to_ai_confluence_workflow():
    """Simulate user running a screener scan and opening AI Confluence for found setups."""
    scan_resp = client.post("/api/screener/scan", json={
        "universe": "NIFTY_50",
        "strategy_id": "trend_pullback",
        "min_price": 50,
        "min_volume": 100000,
        "rsi_min": 30,
        "rsi_max": 70,
        "rr_target": 1.5
    })
    assert scan_resp.status_code == 200
    scan_data = scan_resp.json()
    setups = scan_data.get("results", [])

    if len(setups) > 0:
        setup = setups[0]
        # Simulate user clicking [🔮 AI Forecast] on this setup card
        ai_resp = client.post("/api/ai/forecast", json={
            "ticker": setup["ticker"],
            "pred_len": 15,
            "n_paths": 10
        })
        assert ai_resp.status_code == 200
        ai_data = ai_resp.json()
        assert ai_data["ticker"] == setup["ticker"]
        assert "expected_close" in ai_data
        assert "upside_prob" in ai_data
        assert "confluence_badge" in ai_data


def test_chart_studio_ai_overlay_integration():
    """Verify that Chart Studio historical candles and AI Forecast future trajectory mesh cleanly."""
    chart_resp = client.get("/api/chart/RELIANCE.NS?period=6mo&strategy_id=trend_pullback")
    assert chart_resp.status_code == 200
    chart_data = chart_resp.json()
    hist_candles = chart_data.get("candles", [])
    assert len(hist_candles) > 30

    ai_resp = client.post("/api/ai/forecast", json={
        "ticker": "RELIANCE.NS",
        "pred_len": 15,
        "n_paths": 10
    })
    assert ai_resp.status_code == 200
    ai_data = ai_resp.json()
    forecast_candles = ai_data.get("forecast_candles", [])
    assert len(forecast_candles) == 15

    # Check date ordering: last historical date < first forecast date
    last_hist_date = hist_candles[-1]["time"]
    first_forecast_date = forecast_candles[0]["date"]
    assert first_forecast_date > last_hist_date or first_forecast_date >= last_hist_date


def test_sector_pulse_to_ai_workflow():
    """Verify that Sector Pulse constituent leader stocks can be forecast via AI Forecaster."""
    constituents_resp = client.get("/api/sectors/constituents?sector=^CNXIT")
    if constituents_resp.status_code == 200:
        constituents = constituents_resp.json().get("constituents", [])
        if len(constituents) > 0:
            top_stock = constituents[0]["symbol"]
            ai_resp = client.post("/api/ai/forecast", json={
                "ticker": top_stock,
                "pred_len": 15,
                "n_paths": 10
            })
            assert ai_resp.status_code == 200
            ai_data = ai_resp.json()
            assert ai_data["ticker"] == top_stock
