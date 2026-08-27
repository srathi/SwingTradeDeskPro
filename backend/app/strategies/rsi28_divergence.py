"""
RSI(28) Multi-Week Momentum Divergence Strategy.
Captures high-probability intermediate swing reversals by identifying structural bullish divergences
between price lower-lows and smoothed 28-period Wilder RSI higher-lows.
"""

from typing import Dict, Any, Optional, List, Tuple
import numpy as np
import pandas as pd
from backend.app.strategies.base import BaseStrategy
from backend.app.core.indicator_engine import compute_all_indicators


def find_swing_lows(lows: np.ndarray, rsi_vals: np.ndarray, k: int = 4) -> List[Tuple[int, float, float]]:
    """
    Identifies local swing lows using a k-bar local minimum window.
    Returns a list of tuples: (index, price_low, rsi_at_low).
    """
    n = len(lows)
    pivots = []
    for i in range(k, n - k):
        is_pivot = True
        val = lows[i]
        for j in range(i - k, i + k + 1):
            if j != i and lows[j] <= val:
                is_pivot = False
                break
        if is_pivot and not np.isnan(rsi_vals[i]):
            pivots.append((i, float(val), float(rsi_vals[i])))
    return pivots


class RSI28DivergenceStrategy(BaseStrategy):
    name: str = "RSI(28) Momentum Divergence"
    strategy_id: str = "rsi28_divergence"
    description: str = "Captures high-probability intermediate swing reversals by identifying structural bullish divergences between price lower-lows and 28-period RSI higher-lows."
    default_params: Dict[str, Any] = {
        "min_price": 50.0,
        "min_volume": 300_000,
        "min_pivot_distance": 7,
        "max_pivot_distance": 45,
        "min_rsi_diff": 2.5,
        "max_rsi28": 52.0,
        "rr_target_1": 2.0,
        "rr_target_2": 3.5,
        "max_risk_pct": 8.5
    }

    def evaluate_setup(
        self,
        df: pd.DataFrame,
        ticker: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        p = {**self.default_params, **(params or {})}
        if df is None or len(df) < 80:
            return None

        data = compute_all_indicators(df)
        latest = data.iloc[-1]
        prev = data.iloc[-2] if len(data) >= 2 else latest

        close = float(latest['Close'])
        open_price = float(latest['Open'])
        high = float(latest['High'])
        low = float(latest['Low'])
        vol_sma = float(latest['Vol_SMA20'])
        vol_ratio = float(latest['Vol_Ratio'])
        atr_val = float(latest['ATR_14'])
        rsi28_curr = float(latest.get('RSI_28', 50.0))
        rsi14_curr = float(latest.get('RSI_14', 50.0))
        ema50 = float(latest['EMA_50'])
        ema200 = float(latest['EMA_200']) if 'EMA_200' in latest else ema50

        # 1. Liquidity & Baseline Filter
        if close < p["min_price"] or vol_sma < p["min_volume"]:
            return None

        # 2. RSI Regime (Must be in oversold or value accumulation zone, not overbought)
        if rsi28_curr > p["max_rsi28"]:
            return None

        # 3. Swing Low & Divergence Detection
        lows = data['Low'].values
        rsi_series = data['RSI_28'].values
        pivots = find_swing_lows(lows, rsi_series, k=4)

        if len(pivots) < 2:
            return None

        # Check latest two pivots
        idx2, p_low2, rsi2 = pivots[-1]
        idx1, p_low1, rsi1 = pivots[-2]

        bars_ago = len(data) - 1 - idx2
        # Latest swing low must be recent (within past 8 bars)
        if bars_ago > 8:
            return None

        distance = idx2 - idx1
        if not (p["min_pivot_distance"] <= distance <= p["max_pivot_distance"]):
            return None

        # Bullish Divergence Rule:
        # Price makes a lower low (or equal low), but RSI(28) forms a distinct higher low
        price_lower_low = p_low2 <= p_low1 * 1.005
        rsi_higher_low = rsi2 >= rsi1 + p["min_rsi_diff"]

        if not (price_lower_low and rsi_higher_low):
            return None

        # 4. Reversal Confirmation Trigger
        # Today must be a bullish bounce candle confirming the pivot
        is_bullish_candle = close >= open_price
        is_bounce_confirmed = close >= p_low2 * 1.01

        if not (is_bullish_candle and is_bounce_confirmed):
            return None

        # 5. Stop Loss & Target Geometry
        stop_loss = round(p_low2 - (atr_val * 0.5), 2)
        risk = round(close - stop_loss, 2)
        risk_pct = (risk / close) * 100.0 if close > 0 else 0.0

        if risk_pct > p["max_risk_pct"]:
            stop_loss = round(close * (1.0 - (p["max_risk_pct"] / 100.0)), 2)
            risk = round(close - stop_loss, 2)
        elif risk_pct < 2.0:
            stop_loss = round(close * 0.97, 2)
            risk = round(close - stop_loss, 2)

        if risk <= 0:
            return None

        target_1 = round(close + (risk * p["rr_target_1"]), 2)
        target_2 = round(close + (risk * p["rr_target_2"]), 2)

        # 6. Quality Score (60 - 100)
        score = 65
        rsi_delta = rsi2 - rsi1
        if rsi_delta >= 5.0:
            score += 15
        elif rsi_delta >= 3.5:
            score += 10
        if vol_ratio >= 1.3:
            score += 10
        if rsi28_curr <= 40.0:
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
                "rsi_28": round(rsi28_curr, 1),
                "rsi_14": round(rsi14_curr, 1),
                "atr": round(atr_val, 2),
                "vol_ratio": round(vol_ratio, 2),
                "pivot1_price": round(p_low1, 2),
                "pivot2_price": round(p_low2, 2),
                "pivot1_rsi": round(rsi1, 1),
                "pivot2_rsi": round(rsi2, 1),
                "ema_50": round(ema50, 2),
                "ema_200": round(ema200, 2)
            },
            "reasons": [
                f"Multi-week RSI(28) Bullish Divergence (+{round(rsi_delta, 1)} RSI pts higher low)",
                f"Selling momentum exhaustion (Price ₹{round(p_low2, 1)} vs ₹{round(p_low1, 1)})",
                f"Bullish reversal bounce candle confirming pivot low",
                f"Asymmetric risk-to-reward ({p['rr_target_1']}R / {p['rr_target_2']}R targets)"
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

        if len(data) < 80:
            return data

        lows = data['Low'].values
        rsi_series = data['RSI_28'].values
        pivots = find_swing_lows(lows, rsi_series, k=4)

        if len(pivots) < 2:
            return data

        pivot_map = {idx: (p_low, rsi_val) for idx, p_low, rsi_val in pivots}
        pivot_indices = [p[0] for p in pivots]

        for p_idx_pos in range(1, len(pivot_indices)):
            idx2 = pivot_indices[p_idx_pos]
            idx1 = pivot_indices[p_idx_pos - 1]
            p_low2, rsi2 = pivot_map[idx2]
            p_low1, rsi1 = pivot_map[idx1]

            distance = idx2 - idx1
            if not (p["min_pivot_distance"] <= distance <= p["max_pivot_distance"]):
                continue

            price_lower_low = p_low2 <= p_low1 * 1.005
            rsi_higher_low = rsi2 >= rsi1 + p["min_rsi_diff"]

            if price_lower_low and rsi_higher_low and rsi2 <= p["max_rsi28"]:
                # Trigger on bounce bar right after pivot confirmation
                trigger_idx = min(idx2 + 2, len(data) - 1)
                curr = data.iloc[trigger_idx]
                close = curr['Close']
                open_p = curr['Open']
                atr_val = curr['ATR_14']
                vol_sma = curr['Vol_SMA20']

                if close < p["min_price"] or vol_sma < p["min_volume"]:
                    continue

                if close >= open_p:
                    sl = round(p_low2 - (atr_val * 0.5), 2)
                    risk = close - sl
                    risk_pct = (risk / close) * 100.0 if close > 0 else 0.0

                    if risk_pct > p["max_risk_pct"]:
                        sl = round(close * (1.0 - (p["max_risk_pct"] / 100.0)), 2)
                        risk = close - sl
                    elif risk_pct < 2.0:
                        sl = round(close * 0.97, 2)
                        risk = close - sl

                    if risk > 0:
                        data.iat[trigger_idx, data.columns.get_loc('Signal')] = 1
                        data.iat[trigger_idx, data.columns.get_loc('Stop_Loss')] = sl
                        data.iat[trigger_idx, data.columns.get_loc('Target_1')] = round(close + (risk * p["rr_target_1"]), 2)
                        data.iat[trigger_idx, data.columns.get_loc('Target_2')] = round(close + (risk * p["rr_target_2"]), 2)

        return data
