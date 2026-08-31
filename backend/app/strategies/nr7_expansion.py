"""
Toby Crabel NR7 Volatility Expansion Strategy.
Identifies extreme cyclical range compression where the daily high-low range is the narrowest of the last 7 sessions (NR7),
preceding explosive directional volatility expansion in established Stage 2 trends.
"""

from typing import Dict, Any, Optional
import numpy as np
import pandas as pd
from backend.app.strategies.base import BaseStrategy
from backend.app.core.indicator_engine import compute_all_indicators


class NR7ExpansionStrategy(BaseStrategy):
    name: str = "Toby Crabel NR7 Expansion"
    strategy_id: str = "nr7_expansion"
    description: str = "Captures explosive directional expansion out of extreme 7-day narrow range compression (NR7) coils in macro Stage 2 uptrends."
    default_params: Dict[str, Any] = {
        "min_price": 50.0,
        "min_volume": 100_000,
        "lookback_nr": 7,
        "max_range_atr_mult": 0.85,
        "rr_target_1": 2.0,
        "rr_target_2": 3.0,
        "max_risk_pct": 7.5
    }

    def evaluate_setup(
        self,
        df: pd.DataFrame,
        ticker: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        p = {**self.default_params, **(params or {})}
        if df is None or len(df) < 30:
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
        ema20 = float(latest.get('EMA_20', close))
        ema50 = float(latest.get('EMA_50', close * 0.95))
        ema200 = float(latest.get('EMA_200', ema50))

        # 1. Baseline & Stage 2 Filter
        if close < p["min_price"] or close < ema50 * 0.97:
            return None

        # 2. Daily Ranges calculation
        ranges = (data['High'] - data['Low']).values
        if len(ranges) < p["lookback_nr"] + 2:
            return None

        # Check if today or yesterday was an NR7 bar
        recent_7_ranges = ranges[-p["lookback_nr"]-1:-1]
        min_prior_range = float(np.min(recent_7_ranges))
        
        today_range = ranges[-1]
        prev_range = ranges[-2]

        is_nr7_today = today_range <= min_prior_range * 1.02
        is_nr7_yesterday = prev_range <= float(np.min(ranges[-p["lookback_nr"]-2:-2])) * 1.02

        if not (is_nr7_today or is_nr7_yesterday):
            return None

        # 3. Compression vs ATR (Range must be unusually tight)
        active_range = today_range if is_nr7_today else prev_range
        if active_range > atr_val * p["max_range_atr_mult"]:
            return None

        # 4. Bullish Alignment
        is_bullish = (close >= open_price) or (close >= ema20)
        if not is_bullish:
            return None

        # 5. Stop Loss & Target Geometry
        compression_low = min(low, float(prev['Low']))
        stop_loss = round(compression_low - (atr_val * 0.35), 2)
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
        reward_pct_t1 = round(((target_1 - close) / close) * 100.0, 2) if close > 0 else 0.0
        reward_pct_t2 = round(((target_2 - close) / close) * 100.0, 2) if close > 0 else 0.0

        # 6. Quality Score (60 - 100)
        score = 65
        compression_ratio = active_range / atr_val if atr_val > 0 else 1.0
        if compression_ratio <= 0.40:
            score += 15 # Extreme compression (< 40% ATR)
        elif compression_ratio <= 0.60:
            score += 10
        if close > float(prev['High']):
            score += 10 # Active breakout of NR7 bar
        if close > ema20:
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
            "ema_20": round(float(ema20), 2),
            "rsi": round(float(latest.get('RSI_14', 50.0)), 1),
            "stop_loss": stop_loss,
            "target_1": target_1,
            "target_2": target_2,
            "risk_per_share": risk,
            "risk_pct": round((risk / close) * 100.0, 2),
            "reward_pct_t1": reward_pct_t1,
            "reward_pct_t2": reward_pct_t2,
            "r_multiple_t1": p["rr_target_1"],
            "r_multiple_t2": p["rr_target_2"],
            "setup_summary": f"Toby Crabel NR7 narrow range compression ({round(float(compression_ratio) * 100, 0)}% ATR) in Stage 2 trend.",
            "setup_date": str(latest.name)[:10] if hasattr(latest, 'name') else "",
            "indicators": {
                "nr7_range": round(float(active_range), 2),
                "compression_ratio": round(float(compression_ratio), 2),
                "atr": round(float(atr_val), 2),
                "vol_ratio": round(float(vol_ratio), 2),
                "ema_20": round(float(ema20), 2),
                "ema_50": round(float(ema50), 2),
                "ema_200": round(float(ema200), 2)
            },
            "reasons": [
                f"Toby Crabel NR7 range compression ({round(float(compression_ratio) * 100, 0)}% of ATR)",
                f"Tightest volatility coil of the last 7 sessions",
                f"Stage 2 Bullish alignment (Price > 50 EMA)",
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

        if len(data) < 30:
            return data

        ranges = (data['High'] - data['Low']).values
        lookback = p["lookback_nr"]

        for i in range(lookback + 2, len(data)):
            curr = data.iloc[i]
            close = curr['Close']
            open_p = curr['Open']
            low = curr['Low']
            atr_val = curr['ATR_14']
            ema50 = curr['EMA_50']

            if close < p["min_price"] or close < ema50 * 0.97:
                continue

            r_today = ranges[i]
            min_r = np.min(ranges[i - lookback:i])

            if r_today <= min_r * 1.02 and r_today <= atr_val * p["max_range_atr_mult"]:
                if close >= open_p:
                    sl = round(low - (atr_val * 0.35), 2)
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
