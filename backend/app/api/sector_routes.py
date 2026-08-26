"""
SectorPulse REST API Routes.
Serves real-time quantitative sector rotation intelligence, Relative Strength regimes, and exhaustion forecasts.
"""

from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Query, HTTPException

from sectorpulse.engine import SectorPulseEngine
from sectorpulse.data_ingestion import DEFAULT_NSE_BENCHMARK, DEFAULT_NSE_SECTORS, DEFAULT_US_BENCHMARK, DEFAULT_US_SECTORS

router = APIRouter(prefix="/api/sectors", tags=["SectorPulse"])

# Cached engine instances
_nse_engine = SectorPulseEngine(benchmark_ticker=DEFAULT_NSE_BENCHMARK)
_us_engine = SectorPulseEngine(benchmark_ticker=DEFAULT_US_BENCHMARK)


@router.get("/pulse")
def get_sector_pulse(
    market: str = Query("NSE", description="Market universe: NSE or US"),
    benchmark: Optional[str] = Query(None, description="Custom benchmark ticker"),
    period: str = Query("2y", description="Historical lookback period")
) -> Dict[str, Any]:
    """
    Returns real-time Relative Strength, regime classifications, and regime duration forecasts for all sector indices.
    """
    try:
        if market.upper() == "US":
            bench = benchmark or DEFAULT_US_BENCHMARK
            engine = _us_engine if bench == DEFAULT_US_BENCHMARK else SectorPulseEngine(benchmark_ticker=bench)
            sectors = list(DEFAULT_US_SECTORS.keys())
        else:
            bench = benchmark or DEFAULT_NSE_BENCHMARK
            engine = _nse_engine if bench == DEFAULT_NSE_BENCHMARK else SectorPulseEngine(benchmark_ticker=bench)
            sectors = list(DEFAULT_NSE_SECTORS.keys())

        results = engine.run_pulse(sector_tickers=sectors, period=period)

        # Compute market summary metrics
        uptrend_count = sum(1 for r in results if "UPTREND" in r["regime"]["trend_classification"])
        downtrend_count = sum(1 for r in results if "DOWNTREND" in r["regime"]["trend_classification"])
        total_sectors = len(results)

        market_breadth_score = round((uptrend_count / total_sectors * 100.0), 1) if total_sectors > 0 else 50.0

        return {
            "market": market.upper(),
            "benchmark": bench,
            "total_sectors": total_sectors,
            "market_breadth_score": market_breadth_score,
            "uptrend_sectors": uptrend_count,
            "downtrend_sectors": downtrend_count,
            "sectors": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SectorPulse computation error: {str(e)}")
