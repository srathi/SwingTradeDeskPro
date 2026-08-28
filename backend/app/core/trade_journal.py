"""
Simulated Paper Trading & Trade Journal Studio Engine.
Academic & Behavioral Finance Foundation: Mark Douglas (Trading in the Zone), Brett Steenbarger (The Daily Trading Coach).
Persists simulated positions, calculates real-time mark-to-market P&L, and generates institutional trade analytics.
"""

from typing import Dict, Any, List, Optional
import os
import json
import uuid
import time
from datetime import datetime
import pandas as pd
from backend.app.core.data_engine import data_engine

JOURNAL_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "simulated_journal.json")


class TradeJournalEngine:
    @classmethod
    def _load_data(cls) -> List[Dict[str, Any]]:
        if not os.path.exists(JOURNAL_FILE):
            return []
        try:
            with open(JOURNAL_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return []

    @classmethod
    def _save_data(cls, trades: List[Dict[str, Any]]):
        os.makedirs(os.path.dirname(JOURNAL_FILE), exist_ok=True)
        with open(JOURNAL_FILE, "w") as f:
            json.dump(trades, f, indent=2)

    @classmethod
    def add_trade(
        cls,
        ticker: str,
        strategy: str,
        entry_price: float,
        shares: int,
        stop_loss: float,
        target_1: float,
        target_2: Optional[float] = None,
        notes: Optional[str] = "",
        direction: str = "LONG"
    ) -> Dict[str, Any]:
        trades = cls._load_data()
        trade_id = str(uuid.uuid4())[:8].upper()
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        risk_per_share = max(0.01, entry_price - stop_loss)
        total_risk = round(risk_per_share * shares, 2)
        capital_invested = round(entry_price * shares, 2)

        new_trade = {
            "id": trade_id,
            "ticker": ticker.upper(),
            "strategy": strategy,
            "direction": direction.upper(),
            "status": "OPEN",
            "entry_date": now_str,
            "entry_price": round(entry_price, 2),
            "shares": int(shares),
            "stop_loss": round(stop_loss, 2),
            "target_1": round(target_1, 2),
            "target_2": round(target_2, 2) if target_2 else round(entry_price + (2.5 * risk_per_share), 2),
            "risk_per_share": round(risk_per_share, 2),
            "total_risk_amount": total_risk,
            "capital_invested": capital_invested,
            "exit_date": None,
            "exit_price": None,
            "exit_reason": None,
            "realized_pnl": 0.0,
            "realized_pnl_pct": 0.0,
            "realized_r_multiple": 0.0,
            "notes": notes or ""
        }

        trades.insert(0, new_trade)
        cls._save_data(trades)
        return new_trade

    @classmethod
    def close_trade(
        cls,
        trade_id: str,
        exit_price: float,
        exit_reason: str = "MANUAL",
        notes: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        trades = cls._load_data()
        target_trade = None
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        for t in trades:
            if t["id"] == trade_id:
                entry_p = t["entry_price"]
                shares = t["shares"]
                risk_per_share = max(0.01, t["risk_per_share"])

                pnl = (exit_price - entry_p) * shares
                pnl_pct = ((exit_price - entry_p) / entry_p) * 100.0
                r_multiple = (exit_price - entry_p) / risk_per_share

                t["status"] = "CLOSED"
                t["exit_date"] = now_str
                t["exit_price"] = round(exit_price, 2)
                t["exit_reason"] = exit_reason
                t["realized_pnl"] = round(pnl, 2)
                t["realized_pnl_pct"] = round(pnl_pct, 2)
                t["realized_r_multiple"] = round(r_multiple, 2)
                if notes:
                    t["notes"] = f"{t.get('notes', '')} | {notes}".strip(" | ")
                target_trade = t
                break

        if target_trade:
            cls._save_data(trades)
        return target_trade

    @classmethod
    def delete_trade(cls, trade_id: str) -> bool:
        trades = cls._load_data()
        initial_len = len(trades)
        trades = [t for t in trades if t["id"] != trade_id]
        if len(trades) < initial_len:
            cls._save_data(trades)
            return True
        return False

    @classmethod
    def get_journal_summary(cls) -> Dict[str, Any]:
        """
        Returns real-time aggregated portfolio journal metrics with live CMP quotes.
        """
        trades = cls._load_data()
        open_trades = []
        closed_trades = []

        total_realized_pnl = 0.0
        total_unrealized_pnl = 0.0
        winning_closed = 0
        losing_closed = 0
        total_r_multiples = []

        for t in trades:
            if t["status"] == "OPEN":
                # Fetch live CMP
                ticker = t["ticker"]
                df = data_engine.fetch_ticker_data(ticker, period="5d", interval="1d")
                cmp = t["entry_price"]
                if df is not None and len(df) > 0:
                    cmp = float(df['Close'].iloc[-1])

                entry_p = t["entry_price"]
                shares = t["shares"]
                risk_per_share = max(0.01, t["risk_per_share"])

                unrealized_pnl = (cmp - entry_p) * shares
                unrealized_pnl_pct = ((cmp - entry_p) / entry_p) * 100.0
                current_r = (cmp - entry_p) / risk_per_share

                open_item = {
                    **t,
                    "cmp": round(cmp, 2),
                    "unrealized_pnl": round(unrealized_pnl, 2),
                    "unrealized_pnl_pct": round(unrealized_pnl_pct, 2),
                    "current_r_multiple": round(current_r, 2),
                    "is_stop_loss_hit": cmp <= t["stop_loss"],
                    "is_target_1_hit": cmp >= t["target_1"],
                    "is_target_2_hit": cmp >= t.get("target_2", t["target_1"] * 1.05)
                }
                open_trades.append(open_item)
                total_unrealized_pnl += unrealized_pnl
            else:
                closed_trades.append(t)
                pnl = t.get("realized_pnl", 0.0)
                total_realized_pnl += pnl
                r_mult = t.get("realized_r_multiple", 0.0)
                total_r_multiples.append(r_mult)
                if pnl > 0:
                    winning_closed += 1
                elif pnl < 0:
                    losing_closed += 1

        total_closed_count = len(closed_trades)
        win_rate = round((winning_closed / max(1, total_closed_count)) * 100.0, 1) if total_closed_count > 0 else 0.0
        avg_r_multiple = round(float(np.mean(total_r_multiples)), 2) if total_r_multiples else 0.0

        # Calculate Profit Factor
        gross_profit = sum(t.get("realized_pnl", 0.0) for t in closed_trades if t.get("realized_pnl", 0.0) > 0)
        gross_loss = abs(sum(t.get("realized_pnl", 0.0) for t in closed_trades if t.get("realized_pnl", 0.0) < 0))
        profit_factor = round(gross_profit / max(1.0, gross_loss), 2) if gross_loss > 0 else (99.0 if gross_profit > 0 else 0.0)

        return {
            "portfolio_summary": {
                "total_trades": len(trades),
                "open_trades_count": len(open_trades),
                "closed_trades_count": total_closed_count,
                "win_rate_pct": win_rate,
                "profit_factor": profit_factor,
                "total_realized_pnl": round(total_realized_pnl, 2),
                "total_unrealized_pnl": round(total_unrealized_pnl, 2),
                "net_combined_pnl": round(total_realized_pnl + total_unrealized_pnl, 2),
                "avg_r_multiple": avg_r_multiple
            },
            "open_positions": open_trades,
            "closed_trades": closed_trades
        }
