"""
SectorPulse — Quantitative Sector Trend, Relative Strength & Regime Duration Forecaster.
Developed by rupeemap.in labs (by Sandesh Rathi).
"""

__version__ = "1.0.0"
__author__ = "Sandesh Rathi"
__organization__ = "rupeemap.in labs"

from sectorpulse.data_ingestion import SectorDataIngestion
from sectorpulse.indicators import compute_sector_indicators, calculate_mansfield_rs
from sectorpulse.persistence import calculate_hurst_exponent, compute_markov_regime_duration
from sectorpulse.foundation_forecaster import ChronosForecaster, ForecastResult
from sectorpulse.engine import SectorPulseEngine

__all__ = [
    "SectorDataIngestion",
    "compute_sector_indicators",
    "calculate_mansfield_rs",
    "calculate_hurst_exponent",
    "compute_markov_regime_duration",
    "ChronosForecaster",
    "ForecastResult",
    "SectorPulseEngine",
]
