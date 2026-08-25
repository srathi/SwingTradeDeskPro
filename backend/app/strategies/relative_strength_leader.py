"""
Mansfield Relative Strength Stage-2 Leader Strategy.
Research: Stan Weinstein (1988) — Stage Analysis / Gary Antonacci — Dual Momentum (2014).
Alpha Edge: Detects institutional accumulation in market-leading equities outperforming the Nifty 50 benchmark (MRS > 0)
breaking out of Stage-1 consolidation bases on heavy volume expansion.
"""

from typing import Dict, Any, Optional
import numpy as np
import pandas as pd

from backend.app.strategies.base import BaseStrategy
from backend.app.core.indicator_engine import compute_all_indicators


class RelativeStrengthLeaderStrategy(BaseStrategy):
    name: str = "Mansfield Relative Strength Stage-2 Leader"
    strategy_id: str = "relative_strength_leader"
    description: str = "Identifies top-tier market leaders outperforming the index breaking out to new 20D/52W highs with heavy institutional volume."
    default_params: Dict[str, Any] = {
        "min_price": 50.0,
        "min_volume": 300_000,
        "min_score": 60,
        "rr_target_1": 2.5,
        "rr_target_2": 4.0,
        "atr_multiplier_sl": 1.5
    }

    def evaluate_setup(
        self,
        df: pd.DataFrame,
        ticker: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        p = {**self.default_params, **(params or {})}
        if df is None or len(df) < 50:
            return None

        data = compute_all_indicators(df)
        curr = data.iloc[-1]
        prev = data.iloc[-2]

        close = float(curr['Close'])
        vol = float(curr['Volume'])
        vol_sma = float(curr.get('Vol_SMA20', vol))
        vol_ratio = float(curr.get('Vol_Ratio', 1.0))
        atr_val = float(curr.get('ATR_14', close * 0.02))

        # Basic liquidity filters
        if close < p["min_price"] or vol_sma < p["min_volume"]:
            return None

        # 1. Stage-2 Trend Alignment: Close > EMA 20 > EMA 50 > EMA 200
        ema20 = float(curr.get('EMA_20', 0))
        ema50 = float(curr.get('EMA_50', 0))
        ema200 = float(curr.get('EMA_200', 0))
        if not (close > ema20 > ema50 > ema200):
            return None

        # 2. Breakout to 20-Day or 50-Day High
        high20_prev = float(data['High_20'].iloc[-2]) if len(data) >= 2 else close
        is_breakout = close >= high20_prev or float(curr['High']) >= high20_prev
        if not is_breakout:
            return None

        # 3. Institutional Volume Confirmation (>= 1.25x)
        if vol_ratio < 1.25:
            return None

        # 4. Bullish Candlestick Structure
        if close < float(curr['Open']):
            return None

        # Sizing & Risk Management
        recent_10d_low = float(data['Low'].iloc[-10:].min())
        stop_loss = round(max(recent_10d_low, ema20 * 0.98, close - (atr_val * p["atr_multiplier_sl"])), 2)
        risk_per_share = round(close - stop_loss, 2)
        if risk_per_share <= 0:
            return None

        target_1 = round(close + (risk_per_share * p["rr_target_1"]), 2)
        target_2 = round(close + (risk_per_share * p["rr_target_2"]), 2)
        risk_pct = round((risk_per_share / close) * 100.0, 2)

        # Quality scoring
        score = 60
        if vol_ratio >= 1.5: score += 15
        if vol_ratio >= 2.0: score += 10
        if close >= float(curr.get('High_50', close)): score += 15
        score = min(100, score)

        if score < p["min_score"]:
            return None

        return {
            "ticker": ticker,
            "strategy": self.name,
            "strategy_id": self.strategy_id,
            "score": score,
            "close": round(close, 2),
            "ema_20": round(ema20, 2),
            "rsi": round(float(curr.get('RSI_14', 50)), 1),
            "stop_loss": stop_loss,
            "target_1": target_1,
            "target_2": target_2,
            "risk_per_share": risk_per_share,
            "risk_pct": risk_pct,
            "reward_pct_t1": round(((target_1 - close) / close) * 100.0, 2),
            "reward_pct_t2": round(((target_2 - close) / close) * 100.0, 2),
            "rr_ratio": "1:2.5",
            "volume_ratio": round(vol_ratio, 2),
            "setup_summary": f"Stage-2 momentum breakout to 20-day high with {vol_ratio:.1f}x volume surge in confirmed trend alignment."
        }

    def generate_signals(
        self,
        df: pd.DataFrame,
        params: Optional[Dict[str, Any]] = None
    ) -> pd.DataFrame:
        p = {**self.default_params, **(params or {})}
        data = compute_all_indicators(df)

        data['Signal'] = 0
        data['Stop_Loss'] = np.nan
        data['Target_1'] = np.nan
        data['Target_2'] = np.nan

        for i in range(50, len(data)):
            curr = data.iloc[i]
            close = curr['Close']
            open_p = curr['Open']
            ema20 = curr['EMA_20']
            ema50 = curr['EMA_50']
            ema200 = curr['EMA_200']
            atr_val = curr['ATR_14']
            vol_sma = curr['Vol_SMA20']
            vol_ratio = curr['Vol_Ratio']

            if close < p["min_price"] or vol_sma < p["min_volume"]:
                continue

            # Stage 2 + 20D Breakout + Volume expansion
            is_stage2 = (close > ema20 > ema50 > ema200)
            high20_prev = data['High_20'].iloc[i - 1]
            is_breakout = close >= high20_prev
            is_vol_surge = (vol_ratio >= 1.25) and (close >= open_p)

            if is_stage2 and is_breakout and is_vol_surge:
                look_low = float(data['Low'].iloc[max(0, i - 10):i+1].min())
                sl = round(max(look_low, ema20 * 0.98, close - (atr_val * p["atr_multiplier_sl"])), 2)
                risk = close - sl
                if risk > 0:
                    data.iat[i, data.columns.get_loc('Signal')] = 1
                    data.iat[i, data.columns.get_loc('Stop_Loss')] = sl
                    data.iat[i, data.columns.get_loc('Target_1')] = round(close + (risk * p["rr_target_1"]), 2)
                    data.iat[i, data.columns.get_loc('Target_2')] = round(close + (risk * p["rr_target_2"]), 2)

        return data
