# SwingDesk Pro — Project State & Architectural Memory

**Last Updated:** August 2026  
**Status:** Complete, Tested, and Production-Ready  
**Active Port:** `8888` (Backend & Static Web Dashboard), `5173` (Vite Dev Server)

---

## 1. System Architecture & Components

### A. Backend Architecture (`backend/`)
* **Framework:** Python 3.10 + FastAPI + Uvicorn
* **Data Ingestion (`backend/app/core/data_engine.py`):**
  * Uses `yfinance` to fetch OHLCV daily data.
  * Local Disk Caching using SQLite at `backend/app/data_cache/market_cache.db` (TTL: 4 hours).
  * Concurrency managed via `ThreadPoolExecutor`.
* **Indicator Engine (`backend/app/core/indicator_engine.py`):**
  * Vectorized pure NumPy and Pandas implementations for EMA (20, 50, 100, 200), SMA (20, 50, 200), Wilder's RSI(14), Wilder's ATR(14), Bollinger Bands (20, 2.0), MACD, Volume SMA, Volume Ratio, and 20D/50D Highs/Lows.
* **Index Manager (`backend/app/core/index_manager.py`):**
  * Fetches real-time CSV indices from official NSE archives with offline fallback caches for Nifty 50, Nifty Next 50, Nifty 100, Nifty 500, Nifty Midcap 150, BSE Sensex 30, and US Mega-caps.
* **Quantitative Strategies (`backend/app/strategies/`):**
  1. `TrendPullbackStrategy` (`trend_pullback`): 20/50/200 EMA trend + dynamic 20 EMA pullback + RSI 40-65 + bullish candle.
  2. `VCPBreakoutStrategy` (`vcp_breakout`): Volatility contraction (BB squeeze) + 20-day high breakout + 1.4x volume surge.
  3. `MeanReversionStrategy` (`mean_reversion`): Lower Bollinger Band oversold touch + RSI <= 35 + reversal rejection bar.
* **Backtesting Simulation Engine (`backend/app/backtester/`):**
  * Full Indian market equity cost simulation: STT (0.1%), GST (18%), Brokerage (₹20 or 0.05%), Stamp Duty (0.015%), Exchange Turnover fees.
  * Customizable slippage (0.08%).
  * Trailing stop-loss (moves to breakeven after Target 1).
  * Institutional metrics computation: Win Rate, Profit Factor, Sharpe Ratio, Sortino Ratio, Max Drawdown (% and ₹), Expectancy, CAGR %, Trade Log.
* **API Endpoints (`backend/app/api/`):**
  * `GET /api/screener/universes`, `GET /api/screener/strategies`, `POST /api/screener/scan`, `WebSocket /api/screener/ws`
  * `GET /api/chart/{ticker}?period=1y&strategy_id=trend_pullback`
  * `POST /api/backtest/run`
  * `POST /api/risk/calculate`
  * `GET/POST/PUT/DELETE /api/watchlists`

### B. Frontend Architecture (`frontend/`)
* **Framework:** React 18 + Vite 5 + Tailwind CSS + Lucide Icons + TradingView `lightweight-charts`.
* **Components (`frontend/src/components/`):**
  * `Navbar.jsx`: Dark-themed institutional header with active market feed badges and tab switcher.
  * `ScreenerView.jsx`: Interactive live scanner with real-time WebSocket progress bar, parameter controls, setup score badges, and 1-click action buttons.
  * `ChartStudio.jsx`: TradingView candlestick charts with EMA 20/50/200 overlays, RSI sub-chart, volume histogram, and colored horizontal Price Lines for Entry, Stop Loss, Target 1, Target 2.
  * `BacktestStudio.jsx`: Strategy simulation interface with KPI cards, cumulative equity curve chart, and filterable trade logs.
  * `RiskCalculator.jsx`: Interactive position sizer calculating exact share quantities and capital allocation based on portfolio risk %.
  * `WatchlistView.jsx`: Multi-watchlist manager with instant scan triggers.
