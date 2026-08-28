"""
Alpha Fusion Ensemble Engine.
Blends 12 Quantitative Rule-Based Setups with Kronos AI Foundation Monte Carlo Forecasts, Volume Profile, and Market Regime.
"""

from typing import Dict, Any, Optional
import math
import numpy as np
import pandas as pd
from backend.app.core.data_engine import data_engine
from backend.app.core.indicator_engine import compute_all_indicators
from backend.app.core.volume_profile import compute_volume_profile, compute_institutional_avwaps
from backend.app.core.mtf_engine import MTFConfluenceEngine
from backend.app.core.regime_engine import MarketRegimeEngine
from backend.app.ai_engine.kronos_engine import kronos_engine
from backend.app.strategies import STRATEGY_REGISTRY


class AlphaFusionEngine:
    @classmethod
    def evaluate_alpha_fusion(
        cls,
        ticker: str,
        period: str = "1y",
        strategy_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Computes unified Composite Alpha Score, Statistical Expectancy (EV/R), and AI-Quant Confluence.
        """
        df = data_engine.fetch_ticker_data(ticker, period=period, interval="1d")
        if df is None or len(df) < 50:
            return {"error": f"Insufficient price history for {ticker}"}

        df = df[~df.index.duplicated(keep='first')].sort_index()
        cmp = float(df['Close'].iloc[-1])

        # 1. Best Quantitative Strategy Evaluation
        best_strat_name = "Quantitative Baseline"
        best_strat_score = 65
        active_setup = None

        if strategy_id and strategy_id in STRATEGY_REGISTRY:
            strat = STRATEGY_REGISTRY[strategy_id]
            res = strat.evaluate_setup(df, ticker)
            if res:
                best_strat_name = res.get("strategy", strategy_id)
                best_strat_score = res.get("score", 75)
                active_setup = res
        else:
            # Search across all 12 strategies for highest score
            for s_id, strat in STRATEGY_REGISTRY.items():
                res = strat.evaluate_setup(df, ticker)
                if res and res.get("score", 0) > best_strat_score:
                    best_strat_score = res.get("score", 75)
                    best_strat_name = res.get("strategy", s_id)
                    active_setup = res

        # 2. Kronos AI Foundation Forecast
        try:
            ai_forecast = kronos_engine.forecast(df, ticker=ticker, pred_len=15, n_paths=20)
            raw_upside = ai_forecast.get("upside_prob", 0.55)
            p_upside = raw_upside / 100.0 if raw_upside > 1.0 else raw_upside
            ai_expected_return_pct = ai_forecast.get("expected_chg_pct", 2.0)
            ai_target = ai_forecast.get("expected_close", cmp * 1.03)
        except Exception:
            p_upside = 0.55
            ai_expected_return_pct = 2.0
            ai_target = cmp * 1.03

        # 3. Multi-Timeframe Confluence
        mtf = MTFConfluenceEngine.evaluate_triple_screen(df, ticker)
        mtf_score = mtf.get("confluence_score", 50)

        # 4. Volume Profile Quality
        vp = compute_volume_profile(df, num_bins=35)
        poc = vp.get("poc", cmp)
        vah = vp.get("vah", cmp)
        val = vp.get("val", cmp)

        vp_score = 60
        if cmp >= poc:
            vp_score += 20  # Trading above institutional POC
        if cmp >= vah:
            vp_score += 20  # Blue sky breakout above Value Area
        elif cmp < val:
            vp_score -= 20  # Trapped below Value Area Low
        vp_score = max(20, min(100, vp_score))

        # 5. Macro Market Regime Multiplier
        market = "US" if not ticker.endswith(('.NS', '.BO')) else "NSE"
        regime = MarketRegimeEngine.get_current_regime(market)
        regime_code = regime.get("verdict", {}).get("code", "SELECTIVE_PULLBACKS")

        regime_multiplier = 1.0
        if regime_code == "RISK_ON_EXPANSION":
            regime_multiplier = 1.05
        elif regime_code == "SELECTIVE_PULLBACKS":
            regime_multiplier = 0.90
        elif regime_code == "HIGH_CHOP_MEAN_REVERSION":
            regime_multiplier = 0.75
        else:
            regime_multiplier = 0.60

        # --- COMPOSITE ALPHA SCORE (0 - 100) ---
        raw_alpha = (
            (0.30 * best_strat_score) +
            (0.25 * (p_upside * 100.0)) +
            (0.25 * mtf_score) +
            (0.20 * vp_score)
        ) * regime_multiplier

        composite_alpha = round(max(10.0, min(99.0, raw_alpha)), 1)

        # Statistical Expectancy EV/R
        win_rate = (p_upside * 0.6) + ((best_strat_score / 100.0) * 0.4)
        reward_risk = 2.0
        ev_r = round((win_rate * reward_risk) - ((1.0 - win_rate) * 1.0), 2)

        if composite_alpha >= 85:
            badge = "👑 Elite Institutional Alpha"
            color = "emerald"
            recommendation = "High conviction institutional setup. Neural and multi-timeframe quantitative confluence aligned."
        elif composite_alpha >= 72:
            badge = "🔥 High Conviction Alpha"
            color = "cyan"
            recommendation = "Strong swing trade candidate. Favorable reward-to-risk with positive expected value."
        elif composite_alpha >= 55:
            badge = "⚡ Moderate Tactical Alpha"
            color = "amber"
            recommendation = "Standard setup. Maintain strict stop-loss discipline and standard position sizing."
        else:
            badge = "⚠️ Low Alpha / Gated"
            color = "rose"
            recommendation = "Conflicting signals or unfavorable macro regime. Reduced statistical edge."

        return {
            "ticker": ticker,
            "cmp": round(cmp, 2),
            "composite_alpha_score": composite_alpha,
            "badge": badge,
            "color": color,
            "recommendation": recommendation,
            "statistical_expectancy_ev_r": ev_r,
            "components": {
                "strategy": {
                    "name": best_strat_name,
                    "score": best_strat_score,
                    "weight_pct": 30
                },
                "kronos_ai": {
                    "prob_upside_pct": round(p_upside * 100.0, 1),
                    "expected_return_pct": round(ai_expected_return_pct, 2),
                    "target_price": round(ai_target, 2),
                    "weight_pct": 25
                },
                "mtf_confluence": {
                    "score": mtf_score,
                    "badge": mtf.get("badge", "⭐ Neutral"),
                    "weight_pct": 25
                },
                "volume_profile": {
                    "score": vp_score,
                    "poc": poc,
                    "vah": vah,
                    "val": val,
                    "weight_pct": 20
                },
                "market_regime": {
                    "code": regime_code,
                    "title": regime.get("verdict", {}).get("title", "Market Regime"),
                    "multiplier": regime_multiplier
                }
            },
            "active_setup": active_setup
        }
