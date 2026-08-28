"""
Multi-Timeframe (MTF) Triple-Screen Confluence Engine.
Academic Foundation: Dr. Alexander Elder (Triple Screen Trading System) & Clifford Asness (AQR Capital).
Aligns Screen 1 (Weekly Tide), Screen 2 (Daily Wave), and Screen 3 (Micro Ripple) into an institutional confluence score.
"""

from typing import Dict, Any, Optional
import pandas as pd
import numpy as np
from backend.app.core.indicator_engine import compute_all_indicators, ema, rsi, macd


class MTFConfluenceEngine:
    @classmethod
    def evaluate_triple_screen(cls, df: pd.DataFrame, ticker: str = "") -> Dict[str, Any]:
        """
        Computes Alexander Elder Triple-Screen Confluence on a daily dataframe by resampling to Weekly and analyzing Daily momentum.
        """
        if df is None or len(df) < 50:
            return {
                "confluence_score": 50,
                "rating": "NEUTRAL",
                "badge": "⭐ Neutral",
                "screen_1_weekly": {"trend": "NEUTRAL", "details": "Insufficient history"},
                "screen_2_daily": {"structure": "NEUTRAL", "details": "Insufficient history"},
                "screen_3_timing": {"trigger": "WAIT", "details": "Insufficient history"}
            }

        daily_data = compute_all_indicators(df)
        d_latest = daily_data.iloc[-1]
        d_prev = daily_data.iloc[-2] if len(daily_data) >= 2 else d_latest

        d_close = float(d_latest['Close'])
        d_open = float(d_latest['Open'])
        d_ema20 = float(d_latest.get('EMA_20', d_close))
        d_ema50 = float(d_latest.get('EMA_50', d_close))
        d_ema200 = float(d_latest.get('EMA_200', d_close))
        d_rsi = float(d_latest.get('RSI_14', 50.0))
        d_vol_ratio = float(d_latest.get('Vol_Ratio', 1.0))

        # --- SCREEN 1: Weekly Macro Trend (The Tide) ---
        weekly_df = df.resample('W-FRI').agg({
            'Open': 'first',
            'High': 'max',
            'Low': 'min',
            'Close': 'last',
            'Volume': 'sum'
        }).dropna()

        w_trend = "NEUTRAL"
        w_score = 25
        w_details = "Weekly trend consolidating."
        w_close = d_close
        w_ema13 = d_close
        w_ema26 = d_close
        w_rsi = 50.0

        if len(weekly_df) >= 26:
            weekly_df['EMA_13'] = ema(weekly_df['Close'], 13)
            weekly_df['EMA_26'] = ema(weekly_df['Close'], 26)
            weekly_df['RSI_14'] = rsi(weekly_df['Close'], 14)
            w_line, w_sig, w_hist = macd(weekly_df['Close'])

            w_latest = weekly_df.iloc[-1]
            w_prev = weekly_df.iloc[-2]
            w_close = float(w_latest['Close'])
            w_ema13 = float(w_latest['EMA_13'])
            w_ema26 = float(w_latest['EMA_26'])
            w_rsi = float(w_latest['RSI_14'])
            w_h_now = float(w_hist.iloc[-1])
            w_h_prev = float(w_hist.iloc[-2])

            if w_close > w_ema13 > w_ema26 and w_h_now > w_h_prev:
                w_trend = "STRONG_BULLISH_TIDE"
                w_score = 40
                w_details = f"Weekly close (₹{round(w_close, 1)}) > 13 EMA > 26 EMA with expanding weekly MACD momentum."
            elif w_close > w_ema26:
                w_trend = "HEALTHY_WEEKLY_UPTREND"
                w_score = 30
                w_details = f"Weekly structure is bullish above 26 EMA (₹{round(w_ema26, 1)})."
            elif w_close < w_ema26 and w_h_now < w_h_prev:
                w_trend = "BEARISH_WEEKLY_TIDE"
                w_score = 0
                w_details = "Weekly trend is in active decline below 26 EMA. Counter-trend setups only."

        # --- SCREEN 2: Daily Swing Structure (The Wave) ---
        d_score = 20
        d_structure = "NEUTRAL"
        d_details = "Daily structure is neutral."

        if d_close > d_ema20 > d_ema50 > d_ema200:
            d_structure = "PERFECT_STAGE_2_UPTREND"
            d_score = 35
            d_details = "Daily EMAs stacked in full Stage 2 bull alignment (20 > 50 > 200 EMA)."
        elif d_close >= d_ema50 and d_close >= d_ema200:
            d_structure = "BULLISH_ACCUMULATION"
            d_score = 25
            d_details = "Daily price supported above 50 and 200 EMAs."
        elif d_close < d_ema200:
            d_structure = "BELOW_200_EMA"
            d_score = 5
            d_details = "Trading below 200 EMA. Macro downtrend."

        # --- SCREEN 3: Micro Execution Timing (The Ripple) ---
        t_score = 10
        t_trigger = "WAIT_FOR_TRIGGER"
        t_details = "Awaiting micro momentum volume confirmation."

        is_green = d_close >= d_open
        is_vol_expanding = d_vol_ratio >= 1.15
        is_rsi_hook = d_rsi >= float(d_prev.get('RSI_14', d_rsi))

        if is_green and is_vol_expanding and is_rsi_hook:
            t_trigger = "ACTIVE_MOMENTUM_TRIGGER"
            t_score = 25
            t_details = f"Bullish green bar with {round(d_vol_ratio, 2)}x volume expansion and upward RSI hook ({round(d_rsi, 1)})."
        elif is_green or is_rsi_hook:
            t_trigger = "PARTIAL_MOMENTUM"
            t_score = 15
            t_details = "Positive daily close, awaiting higher volume expansion."

        # Total Confluence Calculation (0 - 100)
        total_score = min(100, w_score + d_score + t_score)

        if total_score >= 85:
            rating = "TRIPLE_SCREEN_A_PLUS"
            badge = "⭐⭐⭐ Triple Screen A+"
            verdict = "Institutional Grade Confluence: Weekly Tide, Daily Wave, and Micro Timing are all strongly bullish."
        elif total_score >= 70:
            rating = "DOUBLE_SCREEN_B_PLUS"
            badge = "⭐⭐ Double Screen B+"
            verdict = "Solid Confluence: Macro Weekly and Daily setups are aligned."
        elif total_score >= 50:
            rating = "MODERATE_CONFLUENCE"
            badge = "⭐ Moderate Confluence"
            verdict = "Mixed Timeframes: Daily setup active, but Weekly macro trend is neutral/lagging."
        else:
            rating = "UNALIGNED"
            badge = "⚠️ Unaligned Timeframes"
            verdict = "Timeframes in conflict. High risk of choppy false moves."

        return {
            "confluence_score": total_score,
            "rating": rating,
            "badge": badge,
            "verdict": verdict,
            "screen_1_weekly": {
                "trend": w_trend,
                "score": w_score,
                "close": round(w_close, 2),
                "ema_13": round(w_ema13, 2),
                "ema_26": round(w_ema26, 2),
                "rsi_14": round(w_rsi, 1),
                "details": w_details
            },
            "screen_2_daily": {
                "structure": d_structure,
                "score": d_score,
                "close": round(d_close, 2),
                "ema_20": round(d_ema20, 2),
                "ema_50": round(d_ema50, 2),
                "ema_200": round(d_ema200, 2),
                "details": d_details
            },
            "screen_3_timing": {
                "trigger": t_trigger,
                "score": t_score,
                "rsi_14": round(d_rsi, 1),
                "vol_ratio": round(d_vol_ratio, 2),
                "is_green_candle": is_green,
                "details": t_details
            }
        }
