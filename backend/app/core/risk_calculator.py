"""
Risk Management and Institutional Position Sizing Engine.
Calculates risk per trade, account exposure, R:R metrics, and lot sizing.
"""

import math
from typing import Dict, Any


def calculate_position_sizing(
    capital: float,
    risk_pct: float,
    entry_price: float,
    stop_loss: float,
    target_price: float = None,
    max_portfolio_allocation_pct: float = 25.0
) -> Dict[str, Any]:
    """
    Computes exact share sizing and risk metrics for a trade setup.
    """
    if entry_price <= 0 or stop_loss <= 0 or capital <= 0:
        return {"error": "Invalid input parameters: prices and capital must be positive."}

    risk_per_share = abs(entry_price - stop_loss)
    if risk_per_share == 0:
        return {"error": "Stop loss cannot be identical to entry price."}

    total_risk_budget = capital * (risk_pct / 100.0)
    raw_shares = total_risk_budget / risk_per_share
    shares = math.floor(raw_shares)

    if shares < 1:
        shares = 1

    capital_required = shares * entry_price
    max_allowed_capital = capital * (max_portfolio_allocation_pct / 100.0)

    # Adjust shares if capital allocation exceeds limit
    if capital_required > capital:
        shares = math.floor(capital / entry_price)
        capital_required = shares * entry_price

    actual_risk_amount = shares * risk_per_share
    actual_risk_pct = (actual_risk_amount / capital) * 100.0
    portfolio_allocation_pct = (capital_required / capital) * 100.0

    target_1 = round(entry_price + (risk_per_share * 2.0), 2)
    target_2 = round(entry_price + (risk_per_share * 3.0), 2)
    custom_target = target_price if target_price else target_1

    reward_per_share_t1 = abs(target_1 - entry_price)
    reward_per_share_t2 = abs(target_2 - entry_price)
    reward_per_share_custom = abs(custom_target - entry_price)

    profit_target_1 = round(shares * reward_per_share_t1, 2)
    profit_target_2 = round(shares * reward_per_share_t2, 2)
    profit_custom = round(shares * reward_per_share_custom, 2)

    rr_ratio = round(reward_per_share_custom / risk_per_share, 2) if risk_per_share > 0 else 0.0

    return {
        "shares": shares,
        "entry_price": round(entry_price, 2),
        "stop_loss": round(stop_loss, 2),
        "target_1_2R": target_1,
        "target_2_3R": target_2,
        "custom_target": round(custom_target, 2),
        "risk_per_share": round(risk_per_share, 2),
        "reward_per_share": round(reward_per_share_custom, 2),
        "risk_reward_ratio": f"1:{rr_ratio}",
        "total_risk_amount": round(actual_risk_amount, 2),
        "total_risk_pct": round(actual_risk_pct, 2),
        "capital_required": round(capital_required, 2),
        "portfolio_allocation_pct": round(portfolio_allocation_pct, 2),
        "potential_profit_target_1": profit_target_1,
        "potential_profit_target_2": profit_target_2,
        "potential_profit_custom": profit_custom,
        "is_over_allocation": capital_required > max_allowed_capital,
        "warnings": [
            "Capital required exceeds recommended single stock exposure (25%)"
        ] if capital_required > max_allowed_capital else []
    }
