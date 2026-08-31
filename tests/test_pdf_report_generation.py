"""
Unit and Integration Tests for Institutional PDF Report Generation Engine.
Verifies PDF binary structure, zero-exception execution, and response headers across all 3 report types.
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.core.pdf_report_engine import PDFReportEngine

client = TestClient(app)


def test_deep_scan_pdf_direct_generation():
    mock_deep_scan = {
        "ticker": "RELIANCE.NS",
        "company_name": "Reliance Industries Limited",
        "cmp": 1275.50,
        "day_change_pct": 1.25,
        "sector": "Energy & Refineries",
        "alpha_fusion": {
            "composite_score": 85,
            "action": "STRONG BUY"
        },
        "mtf_confluence": {
            "screen_1_weekly": {
                "bullish": True,
                "status_label": "Bullish Tide",
                "bias": "Close > 13/26 EMA with expanding MACD",
                "close": 1275.50,
                "ema_13": 1240.0,
                "ema_26": 1210.0
            },
            "screen_2_daily": {
                "bullish": True,
                "status_label": "Stage 2 Bull Wave",
                "bias": "Stacked 20 > 50 > 200 EMA",
                "ema_20": 1250.0,
                "ema_50": 1220.0,
                "ema_200": 1180.0
            },
            "screen_3_timing": {
                "bullish": True,
                "status_label": "Trigger Ready",
                "bias": "Volume Expansion & Upward Hook",
                "rsi_14": 58.5,
                "vol_ratio": 1.45,
                "is_green_candle": True
            },
            "verdict": "High-Conviction MTF Alignment across Weekly, Daily, and Micro Execution."
        },
        "active_strategies": [
            {
                "is_active": True,
                "setup": {
                    "strategy": "Institutional Pocket Pivot",
                    "score": 88,
                    "close": 1275.50,
                    "stop_loss": 1224.50,
                    "target_1": 1377.50,
                    "target_2": 1428.50,
                    "risk_pct": 4.0,
                    "reward_pct_t1": 8.0,
                    "reward_pct_t2": 12.0,
                    "setup_summary": "Volume surge 1.45x bouncing off 20 EMA support."
                }
            }
        ],
        "position_sizing": {
            "shares": 98,
            "total_capital_deployed": 125000.0,
            "potential_profit_target_1": 10000.0
        },
        "ema_20": 1250.0,
        "ema_50": 1220.0,
        "ema_200": 1180.0,
        "rsi_14": 58.5,
        "atr_14": 25.5,
        "vol_ratio": 1.45,
        "vwap": 1270.0,
        "low_52w": 1050.0,
        "high_52w": 1400.0,
        "kronos_forecast": {
            "target_price": 1340.0,
            "target_pct_change": 5.06,
            "overall_projected_low": 1250.0,
            "overall_projected_high": 1370.0,
            "direction": "BULLISH",
            "trajectory": [
                {"day": 1, "predicted_close": 1280.0, "band_low": 1260.0, "band_high": 1300.0},
                {"day": 15, "predicted_close": 1340.0, "band_low": 1250.0, "band_high": 1370.0}
            ]
        },
        "macro_hud": {
            "repo_rate_pct": 6.50,
            "bond_yield_10y_pct": 6.95,
            "cpi_inflation_pct": 3.65,
            "usd_inr_rate": 84.15
        }
    }
    pdf_bytes = PDFReportEngine.generate_deepscan_pdf(mock_deep_scan)
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 2000
    assert pdf_bytes.startswith(b"%PDF-1.4")


def test_backtest_factsheet_pdf_direct_generation():
    mock_backtest_metrics = {
        "ticker": "RELIANCE.NS",
        "strategy_id": "trend_pullback",
        "period": "2y",
        "initial_capital": 500000.0,
        "final_capital": 612450.0,
        "net_profit": 112450.0,
        "net_profit_pct": 22.49,
        "cagr_pct": 10.67,
        "total_trades": 18,
        "winning_trades": 8,
        "losing_trades": 10,
        "win_rate": 44.44,
        "profit_factor": 2.15,
        "payoff_ratio": 2.69,
        "max_drawdown_pct": 4.85,
        "sharpe_ratio": 1.42,
        "sortino_ratio": 1.88,
        "avg_holding_days": 12.5,
        "trades": [
            {
                "trade_no": 1,
                "ticker": "RELIANCE.NS",
                "entry_date": "2024-01-15",
                "exit_date": "2024-01-29",
                "entry_price": 1240.0,
                "exit_price": 1339.2,
                "net_pnl": 9920.0,
                "return_pct": 8.0,
                "exit_reason": "Target 1 Hit"
            }
        ]
    }
    pdf_bytes = PDFReportEngine.generate_backtest_pdf(mock_backtest_metrics)
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 2000
    assert pdf_bytes.startswith(b"%PDF-1.4")


def test_macro_alignment_memo_pdf_direct_generation():
    mock_macro_data = {
        "ticker": "INFY.NS",
        "as_of_date": "2026-08-31",
        "prediction_summary": {
            "forward_horizon": 5,
            "target_threshold_pct": 0.5,
            "swing_up_probability": 68.4,
            "swing_down_probability": 31.6,
            "directional_verdict": "BULLISH",
            "composite_alignment_score": 78,
            "signal_strength": "High Conviction"
        },
        "macro_environment": {
            "repo_rate": 6.50,
            "cpi_inflation": 3.65,
            "bond_yield_10y": 6.95,
            "usd_inr": 84.15
        },
        "feature_attribution": {
            "category_weights": {
                "dense_embedding_pct": 60.0,
                "monetary_policy_pct": 15.0,
                "inflation_pct": 10.0,
                "yield_curve_pct": 7.5,
                "forex_pct": 7.5
            },
            "top_drivers": [
                {"feature": "Transformer Embedding Dim 42", "importance_pct": 14.5, "direction": "Positive", "description": "Persistent institutional accumulation flow"},
                {"feature": "USD/INR Depreciation Impulse", "importance_pct": 9.2, "direction": "Positive", "description": "IT exporter forex revenue expansion"}
            ]
        },
        "out_of_sample_validation": {
            "train_samples": 420,
            "test_samples": 105,
            "metrics": {
                "accuracy": 0.67,
                "precision": 0.66,
                "recall": 0.70,
                "f1_score": 0.68
            }
        }
    }
    pdf_bytes = PDFReportEngine.generate_macro_pdf(mock_macro_data)
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 2000
    assert pdf_bytes.startswith(b"%PDF-1.4")


def test_deep_scan_export_pdf_api_endpoint():
    response = client.get("/api/deep-scan/export/pdf?ticker=RELIANCE.NS")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert "attachment; filename=" in response.headers["content-disposition"]
    assert response.content.startswith(b"%PDF-1.4")


def test_backtest_export_pdf_api_endpoint():
    payload = {
        "ticker": "RELIANCE.NS",
        "strategy_id": "trend_pullback",
        "period": "1y",
        "initial_capital": 500000.0,
        "risk_pct": 1.0
    }
    response = client.post("/api/backtest/export/pdf", json=payload)
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert "attachment; filename=" in response.headers["content-disposition"]
    assert response.content.startswith(b"%PDF-1.4")
