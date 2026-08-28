"""
Simulated Paper Trading & Trade Journal Studio API Routes.
"""

from typing import Optional
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException
from backend.app.core.trade_journal import TradeJournalEngine

router = APIRouter(prefix="/api/journal", tags=["TradeJournal"])


class LogTradeRequest(BaseModel):
    ticker: str = Field(..., description="Stock symbol (e.g. RELIANCE.NS)")
    strategy: str = Field(..., description="Strategy name")
    entry_price: float = Field(..., description="Entry execution price")
    shares: int = Field(..., ge=1, description="Quantity of shares")
    stop_loss: float = Field(..., description="Stop-loss price")
    target_1: float = Field(..., description="First profit target")
    target_2: Optional[float] = Field(None, description="Second profit target")
    notes: Optional[str] = Field(None, description="Trade thesis or notes")
    direction: Optional[str] = Field("LONG", description="LONG or SHORT")


class CloseTradeRequest(BaseModel):
    exit_price: float = Field(..., description="Exit execution price")
    exit_reason: str = Field("MANUAL", description="Reason: TARGET_1, TARGET_2, STOP_LOSS, TRAILING_STOP, MANUAL")
    notes: Optional[str] = Field(None, description="Post-trade review notes")


@router.get("/summary")
def get_journal_summary():
    """Returns open simulated positions, closed trades, and portfolio attribution statistics."""
    return TradeJournalEngine.get_journal_summary()


@router.post("/trade")
def log_new_trade(req: LogTradeRequest):
    """Logs a new simulated swing trade to the forward testing journal."""
    return TradeJournalEngine.add_trade(
        ticker=req.ticker,
        strategy=req.strategy,
        entry_price=req.entry_price,
        shares=req.shares,
        stop_loss=req.stop_loss,
        target_1=req.target_1,
        target_2=req.target_2,
        notes=req.notes,
        direction=req.direction
    )


@router.post("/trade/{trade_id}/close")
def close_existing_trade(trade_id: str, req: CloseTradeRequest):
    """Closes an open simulated trade and calculates realized P&L and R-multiple."""
    closed = TradeJournalEngine.close_trade(
        trade_id=trade_id,
        exit_price=req.exit_price,
        exit_reason=req.exit_reason,
        notes=req.notes
    )
    if not closed:
        raise HTTPException(status_code=404, detail=f"Trade '{trade_id}' not found.")
    return closed


@router.delete("/trade/{trade_id}")
def delete_trade_record(trade_id: str):
    """Deletes a trade record from the journal."""
    deleted = TradeJournalEngine.delete_trade(trade_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Trade '{trade_id}' not found.")
    return {"status": "success", "message": f"Trade {trade_id} deleted."}
