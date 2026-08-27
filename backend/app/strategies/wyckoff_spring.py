"""
Wyckoff Spring & False Breakdown Shakeout Strategy (Richard D. Wyckoff / Volume Spread Analysis).
Identifies institutional liquidity sweeps / stop hunts where price momentarily pierces below key 20-day support
and immediately rejects with a bullish hammer / absorption close back inside the trading range.
"""

from typing import Dict, Any, Optional
import numpy as np
import pandas as pd
from backend.app.strategies.base import BaseStrategy
from backend.app.core.indicator_engine import compute_all_indicators


class WyckoffSpringStrategy(BaseStrategy):
    name: str = "Wyckoff Spring Shakeout"
    strategy_id: str = "wyckoff_spring"
    description: str = "Captures institutional liquidity absorptions as price briefly pierces 20-day support to trap bears and instantly rejects back inside the range."
    default_params: Dict[str, Any] = {
        "min_price": 50.0,
        "min_volume": 100_000,
        "lookback_support": 20,
        "min_rejection_pct": 50.0,
        "rr_target_1": 2.0,
        "rr_target_2": 3.5,
        "max_risk_pct": 8.0
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
        latest = data.iloc[-1]
        prev = data.iloc[-2] if len(data) >= 2 else latest

        close = float(latest['Close'])
        open_price = float(latest['Open'])
        high = float(latest['High'])
        low = float(latest['Low'])
        vol_sma = float(latest.get('Vol_SMA20', 0))
        vol_ratio = float(latest.get('Vol_Ratio', 1.0))
        atr_val = float(latest.get('ATR_14', close * 0.02))
        ema50 = float(latest.get('EMA_50', close))
        ema200 = float(latest.get('EMA_200', ema50))

        # 1. Baseline Filter
        if close < p["min_price"]:
            return None

        # 2. Support Level Calculation (Excluding recent 3 bars)
        lookback = p["lookback_support"]
        if len(data) < lookback + 5:
            return None

        support_level = float(data['Low'].iloc[-lookback-3:-3].min())
        if support_level <= 0:
            return None

        # 3. Wyckoff Spring Condition (Shakeout within recent 3 bars)
        # Low pierced below support, but close is back above support or within 1% of it
        recent_3_lows = data['Low'].iloc[-3:].values
        recent_min_low = float(np.min(recent_3_lows))
        
        is_pierced = recent_min_low < support_level * 0.998
        is_recovered = close >= support_level * 0.99
        
        if not (is_pierced and is_recovered):
            return None

        # 4. Bullish Candlestick Rejection Tail (Hammer / Lower Shadow)
        candle_range = high - low
        if candle_range <= 0:
            return None

        close_location_pct = ((close - low) / candle_range) * 100.0
        if close_location_pct < p["min_rejection_pct"]:
            return None

        # 5. Stop Loss & Target Geometry
        spring_low = recent_min_low
        stop_loss = round(spring_low - (atr_val * 0.5), 2)
        risk = round(close - stop_loss, 2)
        risk_pct = (risk / close) * 100.0 if close > 0 else 0.0

        if risk_pct > p["max_risk_pct"]:
            stop_loss = round(close * (1.0 - (p["max_risk_pct"] / 100.0)), 2)
            risk = round(close - stop_loss, 2)
        elif risk_pct < 1.8:
            stop_loss = round(close * 0.975, 2)
            risk = round(close - stop_loss, 2)

        if risk <= 0:
            return None

        target_1 = round(close + (risk * p["rr_target_1"]), 2)
        target_2 = round(close + (risk * p["rr_target_2"]), 2)

        # 6. Quality Score (60 - 100)
        score = 65
        if close_location_pct >= 70.0:
            score += 15 # Strong pin bar hammer
        elif close_location_pct >= 60.0:
            score += 10
        if vol_ratio >= 1.25:
            score += 10 # High volume institutional absorption
        if close >= open_price:
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
            "volume": int(latest['Volume']),
            "stop_loss": stop_loss,
            "target_1": target_1,
            "target_2": target_2,
            "risk_per_share": risk,
            "risk_pct": round((risk / close) * 100.0, 2),
            "r_multiple_t1": p["rr_target_1"],
            "r_multiple_t2": p["rr_target_2"],
            "setup_date": str(latest.name)[:10] if hasattr(latest, 'name') else "",
            "indicators": {
                "support_level": round(support_level, 2),
                "spring_low": round(spring_low, 2),
                "rejection_pct": round(close_location_pct, 1),
                "rsi": round(float(latest.get('RSI_14', 50.0)), 1),
                "atr": round(atr_val, 2),
                "vol_ratio": round(vol_ratio, 2),
                "ema_50": round(ema50, 2),
                "ema_200": round(ema200, 2)
            },
            "reasons": [
                f"Wyckoff Spring shakeout below ₹{round(support_level, 1)} support floor",
                f"Bullish absorption tail ({round(close_location_pct, 1)}% close location)",
                f"Quick recovery back inside trading range",
                f"Asymmetric risk geometry ({p['rr_target_1']}R / {p['rr_target_2']}R targets)"
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

        if len(data) < 50:
            return data

        lookback = p["lookback_support"]

        for i in range(lookback + 5, len(data)):
            curr = data.iloc[i]
            close = curr['Close']
            low = curr['Low']
            high = curr['High']
            atr_val = curr['ATR_14']

            if close < p["min_price"]:
                continue

            support = data['Low'].iloc[i - lookback - 3:i - 2].min()
            if support <= 0:
                continue

            if low < support * 0.998 and close >= support * 0.99:
                c_range = high - low
                if c_range > 0:
                    c_loc = ((close - low) / c_range) * 100.0
                    if c_loc >= p["min_rejection_pct"]:
                        sl = round(low - (atr_val * 0.5), 2)
                        risk = close - sl
                        risk_pct = (risk / close) * 100.0 if close > 0 else 0.0

                        if risk_pct > p["max_risk_pct"]:
                            sl = round(close * (1.0 - (p["max_risk_pct"] / 100.0)), 2)
                            risk = close - sl
                        elif risk_pct < 1.8:
                            sl = round(close * 0.975, 2)
                            risk = close - sl

                        if risk > 0:
                            data.iat[i, data.columns.get_loc('Signal')] = 1
                            data.iat[i, data.columns.get_loc('Stop_Loss')] = sl
                            data.iat[i, data.columns.get_loc('Target_1')] = round(close + (risk * p["rr_target_1"]), 2)
                            data.iat[i, data.columns.get_loc('Target_2')] = round(close + (risk * p["rr_target_2"]), 2)

        return data
