from typing import Dict
from backend.app.strategies.base import BaseStrategy
from backend.app.strategies.trend_pullback import TrendPullbackStrategy
from backend.app.strategies.vcp_breakout import VCPBreakoutStrategy
from backend.app.strategies.mean_reversion import MeanReversionStrategy

STRATEGY_REGISTRY: Dict[str, BaseStrategy] = {
    "trend_pullback": TrendPullbackStrategy(),
    "vcp_breakout": VCPBreakoutStrategy(),
    "mean_reversion": MeanReversionStrategy()
}


def get_strategy(strategy_id: str) -> BaseStrategy:
    return STRATEGY_REGISTRY.get(strategy_id, STRATEGY_REGISTRY["trend_pullback"])


def list_strategies():
    return [
        {
            "id": k,
            "name": v.name,
            "description": v.description,
            "default_params": v.default_params
        }
        for k, v in STRATEGY_REGISTRY.items()
    ]
