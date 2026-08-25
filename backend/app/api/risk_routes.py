"""
Risk Management and Position Sizing API Routes.
"""

from typing import Optional
from fastapi import APIRouter
from pydantic import BaseModel
from backend.app.core.risk_calculator import calculate_position_sizing

router = APIRouter(prefix="/api/risk", tags=["Risk"])


class SizingRequest(BaseModel):
    capital: float = 500_000.0
    risk_pct: float = 1.0
    entry_price: float
    stop_loss: float
    target_price: Optional[float] = None
    max_portfolio_allocation_pct: float = 25.0


@router.post("/calculate")
def get_position_sizing(req: SizingRequest):
    return calculate_position_sizing(
        capital=req.capital,
        risk_pct=req.risk_pct,
        entry_price=req.entry_price,
        stop_loss=req.stop_loss,
        target_price=req.target_price,
        max_portfolio_allocation_pct=req.max_portfolio_allocation_pct
    )
