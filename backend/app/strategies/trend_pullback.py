"""
Trend-Pullback Swing Trading Strategy (20/50/200 EMA + RSI Momentum).
Rides established macro uptrends by entering on shallow retracements to dynamic support (20 EMA).
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, Optional
from backend.app.strategies.base import BaseStrategy
from backend.app.core.indicator_engine import compute_all_indicators


class TrendPullbackStrategy(BaseStrategy):
    name: str = "Trend Pullback (20/50 EMA)"
    strategy_id: str = "trend_pullback"
    description: str = "Enters on shallow retracements to the rising 20 EMA in strong macro uptrends with bullish candlestick confirmation."
    default_params: Dict[str, Any] = {
        "min_price": 50.0,
        "min_volume": 300_000,
        "rsi_min": 40.0,
        "rsi_max": 65.0,
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
        if df is None or len(df) < 200:
            return None

        data = compute_all_indicators(df)
        latest = data.iloc[-1]
        prev = data.iloc[-2]

        close = float(latest['Close'])
        open_price = float(latest['Open'])
        low = float(latest['Low'])
        high = float(latest['High'])
        ema20 = float(latest['EMA_20'])
        ema50 = float(latest['EMA_50'])
        ema200 = float(latest['EMA_200'])
        rsi_val = float(latest['RSI_14'])
        atr_val = float(latest['ATR_14'])
        vol_sma = float(latest['Vol_SMA20'])
        vol_ratio = float(latest['Vol_Ratio'])

        # 1. Liquidity & Price
        if close < p["min_price"] or vol_sma < p["min_volume"]:
            return None

        # 2. Macro Uptrend (Price > 200 EMA & 20 EMA > 50 EMA & 50 EMA > 200 EMA)
        is_uptrend = (close > ema200) and (ema20 > ema50) and (ema50 > ema200 * 0.98)
        if not is_uptrend:
            return None

        # 3. Pullback to 20 EMA (Low touches/dips below 20 EMA, Close holds above or within 0.5% of 20 EMA)
        tolerance = ema20 * 0.007
        is_pullback = (low <= ema20 + tolerance) and (close >= ema20 - tolerance)
        if not is_pullback:
            return None

        # 4. Momentum & Candlestick Confirmation
        is_rsi_valid = (rsi_val >= p["rsi_min"]) and (rsi_val <= p["rsi_max"])
        is_bullish = close >= open_price
        if not (is_rsi_valid and is_bullish):
            return None

        # Calculate Stop Loss & Targets
        stop_loss = round(min(low, prev['Low']) - (atr_val * p["atr_stop_mult"]), 2)
        risk = round(close - stop_loss, 2)
        if risk <= 0:
            return None

        target_1 = round(close + (risk * p["rr_target_1"]), 2)
        target_2 = round(close + (risk * p["rr_target_2"]), 2)

        # Quality Score Calculation (0 to 100)
        score = 60
        if rsi_val >= 50 and rsi_val <= 60:
            score += 15
        if vol_ratio >= 1.2:
            score += 15
        if close > open_price and (close - open_price) > (high - low) * 0.5:
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
            "ema_20": round(ema20, 2),
            "ema_50": round(ema50, 2),
            "ema_200": round(ema200, 2),
            "rsi": round(rsi_val, 1),
            "atr": round(atr_val, 2),
            "vol_ratio": round(vol_ratio, 2),
            "stop_loss": stop_loss,
            "target_1": target_1,
            "target_2": target_2,
            "risk_per_share": risk,
            "risk_pct": round((risk / close) * 100.0, 2),
            "reward_pct_t1": round(((target_1 - close) / close) * 100.0, 2),
            "rr_ratio": f"1:{p['rr_target_1']}",
            "setup_summary": f"Pullback at ₹{round(ema20, 1)} with RSI {round(rsi_val, 1)} in macro uptrend."
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

        for i in range(200, len(data)):
            curr = data.iloc[i]
            prev = data.iloc[i - 1]

            close = curr['Close']
            open_p = curr['Open']
            low = curr['Low']
            ema20 = curr['EMA_20']
            ema50 = curr['EMA_50']
            ema200 = curr['EMA_200']
            rsi_val = curr['RSI_14']
            atr_val = curr['ATR_14']
            vol_sma = curr['Vol_SMA20']

            if close < p["min_price"] or vol_sma < p["min_volume"]:
                continue

            is_uptrend = (close > ema200) and (ema20 > ema50)
            tolerance = ema20 * 0.007
            is_pullback = (low <= ema20 + tolerance) and (close >= ema20 - tolerance)
            is_rsi_valid = (rsi_val >= p["rsi_min"]) and (rsi_val <= p["rsi_max"])
            is_bullish = close >= open_p

            if is_uptrend and is_pullback and is_rsi_valid and is_bullish:
                sl = round(min(low, prev['Low']) - (atr_val * p["atr_stop_mult"]), 2)
                risk = close - sl
                if risk > 0:
                    data.iat[i, data.columns.get_loc('Signal')] = 1
                    data.iat[i, data.columns.get_loc('Stop_Loss')] = sl
                    data.iat[i, data.columns.get_loc('Target_1')] = round(close + (risk * p["rr_target_1"]), 2)
                    data.iat[i, data.columns.get_loc('Target_2')] = round(close + (risk * p["rr_target_2"]), 2)

        return data
