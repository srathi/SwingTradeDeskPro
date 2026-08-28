"""
Screener API Routes and WebSocket Live Scanner Stream.
"""

import json
import asyncio
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from pydantic import BaseModel

import numpy as np
import pandas as pd
from backend.app.core.index_manager import IndexManager
from backend.app.core.data_engine import data_engine
from backend.app.core.mtf_engine import MTFConfluenceEngine
from backend.app.core.volume_profile import compute_volume_profile
from backend.app.strategies import get_strategy, list_strategies, STRATEGY_REGISTRY

router = APIRouter(prefix="/api/screener", tags=["Screener"])


def sanitize_for_json(obj):
    if isinstance(obj, dict):
        return {k: sanitize_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [sanitize_for_json(v) for v in obj]
    elif isinstance(obj, (np.integer, np.int64, np.int32)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float64, np.float32)):
        return float(obj)
    elif isinstance(obj, (np.bool_, bool)):
        return bool(obj)
    elif isinstance(obj, np.ndarray):
        return [sanitize_for_json(v) for v in obj.tolist()]
    elif hasattr(obj, 'item'):
        return obj.item()
    return obj


class ScanRequest(BaseModel):
    universe: str = "NIFTY_50"
    strategy_id: str = "trend_pullback"
    custom_tickers: Optional[List[str]] = None
    params: Optional[Dict[str, Any]] = None


@router.get("/universes")
def get_universes():
    return IndexManager.get_universes()


@router.get("/strategies")
def get_strategies():
    return list_strategies()


@router.post("/scan")
def run_screener_sync(req: ScanRequest):
    """
    Executes a scan over the requested universe and strategy.
    """
    tickers = req.custom_tickers if req.custom_tickers else IndexManager.get_tickers(req.universe)
    strat = get_strategy(req.strategy_id)

    # Fetch batch data
    batch_df = data_engine.fetch_batch_data(tickers, period="1y", interval="1d", max_workers=10)

    matches = []
    for ticker, df in batch_df.items():
        res = strat.evaluate_setup(df, ticker, req.params)
        if res:
            # Multi-Timeframe Confluence & Volume Profile Enrichment
            try:
                mtf = MTFConfluenceEngine.evaluate_triple_screen(df, ticker)
                res["mtf_confluence"] = {
                    "score": mtf["confluence_score"],
                    "rating": mtf["rating"],
                    "badge": mtf["badge"],
                    "weekly_trend": mtf["screen_1_weekly"]["trend"]
                }
                vp = compute_volume_profile(df, num_bins=20)
                res["volume_profile"] = {
                    "poc": vp["poc"],
                    "vah": vp["vah"],
                    "val": vp["val"]
                }
            except Exception:
                pass
            clean_res = sanitize_for_json(res)
            matches.append(clean_res)

    matches.sort(key=lambda x: x.get("score", 0), reverse=True)
    return {
        "universe": req.universe,
        "strategy": strat.name,
        "scanned_count": len(tickers),
        "matches_count": len(matches),
        "results": matches
    }


@router.websocket("/ws")
async def screener_websocket(websocket: WebSocket):
    """
    WebSocket endpoint for real-time live streaming scan progress and matches.
    """
    await websocket.accept()
    try:
        data = await websocket.receive_text()
        req_json = json.loads(data)

        universe = req_json.get("universe", "NIFTY_50")
        strategy_id = req_json.get("strategy_id", "trend_pullback")
        custom_tickers = req_json.get("custom_tickers", None)
        params = req_json.get("params", None)

        tickers = custom_tickers if custom_tickers else IndexManager.get_tickers(universe)
        strat = get_strategy(strategy_id)
        total = len(tickers)

        await websocket.send_json({
            "type": "START",
            "total": total,
            "universe": universe,
            "strategy": strat.name
        })

        matches = []
        # Process in parallel chunks of 15 symbols asynchronously
        chunk_size = 15
        for i in range(0, total, chunk_size):
            chunk = tickers[i:i + chunk_size]
            batch_df = await asyncio.to_thread(
                data_engine.fetch_batch_data,
                chunk,
                period="1y",
                interval="1d",
                max_workers=10
            )

            for ticker in chunk:
                df = batch_df.get(ticker)
                if df is not None:
                    res = strat.evaluate_setup(df, ticker, params)
                    if res:
                        try:
                            mtf = MTFConfluenceEngine.evaluate_triple_screen(df, ticker)
                            res["mtf_confluence"] = {
                                "score": mtf["confluence_score"],
                                "rating": mtf["rating"],
                                "badge": mtf["badge"],
                                "weekly_trend": mtf["screen_1_weekly"]["trend"]
                            }
                            vp = compute_volume_profile(df, num_bins=20)
                            res["volume_profile"] = {
                                "poc": vp["poc"],
                                "vah": vp["vah"],
                                "val": vp["val"]
                            }
                        except Exception:
                            pass
                        clean_res = sanitize_for_json(res)
                        matches.append(clean_res)
                        await websocket.send_json({
                            "type": "MATCH",
                            "match": clean_res
                        })

            progress_pct = round(((min(i + chunk_size, total)) / total) * 100.0, 1)
            await websocket.send_json({
                "type": "PROGRESS",
                "scanned": min(i + chunk_size, total),
                "total": total,
                "progress_pct": progress_pct,
                "matches_count": len(matches)
            })
            await asyncio.sleep(0.02)

        matches.sort(key=lambda x: x.get("score", 0), reverse=True)
        await websocket.send_json({
            "type": "COMPLETE",
            "total_scanned": total,
            "matches_count": len(matches),
            "results": matches
        })

    except WebSocketDisconnect:
        pass
    except Exception as e:
        try:
            await websocket.send_json({"type": "ERROR", "message": str(e)})
        except Exception:
            pass
