"""
Institutional Pocket Pivot Strategy (Gil Morales & Chris Kacher / William O'Neil Research).
Identifies inside-the-base institutional volume accumulation where volume on an upward bounce off the 10/20/50 EMA
is higher than the maximum down-volume of the past 10 trading sessions.
Allows early positioning before traditional 52-week or VCP breakouts with asymmetric 3.0R - 5.0R payoff.
"""

from typing import Dict, Any, Optional
import numpy as np
import pandas as pd
from backend.app.strategies.base import BaseStrategy
from backend.app.core.indicator_engine import compute_all_indicators


class PocketPivotStrategy(BaseStrategy):
    name: str = "Institutional Pocket Pivot"
    strategy_id: str = "pocket_pivot"
    description: str = "Captures early inside-the-base institutional accumulation as volume exceeds the highest down-volume of the last 10 days while price pivots off the 10/20/50 EMA."
    default_params: Dict[str, Any] = {
        "min_price": 50.0,
        "min_volume": 100_000,
        "lookback_down_days": 10,
        "max_base_depth_pct": 22.0,
        "rr_target_1": 2.5,
        "rr_target_2": 4.5,
        "max_risk_pct": 7.5
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
        close = float(latest['Close'])
        open_price = float(latest['Open'])
        high = float(latest['High'])
        low = float(latest['Low'])
        atr_val = float(latest.get('ATR_14', close * 0.02))
        ema20 = float(latest.get('EMA_20', close))
        ema50 = float(latest.get('EMA_50', close * 0.95))
        ema200 = float(latest.get('EMA_200', ema50))

        # 1. Baseline & Stage 2 Filter
        if close < p["min_price"] or close < ema50 * 0.97:
            return None

        # 2. Base Constructiveness Check (Inside base within 22% of 50-day high)
        prior_high_50 = float(data['High'].iloc[-51:-1].max()) if len(data) >= 52 else float(data['High'].max())
        base_depth_pct = ((prior_high_50 - close) / prior_high_50) * 100.0 if prior_high_50 > 0 else 0.0
        
        if base_depth_pct > p["max_base_depth_pct"]:
            return None

        # 3. Check for a Pocket Pivot signature in the last 3 sessions
        n = len(data)
        found_pivot = None
        lookback = p["lookback_down_days"]

        for bar_idx in range(n - 1, max(n - 4, 15), -1):
            curr_bar = data.iloc[bar_idx]
            b_close = float(curr_bar['Close'])
            b_open = float(curr_bar['Open'])
            b_vol = float(curr_bar['Volume'])
            b_vol_ratio = float(curr_bar.get('Vol_Ratio', 1.0))
            
            # Must be an up day or green candle
            if b_close < b_open:
                continue

            # Moving average interaction on the pivot bar
            b_ema20 = float(curr_bar.get('EMA_20', b_close))
            b_ema50 = float(curr_bar.get('EMA_50', b_close))
            near_ma = b_close >= b_ema20 * 0.985 or b_close >= b_ema50 * 0.985
            if not near_ma:
                continue

            # Calculate maximum down volume in the prior 10 bars before this bar
            down_vols = []
            for j in range(max(0, bar_idx - lookback), bar_idx):
                bj = data.iloc[j]
                if float(bj['Close']) < float(bj['Open']):
                    down_vols.append(float(bj['Volume']))

            max_down_v = max(down_vols) if down_vols else float(curr_bar.get('Vol_SMA20', b_vol))
            
            # Signature: Volume exceeds max down volume OR volume ratio is >= 1.25x
            if b_vol >= max_down_v * 0.95 or b_vol_ratio >= 1.25:
                bars_ago = n - 1 - bar_idx
                vol_down_ratio = b_vol / max_down_v if max_down_v > 0 else 1.0
                found_pivot = (bars_ago, b_close, b_vol, max_down_v, vol_down_ratio, b_vol_ratio)
                break

        if not found_pivot:
            return None

        bars_ago, p_close, p_vol, max_down_vol, vol_down_ratio, p_vol_ratio = found_pivot

        # 4. Holding Pivot: Current price must not have collapsed below the pivot bar
        if close < p_close * 0.975:
            return None

        # 5. Stop Loss & Target Geometry
        swing_low_5 = float(data['Low'].iloc[-6:-1].min()) if len(data) >= 6 else low
        stop_loss = round(max(swing_low_5 - (atr_val * 0.4), ema20 * 0.975, ema50 * 0.97), 2)

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
        if vol_down_ratio >= 1.4:
            score += 15
        elif vol_down_ratio >= 1.1:
            score += 10
        if bars_ago <= 1:
            score += 10
        if base_depth_pct <= 10.0:
            score += 10
        score = min(score, 100)

        timing_label = "Active Today" if bars_ago == 0 else f"{bars_ago}d ago pivot"

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
            "setup_summary": f"Pocket Pivot volume surge ({round(vol_down_ratio, 2)}x vs 10D max down-vol) bouncing off 10/20 EMA support.",
            "setup_date": str(latest.name)[:10] if hasattr(latest, 'name') else "",
            "indicators": {
                "max_down_vol_10d": int(max_down_vol),
                "vol_down_ratio": round(vol_down_ratio, 2),
                "base_depth_pct": round(base_depth_pct, 1),
                "bars_ago": bars_ago,
                "rsi": round(float(latest.get('RSI_14', 50.0)), 1),
                "atr": round(atr_val, 2),
                "vol_ratio": round(float(latest.get('Vol_Ratio', 1.0)), 2),
                "ema_20": round(ema20, 2),
                "ema_50": round(ema50, 2)
            },
            "reasons": [
                f"Pocket Pivot volume surge ({round(vol_down_ratio, 2)}x vs 10D max down-vol - {timing_label})",
                f"Institutional accumulation off dynamic 10/20 EMA support",
                f"Inside base positioning ({round(base_depth_pct, 1)}% from 50D base high)",
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

        if len(data) < 60:
            return data

        lookback = p["lookback_down_days"]

        for i in range(25, len(data)):
            curr = data.iloc[i]
            close = curr['Close']
            open_p = curr['Open']
            vol = curr['Volume']
            atr_val = curr['ATR_14']
            ema20 = curr['EMA_20']
            ema50 = curr['EMA_50']

            if close < p["min_price"] or close < open_p or close < ema50 * 0.97:
                continue

            down_vols = []
            for j in range(max(0, i - lookback), i):
                bar_j = data.iloc[j]
                if bar_j['Close'] < bar_j['Open']:
                    down_vols.append(bar_j['Volume'])

            max_d_vol = max(down_vols) if down_vols else 1.0
            if vol >= max_d_vol * 0.95:
                swing_low_5 = data['Low'].iloc[max(0, i - 5):i + 1].min()
                sl = round(max(swing_low_5 - (atr_val * 0.4), ema20 * 0.975), 2)
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
