"""
Connors RSI(2) Ultra-Mean Reversion Strategy.
Research: Larry Connors & Cesar Alvarez (2009) — Short Term Trading Strategies That Work.
Alpha Edge: Extreme short-term 2-day panic selling (RSI_2 < 10) in confirmed macro uptrends (Price > 200 SMA)
generates the highest empirical snapback win rate (74%–81%) across quantitative equity backtests.
"""

from typing import Dict, Any, Optional
import numpy as np
import pandas as pd

from backend.app.strategies.base import BaseStrategy
from backend.app.core.indicator_engine import compute_all_indicators


class ConnorsRSI2Strategy(BaseStrategy):
    name: str = "Connors RSI-2 Ultra-Mean Reversion"
    strategy_id: str = "connors_rsi2"
    description: str = "Exploits short-term institutional panic selloffs (RSI_2 < 10) in verified 200 SMA macro uptrends for rapid 3-7 day snapbacks."
    default_params: Dict[str, Any] = {
        "min_price": 50.0,
        "min_volume": 300_000,
        "rsi2_max": 10.0,
        "min_score": 60,
        "atr_multiplier_sl": 2.0,
        "rr_target_1": 1.5,
        "rr_target_2": 2.5
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
        curr = data.iloc[-1]
        prev1 = data.iloc[-2]
        prev2 = data.iloc[-3] if len(data) >= 3 else prev1

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

        # 1. Macro Trend Filter (Price > 200 SMA / EMA)
        sma200 = float(curr.get('SMA_200', curr.get('EMA_200', 0)))
        if close < sma200:
            return None

        # 2. Extreme 2-Period RSI Panic Filter (RSI_2 <= 10)
        rsi2_val = float(curr.get('RSI_2', 50.0))
        if rsi2_val > p["rsi2_max"]:
            return None

        # 3. Stop Loss and Target
        stop_loss = round(close - (atr_val * p["atr_multiplier_sl"]), 2)
        risk_per_share = round(close - stop_loss, 2)
        if risk_per_share <= 0:
            return None

        sma5 = float(curr.get('SMA_5', close * 1.03))
        target_1 = round(max(sma5, close + (risk_per_share * p["rr_target_1"])), 2)
        target_2 = round(close + (risk_per_share * p["rr_target_2"]), 2)
        risk_pct = round((risk_per_share / close) * 100.0, 2)

        # Quality scoring
        score = 60
        if rsi2_val <= 5.0: score += 20
        elif rsi2_val <= 10.0: score += 10
        if close > float(curr.get('EMA_50', 0)): score += 10
        if vol_ratio >= 1.2: score += 10
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
            "ema_20": round(float(curr.get('EMA_20', close)), 2),
            "ema_50": round(float(curr.get('EMA_50', close)), 2),
            "ema_200": round(float(sma200), 2),
            "rsi": round(rsi2_val, 1),
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
            "setup_summary": f"Extreme 2-day oversold panic (RSI-2 = {rsi2_val:.1f}) in confirmed >200 SMA macro uptrend.",
            "setup_date": str(curr.name)[:10] if hasattr(curr, 'name') else "",
            "indicators": {
                "rsi_2": round(rsi2_val, 1),
                "rsi": round(rsi2_val, 1),
                "ema_20": round(float(curr.get('EMA_20', close)), 2),
                "ema_50": round(float(curr.get('EMA_50', close)), 2),
                "sma_200": round(float(sma200), 2),
                "atr": round(float(curr.get('ATR_14', close * 0.02)), 2),
                "vol_ratio": round(vol_ratio, 2)
            },
            "reasons": [
                f"Extreme 2-day panic oversold dip (RSI-2: {rsi2_val:.1f} < 10)",
                f"Strict macro bull trend filter (>200 SMA)",
                f"Statistical mean reversion bounce with fast 1:{p['rr_target_1']} payout"
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

        for i in range(50, len(data)):
            curr = data.iloc[i]
            close = curr['Close']
            sma_200 = curr['SMA_200'] if not pd.isna(curr['SMA_200']) else curr['EMA_200']
            rsi2 = curr['RSI_2']
            atr_val = curr['ATR_14']
            vol_sma = curr['Vol_SMA20']

            if close < p["min_price"] or vol_sma < p["min_volume"]:
                continue

            # Long Entry: Price > SMA 200 and RSI_2 <= 10.0
            if (close > sma_200) and (rsi2 <= p["rsi2_max"]):
                sl = round(close - (atr_val * p["atr_multiplier_sl"]), 2)
                risk = close - sl
                if risk > 0:
                    data.iat[i, data.columns.get_loc('Signal')] = 1
                    data.iat[i, data.columns.get_loc('Stop_Loss')] = sl
                    data.iat[i, data.columns.get_loc('Target_1')] = round(close + (risk * p["rr_target_1"]), 2)
                    data.iat[i, data.columns.get_loc('Target_2')] = round(close + (risk * p["rr_target_2"]), 2)

        return data
