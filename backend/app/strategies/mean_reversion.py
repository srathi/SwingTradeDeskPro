"""
Mean Reversion Swing Strategy (Bollinger Bands + Oversold RSI Bounce).
Captures high-probability reversal bounces from extreme oversold price levels back to fair value (20 SMA).
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, Optional
from backend.app.strategies.base import BaseStrategy
from backend.app.core.indicator_engine import compute_all_indicators


class MeanReversionStrategy(BaseStrategy):
    name: str = "Mean Reversion (Bollinger + RSI)"
    strategy_id: str = "mean_reversion"
    description: str = "Enters on oversold extremes when price tests the Lower Bollinger Band with an RSI hook and bullish rejection candle."
    default_params: Dict[str, Any] = {
        "min_price": 50.0,
        "min_volume": 300_000,
        "rsi_oversold": 35.0,
        "bb_length": 20,
        "bb_std": 2.0,
        "rr_target_1": 1.5,
        "rr_target_2": 2.0
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
        bb_lower = float(latest['BB_Lower'])
        bb_mid = float(latest['BB_Middle'])
        bb_upper = float(latest['BB_Upper'])
        rsi_val = float(latest['RSI_14'])
        vol_sma = float(latest['Vol_SMA20'])
        vol_ratio = float(latest['Vol_Ratio'])
        atr_val = float(latest['ATR_14'])

        # 1. Liquidity Check
        if close < p["min_price"] or vol_sma < p["min_volume"]:
            return None

        # 2. Bollinger Band Oversold Test (Low touches/crosses below lower band or Close <= BB_Lower * 1.01)
        is_oversold_band = (low <= bb_lower * 1.01) or (prev['Close'] <= prev['BB_Lower'])

        # 3. RSI Oversold Condition
        is_rsi_oversold = rsi_val <= p["rsi_oversold"] or prev['RSI_14'] <= p["rsi_oversold"]

        # 4. Bullish Reversal Bar (Green candle or long lower shadow / pin bar)
        is_bullish = (close >= open_price) or ((close - low) > (high - close) * 1.5)

        if is_oversold_band and is_rsi_oversold and is_bullish:
            stop_loss = round(min(low, prev['Low']) - (atr_val * 0.4), 2)
            risk = round(close - stop_loss, 2)
            if risk <= 0:
                return None

            target_1 = round(min(bb_mid, close + (risk * p["rr_target_1"])), 2)
            target_2 = round(close + (risk * p["rr_target_2"]), 2)

            # Score Calculation (0-100)
            score = 65
            if rsi_val <= 28:
                score += 15
            elif rsi_val <= 32:
                score += 10
            if close >= open_price:
                score += 10
            if vol_ratio >= 1.2:
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
                "ema_50": round(float(latest['EMA_50']), 2),
                "ema_200": round(float(latest['EMA_200']), 2) if 'EMA_200' in latest else 0.0,
                "rsi": round(rsi_val, 1),
                "atr": round(atr_val, 2),
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
                "setup_summary": f"Oversold RSI {round(rsi_val, 1)} bounce off Lower Bollinger Band ₹{round(bb_lower, 1)}.",
                "setup_date": str(latest.name)[:10] if hasattr(latest, 'name') else "",
                "indicators": {
                    "rsi": round(rsi_val, 1),
                    "bb_lower": round(bb_lower, 2),
                    "bb_middle": round(float(latest.get('BB_Middle', bb_mid)), 2),
                    "ema_20": round(float(latest['EMA_20']), 2),
                    "ema_50": round(float(latest['EMA_50']), 2),
                    "atr": round(atr_val, 2),
                    "vol_ratio": round(vol_ratio, 2)
                },
                "reasons": [
                    f"2-Sigma price deviation bouncing off Lower Bollinger Band (₹{round(bb_lower, 1)})",
                    f"Oversold RSI(14) in accumulation zone ({round(rsi_val, 1)})",
                    f"Reversal rejection candle targeting 20 SMA mean reversion"
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

        for i in range(30, len(data)):
            curr = data.iloc[i]
            prev = data.iloc[i - 1]

            close = curr['Close']
            open_p = curr['Open']
            low = curr['Low']
            high = curr['High']
            bb_lower = curr['BB_Lower']
            bb_mid = curr['BB_Middle']
            rsi_val = curr['RSI_14']
            atr_val = curr['ATR_14']
            vol_sma = curr['Vol_SMA20']

            if close < p["min_price"] or vol_sma < p["min_volume"]:
                continue

            is_oversold_band = (low <= bb_lower * 1.01) or (prev['Close'] <= prev['BB_Lower'])
            is_rsi_oversold = rsi_val <= p["rsi_oversold"] or prev['RSI_14'] <= p["rsi_oversold"]
            is_bullish = (close >= open_p) or ((close - low) > (high - close) * 1.5)

            if is_oversold_band and is_rsi_oversold and is_bullish:
                sl = round(min(low, prev['Low']) - (atr_val * 0.4), 2)
                risk = close - sl
                if risk > 0:
                    data.iat[i, data.columns.get_loc('Signal')] = 1
                    data.iat[i, data.columns.get_loc('Stop_Loss')] = sl
                    data.iat[i, data.columns.get_loc('Target_1')] = round(min(bb_mid, close + (risk * p["rr_target_1"])), 2)
                    data.iat[i, data.columns.get_loc('Target_2')] = round(close + (risk * p["rr_target_2"]), 2)

        return data
