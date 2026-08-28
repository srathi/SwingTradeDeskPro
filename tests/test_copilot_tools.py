"""
Automated Test Suite for AlphaChanakya Tool Calling & Quantitative Execution Layer.

Tests all 8 native tools and dispatchers.
Copyright (c) rupeemap.in labs | by Sandesh Rathi (https://www.rupeemap.in)
"""

import pytest
from backend.app.ai_engine.copilot_tools import execute_copilot_tool, COPILOT_TOOL_DECLARATIONS


def test_copilot_tool_declarations_schema():
    """Verify all 8 quantitative tools have valid JSON declarations."""
    assert len(COPILOT_TOOL_DECLARATIONS) == 8
    tool_names = [t["name"] for t in COPILOT_TOOL_DECLARATIONS]
    
    assert "tool_scan_screener" in tool_names
    assert "tool_deep_scan_stock" in tool_names
    assert "tool_kronos_ai_forecast" in tool_names
    assert "tool_run_backtest" in tool_names
    assert "tool_calculate_position_size" in tool_names
    assert "tool_get_sector_pulse" in tool_names
    assert "tool_get_sector_constituents" in tool_names
    assert "tool_log_paper_trade" in tool_names


def test_tool_calculate_position_size():
    """Test position sizing tool with risk budgeting and exposure checks."""
    res = execute_copilot_tool("tool_calculate_position_size", {
        "capital": 1000000.0,
        "risk_pct": 1.0,
        "entry_price": 1287.0,
        "stop_loss": 1250.0
    })
    
    assert res["success"] is True
    assert res["shares_quantity"] == 270
    assert res["capital_required"] == 347490.0
    assert res["is_over_allocation"] is True  # 34.75% > 25% exposure threshold


def test_tool_sector_constituents():
    """Test sector constituent leaderboard ranking."""
    res = execute_copilot_tool("tool_get_sector_constituents", {
        "sector_name": "AUTO"
    })
    
    assert res["success"] is True
    assert res["sector"] == "AUTO"
    assert res["constituents_count"] >= 1
    assert "top_ranked_leaders" in res
    assert len(res["top_ranked_leaders"]) > 0


def test_tool_run_backtest():
    """Test walk-forward backtest tool execution."""
    res = execute_copilot_tool("tool_run_backtest", {
        "strategy_id": "connors_rsi2",
        "ticker": "TCS.NS",
        "period": "1y",
        "capital": 500000.0,
        "risk_pct": 1.0
    })
    
    assert res["success"] is True
    assert res["strategy_id"] == "connors_rsi2"
    assert "win_rate_pct" in res
    assert "total_trades" in res


def test_tool_paper_trade_journaling():
    """Test paper trade logging via copilot tool."""
    res = execute_copilot_tool("tool_log_paper_trade", {
        "ticker": "INFY.NS",
        "entry_price": 1850.0,
        "stop_loss": 1810.0,
        "target1": 1930.0,
        "quantity": 100,
        "strategy_id": "trend_pullback"
    })
    
    assert res["success"] is True
    assert "logged_trade" in res


def test_unknown_tool_graceful_error():
    """Verify executing an invalid tool returns structured error instead of crashing."""
    res = execute_copilot_tool("tool_nonexistent_xyz", {})
    assert res["success"] is False
    assert "Unknown tool" in res["error"]
