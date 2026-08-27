"""
SectorPulse REST API Routes.
Serves real-time quantitative sector rotation intelligence, Relative Strength regimes, and exhaustion forecasts.
"""

from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Query, HTTPException

from sectorpulse.engine import SectorPulseEngine
from sectorpulse.data_ingestion import DEFAULT_NSE_BENCHMARK, DEFAULT_NSE_SECTORS, DEFAULT_US_BENCHMARK, DEFAULT_US_SECTORS
from sectorpulse.constituents import get_sector_top_constituents

router = APIRouter(prefix="/api/sectors", tags=["SectorPulse"])

# Cached engine instances
_nse_engine = SectorPulseEngine(benchmark_ticker=DEFAULT_NSE_BENCHMARK)
_us_engine = SectorPulseEngine(benchmark_ticker=DEFAULT_US_BENCHMARK)


@router.get("/constituents")
def get_constituents_by_sector(
    sector: str = Query(..., description="Sector index ticker e.g. ^CNXIT or XLK"),
    limit: int = 6
) -> Dict[str, Any]:
    """
    Returns ranked top liquid constituents of a sector with real-time technical metrics, stage, and active setups.
    """
    try:
        s_clean = str(sector).strip()
        l_clean = int(limit) if isinstance(limit, (int, str)) and str(limit).isdigit() else 6
        ranked = get_sector_top_constituents(s_clean, limit=l_clean)
        return {
            "sector": s_clean,
            "count": len(ranked),
            "constituents": ranked
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error computing sector constituents: {str(e)}")


@router.get("/pulse")
def get_sector_pulse(
    market: str = "NSE",
    benchmark: Optional[str] = None,
    period: str = "2y"
) -> Dict[str, Any]:
    """
    Returns real-time Relative Strength, regime classifications, and regime duration forecasts for all sector indices.
    """
    try:
        # Sanitize market
        m_str = str(market).strip().upper() if isinstance(market, str) and not str(market).startswith("annotation=") else "NSE"
        if m_str not in ["NSE", "US"]:
            m_str = "NSE"

        # Sanitize period
        p_str = str(period).strip() if isinstance(period, str) and not str(period).startswith("annotation=") else "2y"

        # Sanitize benchmark
        bench_clean = None
        if isinstance(benchmark, str) and benchmark.strip() and not benchmark.startswith("annotation="):
            bench_clean = benchmark.strip()

        if m_str == "US":
            bench = bench_clean or DEFAULT_US_BENCHMARK
            engine = _us_engine if bench == DEFAULT_US_BENCHMARK else SectorPulseEngine(benchmark_ticker=bench)
            sectors = list(DEFAULT_US_SECTORS.keys())
        else:
            bench = bench_clean or DEFAULT_NSE_BENCHMARK
            engine = _nse_engine if bench == DEFAULT_NSE_BENCHMARK else SectorPulseEngine(benchmark_ticker=bench)
            sectors = list(DEFAULT_NSE_SECTORS.keys())

        results = engine.run_pulse(sector_tickers=sectors, period=p_str)
        if isinstance(results, dict) and "sectors" in results:
            return results

        # Compute market summary metrics if results is a list
        uptrend_count = sum(1 for r in results if "UPTREND" in r.get("regime", {}).get("trend_classification", ""))
        downtrend_count = sum(1 for r in results if "DOWNTREND" in r.get("regime", {}).get("trend_classification", ""))
        total_sectors = len(results)

        market_breadth_score = round((uptrend_count / total_sectors * 100.0), 1) if total_sectors > 0 else 50.0

        return {
            "market": m_str,
            "benchmark": bench,
            "total_sectors": total_sectors,
            "market_breadth_score": market_breadth_score,
            "uptrend_sectors": uptrend_count,
            "downtrend_sectors": downtrend_count,
            "sectors": results
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"SectorPulse computation error: {str(e)}")
