"""
Institutional Backtesting Simulation Engine with Realistic Indian Market Cost Models.
Simulates bar-by-bar trade execution with slippage, STT, GST, brokerage, and risk-managed position sizing.
"""

import math
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional
from backend.app.strategies import get_strategy


class BacktestEngine:
    def __init__(
        self,
        initial_capital: float = 500_000.0,
        risk_per_trade_pct: float = 1.0,
        slippage_pct: float = 0.08,
        enable_indian_taxes: bool = True,
        max_holding_bars: int = 25
    ):
        self.initial_capital = initial_capital
        self.risk_per_trade_pct = risk_per_trade_pct
        self.slippage_pct = slippage_pct / 100.0
        self.enable_indian_taxes = enable_indian_taxes
        self.max_holding_bars = max_holding_bars

    def _calculate_transaction_costs(self, turnover: float, is_buy: bool) -> float:
        """
        Calculates Indian equity delivery transaction costs (STT, GST, Exchange fees, Stamp Duty, Brokerage).
        """
        if not self.enable_indian_taxes:
            return turnover * 0.0005  # Basic flat fee

        # Brokerage (Zerodha/Groww style: ₹20 or 0.05%)
        brokerage = min(20.0, turnover * 0.0005)
        # STT (0.1% on delivery Buy and Sell)
        stt = turnover * 0.001
        # Exchange turnover charges (NSE: ~0.00345%)
        exchange_charges = turnover * 0.0000345
        # SEBI Turnover Fee (₹10 / crore)
        sebi_charges = turnover * 0.000001
        # Stamp Duty (0.015% on Buy only)
        stamp_duty = (turnover * 0.00015) if is_buy else 0.0
        # GST (18% on Brokerage + SEBI + Exchange charges)
        gst = (brokerage + exchange_charges + sebi_charges) * 0.18

        return brokerage + stt + exchange_charges + sebi_charges + stamp_duty + gst

    def run_single(
        self,
        ticker: str,
        df: pd.DataFrame,
        strategy_id: str = "trend_pullback",
        strategy_params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Runs backtest on a single symbol's OHLCV dataframe.
        """
        if df is None or len(df) < 50:
            return {"error": f"Insufficient data for ticker {ticker}"}

        strat = get_strategy(strategy_id)
        data = strat.generate_signals(df, strategy_params)

        equity = self.initial_capital
        cash = self.initial_capital
        trades: List[Dict[str, Any]] = []
        equity_curve: List[Dict[str, Any]] = []

        active_trade: Optional[Dict[str, Any]] = None

        for i in range(len(data)):
            bar = data.iloc[i]
            date_str = data.index[i].strftime("%Y-%m-%d") if hasattr(data.index[i], "strftime") else str(data.index[i])
            open_p = float(bar['Open'])
            high_p = float(bar['High'])
            low_p = float(bar['Low'])
            close_p = float(bar['Close'])

            # If in active trade, check exit conditions first
            if active_trade is not None:
                active_trade["bars_held"] += 1
                exit_price = None
                exit_reason = None

                # 1. Stop Loss Hit
                if low_p <= active_trade["stop_loss"]:
                    exit_price = min(open_p, active_trade["stop_loss"]) * (1.0 - self.slippage_pct)
                    exit_reason = "Stop Loss"

                # 2. Target 2 Hit (Full Take Profit 1:3 R:R)
                elif high_p >= active_trade["target_2"]:
                    exit_price = max(open_p, active_trade["target_2"]) * (1.0 - self.slippage_pct)
                    exit_reason = "Target 2 (3R)"

                # 3. Target 1 Hit -> Move stop to Breakeven
                elif high_p >= active_trade["target_1"] and not active_trade.get("target_1_hit", False):
                    active_trade["target_1_hit"] = True
                    active_trade["stop_loss"] = active_trade["entry_price"]  # Move stop to breakeven

                # 4. Max Holding Period Exceeded
                elif active_trade["bars_held"] >= self.max_holding_bars:
                    exit_price = close_p * (1.0 - self.slippage_pct)
                    exit_reason = "Max Time Exceeded"

                if exit_price is not None:
                    # Close trade
                    exit_turnover = active_trade["shares"] * exit_price
                    exit_costs = self._calculate_transaction_costs(exit_turnover, is_buy=False)
                    gross_pnl = (exit_price - active_trade["entry_price"]) * active_trade["shares"]
                    net_pnl = gross_pnl - active_trade["entry_costs"] - exit_costs

                    cash += exit_turnover - exit_costs
                    equity = cash

                    return_pct = (net_pnl / (active_trade["entry_price"] * active_trade["shares"])) * 100.0

                    trades.append({
                        "trade_no": len(trades) + 1,
                        "ticker": ticker,
                        "entry_date": active_trade["entry_date"],
                        "exit_date": date_str,
                        "entry_price": round(active_trade["entry_price"], 2),
                        "exit_price": round(exit_price, 2),
                        "shares": active_trade["shares"],
                        "capital_deployed": round(active_trade["entry_price"] * active_trade["shares"], 2),
                        "gross_pnl": round(gross_pnl, 2),
                        "net_pnl": round(net_pnl, 2),
                        "return_pct": round(return_pct, 2),
                        "exit_reason": exit_reason,
                        "bars_held": active_trade["bars_held"],
                        "is_win": net_pnl > 0
                    })
                    active_trade = None

            # Check Entry Condition (if not in trade and Signal == 1)
            if active_trade is None and bar.get('Signal', 0) == 1:
                # Enter at next available price (close + slippage)
                entry_price = close_p * (1.0 + self.slippage_pct)
                stop_loss = float(bar['Stop_Loss'])
                target_1 = float(bar['Target_1'])
                target_2 = float(bar['Target_2'])

                risk_per_share = entry_price - stop_loss
                if risk_per_share > 0:
                    risk_budget = equity * (self.risk_per_trade_pct / 100.0)
                    shares = math.floor(risk_budget / risk_per_share)
                    if shares < 1:
                        shares = 1

                    # Cap allocation to max 30% of total equity
                    max_allowed_shares = math.floor((equity * 0.30) / entry_price)
                    shares = min(shares, max(1, max_allowed_shares))

                    entry_turnover = shares * entry_price
                    if entry_turnover <= cash:
                        entry_costs = self._calculate_transaction_costs(entry_turnover, is_buy=True)
                        cash -= (entry_turnover + entry_costs)

                        active_trade = {
                            "ticker": ticker,
                            "entry_date": date_str,
                            "entry_price": entry_price,
                            "stop_loss": stop_loss,
                            "target_1": target_1,
                            "target_2": target_2,
                            "shares": shares,
                            "entry_costs": entry_costs,
                            "bars_held": 0,
                            "target_1_hit": False
                        }

            # Update daily equity curve
            current_portfolio_val = cash
            if active_trade is not None:
                current_portfolio_val += active_trade["shares"] * close_p

            equity_curve.append({
                "date": date_str,
                "equity": round(current_portfolio_val, 2),
                "cash": round(cash, 2),
                "in_trade": active_trade is not None
            })

        # Close open trade at end if any
        if active_trade is not None:
            last_bar = data.iloc[-1]
            last_date = data.index[-1].strftime("%Y-%m-%d") if hasattr(data.index[-1], "strftime") else str(data.index[-1])
            exit_price = float(last_bar['Close']) * (1.0 - self.slippage_pct)
            exit_turnover = active_trade["shares"] * exit_price
            exit_costs = self._calculate_transaction_costs(exit_turnover, is_buy=False)
            gross_pnl = (exit_price - active_trade["entry_price"]) * active_trade["shares"]
            net_pnl = gross_pnl - active_trade["entry_costs"] - exit_costs
            return_pct = (net_pnl / (active_trade["entry_price"] * active_trade["shares"])) * 100.0

            trades.append({
                "trade_no": len(trades) + 1,
                "ticker": ticker,
                "entry_date": active_trade["entry_date"],
                "exit_date": last_date,
                "entry_price": round(active_trade["entry_price"], 2),
                "exit_price": round(exit_price, 2),
                "shares": active_trade["shares"],
                "capital_deployed": round(active_trade["entry_price"] * active_trade["shares"], 2),
                "gross_pnl": round(gross_pnl, 2),
                "net_pnl": round(net_pnl, 2),
                "return_pct": round(return_pct, 2),
                "exit_reason": "End of Backtest",
                "bars_held": active_trade["bars_held"],
                "is_win": net_pnl > 0
            })

        return {
            "ticker": ticker,
            "strategy_id": strategy_id,
            "trades": trades,
            "equity_curve": equity_curve,
            "initial_capital": self.initial_capital,
            "final_capital": round(equity_curve[-1]["equity"] if equity_curve else self.initial_capital, 2)
        }
