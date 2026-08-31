"""
Trend-Pullback Swing Trading Strategy (20/50/200 EMA + RSI Momentum).
Rides established macro uptrends by entering on shallow retracements to dynamic support (20 or 50 EMA).
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, Optional
from backend.app.strategies.base import BaseStrategy
from backend.app.core.indicator_engine import compute_all_indicators


class TrendPullbackStrategy(BaseStrategy):
    name: str = "Trend Pullback (20/50 EMA)"
    strategy_id: str = "trend_pullback"
    description: str = "Enters on shallow retracements to the rising 20 or 50 EMA in strong macro uptrends with bullish candlestick confirmation."
    default_params: Dict[str, Any] = {
        "min_price": 50.0,
        "min_volume": 100_000,
        "rsi_min": 38.0,
        "rsi_max": 68.0,
        "atr_stop_mult": 0.5,
        "rr_target_1": 2.0,
        "rr_target_2": 3.0
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
        latest = data.iloc[-1]
        prev = data.iloc[-2] if len(data) >= 2 else latest

        close = float(latest['Close'])
        open_price = float(latest['Open'])
        low = float(latest['Low'])
        high = float(latest['High'])
        ema20 = float(latest.get('EMA_20', close))
        ema50 = float(latest.get('EMA_50', close))
        ema200 = float(latest.get('EMA_200', ema50))
        rsi_val = float(latest.get('RSI_14', 50.0))
        atr_val = float(latest.get('ATR_14', close * 0.02))
        vol_sma = float(latest.get('Vol_SMA20', 100_000))
        vol_ratio = float(latest.get('Vol_Ratio', 1.0))

        # 1. Liquidity & Price
        if close < p["min_price"] or vol_sma < p["min_volume"]:
            return None

        # 2. Macro Uptrend (Price > 200 EMA & 20 EMA > 50 EMA or Price > 50 EMA)
        is_uptrend = (ema20 >= ema50 * 0.985) and (close >= ema200 * 0.98 if len(df) >= 150 else close >= ema50 * 0.98)
        if not is_uptrend:
            return None

        # 3. Pullback to 20 EMA or 50 EMA (Low touches/dips near dynamic support, Close holds or bounces)
        is_pb_20 = (low <= ema20 * 1.015) and (close >= ema20 * 0.985)
        is_pb_50 = (low <= ema50 * 1.015) and (close >= ema50 * 0.985)
        is_pullback = is_pb_20 or is_pb_50
        if not is_pullback:
            return None

        # 4. Momentum & Candlestick Confirmation
        is_rsi_valid = (rsi_val >= p["rsi_min"]) and (rsi_val <= p["rsi_max"])
        is_bullish = (close >= open_price) or (close >= low + (high - low) * 0.35)
        if not (is_rsi_valid and is_bullish):
            return None

        # Calculate Stop Loss & Targets
        stop_loss = round(min(low, float(prev['Low'])) - (atr_val * p["atr_stop_mult"]), 2)
        risk = round(close - stop_loss, 2)
        risk_pct = round((risk / close) * 100.0, 2) if close > 0 else 0.0
        if risk <= 0 or risk_pct > 9.0:
            return None

        target_1 = round(close + (risk * p["rr_target_1"]), 2)
        target_2 = round(close + (risk * p["rr_target_2"]), 2)
        reward_pct_t1 = round(((target_1 - close) / close) * 100.0, 2)
        reward_pct_t2 = round(((target_2 - close) / close) * 100.0, 2)

        # Quality Score Calculation (0 to 100)
        score = 60
        if rsi_val >= 48 and rsi_val <= 62:
            score += 15
        if vol_ratio >= 1.15:
            score += 15
        if close > open_price and (close - open_price) > (high - low) * 0.4:
            score += 10
        score = min(score, 100)

        pb_support_label = "20 EMA" if is_pb_20 else "50 EMA"
        pb_price = ema20 if is_pb_20 else ema50

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
            "ema_20": round(float(ema20), 2),
            "ema_50": round(float(ema50), 2),
            "ema_200": round(float(ema200), 2),
            "rsi": round(float(rsi_val), 1),
            "atr": round(float(atr_val), 2),
            "vol_ratio": round(float(vol_ratio), 2),
            "stop_loss": stop_loss,
            "target_1": target_1,
            "target_2": target_2,
            "risk_per_share": risk,
            "risk_pct": risk_pct,
            "reward_pct_t1": reward_pct_t1,
            "reward_pct_t2": reward_pct_t2,
            "r_multiple_t1": p["rr_target_1"],
            "r_multiple_t2": p["rr_target_2"],
            "rr_ratio": f"1:{p['rr_target_1']}",
            "setup_summary": f"Pullback to {pb_support_label} (₹{round(pb_price, 1)}) with RSI {round(rsi_val, 1)} in Stage 2 uptrend.",
            "setup_date": str(latest.name)[:10] if hasattr(latest, 'name') else "",
            "indicators": {
                "ema_20": round(float(ema20), 2),
                "ema_50": round(float(ema50), 2),
                "ema_200": round(float(ema200), 2),
                "rsi": round(float(rsi_val), 1),
                "atr": round(float(atr_val), 2),
                "vol_ratio": round(float(vol_ratio), 2)
            },
            "reasons": [
                f"Pullback to {pb_support_label} (₹{round(pb_price, 1)}) support in verified Stage 2 trend",
                f"Momentum RSI(14) in optimal entry zone ({round(rsi_val, 1)})",
                f"Bullish confirmation close with 1:{p['rr_target_1']} risk-to-reward (+{reward_pct_t1}%)"
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
            prev = data.iloc[i - 1]

            close = float(curr['Close'])
            open_p = float(curr['Open'])
            low = float(curr['Low'])
            high = float(curr['High'])
            ema20 = float(curr.get('EMA_20', close))
            ema50 = float(curr.get('EMA_50', close))
            ema200 = float(curr.get('EMA_200', ema50))
            rsi_val = float(curr.get('RSI_14', 50.0))
            atr_val = float(curr.get('ATR_14', close * 0.02))
            vol_sma = float(curr.get('Vol_SMA20', 100_000))

            if close < p["min_price"] or vol_sma < p["min_volume"]:
                continue

            # Macro Uptrend
            is_uptrend = (ema20 >= ema50 * 0.985) and (close >= ema200 * 0.98 if i >= 150 else close >= ema50 * 0.98)

            # Pullback to 20 or 50 EMA
            is_pb_20 = (low <= ema20 * 1.015) and (close >= ema20 * 0.985)
            is_pb_50 = (low <= ema50 * 1.015) and (close >= ema50 * 0.985)
            is_pullback = is_pb_20 or is_pb_50

            is_rsi_valid = (rsi_val >= p["rsi_min"]) and (rsi_val <= p["rsi_max"])
            is_bullish = (close >= open_p) or (close >= low + (high - low) * 0.35)

            if is_uptrend and is_pullback and is_rsi_valid and is_bullish:
                sl = round(min(low, float(prev['Low'])) - (atr_val * p["atr_stop_mult"]), 2)
                risk = close - sl
                risk_pct = (risk / close) * 100.0 if close > 0 else 0.0
                if risk > 0 and risk_pct <= 9.0:
                    data.iat[i, data.columns.get_loc('Signal')] = 1
                    data.iat[i, data.columns.get_loc('Stop_Loss')] = sl
                    data.iat[i, data.columns.get_loc('Target_1')] = round(close + (risk * p["rr_target_1"]), 2)
                    data.iat[i, data.columns.get_loc('Target_2')] = round(close + (risk * p["rr_target_2"]), 2)

        return data

