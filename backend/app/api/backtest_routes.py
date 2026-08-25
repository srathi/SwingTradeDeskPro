"""
Backtest API Routes.
"""

from typing import Optional, Dict, Any, List
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.app.core.data_engine import data_engine
from backend.app.core.index_manager import IndexManager
from backend.app.backtester.engine import BacktestEngine
from backend.app.backtester.analytics import compute_performance_metrics

router = APIRouter(prefix="/api/backtest", tags=["Backtest"])


class BacktestRequest(BaseModel):
    ticker: Optional[str] = "RELIANCE.NS"
    universe: Optional[str] = None
    strategy_id: str = "trend_pullback"
    period: str = "2y"
    initial_capital: float = 500_000.0
    risk_pct: float = 1.0
    slippage_pct: float = 0.08
    enable_indian_taxes: bool = True
    params: Optional[Dict[str, Any]] = None


@router.post("/run")
def run_backtest(req: BacktestRequest):
    """
    Executes a backtest for the specified ticker/universe and strategy.
    """
    engine = BacktestEngine(
        initial_capital=req.initial_capital,
        risk_per_trade_pct=req.risk_pct,
        slippage_pct=req.slippage_pct,
        enable_indian_taxes=req.enable_indian_taxes
    )

    # Single ticker backtest
    if req.ticker and not req.universe:
        df = data_engine.fetch_ticker_data(req.ticker, period=req.period, interval="1d")
        if df is None or len(df) < 50:
            raise HTTPException(status_code=404, detail=f"Insufficient historical data for {req.ticker}")

        sim_res = engine.run_single(req.ticker, df, strategy_id=req.strategy_id, strategy_params=req.params)
        if "error" in sim_res:
            raise HTTPException(status_code=400, detail=sim_res["error"])

        metrics = compute_performance_metrics(sim_res["trades"], sim_res["equity_curve"], req.initial_capital)
        metrics["ticker"] = req.ticker
        metrics["strategy_id"] = req.strategy_id
        metrics["period"] = req.period
        return metrics

    # Portfolio basket backtest
    tickers = IndexManager.get_tickers(req.universe or "NIFTY_50")[:15]  # Top 15 liquid for speed
    all_trades = []
    combined_equity = []
    
    # Run backtest across basket
    for t in tickers:
        df = data_engine.fetch_ticker_data(t, period=req.period, interval="1d")
        if df is not None and len(df) > 50:
            res = engine.run_single(t, df, strategy_id=req.strategy_id, strategy_params=req.params)
            if "trades" in res:
                all_trades.extend(res["trades"])

    all_trades.sort(key=lambda x: x["entry_date"])
    for i, tr in enumerate(all_trades):
        tr["trade_no"] = i + 1

    # Reconstruct portfolio equity curve
    portfolio_equity = req.initial_capital
    portfolio_curve = [{"date": "Start", "equity": portfolio_equity, "cash": portfolio_equity, "in_trade": False}]
    for tr in all_trades:
        portfolio_equity += tr["net_pnl"]
        portfolio_curve.append({
            "date": tr["exit_date"],
            "equity": round(portfolio_equity, 2),
            "cash": round(portfolio_equity, 2),
            "in_trade": False
        })

    metrics = compute_performance_metrics(all_trades, portfolio_curve, req.initial_capital)
    metrics["ticker"] = f"Basket: {req.universe or 'NIFTY_50'}"
    metrics["strategy_id"] = req.strategy_id
    metrics["period"] = req.period
    return metrics
