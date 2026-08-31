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
        "min_volume": 100_000,
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
        if df is None or len(df) < 35:
            return None

        data = compute_all_indicators(df)
        curr = data.iloc[-1]
        prev = data.iloc[-2] if len(data) >= 2 else curr

        close = float(curr['Close'])
        open_p = float(curr['Open'])
        high = float(curr['High'])
        low = float(curr['Low'])
        vol = float(curr['Volume'])
        vol_sma = float(curr.get('Vol_SMA20', vol))
        vol_ratio = float(curr.get('Vol_Ratio', 1.0))
        atr_val = float(curr.get('ATR_14', close * 0.02))

        # Basic liquidity filters
        if close < p["min_price"] or vol_sma < p["min_volume"]:
            return None

        # 1. Stage-2 Trend Alignment: Close >= EMA 20, EMA 20 >= EMA 50, EMA 50 >= EMA 200
        ema20 = float(curr.get('EMA_20', close))
        ema50 = float(curr.get('EMA_50', close))
        ema200 = float(curr.get('EMA_200', ema50))
        is_stage2 = (close >= ema20 * 0.99) and (ema20 >= ema50 * 0.99) and (ema50 >= ema200 * 0.98 if len(data) >= 150 else True)
        if not is_stage2:
            return None

        # 2. Breakout to 20-Day or 50-Day High (or near-high handle)
        high20_prev = float(data['High_20'].iloc[-2]) if len(data) >= 2 else close
        is_breakout = (close >= high20_prev * 0.995) or (high >= high20_prev)
        if not is_breakout:
            return None

        # 3. Institutional Volume Confirmation (>= 1.15x)
        if vol_ratio < 1.15:
            return None

        # 4. Bullish Candlestick Structure
        if close < open_p and close < (low + (high - low) * 0.35):
            return None

        # Sizing & Risk Management
        recent_10d_low = float(data['Low'].iloc[-10:].min())
        stop_loss = round(max(recent_10d_low, ema20 * 0.98, close - (atr_val * p["atr_multiplier_sl"])), 2)
        risk_per_share = round(close - stop_loss, 2)
        risk_pct = round((risk_per_share / close) * 100.0, 2) if close > 0 else 0.0
        if risk_per_share <= 0 or risk_pct > 9.0:
            return None

        target_1 = round(close + (risk_per_share * p["rr_target_1"]), 2)
        target_2 = round(close + (risk_per_share * p["rr_target_2"]), 2)

        # Quality scoring
        score = 60
        if vol_ratio >= 1.35: score += 15
        if vol_ratio >= 1.8: score += 10
        if close >= float(curr.get('High_50', close)) * 0.995: score += 15
        score = min(100, score)

        if score < p["min_score"]:
            return None

        return {
            "ticker": ticker,
            "strategy": self.name,
            "strategy_id": self.strategy_id,
            "score": score,
            "close": round(close, 2),
            "open": round(open_p, 2),
            "high": round(high, 2),
            "low": round(low, 2),
            "volume": int(curr.get('Volume', 0)),
            "ema_20": round(ema20, 2),
            "ema_50": round(ema50, 2),
            "ema_200": round(ema200, 2),
            "rsi": round(float(curr.get('RSI_14', 50.0)), 1),
            "atr": round(float(curr.get('ATR_14', close * 0.02)), 2),
            "vol_ratio": round(vol_ratio, 2),
            "stop_loss": stop_loss,
            "target_1": target_1,
            "target_2": target_2,
            "risk_per_share": risk_per_share,
            "risk_pct": risk_pct,
            "r_multiple_t1": p["rr_target_1"],
            "r_multiple_t2": p["rr_target_2"],
            "reward_pct_t1": round(((target_1 - close) / close) * 100.0, 2),
            "reward_pct_t2": round(((target_2 - close) / close) * 100.0, 2),
            "rr_ratio": f"1:{p['rr_target_1']}",
            "volume_ratio": round(vol_ratio, 2),
            "setup_summary": f"Stage-2 momentum breakout to 20-day high with {vol_ratio:.1f}x volume surge in confirmed trend alignment.",
            "setup_date": str(curr.name)[:10] if hasattr(curr, 'name') else "",
            "indicators": {
                "rsi": round(float(curr.get('RSI_14', 50.0)), 1),
                "ema_20": round(ema20, 2),
                "ema_50": round(ema50, 2),
                "ema_200": round(ema200, 2),
                "atr": round(float(curr.get('ATR_14', close * 0.02)), 2),
                "vol_ratio": round(vol_ratio, 2)
            },
            "reasons": [
                f"Breakout to new 20-day high on {vol_ratio:.1f}x volume surge",
                f"Stage-2 Bullish alignment (Close > 20 EMA > 50 EMA)",
                f"Mansfield Relative Strength market outperformance"
            ]
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

        start_idx = 35 if len(data) >= 50 else 20
        for i in range(start_idx, len(data)):
            curr = data.iloc[i]
            close = float(curr['Close'])
            open_p = float(curr['Open'])
            high = float(curr['High'])
            low = float(curr['Low'])
            ema20 = float(curr.get('EMA_20', close))
            ema50 = float(curr.get('EMA_50', close))
            ema200 = float(curr.get('EMA_200', ema50))
            atr_val = float(curr.get('ATR_14', close * 0.02))
            vol_sma = float(curr.get('Vol_SMA20', 100_000))
            vol_ratio = float(curr.get('Vol_Ratio', 1.0))

            if close < p["min_price"] or vol_sma < p["min_volume"]:
                continue

            # Stage 2 + 20D Breakout + Volume expansion
            is_stage2 = (close >= ema20 * 0.99) and (ema20 >= ema50 * 0.99) and (ema50 >= ema200 * 0.98 if i >= 150 else True)
            high20_prev = float(data['High_20'].iloc[i - 1]) if i >= 1 else close
            is_breakout = (close >= high20_prev * 0.995) or (high >= high20_prev)
            is_vol_surge = (vol_ratio >= 1.15) and (close >= open_p or close >= low + (high - low) * 0.35)

            if is_stage2 and is_breakout and is_vol_surge:
                look_low = float(data['Low'].iloc[max(0, i - 10):i+1].min())
                sl = round(max(look_low, ema20 * 0.98, close - (atr_val * p["atr_multiplier_sl"])), 2)
                risk = close - sl
                risk_pct = (risk / close) * 100.0 if close > 0 else 0.0
                if risk > 0 and risk_pct <= 9.0:
                    data.iat[i, data.columns.get_loc('Signal')] = 1
                    data.iat[i, data.columns.get_loc('Stop_Loss')] = sl
                    data.iat[i, data.columns.get_loc('Target_1')] = round(close + (risk * p["rr_target_1"]), 2)
                    data.iat[i, data.columns.get_loc('Target_2')] = round(close + (risk * p["rr_target_2"]), 2)

        return data
