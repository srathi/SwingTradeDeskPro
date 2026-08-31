"""
TTM Volatility Squeeze Breakout Strategy.
Research: John Carter (2007) / Volatility Regime Models.
Alpha Edge: Detects volatility compression where Bollinger Bands (20, 2.0) narrow inside Keltner Channels (20, 1.5 ATR).
When bands expand outward with accelerating positive MACD momentum, it signals explosive directional continuation.
"""

from typing import Dict, Any, Optional
import numpy as np
import pandas as pd

from backend.app.strategies.base import BaseStrategy
from backend.app.core.indicator_engine import compute_all_indicators


class VolatilitySqueezeStrategy(BaseStrategy):
    name: str = "TTM Volatility Squeeze Expansion"
    strategy_id: str = "volatility_squeeze"
    description: str = "Identifies explosive swing moves as Bollinger Bands expand outside Keltner Channels with accelerating MACD momentum."
    default_params: Dict[str, Any] = {
        "min_price": 50.0,
        "min_volume": 100_000,
        "min_score": 60,
        "rr_target_1": 2.0,
        "rr_target_2": 3.5,
        "atr_multiplier_sl": 1.5
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
        curr = data.iloc[-1]
        prev = data.iloc[-2] if len(data) >= 2 else curr

        close = float(curr['Close'])
        open_p = float(curr['Open'])
        high = float(curr['High'])
        low = float(curr['Low'])
        vol = float(curr['Volume'])
        vol_sma = float(curr.get('Vol_SMA20', vol))
        vol_ratio = float(curr.get('Vol_Ratio', 1.0))
        atr_val = float(curr.get('ATR_14', close * 0.02))

        # Basic liquidity filters
        if close < p["min_price"] or vol_sma < p["min_volume"]:
            return None

        # 1. Macro Trend Filter (Price >= 50 EMA and 20 EMA >= 50 EMA or Price >= 200 EMA)
        ema20 = float(curr.get('EMA_20', close))
        ema50 = float(curr.get('EMA_50', close))
        ema200 = float(curr.get('EMA_200', ema50))
        is_macro_bull = (close >= ema50 * 0.985) and (ema20 >= ema50 * 0.985 or (close >= ema200 * 0.98 if len(data) >= 150 else True))
        if not is_macro_bull:
            return None

        # 2. Check Squeeze in the last 10 sessions (BB inside KC)
        lookback = min(12, len(data))
        squeeze_active_recently = False
        for i in range(len(data) - lookback, len(data) - 1):
            row = data.iloc[i]
            if float(row['BB_Upper']) <= float(row['KC_Upper']) and float(row['BB_Lower']) >= float(row['KC_Lower']):
                squeeze_active_recently = True
                break

        if not squeeze_active_recently:
            return None

        # 3. Squeeze Firing / Expansion: Today BB Upper >= KC Upper or expanding
        bb_upper = float(curr['BB_Upper'])
        kc_upper = float(curr['KC_Upper'])
        is_expansion = (bb_upper >= kc_upper * 0.998) or (bb_upper > float(prev['BB_Upper']) and close >= ema20)
        if not is_expansion:
            return None

        # 4. Momentum Direction: MACD Histogram accelerating upward
        macd_h_curr = float(curr.get('MACD_Hist', 0))
        macd_h_prev = float(prev.get('MACD_Hist', 0))
        if macd_h_curr <= macd_h_prev:
            return None

        # 5. Bullish Candle or Lower Rejection confirmation
        if close < open_p and close < (low + (high - low) * 0.35):
            return None

        # Sizing & Risk Management
        recent_low = float(data['Low'].iloc[-lookback:].min())
        stop_loss = round(min(recent_low, close - (atr_val * p["atr_multiplier_sl"])), 2)
        risk_per_share = round(close - stop_loss, 2)
        risk_pct = round((risk_per_share / close) * 100.0, 2) if close > 0 else 0.0
        if risk_per_share <= 0 or risk_pct > 9.0:
            return None

        target_1 = round(close + (risk_per_share * p["rr_target_1"]), 2)
        target_2 = round(close + (risk_per_share * p["rr_target_2"]), 2)

        # Quality scoring
        score = 60
        if vol_ratio >= 1.2: score += 15
        if vol_ratio >= 1.6: score += 10
        if close > float(curr.get('High_20', close)) * 0.995: score += 15
        score = min(100, score)

        if score < p["min_score"]:
            return None

        return {
            "ticker": ticker,
            "strategy": self.name,
            "strategy_id": self.strategy_id,
            "score": score,
            "close": round(close, 2),
            "open": round(open_p, 2),
            "high": round(high, 2),
            "low": round(low, 2),
            "volume": int(curr.get('Volume', 0)),
            "ema_20": round(ema20, 2),
            "ema_50": round(ema50, 2),
            "ema_200": round(ema200, 2),
            "rsi": round(float(curr.get('RSI_14', 50.0)), 1),
            "atr": round(float(curr.get('ATR_14', close * 0.02)), 2),
            "vol_ratio": round(vol_ratio, 2),
            "stop_loss": stop_loss,
            "target_1": target_1,
            "target_2": target_2,
            "risk_per_share": risk_per_share,
            "risk_pct": risk_pct,
            "r_multiple_t1": p["rr_target_1"],
            "r_multiple_t2": p["rr_target_2"],
            "reward_pct_t1": round(((target_1 - close) / close) * 100.0, 2),
            "reward_pct_t2": round(((target_2 - close) / close) * 100.0, 2),
            "rr_ratio": f"1:{p['rr_target_1']}",
            "volume_ratio": round(vol_ratio, 2),
            "setup_summary": f"TTM Volatility Squeeze breakout from {lookback}-bar compression with accelerating MACD momentum.",
            "setup_date": str(curr.name)[:10] if hasattr(curr, 'name') else "",
            "indicators": {
                "rsi": round(float(curr.get('RSI_14', 50.0)), 1),
                "ema_20": round(ema20, 2),
                "ema_50": round(ema50, 2),
                "ema_200": round(ema200, 2),
                "macd_hist": round(macd_h_curr, 3),
                "atr": round(float(curr.get('ATR_14', close * 0.02)), 2),
                "vol_ratio": round(vol_ratio, 2)
            },
            "reasons": [
                f"TTM Volatility Squeeze expansion out of Keltner Channel compression",
                f"Accelerating MACD histogram momentum ({macd_h_curr:.2f} > {macd_h_prev:.2f})",
                f"Stage 2 Bullish alignment (Price > 50 EMA & 20 EMA > 50 EMA)"
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
            high = float(curr['High'])
            low = float(curr['Low'])
            ema20 = float(curr.get('EMA_20', close))
            ema50 = float(curr.get('EMA_50', close))
            ema200 = float(curr.get('EMA_200', ema50))
            atr_val = float(curr.get('ATR_14', close * 0.02))
            vol_sma = float(curr.get('Vol_SMA20', 100_000))

            if close < p["min_price"] or vol_sma < p["min_volume"]:
                continue

            # Check recent squeeze (1 to 10 bars back)
            had_squeeze = False
            for look in range(max(0, i - 10), i):
                row = data.iloc[look]
                if float(row['BB_Upper']) <= float(row['KC_Upper']) and float(row['BB_Lower']) >= float(row['KC_Lower']):
                    had_squeeze = True
                    break

            if not had_squeeze:
                continue

            # Breakout expansion + MACD Hist accelerating + macro bull
            bb_upper = float(curr['BB_Upper'])
            kc_upper = float(curr['KC_Upper'])
            is_expansion = (bb_upper >= kc_upper * 0.998) or (bb_upper > float(prev['BB_Upper']) and close >= ema20)
            is_macd_up = float(curr.get('MACD_Hist', 0)) > float(prev.get('MACD_Hist', 0))
            is_macro_bull = (close >= ema50 * 0.985) and (ema20 >= ema50 * 0.985 or (close >= ema200 * 0.98 if i >= 150 else True)) and (close >= open_p or close >= low + (high - low) * 0.35)

            if is_expansion and is_macd_up and is_macro_bull:
                look_low = float(data['Low'].iloc[max(0, i - 8):i+1].min())
                sl = round(min(look_low, close - (atr_val * p["atr_multiplier_sl"])), 2)
                risk = close - sl
                risk_pct = (risk / close) * 100.0 if close > 0 else 0.0
                if risk > 0 and risk_pct <= 9.0:
                    data.iat[i, data.columns.get_loc('Signal')] = 1
                    data.iat[i, data.columns.get_loc('Stop_Loss')] = sl
                    data.iat[i, data.columns.get_loc('Target_1')] = round(close + (risk * p["rr_target_1"]), 2)
                    data.iat[i, data.columns.get_loc('Target_2')] = round(close + (risk * p["rr_target_2"]), 2)

        return data
