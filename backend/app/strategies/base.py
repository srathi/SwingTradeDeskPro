"""
Base Strategy Interface for Quantitative Swing Trading Models.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import pandas as pd


class BaseStrategy(ABC):
    name: str = "Base Strategy"
    strategy_id: str = "base"
    description: str = ""
    default_params: Dict[str, Any] = {}

    @abstractmethod
    def evaluate_setup(
        self,
        df: pd.DataFrame,
        ticker: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Evaluates the latest bar of the OHLCV dataframe for live screening setups.
        Returns a setup dictionary with Entry, Stop Loss, Targets, and Score, or None.
        """
        pass

    @abstractmethod
    def generate_signals(
        self,
        df: pd.DataFrame,
        params: Optional[Dict[str, Any]] = None
    ) -> pd.DataFrame:
        """
        Generates historical signal series for backtesting.
        Appends:
          - 'Signal': 1 (Buy Entry), 0 (Hold), -1 (Exit)
          - 'Stop_Loss': price level for stop
          - 'Target_1': price level for 1:2 R:R
          - 'Target_2': price level for 1:3 R:R
        """
        pass
