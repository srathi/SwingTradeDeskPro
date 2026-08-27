"""
Guppy Multiple Moving Average (GMMA) Weekly Breakout Strategy.
Combines Weekly institutional investor ribbon (30-60 EMA) expansion with daily volume-backed breakouts.
Captures high-probability multi-week Stage 2 markup runners with asymmetric 2.5R - 4.0R payoff targets.
"""

from typing import Dict, Any, Optional
import numpy as np
import pandas as pd
from backend.app.strategies.base import BaseStrategy
from backend.app.core.indicator_engine import compute_all_indicators, gmma_ribbons, resample_weekly


class GMMABreakoutStrategy(BaseStrategy):
    name: str = "GMMA Weekly Breakout"
    strategy_id: str = "gmma_breakout"
    description: str = "Captures explosive multi-week Stage 2 trend expansions by entering daily breakouts aligned with weekly Guppy institutional ribbon divergence."
    default_params: Dict[str, Any] = {
        "min_price": 50.0,
        "min_volume": 300_000,
        "vol_surge_mult": 1.3,
        "min_weekly_spread_pct": 1.8,
        "rr_target_1": 2.5,
        "rr_target_2": 4.0,
        "max_risk_pct": 9.0
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

        # 1. Daily indicators
        daily_data = compute_all_indicators(df)
        latest_daily = daily_data.iloc[-1]
        prev_daily = daily_data.iloc[-2] if len(daily_data) >= 2 else latest_daily

        close = float(latest_daily['Close'])
        open_price = float(latest_daily['Open'])
        high = float(latest_daily['High'])
        low = float(latest_daily['Low'])
        vol_sma = float(latest_daily['Vol_SMA20'])
        vol_ratio = float(latest_daily['Vol_Ratio'])
        atr_val = float(latest_daily['ATR_14'])
        ema50_d = float(latest_daily['EMA_50'])
        ema200_d = float(latest_daily['EMA_200']) if 'EMA_200' in latest_daily else ema50_d

        # 2. Liquidity & Baseline Filter
        if close < p["min_price"] or vol_sma < p["min_volume"]:
            return None

        # Daily price must be in Stage 2 structure (Close > 50 EMA)
        if close < ema50_d:
            return None

        # 3. Weekly GMMA Computation
        weekly_df = resample_weekly(df)
        if weekly_df is None or len(weekly_df) < 30:
            weekly_close = df['Close']
        else:
            weekly_close = weekly_df['Close']

        fast_ribbon, slow_ribbon = gmma_ribbons(weekly_close)
        
        # Get latest weekly values
        fast_vals = [float(s.iloc[-1]) for s in fast_ribbon.values() if len(s) > 0 and not np.isnan(s.iloc[-1])]
        slow_vals = [float(s.iloc[-1]) for s in slow_ribbon.values() if len(s) > 0 and not np.isnan(s.iloc[-1])]

        if not fast_vals or not slow_vals:
            return None

        min_fast = min(fast_vals)
        max_slow = max(slow_vals)
        slow_30 = float(slow_ribbon['EMA_30'].iloc[-1])
        slow_60 = float(slow_ribbon['EMA_60'].iloc[-1])

        # 4. Weekly GMMA Alignment & Expansion Rules
        is_ribbon_bullish = min_fast >= max_slow * 0.99
        is_slow_expanding = slow_30 > slow_60
        slow_spread_pct = ((slow_30 - slow_60) / slow_60) * 100.0 if slow_60 > 0 else 0.0

        if not (is_ribbon_bullish and is_slow_expanding and slow_spread_pct >= p["min_weekly_spread_pct"]):
            return None

        # 5. Daily Breakout & Momentum Trigger
        prev_20d_high = float(daily_data['High'].iloc[-21:-1].max()) if len(daily_data) >= 22 else float(daily_data['High'].max())
        is_daily_breakout = (close >= prev_20d_high * 0.995) and (close >= open_price)
        is_vol_confirmed = vol_ratio >= p["vol_surge_mult"] or vol_ratio >= 1.25

        if not (is_daily_breakout and is_vol_confirmed):
            return None

        # 6. Stop Loss & Target Geometry
        slow_support = max_slow
        swing_low_10 = float(daily_data['Low'].iloc[-10:].min())
        stop_loss = round(max(swing_low_10 - (atr_val * 0.5), slow_support * 0.98), 2)

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
        if slow_spread_pct >= 3.0:
            score += 10
        if vol_ratio >= 1.8:
            score += 15
        elif vol_ratio >= 1.4:
            score += 10
        if close > prev_20d_high:
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
            "volume": int(latest_daily['Volume']),
            "stop_loss": stop_loss,
            "target_1": target_1,
            "target_2": target_2,
            "risk_per_share": risk,
            "risk_pct": round((risk / close) * 100.0, 2),
            "r_multiple_t1": p["rr_target_1"],
            "r_multiple_t2": p["rr_target_2"],
            "setup_date": str(latest_daily.name)[:10] if hasattr(latest_daily, 'name') else "",
            "indicators": {
                "rsi": round(float(latest_daily.get('RSI_14', 50.0)), 1),
                "atr": round(atr_val, 2),
                "vol_ratio": round(vol_ratio, 2),
                "weekly_slow_spread_pct": round(slow_spread_pct, 2),
                "ema_50": round(ema50_d, 2),
                "ema_200": round(ema200_d, 2)
            },
            "reasons": [
                f"Weekly GMMA slow investor ribbon expanding (+{round(slow_spread_pct, 1)}% spread)",
                f"Fast trader ribbon aligned above slow investor ribbon",
                f"Daily breakout with {round(vol_ratio, 1)}x volume surge",
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

        if len(data) < 120:
            return data

        # Precompute GMMA ribbons on daily/weekly approximation for rolling backtest speed
        fast_ribbon, slow_ribbon = gmma_ribbons(data['Close'])
        slow_30 = slow_ribbon['EMA_30']
        slow_60 = slow_ribbon['EMA_60']
        fast_15 = fast_ribbon['EMA_15']

        for i in range(60, len(data)):
            curr = data.iloc[i]
            close = curr['Close']
            open_p = curr['Open']
            vol_sma = curr['Vol_SMA20']
            vol_ratio = curr['Vol_Ratio']
            atr_val = curr['ATR_14']
            ema50 = curr['EMA_50']

            if close < p["min_price"] or vol_sma < p["min_volume"]:
                continue

            if close < ema50:
                continue

            # Ribbon expansion check
            s30 = slow_30.iat[i]
            s60 = slow_60.iat[i]
            f15 = fast_15.iat[i]

            if np.isnan(s30) or np.isnan(s60) or np.isnan(f15):
                continue

            is_ribbon_bullish = f15 >= s30 * 0.99
            is_slow_expanding = s30 > s60
            spread_pct = ((s30 - s60) / s60) * 100.0 if s60 > 0 else 0.0

            if not (is_ribbon_bullish and is_slow_expanding and spread_pct >= p["min_weekly_spread_pct"]):
                continue

            # Breakout check
            prev_20_high = data['High'].iloc[max(0, i - 20):i].max() if i >= 20 else close
            is_breakout = close >= prev_20_high * 0.995 and close >= open_p
            is_vol_confirmed = vol_ratio >= p["vol_surge_mult"] or vol_ratio >= 1.25

            if is_breakout and is_vol_confirmed:
                swing_low_10 = data['Low'].iloc[max(0, i - 10):i + 1].min()
                sl = round(max(swing_low_10 - (atr_val * 0.5), s30 * 0.98), 2)
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
