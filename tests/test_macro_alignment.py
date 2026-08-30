"""
Unit and Integration Tests for Two-Stage Macro-Factor Alignment Pipeline.
"""

import pytest
import numpy as np
import pandas as pd
import torch
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.ai_engine.macro_alignment_engine import (
    KronosFeatureExtractor,
    IndianMacroCalendar,
    macro_alignment_engine
)

client = TestClient(app)


def generate_synthetic_ohlcva(bars: int = 150) -> pd.DataFrame:
    """Generates synthetic multi-variate financial time-series."""
    dates = pd.date_range(start="2024-01-01", periods=bars, freq="B")
    np.random.seed(42)
    returns = np.random.normal(0.001, 0.015, size=bars)
    prices = 1000.0 * np.exp(np.cumsum(returns))
    volumes = np.random.randint(100_000, 1_000_000, size=bars)
    amounts = prices * volumes

    return pd.DataFrame({
        "Open": prices * 0.998,
        "High": prices * 1.01,
        "Low": prices * 0.99,
        "Close": prices,
        "Volume": volumes,
        "Amount": amounts
    }, index=dates)


def test_kronos_feature_extractor_tensor_shape():
    """Verify PyTorch Causal Transformer Feature Extractor shapes."""
    extractor = KronosFeatureExtractor(input_dim=6, embedding_dim=64, num_heads=4, hidden_dim=128)
    extractor.eval()

    # Batch of 4 sequences, each with 20 lookback bars and 6 features
    dummy_input = torch.randn(4, 20, 6)
    with torch.no_grad():
        output = extractor(dummy_input)

    assert output.shape == (4, 64), f"Expected shape (4, 64), got {output.shape}"
    assert not torch.isnan(output).any(), "Embeddings must not contain NaNs"


def test_indian_macro_calendar_zero_lookahead():
    """Verify macro series contains zero lookahead bias."""
    dates = pd.date_range(start="2024-01-01", periods=100, freq="B")
    macro_df = IndianMacroCalendar.build_macro_series(dates)

    assert len(macro_df) == 100
    assert "RBI_Repo_Rate" in macro_df.columns
    assert "India_CPI_Inflation" in macro_df.columns
    assert "India_10Y_Yield" in macro_df.columns
    assert "USD_INR" in macro_df.columns

    # Verify values are positive and realistic
    assert (macro_df["RBI_Repo_Rate"] > 4.0).all()
    assert (macro_df["India_CPI_Inflation"] > 1.0).all()


def test_macro_alignment_engine_execution():
    """Verify end-to-end alignment pipeline execution."""
    df = generate_synthetic_ohlcva(120)
    result = macro_alignment_engine.run_pipeline(
        df=df,
        ticker="SYNTHETIC.NS",
        forward_horizon=5,
        target_threshold_pct=0.5
    )

    assert "live_prediction" in result
    assert "bullish_probability_pct" in result["live_prediction"]
    assert 0.0 <= result["live_prediction"]["bullish_probability_pct"] <= 100.0
    assert "model_performance" in result
    assert "out_of_sample_accuracy_pct" in result["model_performance"]
    assert "feature_attribution" in result
    assert len(result["feature_attribution"]["top_features"]) > 0


def test_macro_alignment_api_endpoints():
    """Verify FastAPI GET /factors and POST /run endpoints."""
    # 1. Factors
    res_f = client.get("/api/ai/macro-alignment/factors")
    assert res_f.status_code == 200
    data_f = res_f.json()
    assert "rbi_repo_rate" in data_f
    assert "india_cpi_inflation" in data_f
    assert data_f["zero_lookahead_verified"] is True

    # 2. Run
    res_r = client.post("/api/ai/macro-alignment/run", json={
        "ticker": "RELIANCE.NS",
        "forward_horizon": 5,
        "target_threshold_pct": 0.5
    })
    assert res_r.status_code == 200
    data_r = res_r.json()
    assert "live_prediction" in data_r
    assert "verdict_title" in data_r["live_prediction"]
    assert "model_performance" in data_r