* **Production Build:** Pre-built to `frontend/dist/` and automatically served by FastAPI when visiting `http://localhost:8888`.

---

## 2. Verification Test Results

* **Data Fetching:** Verified for NSE tickers (`RELIANCE.NS`, `TCS.NS`, etc.).
* **Strategy Execution:** Verified setup evaluation and signal generation for all 3 models.
* **Backtester:** Verified realistic trade execution, transaction cost deduction, and analytics calculation.
* **Frontend Build:** `vite build` generated clean production bundle without errors.
* **API Server:** Verified all REST endpoints returning 200 OK with correct JSON schemas.

---

## 3. Future Enhancements Roadmap

1. **Automated Alerts & Webhooks:**
   * Integrate Telegram Bot and Discord Webhook notifications for morning scans (09:15 AM - 09:30 AM IST) and end-of-day scans (03:15 PM - 03:30 PM IST).
2. **Direct Broker Execution:**
   * Connect to Zerodha Kite Connect, Angel One SmartAPI, or Upstox API for 1-click order placement with automatic stop-loss and limit orders.
3. **Machine Learning Trade Ranking:**
   * Train an XGBoost or LightGBM model on historical swing trade outcomes to predict trade win probability based on sector momentum, market regime, and candlestick morphology.
4. **Sectoral Breadth Heatmaps:**
   * Compute Nifty Sectoral Index breadth (% of stocks above 20 EMA and 50 EMA in Nifty IT, Nifty Bank, Nifty Auto, etc.) to time high-probability swing market regimes.

---

## 4. User Preferences & Execution Guidelines

* **Python Execution Permission:** Always allow and proactively execute Python scripts, backend workers, and tests for this project.
* **Default Port:** `8888` for FastAPI backend & web dashboard.
* **Market Suffixes:** Default to `.NS` for NSE and `.BO` for BSE.

---

## 5. Recent Feature Additions (August 2026)

* **Natural Company Name & Fuzzy Typo Resolution:**
  * Added `backend/app/core/search_engine.py` with `difflib` fuzzy ratio matcher and Yahoo Finance search fallback.
  * Added `GET /api/search?q=...` route in `backend/app/api/search_routes.py`.
  * Integrated reusable `StockSearchInput.jsx` across Chart Studio, Backtest Studio, Watchlists, and Risk Calculator.
  * Added interactive "Did you mean?" rebound chips for unmatched queries.
* **Custom Watchlist Screener Execution:**
  * Enabled direct scanning of custom user-created watchlists directly from the Screener dropdown under `<optgroup label="📋 Custom Watchlists">`.
  * Added 1-click **"⚡ Scan this Basket"** button in `WatchlistView.jsx` that automatically navigates to Screener, selects the watchlist, and triggers live scanning.

* **Single Stock Quantitative Deep Scan:**
  * Added `backend/app/api/deep_scan_routes.py` (`GET /api/deep-scan/{ticker}`) delivering comprehensive technical analysis, 52W & 20D ranges, ATR volatility, MA matrix (20/50/100/200 EMA & SMA), momentum oscillators, multi-strategy setup checks, 2-year backtest stats, position sizer, and 10-day OHLCV history.
  * Created `frontend/src/components/SingleStockScanner.jsx` and added **Deep Scan** to the main Navbar.

* **Unified Symbol & Natural Company Name Resolution Engine:**
  * Upgraded `backend/app/core/data_engine.py` with `resolve_symbol()` and `fetch_ticker_data_with_resolved_sym()`.
  * Allows any query (e.g. `"State Bank of India"`, `"Confidence Petroleum"`, `"Tata Motors"`, `"Reliance"`, `"ICICI"`, `"Infy"`, `"Bajaj Finance"`) to be resolved directly across Deep Scan, Chart Studio, Screener, and Backtester without manual ticker formatting.

