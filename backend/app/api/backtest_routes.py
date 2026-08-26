"""
Backtest API Routes with Symbol Resolution and Robust Cost Models.
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

    # 1. Single ticker backtest
    if req.ticker and not req.universe:
        query = req.ticker.strip()
        clean_ticker, df = data_engine.fetch_ticker_data_with_resolved_sym(query, period=req.period, interval="1d")
        
        if df is None or len(df) < 40:
            # Fallback retry with 1y or 5y
            clean_ticker, df = data_engine.fetch_ticker_data_with_resolved_sym(query, period="1y", interval="1d")

        if df is None or len(df) < 40:
            raise HTTPException(
                status_code=404, 
                detail=f"Insufficient price history found for '{req.ticker}'. Please select a valid ticker or try another period."
            )

        sim_res = engine.run_single(clean_ticker, df, strategy_id=req.strategy_id, strategy_params=req.params)
        if "error" in sim_res:
            raise HTTPException(status_code=400, detail=sim_res["error"])

        metrics = compute_performance_metrics(sim_res["trades"], sim_res["equity_curve"], req.initial_capital)
        metrics["ticker"] = clean_ticker
        metrics["strategy_id"] = req.strategy_id
        metrics["period"] = req.period
        return metrics

    # 2. Portfolio basket backtest
    universe_id = req.universe or "NIFTY_50"
    tickers = IndexManager.get_tickers(universe_id)[:15]  # Top 15 liquid for responsive backtesting
    all_trades = []
    
    # Run backtest across basket
    for t in tickers:
        try:
            _, df = data_engine.fetch_ticker_data_with_resolved_sym(t, period=req.period, interval="1d")
            if df is not None and len(df) >= 40:
                res = engine.run_single(t, df, strategy_id=req.strategy_id, strategy_params=req.params)
                if "trades" in res:
                    all_trades.extend(res["trades"])
        except Exception:
            continue

    all_trades.sort(key=lambda x: x.get("entry_date", ""))
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
    metrics["ticker"] = f"Basket: {universe_id}"
    metrics["strategy_id"] = req.strategy_id
    metrics["period"] = req.period
    return metrics
