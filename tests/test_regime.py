"""
Unit and Integration Tests for Macro Market Regime & Breadth Intelligence.
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.core.regime_engine import MarketRegimeEngine

client = TestClient(app)


def test_market_regime_engine_direct():
    """Verify MarketRegimeEngine returns complete breadth, volatility, and verdict fields."""
    MarketRegimeEngine._cache.clear() # clear cache
    res = MarketRegimeEngine.get_current_regime("NSE")

    # 1. Benchmark
    assert "benchmark" in res
    assert res["benchmark"]["name"] == "NIFTY 50"
    assert res["benchmark"]["close"] > 0
    assert "trend_status" in res["benchmark"]

    # 2. Volatility
    assert "volatility" in res
    assert res["volatility"]["value"] > 0
    assert "implied_daily_move_pct" in res["volatility"]
    assert res["volatility"]["implied_daily_move_pct"] > 0

    # 3. Market Breadth (% Above 200 EMA & Rating)
    assert "breadth" in res
    assert "pct_above_200_ema" in res["breadth"]
    assert res["breadth"]["pct_above_200_ema"] is not None
    assert 0.0 <= res["breadth"]["pct_above_200_ema"] <= 100.0
    assert "rating" in res["breadth"]
    assert len(res["breadth"]["rating"]) > 0

    # 4. Verdict
    assert "verdict" in res
    assert "title" in res["verdict"]
    assert "description" in res["verdict"]
    assert "recommended_allocation_multiplier" in res["verdict"]

    # 5. Market Mood Index (MMI)
    assert "mmi" in res
    assert 0.0 <= res["mmi"]["value"] <= 100.0
    assert res["mmi"]["zone"] in ["EXTREME_FEAR", "FEAR", "GREED", "EXTREME_GREED"]
    assert "components" in res["mmi"]

    # 6. Brent Crude Oil
    assert "brent_crude" in res
    assert res["brent_crude"]["symbol"] == "BZ=F"
    assert res["brent_crude"]["price"] > 0
    assert "impact_label" in res["brent_crude"]


def test_market_regime_api_endpoint():
    """Verify GET /api/market-regime/current returns valid JSON structure."""
    resp = client.get("/api/market-regime/current?market=NSE")
    assert resp.status_code == 200
    data = resp.json()

    assert data["market"] == "NSE"
    assert "mmi" in data
    assert 0.0 <= data["mmi"]["value"] <= 100.0
    assert data["breadth"]["pct_above_200_ema"] is not None
    assert data["breadth"]["rating"] is not None
    assert data["volatility"]["implied_daily_move_pct"] is not None
    assert data["verdict"]["description"] is not None
    assert "brent_crude" in data
    assert data["brent_crude"]["price"] > 0
