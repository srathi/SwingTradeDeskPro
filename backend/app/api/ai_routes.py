"""
AI Engine API routes for Kronos Financial Foundation Model forecasting.
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from backend.app.core.data_engine import data_engine
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
    """
    ticker = req.ticker.strip().upper()
    if not ticker.endswith(".NS") and not ticker.endswith(".BO") and not ticker.startswith("^"):
        ticker = f"{ticker}.NS"

    try:
        df = data_engine.fetch_ticker_data(ticker, period="1y")
        if df is None or len(df) < 50:
            raise HTTPException(
                status_code=404,
                detail=f"Insufficient price history found for ticker '{ticker}'. Please ensure it is a valid NSE/BSE symbol."
            )

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
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"AI Forecast calculation failed: {str(e)}"
        )