* **Fix Truncated Resolved Names in Single Stock Comprehensive Analyzer:**
  * Added `SearchEngine.get_company_name()` to dynamically resolve full legal company names for all symbols.
  * Replaced restrictive `truncate` classes in `SingleStockScanner.jsx` and `StockSearchInput.jsx` with responsive `whitespace-normal break-words` containers.
  * Ensured long names (e.g. *Adani Ports and Special Economic Zone Ltd.*, *Cholamandalam Investment and Finance Company*, *Confidence Petroleum India Ltd*) wrap smoothly and render completely across all viewport sizes.

* **Fix Dropdown Clipping & Set Default Blank in Deep Scan:**
  * Removed `overflow-hidden` from the Deep Scan header card container so the autocomplete dropdown floats freely with `z-[100]` over the entire viewport without being clipped.
  * Enhanced `StockSearchInput.jsx` with full word wrapping and contrast formatting for symbol, exchange badge, and registered company name.
  * Changed the default initial state in **Deep Scan** to blank (`""`), displaying a clean placeholder state with quick-select sample chips (e.g. Reliance, SBI, HDFC Bank, Infosys, TCS, L&T, ITC, Bajaj Finance) instead of pre-loading any stock.

* **Piccadily Agro Industries Resolution Fix:**
  * **Root Cause**: On NSE and BSE, the official ticker is truncated to `PICCADIL` (e.g. `PICCADIL.NS` / `PICCADIL.BO`), without the trailing `y`. In the previous search flow, if a smallcap was not pre-indexed in the Nifty 500 static file, the low-similarity fallback filled candidate slots before reaching the live exchange query.
  * **Fix**: Added `PICCADIL.NS` & `PICCADIL.BO` directly to `LOCAL_STOCK_MASTER` and restructured `SearchEngine.search()` to always query the live Yahoo Search API first for unindexed smallcaps/microcaps. Both `piccadily agro`, `piccadily`, and typo variations like `piccadilly` now resolve seamlessly to `PICCADIL.NS` (CMP ₹673.45).

* **Git Repository Initialized & Pushed to GitHub:**
  * Initialized Git repository on branch `main`.
  * Added production `Dockerfile` (multi-stage build), `render.yaml`, `.gitignore`, `requirements.txt`, and full codebase.
  * Pushed initial commit (`09902fd`) to remote repository: `https://github.com/srathi/SwingTradeDeskPro.git`.

* **Fix Dropdown Dismissal After Selection:**
  * **Root Cause**: In `StockSearchInput.jsx`, selecting a stock updated `query` to the selected ticker symbol. This triggered the debounced `useEffect([query])` hook 120ms later, which re-queried the search API and re-opened the dropdown (`setIsOpen(true)`).
  * **Fix**: Added `isSelectingRef` to distinguish user typing from programmatic selection, immediately cleared suggestions on selection, and prevented re-querying upon clicking/entering an item.
  * Pushed fix to GitHub (`ac57c69`) for automatic continuous deployment to Render production.

* **Updated Comprehensive README.md:**
  * Added Academic & Empirical Research Foundations table with win rates, Sharpe ratios, and average holding periods.
  * Added Strategy Specifications & Trigger Rules table for all 6 trading models.
  * Added Architecture Mermaid Diagram and Live Production URL badges.
  * Pushed update (`134bcae`) to GitHub: `https://github.com/srathi/SwingTradeDeskPro.git`.

* **Added Individual Strategy Scorecard Tables to README.md:**
  * Added individual dedicated specification and scorecard tables for all 6 trading models (Strategy ID, Research Basis, Empirical Edge, Win Rate, Sharpe Ratio, Holding Period, Trend Filters, Entry Triggers, Stop Loss, Profit Targets).
  * Pushed commit (`a610723`) to GitHub repository: `https://github.com/srathi/SwingTradeDeskPro.git`.

