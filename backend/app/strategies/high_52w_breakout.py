"""
52-Week High Breakout Strategy (George & Hwang 2004 / Mark Minervini / William O'Neil SEPA).
Identifies leading equities emerging from tight consolidation bases to new 52-week or all-time highs
(or coiling within 3.5% of 52-week resistance) with institutional Stage-2 trend structure.
"""

from typing import Dict, Any, Optional
import numpy as np
import pandas as pd
from backend.app.strategies.base import BaseStrategy
from backend.app.core.indicator_engine import compute_all_indicators


class High52WBreakoutStrategy(BaseStrategy):
    name: str = "52-Week High Breakout"
    strategy_id: str = "high_52w_breakout"
    description: str = "Captures high-velocity Stage 2 price discovery runs as equities break to new 52-week highs (or coil within 3.5% of 52W resistance) from tight bases."
    default_params: Dict[str, Any] = {
        "min_price": 50.0,
        "min_volume": 100_000,
        "min_proximity_pct": 96.5,
        "lookback_52w_bars": 250,
        "base_tightness_pct": 18.0,
        "rr_target_1": 2.5,
        "rr_target_2": 4.0,
        "max_risk_pct": 8.5
    }

    def evaluate_setup(
        self,
        df: pd.DataFrame,
        ticker: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        p = {**self.default_params, **(params or {})}
        if df is None or len(df) < 100:
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

        # 1. Baseline & Liquidity Filter
        if close < p["min_price"]:
            return None

        # 2. Macro Uptrend Template (Minervini Stage 2: Close > 50 EMA)
        if close < ema50 * 0.98:
            return None

        # 3. 52-Week High Calculation (Past 250 bars excluding today)
        lookback = min(p["lookback_52w_bars"], len(data) - 1)
        if lookback < 40:
            return None

        prior_52w_high = float(data['High'].iloc[-lookback:-1].max())
        if prior_52w_high <= 0:
            return None

        # 4. Proximity & Breakout Check
        proximity_pct = (close / prior_52w_high) * 100.0
        if proximity_pct < p["min_proximity_pct"]:
            return None

        # 5. Base Consolidation / Tightness Check (Must not be a loose, wild swing)
        recent_20_low = float(data['Low'].iloc[-21:-1].min())
        base_depth_pct = ((prior_52w_high - recent_20_low) / prior_52w_high) * 100.0 if prior_52w_high > 0 else 99.0
        
        if base_depth_pct > p["base_tightness_pct"]:
            return None

        # 6. Volume Expansion / Accumulation Check (Recent 5 bars or today)
        recent_vol_ratios = data['Vol_Ratio'].iloc[-5:].values
        max_recent_vol = float(np.nanmax(recent_vol_ratios)) if len(recent_vol_ratios) > 0 else 1.0
        is_accumulated = max_recent_vol >= 1.15 or vol_ratio >= 1.1 or proximity_pct >= 99.0

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
        if proximity_pct >= 100.0:
            score += 15 # New all-time/52W high breakout
        elif proximity_pct >= 98.5:
            score += 10 # Within 1.5% of high
        if max_recent_vol >= 1.5:
            score += 10
        if base_depth_pct <= 10.0:
            score += 10 # Extremely tight pivot handle
        score = min(score, 100)

        is_new_high = proximity_pct >= 100.0
        status_label = "New 52W High Breakout" if is_new_high else f"Near 52W High Base ({round(proximity_pct, 1)}%)"

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
                "proximity_pct": round(proximity_pct, 1),
                "base_depth_pct": round(base_depth_pct, 1),
                "rsi": round(float(latest.get('RSI_14', 50.0)), 1),
                "atr": round(atr_val, 2),
                "vol_ratio": round(vol_ratio, 2),
                "ema_50": round(ema50, 2),
                "ema_200": round(ema200, 2)
            },
            "reasons": [
                f"{status_label} vs prior ₹{round(prior_52w_high, 1)} resistance",
                f"Consolidation base depth: {round(base_depth_pct, 1)}%",
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

        if len(data) < 100:
            return data

        lookback = p["lookback_52w_bars"]

        for i in range(50, len(data)):
            curr = data.iloc[i]
            close = curr['Close']
            open_p = curr['Open']
            vol_sma = curr['Vol_SMA20']
            atr_val = curr['ATR_14']
            ema20 = curr['EMA_20']
            ema50 = curr['EMA_50']

            if close < p["min_price"]:
                continue

            if close < ema50 * 0.98:
                continue

            start_idx = max(0, i - lookback)
            prior_high = data['High'].iloc[start_idx:i].max()
            if prior_high <= 0:
                continue

            proximity = (close / prior_high) * 100.0
            if proximity >= p["min_proximity_pct"]:
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
