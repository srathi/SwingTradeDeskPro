"""
AI Engine API routes for Kronos Financial Foundation Model forecasting.
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from backend.app.core.data_engine import data_engine
from backend.app.core.search_engine import SearchEngine
from backend.app.ai_engine.kronos_engine import kronos_engine

router = APIRouter(prefix="/api/ai", tags=["AI Forecast"])


class ForecastRequest(BaseModel):
    ticker: str = Field(..., description="NSE ticker symbol (e.g. RELIANCE.NS, TCS.NS) or company name")
    pred_len: int = Field(default=15, ge=5, le=60, description="Forecast horizon in trading days")
    n_paths: int = Field(default=20, ge=1, le=50, description="Monte Carlo simulation sample paths")
    temperature: float = Field(default=1.0, ge=0.1, le=2.0, description="Sampling entropy")
    top_p: float = Field(default=0.9, ge=0.1, le=1.0, description="Nucleus sampling probability cutoff")
    model_type: str = Field(default="mini", description="Model tier: mini, small, or base")


@router.get("/model-status")
async def get_model_status():
    """Return runtime status of the Kronos foundation model and compute device."""
    return kronos_engine.get_status()


@router.post("/forecast")
async def generate_ai_forecast(req: ForecastRequest):
    """
    Generate an autoregressive multi-path K-line forecast using the Kronos Foundation Model.
    Returns future candlestick trajectory, 90% confidence dispersion corridor,
    upside probability %, and volatility metrics.
    Automatically resolves typos and company names (e.g. PICCADILLY -> PICCADIL.NS).
    """
    raw_query = req.ticker.strip()
    ticker = raw_query.upper()

    # 1. Try direct fetch
    df = data_engine.fetch_ticker_data(ticker, period="1y")

    # 2. Try with .NS / .BO if not present
    if (df is None or len(df) < 50) and not ticker.endswith(".NS") and not ticker.endswith(".BO") and not ticker.startswith("^"):
        alt_ticker = f"{ticker}.NS"
        df_alt = data_engine.fetch_ticker_data(alt_ticker, period="1y")
        if df_alt is not None and len(df_alt) >= 50:
            ticker = alt_ticker
            df = df_alt

    # 3. If still not found, run fuzzy resolution via SearchEngine
    if df is None or len(df) < 50:
        suggestions = SearchEngine.search(raw_query, limit=5)
        for cand in suggestions:
            cand_sym = cand.get("symbol")
            if cand_sym and cand_sym != ticker:
                df_cand = data_engine.fetch_ticker_data(cand_sym, period="1y")
                if df_cand is not None and len(df_cand) >= 50:
                    ticker = cand_sym
                    df = df_cand
                    break

    # 4. If all fail, return helpful error with did-you-mean suggestions
    if df is None or len(df) < 50:
        suggestions = SearchEngine.search(raw_query, limit=4)
        suggested_names = [f"{s['symbol']} ({s['name']})" for s in suggestions]
        detail_msg = f"Insufficient price history found for ticker '{raw_query}'."
        if suggested_names:
            detail_msg += f" Did you mean: {', '.join(suggested_names[:3])}?"
        raise HTTPException(
            status_code=404,
            detail=detail_msg
        )

    try:
        forecast_data = kronos_engine.forecast(
            df=df,
            ticker=ticker,
            pred_len=req.pred_len,
            n_paths=req.n_paths,
            temperature=req.temperature,
            top_p=req.top_p,
            model_type=req.model_type
        )
        return forecast_data
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"AI Forecast calculation failed for '{ticker}': {str(e)}"
        )
