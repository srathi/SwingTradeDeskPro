"""
Macro Market Regime & Volatility Gating API Routes.
"""

from typing import Optional
from fastapi import APIRouter, Query
from backend.app.core.regime_engine import MarketRegimeEngine

router = APIRouter(prefix="/api/market-regime", tags=["MarketRegime"])


@router.get("/current")
def get_current_market_regime(
    market: Optional[str] = Query("NSE", description="Market identifier: NSE, BSE, or US")
):
    """
    Returns real-time macro volatility regime, benchmark trend alignment, and strategy gating guidelines.
    """
    # Sanitize FastAPI Query parameter if passed directly
    if not isinstance(market, str) or market.startswith("annotation="):
        market = "NSE"
    return MarketRegimeEngine.get_current_regime(market)
