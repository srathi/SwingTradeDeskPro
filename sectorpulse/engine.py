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

        # 4. Regime Classification
        # STRONG_UPTREND: MRS > 0, MA Hierarchy == 3 (Close > 20 > 50 > 200), ADX > 20
        # EARLY_UPTREND: MRS > 0 or MRS Slope > 0, MA Hierarchy >= 2
        # NEUTRAL_RANGE: -2.0 <= MRS <= 2.0 and ADX < 20
        # EARLY_DOWNTREND: MRS < 0, MA Hierarchy <= 1
        # STRONG_DOWNTREND: MRS < -2.0, Close < 50 EMA < 200 EMA
        if mrs_score > 1.5 and ma_hierarchy == 3 and adx_14 >= 20.0:
            classification = "STRONG_UPTREND"
        elif (mrs_score > 0.0 or mrs_slope_5d > 0.5) and ma_hierarchy >= 2:
            classification = "EARLY_UPTREND"
        elif mrs_score < -2.5 and ma_hierarchy == 0:
            classification = "STRONG_DOWNTREND"
        elif mrs_score < 0.0 or ma_hierarchy <= 1:
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
            action = "ACCUMULATE_BREAKOUT"
            multiplier = 1.15
        elif classification == "NEUTRAL_RANGE":
            action = "SELECTIVE_RANGE_TRADE"
            multiplier = 0.75
        elif classification == "EARLY_DOWNTREND":
            action = "REDUCE_EXPOSURE"
            multiplier = 0.50
        else:  # STRONG_DOWNTREND
            action = "AVOID_DOWNTREND"
            multiplier = 0.0

        # Construct strictly typed JSON response schema
        now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        return {
            "timestamp": now_iso,
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
                "current_regime_age_days": markov_stats["current_regime_age_days"],
                "expected_total_duration_days": markov_stats["expected_total_duration_days"],
                "estimated_remaining_days": markov_stats["estimated_remaining_days"],
                "chronos_median_peak_horizon_days": fc_result.median_peak_horizon_days,
                "exhaustion_probability": fc_result.exhaustion_probability
            },
            "risk_parameters": {
                "atr_14": atr_14,
                "trailing_stop_level": trailing_stop,
                "overextension_flag": is_overextended
            },
            "trade_recommendation": {
                "action": action,
                "sector_weight_multiplier": round(float(multiplier), 2)
            },
            "metadata": {
                "close": round(close, 2),
                "ema_20": round(ema_20, 2),
                "ema_50": round(ema_50, 2),
                "ema_200": round(ema_200, 2),
                "forecaster_model": fc_result.model_name
            }
        }

    def run_pulse(
        self,
        sector_tickers: Optional[List[str]] = None,
        period: str = "2y"
    ) -> List[Dict[str, Any]]:
        """
        Executes pipeline across all sectors in the universe.
        """
        bench_df, sector_dfs = self.ingestion.ingest_sector_universe(
            benchmark_ticker=self.benchmark_ticker,
            sector_tickers=sector_tickers,
            period=period
        )

        results = []
        for sec, df in sector_dfs.items():
            try:
                res = self.analyze_sector(sec, df, bench_df)
                results.append(res)
            except Exception as e:
                continue

        # Sort by Mansfield Relative Strength (descending)
        results.sort(key=lambda x: x["regime"]["mrs_score"], reverse=True)
        return results
