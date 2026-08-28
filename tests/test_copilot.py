"""
Unit and Integration Tests for AlphaChanakya AI Financial Copilot.
Tests:
1. Operational status endpoint
2. Financial & quantitative questions returning valid structured analysis
3. Strict guardrail deflection on non-financial off-topic queries
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_copilot_status_endpoint():
    """Verify copilot status endpoint."""
    resp = client.get("/api/ai/copilot/status")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ONLINE"
    assert data["bot_name"] == "AlphaChanakya"
    assert "supported_topics" in data


def test_copilot_financial_query_response():
    """Verify financial questions return quantitative markdown guidance."""
    # Test 1: Alpha Fusion question
    resp1 = client.post("/api/ai/copilot/chat", json={
        "message": "Explain how Alpha Fusion scoring works on a stock with score 85",
        "active_tab": "deepscan"
    })
    assert resp1.status_code == 200
    data1 = resp1.json()
    assert data1["is_deflection"] is False
    assert "Alpha" in data1["reply"] or "Score" in data1["reply"] or "Pillar" in data1["reply"]

    # Test 2: Sector runway question
    resp2 = client.post("/api/ai/copilot/chat", json={
        "message": "What does 16 Days Estimated Runway mean in Sector Pulse?",
        "active_tab": "sectors"
    })
    assert resp2.status_code == 200
    data2 = resp2.json()
    assert data2["is_deflection"] is False
    assert "Runway" in data2["reply"] or "Sector" in data2["reply"] or "Markov" in data2["reply"]

    # Test 3: Chandelier stop question
    resp3 = client.post("/api/ai/copilot/chat", json={
        "message": "How do I set an ATR Chandelier stop for my swing trade?",
        "active_tab": "risk"
    })
    assert resp3.status_code == 200
    data3 = resp3.json()
    assert data3["is_deflection"] is False
    assert "Chandelier" in data3["reply"] or "Stop" in data3["reply"] or "ATR" in data3["reply"]

    # Test 4: Live Stock Price query for TCS
    resp4 = client.post("/api/ai/copilot/chat", json={
        "message": "what is stock price TCS today?",
        "active_tab": "screener"
    })
    assert resp4.status_code == 200
    data4 = resp4.json()
    assert data4["is_deflection"] is False
    assert "TCS" in data4["reply"]
    assert "₹" in data4["reply"] or "2,342" in data4["reply"] or "CMP" in data4["reply"]


def test_copilot_off_topic_guardrail_deflection():
    """Verify non-financial off-topic queries trigger witty financial deflections."""
    # Off-topic query: Recipe
    resp_recipe = client.post("/api/ai/copilot/chat", json={
        "message": "How do I bake a chocolate cake with frosting?",
        "active_tab": "screener"
    })
    assert resp_recipe.status_code == 200
    data_recipe = resp_recipe.json()
    assert data_recipe["is_deflection"] is True
    assert "AlphaChanakya" in data_recipe["reply"]
    assert "suggested_topics" in data_recipe and len(data_recipe["suggested_topics"]) > 0

    # Off-topic query: Casual / general coding
    resp_poem = client.post("/api/ai/copilot/chat", json={
        "message": "Write a romantic poem about rain in Paris",
        "active_tab": "chart"
    })
    assert resp_poem.status_code == 200
    data_poem = resp_poem.json()
    assert data_poem["is_deflection"] is True
    assert "AlphaChanakya" in data_poem["reply"]


def test_copilot_multiturn_context_awareness_and_examples():
    """Verify follow-up questions with 'give details with an example' remember the previous topic."""
    # Turn 1: User asks about Sector Runway
    turn1_user = "What does Estimated Runway mean in Sector Pulse?"
    resp1 = client.post("/api/ai/copilot/chat", json={
        "message": turn1_user,
        "history": [],
        "active_tab": "sectors"
    })
    assert resp1.status_code == 200
    turn1_reply = resp1.json()["reply"]

    # Turn 2: User asks follow-up: "can you give details with an example?"
    history = [
        {"role": "user", "content": turn1_user},
        {"role": "assistant", "content": turn1_reply}
    ]
    resp2 = client.post("/api/ai/copilot/chat", json={
        "message": "can you give details with an example?",
        "history": history,
        "active_tab": "sectors"
    })
    assert resp2.status_code == 200
    data2 = resp2.json()
    assert data2["is_deflection"] is False
    # Turn 2 should connect to the previous topic (Hurst / Sector / Runway) and provide concrete example numbers
    assert "NIFTY" in data2["reply"] or "Runway" in data2["reply"] or "AUTO" in data2["reply"]
    assert "Days" in data2["reply"] or "Hurst" in data2["reply"]

    # Turn 3: Follow-up on Alpha Fusion
    history_fusion = [
        {"role": "user", "content": "Explain Alpha Fusion score 85"},
        {"role": "assistant", "content": "Alpha Fusion synthesizes 4 pillars..."}
    ]
    resp3 = client.post("/api/ai/copilot/chat", json={
        "message": "give details with a real world numerical example",
        "history": history_fusion,
        "active_tab": "deepscan"
    })
    assert resp3.status_code == 200
    data3 = resp3.json()
    assert data3["is_deflection"] is False
    assert any(k in data3["reply"] for k in ["Alpha", "Fusion", "85", "Score", "RELIANCE", "Pillar", "₹"])
    assert len(data3["reply"]) > 50