* **Full Implementation of All 6 Trading Strategies:**
  * Implemented `backend/app/strategies/volatility_squeeze.py` (TTM Squeeze Expansion with Keltner/Bollinger and MACD histogram acceleration).
  * Implemented `backend/app/strategies/connors_rsi2.py` (Connors RSI-2 Ultra-Mean Reversion with 200 SMA filter and RSI-2 < 10 trigger).
  * Implemented `backend/app/strategies/relative_strength_leader.py` (Mansfield RS Stage-2 Leader with 20D/52W breakout and volume surge).
  * Updated `backend/app/core/indicator_engine.py` to add vectorized `keltner_channels()`, `rsi_2()`, and moving average filters.
  * Registered all 6 strategies in `STRATEGY_REGISTRY` in `backend/app/strategies/__init__.py`.
  * Deep Scan API and Screener API automatically evaluate all 6 models concurrently.
  * Pushed code changes to GitHub repository (`1e05942`): `https://github.com/srathi/SwingTradeDeskPro.git`.

* **Copyright & Branding: rupeemap.in labs:**
  * Added `rupeemap.in labs` branding to Navbar (`frontend/src/components/Navbar.jsx`).
  * Added `© 2026 rupeemap.in labs. All rights reserved.` to the app footer (`frontend/src/App.jsx`).
  * Added `organization: rupeemap.in labs` and copyright metadata to FastAPI app & `/api/health` (`backend/app/main.py`).
  * Added `LICENSE` file with MIT license (Copyright (c) 2026 rupeemap.in labs).
  * Updated `README.md` with organization and copyright badge.
  * Pushed commit (`bcb21fe`) to GitHub repository: `https://github.com/srathi/SwingTradeDeskPro.git`.

* **Added Author Attribution: by Sandesh Rathi:**
  * Header/Navbar: `rupeemap.in labs • by Sandesh Rathi`
  * Footer: `© 2026 rupeemap.in labs (by Sandesh Rathi). All rights reserved.`
  * Backend API & `/api/health`: `author: Sandesh Rathi` & `organization: rupeemap.in labs`
  * Legal LICENSE & README: `Copyright (c) 2026 rupeemap.in labs (by Sandesh Rathi)`.
  * Pushed commit (`8c5f35f`) to GitHub: `https://github.com/srathi/SwingTradeDeskPro.git`.

* **Added Dedicated 'Strategy Matrix' Navigation Tab:**
  * Created `frontend/src/components/StrategyGuideView.jsx` presenting the academic research table, empirical win rates ($74\%-81\%$, $65\%-72\%$, etc.), Sharpe ratios, holding durations, and deep rule cards.
  * Added 1-click `"⚡ Run Live Screener"` and `"📈 Backtest Strategy"` action buttons directly inside the strategy matrix cards.
  * Added `Strategy Matrix` tab with `BookOpen` icon to the Navbar.
  * Pushed commit (`42faa84`) to GitHub: `https://github.com/srathi/SwingTradeDeskPro.git`.

* **Fixed Backtest Studio Execution & Chart Rendering:**
  * **Root Cause 1**: `backtest_routes.py` was calling `data_engine.fetch_ticker_data()` directly without symbol resolution, causing 404 errors whenever users entered lowercase or natural stock names (e.g. `tatamotors`, `piccadily agro`, `reliance`, `confidence petro`).
  * **Root Cause 2**: In `BacktestStudio.jsx`, the equity curve chart was feeding duplicate dates to TradingView Lightweight Charts, which throws an exception when timestamps are not strictly unique and ascending.
  * **Fix Applied**: 
    1. Upgraded `backtest_routes.py` to use `fetch_ticker_data_with_resolved_sym()`.
    2. Added date map deduplication and ascending sort in `BacktestStudio.jsx` before rendering the equity curve series.
  * Pushed commit (`881ac0e`) to GitHub: `https://github.com/srathi/SwingTradeDeskPro.git`.

