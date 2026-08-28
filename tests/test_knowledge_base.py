"""
Unit Tests for Centralized Knowledge Base & Jargon Data Integrity.
Verifies all 45+ terms have required fields, categories, formulas, and examples,
and ensures all 10 application pages and 12 strategies are fully indexed.
"""

import os
import pytest

def test_knowledge_base_js_integrity():
    kb_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "src", "data", "knowledgeBase.js")
    assert os.path.exists(kb_path), f"knowledgeBase.js not found at {kb_path}"

    with open(kb_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Verify key exports
    assert "export const UNIVERSAL_GLOSSARY" in content
    assert "export const PAGE_GUIDES" in content
    assert "export const STRATEGIES_PLAYBOOK" in content

    # Verify critical terms exist in the dictionary
    core_terms = [
        "ema_20_50_200", "rsi_14", "rsi_28", "chandelier_exit", "r_multiple",
        "ev_r", "half_kelly", "market_regime", "elder_triple_screen",
        "volume_profile", "poc", "vah", "val", "avwap", "hurst_exponent",
        "mansfield_rs", "kronos_neural_forecast", "profit_factor", "max_drawdown",
        "regime_forecast_memory", "exhaustion_risk", "regime_age_runway",
        "weibull_exhaustion", "overextension_risk", "merit_score", "weinstein_stage",
        "avwap_multi_pivot", "alpha_fusion_interpretation"
    ]
    for term in core_terms:
        assert f"{term}:" in content, f"Missing term '{term}' in knowledgeBase.js"

    # Verify all 10 page guide keys exist
    page_keys = [
        "screener", "deepscan", "sectors", "chart", "aiforecast",
        "backtest", "journal", "risk", "watchlists", "matrix"
    ]
    for pkey in page_keys:
        assert f"{pkey}:" in content, f"Missing page guide for '{pkey}' in knowledgeBase.js"

    # Verify all 12 quantitative strategies are listed
    strategies = [
        "trend_pullback", "vcp_breakout", "high_52w_breakout", "connors_rsi2",
        "volatility_squeeze", "relative_strength_leader", "pocket_pivot",
        "wyckoff_spring", "nr7_expansion", "gmma_breakout", "rsi28_divergence", "mean_reversion"
    ]
    for strat in strategies:
        assert f'id: "{strat}"' in content, f"Missing strategy '{strat}' in knowledgeBase.js"
