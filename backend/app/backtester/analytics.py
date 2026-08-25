"""
Performance Analytics and Institutional Metrics Computation.
Calculates Sharpe, Sortino, Drawdown, Profit Factor, Win Rate, and Expectancy.
"""

import math
import numpy as np
import pandas as pd
from typing import Dict, List, Any


def compute_performance_metrics(
    trades: List[Dict[str, Any]],
    equity_curve: List[Dict[str, Any]],
    initial_capital: float
) -> Dict[str, Any]:
    """
    Computes all standard quantitative metrics from backtest trade logs and equity curve.
    """
    if not equity_curve:
        return {
            "initial_capital": initial_capital,
            "final_capital": initial_capital,
            "net_profit": 0.0,
            "net_profit_pct": 0.0,
            "total_trades": 0,
            "win_rate": 0.0,
            "profit_factor": 0.0,
            "max_drawdown_pct": 0.0
        }

    final_capital = equity_curve[-1]["equity"]
    net_profit = final_capital - initial_capital
    net_profit_pct = (net_profit / initial_capital) * 100.0

    total_trades = len(trades)
    winning_trades = [t for t in trades if t["is_win"]]
    losing_trades = [t for t in trades if not t["is_win"]]

    win_count = len(winning_trades)
    loss_count = len(losing_trades)
    win_rate = (win_count / total_trades * 100.0) if total_trades > 0 else 0.0

    gross_profits = sum(t["net_pnl"] for t in winning_trades)
    gross_losses = abs(sum(t["net_pnl"] for t in losing_trades))
    profit_factor = (gross_profits / gross_losses) if gross_losses > 0 else (99.0 if gross_profits > 0 else 0.0)

    avg_win = (gross_profits / win_count) if win_count > 0 else 0.0
    avg_loss = (gross_losses / loss_count) if loss_count > 0 else 0.0
    payoff_ratio = (avg_win / avg_loss) if avg_loss > 0 else 0.0

    # Expectancy = (Win% * AvgWin) - (Loss% * AvgLoss)
    win_prob = win_count / total_trades if total_trades > 0 else 0.0
    loss_prob = loss_count / total_trades if total_trades > 0 else 0.0
    expectancy = (win_prob * avg_win) - (loss_prob * avg_loss)

    avg_holding_bars = (sum(t["bars_held"] for t in trades) / total_trades) if total_trades > 0 else 0.0

    # Drawdown Analytics
    equities = [pt["equity"] for pt in equity_curve]
    peak = equities[0]
    drawdowns = []
    max_dd_val = 0.0
    max_dd_pct = 0.0

    for eq in equities:
        if eq > peak:
            peak = eq
        dd_val = peak - eq
        dd_pct = (dd_val / peak) * 100.0 if peak > 0 else 0.0
        drawdowns.append(dd_pct)
        if dd_pct > max_dd_pct:
            max_dd_pct = dd_pct
            max_dd_val = dd_val

    # Daily returns for Sharpe & Sortino (assuming 252 trading days)
    eq_series = pd.Series(equities)
    daily_returns = eq_series.pct_change().dropna()

    if len(daily_returns) > 1 and daily_returns.std() > 0:
        mean_ret = daily_returns.mean() * 252
        vol = daily_returns.std() * math.sqrt(252)
        sharpe_ratio = round(mean_ret / vol, 2)

        downside_returns = daily_returns[daily_returns < 0]
        downside_vol = downside_returns.std() * math.sqrt(252) if len(downside_returns) > 0 else vol
        sortino_ratio = round(mean_ret / downside_vol, 2) if downside_vol > 0 else 0.0
    else:
        sharpe_ratio = 0.0
        sortino_ratio = 0.0

    # Approximate CAGR
    num_years = max(len(equity_curve) / 252.0, 0.1)
    if final_capital > 0 and initial_capital > 0:
        cagr = ((final_capital / initial_capital) ** (1.0 / num_years) - 1.0) * 100.0
    else:
        cagr = 0.0

    return {
        "initial_capital": round(initial_capital, 2),
        "final_capital": round(final_capital, 2),
        "net_profit": round(net_profit, 2),
        "net_profit_pct": round(net_profit_pct, 2),
        "cagr_pct": round(cagr, 2),
        "total_trades": total_trades,
        "winning_trades": win_count,
        "losing_trades": loss_count,
        "win_rate": round(win_rate, 2),
        "profit_factor": round(profit_factor, 2),
        "payoff_ratio": round(payoff_ratio, 2),
        "expectancy_per_trade": round(expectancy, 2),
        "average_win": round(avg_win, 2),
        "average_loss": round(avg_loss, 2),
        "max_drawdown_pct": round(max_dd_pct, 2),
        "max_drawdown_val": round(max_dd_val, 2),
        "sharpe_ratio": sharpe_ratio,
        "sortino_ratio": sortino_ratio,
        "avg_holding_days": round(avg_holding_bars, 1),
        "trades": trades,
        "equity_curve": equity_curve
    }
