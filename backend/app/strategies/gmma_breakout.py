"""
Guppy Multiple Moving Average (GMMA) Breakout & Trend Expansion Strategy.
Identifies high-probability Stage 2 trend expansions by entering equities where the fast trader ribbon (3-15 EMA)
is actively expanding above the fanning slow investor ribbon (30-60 EMA) with breakout/trend momentum.
"""

from typing import Dict, Any, Optional
import numpy as np
import pandas as pd
from backend.app.strategies.base import BaseStrategy
from backend.app.core.indicator_engine import compute_all_indicators, gmma_ribbons


class GMMABreakoutStrategy(BaseStrategy):
    name: str = "GMMA Weekly Breakout"
    strategy_id: str = "gmma_breakout"
    description: str = "Captures high-velocity Stage 2 trend expansions where the fast trader ribbon (3-15 EMA) fans outward above an expanding slow investor ribbon (30-60 EMA)."
    default_params: Dict[str, Any] = {
        "min_price": 50.0,
        "min_volume": 100_000,
        "min_slow_spread_pct": 1.5,
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
        if df is None or len(df) < 80:
            return None

        # 1. Compute indicators
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

        # 2. Baseline Filter
        if close < p["min_price"]:
            return None

        # Price must be in Stage 2 structure (Close > 50 EMA)
        if close < ema50 * 0.98:
            return None

        # 3. GMMA Ribbons Evaluation
        fast_ribbon, slow_ribbon = gmma_ribbons(data['Close'])
        f_vals = [float(s.iloc[-1]) for s in fast_ribbon.values() if len(s) > 0 and not np.isnan(s.iloc[-1])]
        s_vals = [float(s.iloc[-1]) for s in slow_ribbon.values() if len(s) > 0 and not np.isnan(s.iloc[-1])]

        if not f_vals or not s_vals:
            return None

        min_fast = min(f_vals)
        max_slow = max(s_vals)
        slow_30 = float(slow_ribbon['EMA_30'].iloc[-1])
        slow_60 = float(slow_ribbon['EMA_60'].iloc[-1])

        # 4. Ribbon Alignment & Expansion Rules
        # Fast ribbon is aligned above or touching the slow ribbon
        is_ribbon_bullish = min_fast >= max_slow * 0.985
        
        # Slow investor ribbon is expanding upward (30 EMA > 60 EMA)
        is_slow_expanding = slow_30 > slow_60
        slow_spread_pct = ((slow_30 - slow_60) / slow_60) * 100.0 if slow_60 > 0 else 0.0

        if not (is_ribbon_bullish and is_slow_expanding and slow_spread_pct >= p["min_slow_spread_pct"]):
            return None

        # 5. Breakout or Trend Continuation Condition
        prev_20_high = float(data['High'].iloc[-21:-1].max()) if len(data) >= 22 else close
        is_trend_leader = (close >= prev_20_high * 0.97) and (close >= open_price * 0.99)

        if not is_trend_leader:
            return None

        # 6. Stop Loss & Target Geometry
        swing_low_10 = float(data['Low'].iloc[-11:-1].min())
        stop_loss = round(max(swing_low_10 - (atr_val * 0.5), max_slow * 0.98, ema20 * 0.97), 2)

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

        # 7. Setup Score (60 - 100)
        score = 65
        if slow_spread_pct >= 4.0:
            score += 15
        elif slow_spread_pct >= 2.5:
            score += 10
        if close >= prev_20_high * 0.995:
            score += 10 # Active 20D breakout
        if vol_ratio >= 1.3:
            score += 10
        score = min(score, 100)

        is_breaking = close >= prev_20_high * 0.995
        status_label = "GMMA Ribbon Expansion Breakout" if is_breaking else f"GMMA Trend Runner (+{round(slow_spread_pct, 1)}% Spread)"

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
            "r_multiple_t1": p["rr_target_1"],
            "r_multiple_t2": p["rr_target_2"],
            "setup_summary": f"{status_label} with expanding Guppy investor ribbons (+{round(slow_spread_pct, 1)}% spread).",
            "setup_date": str(latest.name)[:10] if hasattr(latest, 'name') else "",
            "indicators": {
                "slow_spread_pct": round(slow_spread_pct, 1),
                "fast_min_ema": round(min_fast, 2),
                "slow_max_ema": round(max_slow, 2),
                "rsi": round(float(latest.get('RSI_14', 50.0)), 1),
                "atr": round(atr_val, 2),
                "vol_ratio": round(vol_ratio, 2),
                "ema_50": round(ema50, 2),
                "ema_200": round(ema200, 2)
            },
            "reasons": [
                f"{status_label} (Slow Ribbon Spread: +{round(slow_spread_pct, 1)}%)",
                f"Fast Trader Ribbon (3-15 EMA) aligned above Slow Investor Ribbon",
                f"Stage 2 Bullish momentum (Price > 50 EMA)",
                f"Asymmetric risk profile ({p['rr_target_1']}R / {p['rr_target_2']}R targets)"
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

        fast_ribbon, slow_ribbon = gmma_ribbons(data['Close'])
        slow_30 = slow_ribbon['EMA_30']
        slow_60 = slow_ribbon['EMA_60']
        fast_15 = fast_ribbon['EMA_15']

        for i in range(50, len(data)):
            curr = data.iloc[i]
            close = curr['Close']
            open_p = curr['Open']
            atr_val = curr['ATR_14']
            ema20 = curr['EMA_20']
            ema50 = curr['EMA_50']

            if close < p["min_price"]:
                continue

            if close < ema50 * 0.98:
                continue

            s30 = slow_30.iat[i]
            s60 = slow_60.iat[i]
            f15 = fast_15.iat[i]

            if np.isnan(s30) or np.isnan(s60) or np.isnan(f15):
                continue

            is_ribbon_bullish = f15 >= s30 * 0.985
            is_slow_expanding = s30 > s60
            spread_pct = ((s30 - s60) / s60) * 100.0 if s60 > 0 else 0.0

            if not (is_ribbon_bullish and is_slow_expanding and spread_pct >= p["min_slow_spread_pct"]):
                continue

            prev_20_high = data['High'].iloc[max(0, i - 20):i].max() if i >= 20 else close
            is_breakout = close >= prev_20_high * 0.97

            if is_breakout:
                swing_low_10 = data['Low'].iloc[max(0, i - 10):i + 1].min()
                sl = round(max(swing_low_10 - (atr_val * 0.5), s30 * 0.98, ema20 * 0.97), 2)
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
