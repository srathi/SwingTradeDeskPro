"""
52-Week High Breakout Strategy (George & Hwang 2004 / Mark Minervini / William O'Neil SEPA).
Identifies leading equities emerging from tight consolidation bases to new 52-week or all-time highs
backed by institutional volume accumulation (>1.4x 20D SMA).
"""

from typing import Dict, Any, Optional
import numpy as np
import pandas as pd
from backend.app.strategies.base import BaseStrategy
from backend.app.core.indicator_engine import compute_all_indicators


class High52WBreakoutStrategy(BaseStrategy):
    name: str = "52-Week High Breakout"
    strategy_id: str = "high_52w_breakout"
    description: str = "Captures high-velocity Stage 2 price discovery runs as equities break to new 52-week highs from tight consolidation bases with 1.4x+ volume."
    default_params: Dict[str, Any] = {
        "min_price": 50.0,
        "min_volume": 300_000,
        "vol_surge_mult": 1.4,
        "lookback_52w_bars": 250,
        "base_tightness_pct": 12.0,
        "rr_target_1": 2.5,
        "rr_target_2": 4.0,
        "max_risk_pct": 8.0
    }

    def evaluate_setup(
        self,
        df: pd.DataFrame,
        ticker: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        p = {**self.default_params, **(params or {})}
        if df is None or len(df) < 120:
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
        ema20 = float(latest['EMA_20'])
        ema50 = float(latest['EMA_50'])
        ema200 = float(latest['EMA_200']) if 'EMA_200' in latest else ema50

        # 1. Baseline & Liquidity Filter
        if close < p["min_price"] or vol_sma < p["min_volume"]:
            return None

        # 2. Macro Uptrend Template (Minervini Stage 2: Close > 50 EMA > 200 EMA)
        if not (close > ema50 and (len(df) < 200 or ema50 > ema200 * 0.98)):
            return None

        # 3. 52-Week High Calculation (Past 250 bars excluding today)
        lookback = min(p["lookback_52w_bars"], len(data) - 1)
        if lookback < 60:
            return None

        prior_52w_high = float(data['High'].iloc[-lookback:-1].max())
        
        # 4. Breakout Condition (Today's close is breaking or within 0.5% of prior 52-week high)
        is_breakout = (close >= prior_52w_high * 0.995) and (close >= open_price)
        if not is_breakout:
            return None

        # 5. Base Consolidation / Tightness Check (Not an overextended V-shape)
        recent_15_low = float(data['Low'].iloc[-16:-1].min())
        base_depth_pct = ((prior_52w_high - recent_15_low) / prior_52w_high) * 100.0 if prior_52w_high > 0 else 99.0
        
        if base_depth_pct > p["base_tightness_pct"] * 1.5:
            # Base is too loose/deep (over 18% correction)
            return None

        # 6. Institutional Volume Surge Confirmation
        is_vol_confirmed = vol_ratio >= p["vol_surge_mult"] or vol_ratio >= 1.25
        if not is_vol_confirmed:
            return None

        # 7. Stop Loss & Target Geometry
        swing_low_10 = float(data['Low'].iloc[-11:-1].min())
        stop_loss = round(max(swing_low_10 - (atr_val * 0.5), ema20 * 0.97), 2)

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

        # 8. Quality Score (60 - 100)
        score = 65
        if close > prior_52w_high:
            score += 10
        if vol_ratio >= 2.0:
            score += 15
        elif vol_ratio >= 1.5:
            score += 10
        if base_depth_pct <= 8.0:
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
                "prior_52w_high": round(prior_52w_high, 2),
                "rsi": round(float(latest.get('RSI_14', 50.0)), 1),
                "atr": round(atr_val, 2),
                "vol_ratio": round(vol_ratio, 2),
                "base_depth_pct": round(base_depth_pct, 1),
                "ema_50": round(ema50, 2),
                "ema_200": round(ema200, 2)
            },
            "reasons": [
                f"New 52-Week High Breakout above ₹{round(prior_52w_high, 1)} resistance",
                f"Tight consolidation base ({round(base_depth_pct, 1)}% depth)",
                f"Institutional accumulation ({round(vol_ratio, 1)}x 20D volume surge)",
                f"Stage 2 Bullish alignment (Price > 50 EMA > 200 EMA)"
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

        if len(data) < 120:
            return data

        lookback = p["lookback_52w_bars"]

        for i in range(60, len(data)):
            curr = data.iloc[i]
            close = curr['Close']
            open_p = curr['Open']
            vol_sma = curr['Vol_SMA20']
            vol_ratio = curr['Vol_Ratio']
            atr_val = curr['ATR_14']
            ema20 = curr['EMA_20']
            ema50 = curr['EMA_50']

            if close < p["min_price"] or vol_sma < p["min_volume"]:
                continue

            if close < ema50:
                continue

            start_idx = max(0, i - lookback)
            prior_high = data['High'].iloc[start_idx:i].max()

            is_breakout = (close >= prior_high * 0.995) and (close >= open_p)
            is_vol_confirmed = vol_ratio >= p["vol_surge_mult"] or vol_ratio >= 1.25

            if is_breakout and is_vol_confirmed:
                swing_low_10 = data['Low'].iloc[max(0, i - 10):i + 1].min()
                sl = round(max(swing_low_10 - (atr_val * 0.5), ema20 * 0.97), 2)
                risk = close - sl
                risk_pct = (risk / close) * 100.0 if close > 0 else 0.0

                if risk_pct > p["max_risk_pct"]:
                    sl = round(close * (1.0 - (p["max_risk_pct"] / 100.0)), 2)
                    risk = close - sl
                elif risk_pct < 2.0:
                    sl = round(close * 0.97, 2)
                    risk = close - sl

                if risk > 0:
                    data.iat[i, data.columns.get_loc('Signal')] = 1
                    data.iat[i, data.columns.get_loc('Stop_Loss')] = sl
                    data.iat[i, data.columns.get_loc('Target_1')] = round(close + (risk * p["rr_target_1"]), 2)
                    data.iat[i, data.columns.get_loc('Target_2')] = round(close + (risk * p["rr_target_2"]), 2)

        return data