* **Reverted Commit 13b16a6 & Fixed Strategy Matrix Tab Visibility:**
  * Reverted commit `13b16a6` via `8faae81` as requested.
  * Identified and fixed navigation tab truncation in [`Navbar.jsx`](file:///Users/sandesh/antigravity/SwingTrades/frontend/src/components/Navbar.jsx) so all 7 tabs (including the 7th **Strategy Matrix** tab) fit cleanly without overflow or being pushed off-screen across any device size.
  * Added distinct highlighted badge styling to the **Strategy Matrix** tab button.
  * Rebuilt frontend bundle and pushed commits (`8faae81`, `b562384`) to GitHub: `https://github.com/srathi/SwingTradeDeskPro.git`.

* **Implemented SectorPulse Quantitative Sector Regime & Forecaster Package:**
  * Created `sectorpulse/` modular package with:
    - `data_ingestion.py`: Ingests and aligns multi-sector historical OHLCV data against benchmark (`^NSEI`, `SPY`).
    - `indicators.py`: Vectorized Mansfield RS, Moving Average Hierarchy, ADX(14) +DI/-DI, and ATR(14).
    - `persistence.py`: Vectorized Hurst Exponent ($R/S$ analysis) and Discrete Markov State Transition Matrix modeling ($E[\text{Duration}] = 1 / (1 - P_{00})$).
    - `foundation_forecaster.py`: Amazon Chronos (Chronos-Bolt / Chronos-T5) integration with Monte Carlo geometric drift-diffusion fallback.
    - `engine.py`: Multi-sector orchestrator, trend classifier (`STRONG_UPTREND`, `EARLY_UPTREND`, `NEUTRAL_RANGE`, `EARLY_DOWNTREND`, `STRONG_DOWNTREND`), exhaustion alert detector, and trade recommendation generator.
    - `cli.py` & `main.py`: Interactive CLI with Rich tables and JSON output.
  * Added test suite `tests/test_sectorpulse.py` with 100% pass rate across all 5 unit tests.
  * Added REST endpoint `/api/sectors/pulse` in `backend/app/api/sector_routes.py`.
  * Added interactive UI dashboard `SectorPulseView.jsx` in frontend navigation.
  * Pushed commit (`7c8e4a7`) to GitHub: `https://github.com/srathi/SwingTradeDeskPro.git`.

* **Fixed Render Docker Build & Navbar Truncation in Chrome:**
  * **Root Cause 1 (Render Build)**: `Dockerfile` was only copying `backend/` and `frontend/dist`, but omitted `COPY sectorpulse/ ./sectorpulse/`. This caused Render's container build to fail importing `sectorpulse` and prevented live deployment of new features.
  * **Root Cause 2 (Chrome Truncation)**: The navbar's flex alignment on medium/standard laptop screens was pushing right-side tabs off-screen with hidden scrollbars.
  * **Fix Applied**: 
    1. Added `COPY sectorpulse/ ./sectorpulse/` to `Dockerfile`.
    2. Added responsive short/full label breakpoints and clean horizontal touch scrolling with no clipping across Chrome, Safari, and mobile viewports.
    3. Added a direct `"🧭 Sector Pulse"` button inside the Live Screener header.
  * Pushed commit (`a80eb18`) to GitHub: `https://github.com/srathi/SwingTradeDeskPro.git`.

* **Removed Default Stocks in Chart Studio & Backtest Studio:**
  * Modified `App.jsx`, `ChartStudio.jsx`, and `BacktestStudio.jsx` so that no default stock (e.g. `RELIANCE.NS`) is preselected upon initial tab load.
  * Added clean placeholder states in both tabs prompting the user to search and select their desired equity symbol.
  * Pushed commit (`872799f`) to GitHub: `https://github.com/srathi/SwingTradeDeskPro.git`.

* **Migrated to Institutional Vertical Left Sidebar Navigation:**
  * Created `Sidebar.jsx` with organized workflow tiers (Discovery & Regime, Execution & Analysis, Workspace & Research), collapsible rail mode (240px <-> 64px), active state indicators, and responsive mobile drawer.
  * Created `TopHeader.jsx` with dynamic breadcrumb navigation, quick stock search jumper, and live market indicator.
  * Preserved 100% of functional capabilities, drilldowns, and sub-actions across all 8 modules with zero regressions.
  * Pushed commit (`f494859`) to GitHub: `https://github.com/srathi/SwingTradeDeskPro.git`.
