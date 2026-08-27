from typing import Dict
from backend.app.strategies.base import BaseStrategy
from backend.app.strategies.trend_pullback import TrendPullbackStrategy
from backend.app.strategies.vcp_breakout import VCPBreakoutStrategy
from backend.app.strategies.mean_reversion import MeanReversionStrategy
from backend.app.strategies.volatility_squeeze import VolatilitySqueezeStrategy
from backend.app.strategies.connors_rsi2 import ConnorsRSI2Strategy
from backend.app.strategies.relative_strength_leader import RelativeStrengthLeaderStrategy
from backend.app.strategies.gmma_breakout import GMMABreakoutStrategy
from backend.app.strategies.high_52w_breakout import High52WBreakoutStrategy

STRATEGY_REGISTRY: Dict[str, BaseStrategy] = {
    "trend_pullback": TrendPullbackStrategy(),
    "vcp_breakout": VCPBreakoutStrategy(),
    "high_52w_breakout": High52WBreakoutStrategy(),
    "gmma_breakout": GMMABreakoutStrategy(),
    "mean_reversion": MeanReversionStrategy(),
    "volatility_squeeze": VolatilitySqueezeStrategy(),
    "connors_rsi2": ConnorsRSI2Strategy(),
    "relative_strength_leader": RelativeStrengthLeaderStrategy()
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
