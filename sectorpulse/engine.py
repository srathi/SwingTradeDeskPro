"""
SectorPulse Engine Orchestrator.
Executes multi-sector ingestion, indicator calculations, econometric persistence modeling,
foundation forecasting, and generates strict JSON contract reports.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
import numpy as np
import pandas as pd

from sectorpulse.data_ingestion import SectorDataIngestion, DEFAULT_NSE_BENCHMARK, DEFAULT_NSE_SECTORS
from sectorpulse.indicators import compute_sector_indicators
from sectorpulse.persistence import calculate_hurst_exponent, compute_markov_regime_duration
from sectorpulse.foundation_forecaster import ChronosForecaster
from sectorpulse.constituents import get_sector_top_constituents


class SectorPulseEngine:
    """
    Principal orchestrator for SectorPulse quantitative sector rotation intelligence.
    """

    def __init__(
        self,
        benchmark_ticker: str = DEFAULT_NSE_BENCHMARK,
        chronos_model: str = "amazon/chronos-bolt-small"
    ):
        self.benchmark_ticker = benchmark_ticker
        self.ingestion = SectorDataIngestion()
        self.forecaster = ChronosForecaster(model_name=chronos_model)

    def analyze_sector(
        self,
        sector_ticker: str,
        sector_df: pd.DataFrame,
        benchmark_df: pd.DataFrame,
        sector_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Runs comprehensive analysis on a single sector time-series relative to the benchmark.
        Conforms strictly to the institutional JSON contract.
        """
        # 1. Compute vectorized indicators
        df = compute_sector_indicators(sector_df, benchmark_df, mrs_lookback=50)
        latest = df.iloc[-1]

        close = float(latest["Close"])
        ema_20 = float(latest["EMA_20"])
        ema_50 = float(latest["EMA_50"])
        ema_200 = float(latest["EMA_200"])
        mrs_score = round(float(latest["MRS"]), 2)
        mrs_slope_5d = round(float(latest["MRS_Slope_5d"]), 2)
        adx_14 = round(float(latest["ADX_14"]), 1)
        atr_14 = round(float(latest["ATR_14"]), 2)
        ma_hierarchy = int(latest["MA_Hierarchy_Score"])

        # 2. Persistence & Econometric Modeling
        hurst_exponent = round(calculate_hurst_exponent(df["Close"]), 2)
        markov_stats = compute_markov_regime_duration(df["MRS"], df["MA_Hierarchy_Score"])

        # 3. Foundation / Monte Carlo Probabilistic Forecasting
        fc_result = self.forecaster.forecast_relative_strength(df["MRS"])

        # 4. Institutional Trend & Relative Strength Regime Classification
        # STRONG_UPTREND: Close > EMA50 > EMA200 (Hier >= 2), MRS > 0, ADX >= 18
        # EARLY_UPTREND: Close > EMA50 and (MRS >= -0.5 or MRS Slope > 0)
        # STRONG_DOWNTREND: Close < EMA50 < EMA200 (Hier == 0) and MRS < -1.5
        # EARLY_DOWNTREND: Close < EMA50 and MRS < 0
        # NEUTRAL_RANGE: Consolidation / transition range
        if close > ema_50 > ema_200 and mrs_score > 0.0 and adx_14 >= 18.0:
            classification = "STRONG_UPTREND"
        elif close > ema_50 and (mrs_score >= -0.5 or mrs_slope_5d > 0.0):
            classification = "EARLY_UPTREND"
        elif close < ema_50 < ema_200 and mrs_score < -1.5:
            classification = "STRONG_DOWNTREND"
        elif close < ema_50 and mrs_score < 0.0:
            classification = "EARLY_DOWNTREND"
        else:
            classification = "NEUTRAL_RANGE"

        # 5. Overextension & Risk Parameters
        # Overextension: Price > 3.0 * ATR(14) above 50 EMA
        overextension_threshold = ema_50 + (3.0 * atr_14)
        is_overextended = bool(close > overextension_threshold)
        
        # Trailing stop: 2.0 ATR below EMA 20
        trailing_stop = round(max(0.0, ema_20 - (2.0 * atr_14)), 2)

        # 6. Trade Recommendation & Sector Allocation Multiplier
        if classification == "STRONG_UPTREND":
            if is_overextended:
                action = "HOLD_TRAILING_STOP"
                multiplier = 1.10
            elif fc_result.exhaustion_probability > 0.70:
                action = "REDUCE_OVEREXTENDED"
                multiplier = 0.80
            else:
                action = "BUY_ON_PULLBACK"
                multiplier = 1.25
        elif classification == "EARLY_UPTREND":
            if is_overextended:
                action = "ACCUMULATE_BREAKOUT"
                multiplier = 1.15
            else:
                action = "ACCUMULATE_BREAKOUT"
                multiplier = 1.15
        elif classification == "NEUTRAL_RANGE":
            action = "NEUTRAL_HOLD"
            multiplier = 1.0
        elif classification == "EARLY_DOWNTREND":
            action = "REDUCE_EXPOSURE"
            multiplier = 0.5
        else:  # STRONG_DOWNTREND
            action = "AVOID_UNDERWEIGHT"
            multiplier = 0.0

        # Strict JSON contract assembly
        report = {
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "sector": sector_ticker,
            "name": sector_name or DEFAULT_NSE_SECTORS.get(sector_ticker, sector_ticker),
            "regime": {
                "trend_classification": classification,
                "mrs_score": mrs_score,
                "mrs_slope_5d": mrs_slope_5d,
                "adx_14": adx_14,
                "hurst_exponent": hurst_exponent
            },
            "duration_forecast": {
                "current_regime_age_days": markov_stats.get("current_regime_age_days", 1) if isinstance(markov_stats, dict) else markov_stats.current_regime_age_days,
                "expected_total_duration_days": markov_stats.get("expected_total_duration_days", 20) if isinstance(markov_stats, dict) else markov_stats.expected_total_duration_days,
                "estimated_remaining_days": markov_stats.get("estimated_remaining_days", 19) if isinstance(markov_stats, dict) else markov_stats.estimated_remaining_days,
                "chronos_median_peak_horizon_days": getattr(fc_result, "median_peak_horizon_days", 10),
                "exhaustion_probability": getattr(fc_result, "exhaustion_probability", 0.15)
            },
            "risk_parameters": {
                "atr_14": atr_14,
                "trailing_stop_level": trailing_stop,
                "overextension_flag": is_overextended
            },
            "trade_recommendation": {
                "action": action,
                "sector_weight_multiplier": multiplier
            },
            "metadata": {
                "close": round(close, 2),
                "ema_20": round(ema_20, 2),
                "ema_50": round(ema_50, 2),
                "ema_200": round(ema_200, 2),
                "forecaster_model": getattr(fc_result, "model_name", "Vectorized_MonteCarlo_OU")
            },
            "top_constituents": get_sector_top_constituents(sector_ticker, limit=5)
        }
        return report

    def run_multi_sector_pipeline(
        self,
        sector_tickers: Optional[List[str]] = None,
        period: str = "2y"
    ) -> Dict[str, Any]:
        """
        Executes full pipeline across all requested sector indices against benchmark.
        """
        benchmark_df, sector_dfs = self.ingestion.ingest_sector_universe(
            benchmark_ticker=self.benchmark_ticker,
            sector_tickers=sector_tickers,
            period=period
        )

        results = []
        for sec_ticker, sec_df in sector_dfs.items():
            try:
                name = DEFAULT_NSE_SECTORS.get(sec_ticker, sec_ticker)
                rep = self.analyze_sector(
                    sector_ticker=sec_ticker,
                    sector_df=sec_df,
                    benchmark_df=benchmark_df,
                    sector_name=name
                )
                results.append(rep)
            except Exception as e:
                continue

        # Sort by MRS score descending (relative leaders at the top)
        results.sort(key=lambda x: x["regime"]["mrs_score"], reverse=True)

        uptrend_count = sum(1 for r in results if "UPTREND" in r["regime"]["trend_classification"])
        downtrend_count = sum(1 for r in results if "DOWNTREND" in r["regime"]["trend_classification"])
        total = len(results)
        breadth_score = round((uptrend_count / total * 100.0), 1) if total > 0 else 0.0

        return {
            "market": "NSE" if "^NSE" in self.benchmark_ticker else "US",
            "benchmark": self.benchmark_ticker,
            "total_sectors": total,
            "market_breadth_score": breadth_score,
            "uptrend_sectors": uptrend_count,
            "downtrend_sectors": downtrend_count,
            "sectors": results
        }

    # Alias for CLI and API consumers
    run_pulse = run_multi_sector_pipeline
