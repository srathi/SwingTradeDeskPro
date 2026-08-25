# SwingDesk Pro — Institutional Swing Trading Platform

An institutional-grade quantitative swing trading suite designed for Indian equities (NSE & BSE) and global markets. Features automated multi-strategy screening, realistic backtesting with Indian tax/slippage models, interactive TradingView charts, and exact risk-managed position sizing.

---

## ⚡ Quick Start (Single Command)

```bash
# 1. Clone or navigate to the repository
cd SwingTrades

# 2. Launch the entire application (Backend + Frontend)
./run.sh
```

Once running:
* **Web Dashboard**: [http://localhost:8888](http://localhost:8888)
* **Interactive API Docs (Swagger UI)**: [http://localhost:8888/docs](http://localhost:8888/docs)

---

## 🎯 Implemented Quantitative Strategies

| Strategy | Setup Mechanics | Target R:R | Historical Win Rate | Best Market Condition |
| :--- | :--- | :---: | :---: | :--- |
| **1. Trend-Pullback (20/50 EMA)** | Enters when price retraces to the rising 20 EMA in a macro uptrend ($\text{Price} > 200\text{ EMA}$) with a bullish reversal candlestick and $40 \le \text{RSI} \le 65$. | $1:2 - 1:3$ | **$48\% - 56\%$** | Bullish & Trending |
| **2. VCP & Base Breakout** | Detects volatility contraction (ATR / Bollinger Band squeeze) followed by a 20-day high breakout backed by $1.4\times+$ volume expansion. | $1:2.5 - 1:3.5$ | **$38\% - 46\%$** | Early Stage Bull Moves |
| **3. Mean Reversion** | Captures oversold bounces when price touches the Lower Bollinger Band with $\text{RSI} \le 35$ and a bullish rejection candle. | $1:1.5 - 1:2$ | **$60\% - 68\%$** | Sideways / Volatile Ranges |

---

## 🏗️ Architecture & Key Features

### 1. Data Ingestion & Caching Engine
* **Yahoo Finance API Integration**: Free, automatic ingestion for NSE (`.NS`), BSE (`.BO`), and US equities.
* **Intelligent SQLite Disk Cache**: Stores 1-year OHLCV candles locally with configurable TTL (4 hours) for instant, sub-second rescans without rate limits.
* **Official Exchange Universe Scraper**: Ingests Nifty 50, Nifty Next 50, Nifty 100, Nifty 500, Nifty Midcap 150, BSE Sensex 30, and US Top Equities.

### 2. Live Quantitative Screener
* Multi-threaded parallel scanner with WebSocket real-time progress bar.
* Quality Scoring algorithm ($0\text{--}100$) evaluating volume expansion, candlestick structure, and momentum.
* Direct action buttons: 1-click **Chart Studio**, 1-click **Risk Calculator**, and 1-click **Backtest**.
* Export results to CSV/JSON.

### 3. TradingView Chart Studio
* Powered by **TradingView Lightweight Charts**.
* Indicators: 20 EMA (Cyan), 50 EMA (Amber), 200 EMA (Purple), Bollinger Bands, and Volume histogram.
* Dedicated **RSI(14)** sub-chart with 70, 50, 30 reference levels.
* Visual Horizontal Price Lines on the chart for **Entry Price**, **Stop Loss**, **Target 1 (2R)**, and **Target 2 (3R)**.

### 4. Institutional Backtesting Studio
* **Realistic Cost Simulation**: Incorporates Indian equity delivery taxes (STT $0.1\%$, GST $18\%$, Brokerage ₹20, Stamp Duty, Exchange turnover fees) and customizable slippage ($0.08\%$).
* **Trade Lifecycle Management**: Trailing stop loss (moves to breakeven after Target 1), multi-target profit taking, and maximum holding period timeouts.
* **KPI Metrics**: Net Profit, Win Rate %, Profit Factor, Max Drawdown %, Sharpe Ratio, Sortino Ratio, CAGR %, and full Trade-by-Trade logs.

### 5. Risk & Position Sizer
* Mathematical position sizing based on Fixed Fractional Risk ($1.0\%\text{--}2.0\%$ of account equity).
* Calculates exact share quantities, capital outlay, portfolio allocation %, and monetary loss/profit scenarios.

### 6. Custom Watchlists Manager
* Organize and save custom stock baskets with instant scanning capabilities.

---

## 📂 Project Structure

```
SwingTrades/
├── backend/
│   ├── app/
│   │   ├── main.py                     # FastAPI entrypoint
│   │   ├── api/
│   │   │   ├── screener_routes.py      # Screener REST & WebSocket
│   │   │   ├── chart_routes.py         # TradingView chart data & overlays
│   │   │   ├── backtest_routes.py      # Backtesting execution
│   │   │   ├── risk_routes.py          # Risk calculator
│   │   │   └── watchlist_routes.py     # SQLite watchlists CRUD
│   │   ├── core/
│   │   │   ├── data_engine.py          # Yahoo Finance + SQLite disk cache
│   │   │   ├── index_manager.py        # Official NSE/BSE universes
│   │   │   ├── indicator_engine.py     # Vectorized pure NumPy/Pandas indicators
│   │   │   └── risk_calculator.py      # Position sizing math
│   │   ├── strategies/
│   │   │   ├── base.py                 # Abstract BaseStrategy
│   │   │   ├── trend_pullback.py       # 20/50 EMA Pullback model
│   │   │   ├── vcp_breakout.py         # VCP Base Breakout model
│   │   │   └── mean_reversion.py       # Bollinger + RSI model
│   │   └── backtester/
│   │       ├── engine.py               # Indian market simulation engine
│   │       └── analytics.py            # Sharpe, Sortino, Drawdown, Profit Factor
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Navbar.jsx              # Institutional navigation
│   │   │   ├── ScreenerView.jsx        # Live screener with WebSocket progress
│   │   │   ├── ChartStudio.jsx         # Lightweight Charts with overlays
│   │   │   ├── BacktestStudio.jsx      # Equity curve & KPI analyzer
│   │   │   ├── RiskCalculator.jsx      # Position sizer
│   │   │   └── WatchlistView.jsx       # Watchlist manager
│   │   ├── services/api.js             # API client
│   │   ├── App.jsx                     # Root UI state container
│   │   └── index.css                   # Dark-themed styling
│   ├── package.json
│   └── vite.config.js
├── run.sh                              # One-click launcher script
├── STATE.md                            # Project state & persistence tracker
└── README.md                           # Documentation
```

---

## 🛠️ Manual Startup (Alternative)

```bash
# Terminal 1: Backend
python3 -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8888 --reload

# Terminal 2: Frontend (Dev Mode)
cd frontend && npm run dev
```
