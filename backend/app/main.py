"""
FastAPI Main Application Entrypoint for Institutional Swing Trading Platform.
Developed by rupeemap.in labs (by Sandesh Rathi).
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from backend.app.api.screener_routes import router as screener_router
from backend.app.api.chart_routes import router as chart_router
from backend.app.api.backtest_routes import router as backtest_router
from backend.app.api.risk_routes import router as risk_router
from backend.app.api.watchlist_routes import router as watchlist_router
from backend.app.api.search_routes import router as search_router
from backend.app.api.deep_scan_routes import router as deep_scan_router
from backend.app.api.sector_routes import router as sector_router

app = FastAPI(
    title="SwingDesk Pro — rupeemap.in labs (by Sandesh Rathi)",
    description="Quantitative Screener, TradingView Charting Engine, SectorPulse Rotation Matrix, and Backtest Studio for NSE/BSE and Global Equities. Developed by Sandesh Rathi at rupeemap.in labs.",
    version="1.0.0",
    contact={
        "name": "Sandesh Rathi (rupeemap.in labs)",
        "url": "https://rupeemap.in"
    }
)

# Enable CORS for local dev and frontend ports
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(screener_router)
app.include_router(chart_router)
app.include_router(backtest_router)
app.include_router(risk_router)
app.include_router(watchlist_router)
app.include_router(search_router)
app.include_router(deep_scan_router)
app.include_router(sector_router)


@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": "SwingDesk Pro Quantitative Engine",
        "author": "Sandesh Rathi",
        "organization": "rupeemap.in labs",
        "copyright": "© 2026 rupeemap.in labs (by Sandesh Rathi). All rights reserved.",
        "market_supported": ["NSE", "BSE", "US"],
        "modules": [
            "screener",
            "chart_studio",
            "backtest_studio",
            "risk_calculator",
            "sector_pulse",
            "strategy_matrix"
        ],
        "strategies": [
            "trend_pullback",
            "vcp_breakout",
            "mean_reversion",
            "volatility_squeeze",
            "connors_rsi2",
            "relative_strength_leader"
        ]
    }


# Mount production React build if dist directory exists
frontend_dist = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "frontend", "dist")

if os.path.exists(frontend_dist):
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dist, "assets")), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        file_path = os.path.join(frontend_dist, full_path)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(frontend_dist, "index.html"))
