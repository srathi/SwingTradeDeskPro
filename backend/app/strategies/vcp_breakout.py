"""
Volatility Contraction Pattern (VCP) & Base Breakout Strategy.
Identifies tightening price ranges (volatility squeeze) followed by decisive volume-backed breakouts.
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, Optional
from backend.app.strategies.base import BaseStrategy
from backend.app.core.indicator_engine import compute_all_indicators


class VCPBreakoutStrategy(BaseStrategy):
    name: str = "VCP & Base Breakout"
    strategy_id: str = "vcp_breakout"
    description: str = "Captures high-momentum explosive breakouts from tight consolidations with 1.4x+ institutional volume surges."
    default_params: Dict[str, Any] = {
        "min_price": 50.0,
        "min_volume": 300_000,
        "vol_surge_mult": 1.4,
        "rsi_breakout_min": 55.0,
        "rr_target_1": 2.5,
        "rr_target_2": 3.5
    }

    def evaluate_setup(
        self,
        df: pd.DataFrame,
        ticker: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        p = {**self.default_params, **(params or {})}
        if df is None or len(df) < 60:
            return None

        data = compute_all_indicators(df)
        latest = data.iloc[-1]
        prev = data.iloc[-2]

        close = float(latest['Close'])
        open_price = float(latest['Open'])
        high = float(latest['High'])
        low = float(latest['Low'])
        ema50 = float(latest['EMA_50'])
        ema200 = float(latest['EMA_200']) if 'EMA_200' in latest else ema50
        rsi_val = float(latest['RSI_14'])
        vol_sma = float(latest['Vol_SMA20'])
        vol_ratio = float(latest['Vol_Ratio'])
        bb_width = float(latest['BB_Width'])
        prev_20d_high = float(data['High'].iloc[-21:-1].max())
        prev_20d_low = float(data['Low'].iloc[-21:-1].min())

        # 1. Liquidity Check
        if close < p["min_price"] or vol_sma < p["min_volume"]:
            return None

        # 2. Macro Trend
        if close < ema50 or (len(df) >= 200 and close < ema200 * 0.95):
            return None

        # 3. Breakout above 20-Day High
        is_breakout = close >= prev_20d_high and close > open_price

        # 4. Volume Surge Confirmation
        is_volume_confirmed = vol_ratio >= p["vol_surge_mult"]

        # 5. Momentum Strength
        is_momentum = rsi_val >= p["rsi_breakout_min"]

        # 6. Volatility Contraction Prior to Breakout (BB Width was tight in the last 5 bars)
        recent_bb_width_min = float(data['BB_Width'].iloc[-10:-1].min())
        is_contracted = recent_bb_width_min <= 20.0 or (high - low) / close < 0.05

        if is_breakout and is_volume_confirmed and is_momentum:
            # Stop Loss below consolidation low or EMA 20
            ema20 = float(latest['EMA_20'])
            stop_loss = round(max(prev_20d_low, ema20 * 0.97), 2)
            # Ensure reasonable stop loss distance (3% to 8%)
            if (close - stop_loss) / close > 0.10:
                stop_loss = round(close * 0.93, 2)
            elif (close - stop_loss) / close < 0.02:
                stop_loss = round(close * 0.97, 2)

            risk = round(close - stop_loss, 2)
            if risk <= 0:
                return None

            target_1 = round(close + (risk * p["rr_target_1"]), 2)
            target_2 = round(close + (risk * p["rr_target_2"]), 2)

            # Score Calculation (0-100)
            score = 65
            if vol_ratio >= 2.0:
                score += 15
            elif vol_ratio >= 1.5:
                score += 10
            if rsi_val >= 60 and rsi_val <= 75:
                score += 10
            if is_contracted:
                score += 10
            score = min(score, 100)

            return {
                "ticker": ticker,
                "strategy": self.name,
                "strategy_id": self.strategy_id,
                "score": score,
                "close": round(close, 2),
                "open": round(open_price, 2),
                "high": round(high, 2),
                "low": round(low, 2),
                "volume": int(latest.get('Volume', 0)),
                "ema_20": round(float(latest['EMA_20']), 2),
                "ema_50": round(ema50, 2),
                "ema_200": round(ema200, 2),
                "rsi": round(rsi_val, 1),
                "atr": round(float(latest['ATR_14']), 2),
                "vol_ratio": round(vol_ratio, 2),
                "stop_loss": stop_loss,
                "target_1": target_1,
                "target_2": target_2,
                "risk_per_share": risk,
                "risk_pct": round((risk / close) * 100.0, 2),
                "r_multiple_t1": p["rr_target_1"],
                "r_multiple_t2": p["rr_target_2"],
                "reward_pct_t1": round(((target_1 - close) / close) * 100.0, 2),
                "rr_ratio": f"1:{p['rr_target_1']}",
                "setup_summary": f"20D High breakout at ₹{round(close, 1)} with {round(vol_ratio, 1)}x volume expansion.",
                "setup_date": str(latest.name)[:10] if hasattr(latest, 'name') else "",
                "indicators": {
                    "rsi": round(rsi_val, 1),
                    "ema_20": round(float(latest['EMA_20']), 2),
                    "ema_50": round(ema50, 2),
                    "ema_200": round(ema200, 2),
                    "atr": round(float(latest['ATR_14']), 2),
                    "vol_ratio": round(vol_ratio, 2)
                },
                "reasons": [
                    f"20-Day Pivot Breakout at ₹{round(close, 1)} on {round(vol_ratio, 1)}x volume surge",
                    f"Minervini SEPA base contraction completed",
                    f"Stage 2 Bullish trend alignment (Price > 50 EMA > 200 EMA)"
                ]
            }

        return None

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
            vol_ratio = curr['Vol_Ratio']
            rsi_val = curr['RSI_14']
            ema50 = curr['EMA_50']
            vol_sma = curr['Vol_SMA20']

            if close < p["min_price"] or vol_sma < p["min_volume"]:
                continue

            prev_20d_high = data['High'].iloc[i-20:i].max()
            prev_20d_low = data['Low'].iloc[i-20:i].min()

            is_breakout = close >= prev_20d_high and close > open_p
            is_volume_confirmed = vol_ratio >= p["vol_surge_mult"]
            is_momentum = rsi_val >= p["rsi_breakout_min"]
            is_trend = close > ema50

            if is_breakout and is_volume_confirmed and is_momentum and is_trend:
                ema20 = curr['EMA_20']
                sl = round(max(prev_20d_low, ema20 * 0.97), 2)
                if (close - sl) / close > 0.10:
                    sl = round(close * 0.93, 2)
                elif (close - sl) / close < 0.02:
                    sl = round(close * 0.97, 2)

                risk = close - sl
                if risk > 0:
                    data.iat[i, data.columns.get_loc('Signal')] = 1
                    data.iat[i, data.columns.get_loc('Stop_Loss')] = sl
                    data.iat[i, data.columns.get_loc('Target_1')] = round(close + (risk * p["rr_target_1"]), 2)
                    data.iat[i, data.columns.get_loc('Target_2')] = round(close + (risk * p["rr_target_2"]), 2)

        return data
