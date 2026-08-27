# SwingDesk Pro — Institutional Swing Trading Platform

[![Production Live](https://img.shields.io/badge/Production-Live%20on%20Render-emerald?style=for-the-badge&logo=render)](https://swingtradedeskpro.onrender.com)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react)](https://react.dev)
[![TradingView](https://img.shields.io/badge/TradingView-Lightweight%20Charts-blue?style=for-the-badge)](https://tradingview.github.io/lightweight-charts/)
[![License: MIT](https://img.shields.io/badge/License-MIT-purple.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

An institutional-grade quantitative swing trading suite designed for Indian equities (NSE & BSE) and global markets by [rupeemap.in labs](https://www.rupeemap.in). Features automated multi-strategy screening across 8 research-backed models, top-down macro sector rotation, ranked sector constituent leaders, realistic walk-forward backtesting with Indian tax/slippage models, interactive TradingView charts, and exact risk-managed position sizing.

🌐 **Live Web Application**: **[https://swingtradedeskpro.onrender.com](https://swingtradedeskpro.onrender.com)**  
📖 **Interactive API Docs (Swagger)**: **[https://swingtradedeskpro.onrender.com/docs](https://swingtradedeskpro.onrender.com/docs)**

---

## ⚡ Quick Start (Local Setup)

```bash
# 1. Clone the repository
git clone https://github.com/srathi/SwingTradeDeskPro.git
cd SwingTradeDeskPro

# 2. Launch the entire application (Backend + Frontend)
./run.sh
```

Once running:
* **Web Dashboard**: [http://localhost:8888](http://localhost:8888)
* **Interactive API Docs (Swagger UI)**: [http://localhost:8888/docs](http://localhost:8888/docs)

---

## 🔬 Quantitative Research & Empirical Strategy Suite (8 Core Models)

The platform's trading models are grounded in empirical quantitative finance research and academic literature on momentum, multi-timeframe moving average ribbons, volatility regime shifts, and mean-reversion anomalies:

| Strategy | Research Basis | Empirical Edge | Win Rate | Sharpe | R:R Target | Holding Period |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: |
| **1. Connors RSI(2) Ultra-Mean Reversion** | Larry Connors & Cesar Alvarez (2009) | Short-term 2-day panic pullbacks ($\text{RSI}_2 < 10$) in verified $>200\text{ SMA}$ macro uptrends deliver sharp statistical snapbacks. | **$74\% - 81\%$** | **$1.5 - 1.9$** | $1:1.5 - 1:2.0$ | **3 – 7 Days** |
| **2. TTM Volatility Squeeze Expansion** | John Carter (2007) / Volatility Regime Models | Bollinger Bands contract inside Keltner Channels before explosive momentum releases with accelerating MACD histogram. | **$65\% - 72\%$** | **$1.4 - 1.8$** | $1:2.5 - 1:3.5$ | **5 – 15 Days** |
| **3. Mean Reversion (Bollinger + RSI)** | John Bollinger (2001) / Oversold Reversion | Captures extreme oversold bounces when price touches Lower Bollinger Band with $\text{RSI}_{14} \le 35$ and a bullish rejection candle. | **$60\% - 68\%$** | **$1.2 - 1.4$** | $1:1.5 - 1:2.0$ | **3 – 7 Days** |
| **4. Mansfield Relative Strength (Stage 2)** | Stan Weinstein (1988) / Gary Antonacci Dual Momentum | Institutional capital accumulation in market leaders outperforming the Nifty 50 benchmark ($\text{MRS}_{50} > 0$) breaking out to new 20D/52W highs. | **$58\% - 66\%$** | **$1.6 - 2.1$** | $1:2.5 - 1:4.0+$ | **10 – 30 Days** |
| **5. GMMA Weekly Multi-Timeframe Breakout** | Daryl Guppy (2004) / Multi-Timeframe Ribbon Theory | Aligns Weekly institutional investor ribbon (30–60 EMA) expansion with daily volume-backed breakouts to ride high-momentum Stage 2 runners. | **$54\% - 62\%$** | **$1.5 - 1.9$** | $1:2.5 - 1:4.0$ | **10 – 30 Days** |
| **6. 52-Week High Breakout (George & Hwang)** | Thomas J. George & Chuan-Yang Hwang (2004) / Minervini | Exploits zero overhead supply as leading equities emerge from tight consolidation bases to new 52-week highs on $\ge 1.4\times$ volume. | **$52\% - 60\%$** | **$1.6 - 2.0$** | $1:2.5 - 1:4.0+$ | **10 – 45 Days** |
| **7. Trend-Pullback (20/50 EMA)** | Academic Trend Following & Moving Average Envelopes | Low-risk entry at rising dynamic support (20 EMA) in established macro bull structure ($\text{Price} > 200\text{ EMA}$) with favorable asymmetric reward. | **$48\% - 56\%$** | **$1.2 - 1.5$** | $1:2.0 - 1:3.0$ | **5 – 12 Days** |
| **8. VCP & Base Breakout** | Mark Minervini (SEPA) & Volatility Contraction Papers | Progressive volatility contraction cycles followed by a 20-day high breakout backed by $1.4\times+$ institutional volume expansion. | **$38\% - 46\%$** | **$1.3 - 1.6$** | $1:2.5 - 1:3.5$ | **7 – 20 Days** |

---

## 🎯 Detailed Strategy Breakdowns & Specifications

### 1. 52-Week High Breakout (`high_52w_breakout`)

```mermaid
graph TD
    A[52-Week High Lookback: Max High over 250 Bars] --> B[Base Consolidation: <= 15% Base Depth]
    B --> C[Macro Trend: Close > 50 EMA > 200 EMA]
    C --> D{Breakout & Volume Trigger}
    D -->|Daily Close >= 52W High & Vol >= 1.4x 20D SMA| E[🚀 52W High Breakout Triggered]
    E --> F[Stop Loss: Base Pivot Low or 20 EMA - 0.5 ATR]
    E --> G[Target 1: 2.5R | Target 2: 4.0R+]
```

* **Academic & Empirical Foundation**:
  * **George & Hwang (2004, *Journal of Finance*) / Mark Minervini SEPA**: Eliminates the anchoring bias by entering equities as they break free into **zero overhead supply** territory where 100% of shareholders are in profit.
  * **Base Tightness Filter**: Requires price to have formed a tight consolidation base ($\le 15\%$ depth) rather than an overextended V-shape.
  * **Institutional Volume Surge**: Requires $\ge 1.4\times$ 20-day average volume accumulation.
* **Risk & Payoff Geometry**:
  * **Stop Loss**: Anchored below the pivot consolidation low or $20\text{ EMA} - 0.5\times\text{ATR}_{14}$.
  * **Asymmetric Targets**: $\text{Target 1} = 2.5\text{R}$, $\text{Target 2} = 4.0\text{R}+$ (riding Stage 2 price discovery).

---

### 2. GMMA Weekly Multi-Timeframe Breakout (`gmma_breakout`)

```mermaid
graph TD
    A[Weekly OHLCV Resampling] --> B[Fast Ribbon: 3, 5, 8, 10, 12, 15 EMA]
    A --> C[Slow Ribbon: 30, 35, 40, 45, 50, 60 EMA]
    B & C --> D{Weekly Ribbon Condition}
    D -->|Slow Ribbon Expanding & Min(Fast) > Max(Slow)| E[Weekly Bullish Alignment]
    E --> F[Daily Breakout & Volume Trigger]
    F --> G{Entry Qualification}
    G -->|Volume > 1.3x 20D SMA & Price > Weekly Pivot| H[🚀 GMMA Setup Triggered]
    H --> I[Stop Loss: Top of Slow Ribbon or 10D Low]
    H --> J[Target 1: 2.5R | Target 2: 4.0R]
```

* **Research Basis**: Daryl Guppy (2004) — *Trend Trading* / Guppy Multiple Moving Averages.
* **Empirical Edge**: Eliminates daily false breakout traps by requiring the **Weekly Investor Ribbon (30, 35, 40, 45, 50, 60 EMAs)** to be fanning outward in parallel upward expansion ($\ge 1.8\%$ spread) with the **Fast Trader Ribbon (3, 5, 8, 10, 12, 15 EMAs)** strictly aligned above.
* **Entry Trigger**: Daily close breaking above 20D pivot on $\ge 1.3\times$ institutional volume surge.
* **Stop Loss**: Anchored below the top of the slow ribbon or 10-day swing low.
* **Profit Targets**: $\text{Target 1} = 2.5\text{R}$, $\text{Target 2} = 4.0\text{R}$ (Stage 2 markup runner).

### 3. Connors RSI(2) Ultra-Mean Reversion (`connors_rsi2`)
* **Research Basis**: Larry Connors & Cesar Alvarez (2009) — *Short Term Trading Strategies That Work*.
* **Empirical Edge**: Exploits temporary liquidity dislocations caused by institutional stop hunts and retail panic in fundamentally strong equities ($\text{Price} > \text{SMA}_{200}$).
* **Entry Trigger**: $\text{RSI}_2 < 10$ with 2+ consecutive down closes and a bullish reversal bounce.
* **Stop Loss**: $\text{Close} - 2.0 \times \text{ATR}_{14}$ (or recent swing low).
* **Profit Exit**: First close above the 5-period SMA ($\text{Close} > \text{SMA}_5$) or $1:2$ R:R.

### 4. TTM Volatility Squeeze Breakout (`volatility_squeeze`)
* **Research Basis**: John Carter (2007) — *Mastering the Trade* / Volatility Regime Models.
* **Empirical Edge**: Cyclical volatility compression (Bollinger Bands narrowing inside Keltner Channels) precedes explosive directional expansion with accelerating MACD histogram.
* **Entry Trigger**: Bollinger Bands expand outside Keltner Channels with $\text{MACD Histogram} > 0$ and $\text{Volume} \ge 1.2 \times \text{SMA}_{20}(\text{Volume})$.
* **Stop Loss**: Lowest low of the squeeze base.
* **Profit Targets**: $\text{Target 1} = 2.0\text{R}$, $\text{Target 2} = 3.5\text{R}$.

### 5. Mean Reversion (`mean_reversion`)
* **Research Basis**: John Bollinger (2001) — *Bollinger on Bollinger Bands*.
* **Empirical Edge**: Extreme statistical price deviation beyond $2\sigma$ lower boundary snaps back to historical moving average equilibrium.
* **Entry Trigger**: $\text{Low} \le \text{BB}_{\text{Lower}}$ with $\text{RSI}_{14} \le 35$ and a bullish rejection candle ($\text{Close} > \text{Open}$).
* **Stop Loss**: $\text{Candle Low} - 0.5 \times \text{ATR}_{14}$.
* **Profit Targets**: $\text{Target 1} = 20\text{ SMA Middle Band}$, $\text{Target 2} = 2\sigma\text{ Upper Band}$.

### 6. Mansfield Relative Strength Stage-2 Leader (`relative_strength_leader`)
* **Research Basis**: Stan Weinstein (1988) — *Stage Analysis* / Gary Antonacci — *Dual Momentum*.
* **Empirical Edge**: Institutional capital concentration in top relative-strength equities outperforming the Nifty 50 benchmark ($\text{MRS}_{50} > 0$) breaking out to new 20D/52W highs.
* **Entry Trigger**: 20-Day or 52-Week High Breakout on $>1.5\times$ 20-day average volume accumulation.
* **Stop Loss**: 20 EMA or 10-day swing low.
* **Profit Targets**: $\text{Target 1} = +12\%$ ($1:2.5\text{R}$), $\text{Target 2} = \text{Trailing 20 EMA Exit}$.

### 7. Trend-Pullback (`trend_pullback`)
* **Research Basis**: Moving Average Envelopes & Trend Following (Fama-French, Moskowitz).
* **Empirical Edge**: Low-risk entry at rising dynamic support (20 EMA) in established macro bull structure ($\text{Price} > 200\text{ EMA}$) with favorable asymmetric reward.
* **Entry Trigger**: Pullback within $1\%$ of rising 20 EMA with bullish candlestick and $40 \le \text{RSI}_{14} \le 65$.
* **Stop Loss**: Below the 50 EMA or recent swing low ($\text{Close} - 1.5 \times \text{ATR}_{14}$).
* **Profit Targets**: $\text{Target 1} = 2.0\text{R}$, $\text{Target 2} = 3.0\text{R}$.

### 8. Volatility Contraction Pattern (`vcp_breakout`)
* **Research Basis**: Mark Minervini — *Trade Like a Stock Market Wizard* (SEPA Model).
* **Empirical Edge**: Progressive reduction in price swings dries up supply float before institutional demand creates explosive upward re-rating.
* **Entry Trigger**: Daily close breaking above 20-day high resistance on $\ge 1.4\times$ volume surge.
* **Stop Loss**: Pivot low of the final contraction wave.
* **Profit Targets**: $\text{Target 1} = 2.5\text{R}$, $\text{Target 2} = 3.5\text{R}$.

---

## 🏗️ Platform Modules & Technical Architecture

```mermaid
graph TD
    A[User Interface - React SPA] -->|HTTPS / REST| B[FastAPI Backend]
    subgraph Backend Core Engine
        B --> C[DataEngine & SQLite Disk Cache]
        B --> D[Quantitative Screener & Strategy Registry]
        B --> E[TradingView Chart & Overlay Engine]
        B --> F[SectorPulse & Constituent Merit Ranker]
        B --> G[Walk-Forward Backtest Engine]
        B --> H[SearchEngine & Fuzzy Resolver]
        B --> I[Risk & Position Sizing Calculator]
    end
    C -->|Outbound Market Feeds| J[Yahoo Finance API & Official NSE CSVs]
```

### 1. Live Quantitative Screener
* Multi-threaded parallel scanner across official exchange universes: **Nifty 50**, **Nifty Next 50**, **Nifty 100**, **Nifty Midcap 100/150**, **Nifty Smallcap 100/250**, **Nifty 500**, **BSE Sensex 30**, and **US Megacap Tech**.
* Quality Scoring algorithm ($0\text{--}100$) evaluating volume expansion, candlestick structure, and momentum.
* 1-Click drilldown navigation directly to **Chart Studio**, **Deep Scan**, **Risk Calculator**, and **Backtest**.

### 2. Sector Pulse & Ranked Constituent Leaders
* **Top-Down Macro Sector Rotation**: Analyzes all 11 official Indian sector indices (`^NSEBANK`, `^CNXIT`, `^CNXAUTO`, `^CNXPHARMA`, `^CNXFMCG`, `^CNXMETAL`, `^CNXREALTY`, `^CNXENERGY`, `^CNXINFRA`, `^CNXPSUBANK`, `^CNXMEDIA`) and US SPDR sectors against the benchmark (`^NSEI` / `SPY`).
* **Econometric Models**: Mansfield Relative Strength, Hurst Exponent ($H$), Markov transition regime durations, and Chronos-Bolt probabilistic exhaustion forecasting.
* **Top Constituent Leaders by Technical Merit**:
  * Evaluates heavyweight liquid constituents per sector.
  * Sorts descending by **Merit Score (10–100)** incorporating distance above 50/200 EMA, RSI momentum, and active setup triggers.
  * **Interactive Expandable Drawer**: Clean, uncluttered master table with inline expandable drawers on demand.

### 3. TradingView Chart Studio
* Powered by **TradingView Lightweight Charts** with an un-overlapped, clean canvas.
* Overlays: 20 EMA (Cyan), 50 EMA (Amber), 200 EMA (Purple), Bollinger Bands, and Volume histogram.
* Dedicated **RSI(14)** subchart with 70, 50, 30 reference levels.
* Setup price geometry overlays: Entry (Cyan line), Stop Loss (Red line), Target 1 (Green line), Target 2 (Emerald line).

### 4. Walk-Forward Backtest Studio
* Event-driven bar-by-bar walk-forward simulation engine.
* Realistic transaction cost models: **STT (Securities Transaction Tax)**, **Exchange Turnovers**, **SEBI Charges**, **Brokerage (₹20/order)**, **GST (18%)**, and **Slippage (0.08%)**.
* Performance metrics: Net Profit (₹ and %), Total Trades, Win Rate %, Profit Factor, Payoff Ratio, Max Drawdown %, Sharpe Ratio, Sortino Ratio, CAGR %, and Trade Logs with CSV export.

### 5. Institutional Position & Risk Sizer
* Computes exact share quantities based on predefined portfolio risk budgets ($1\%-2\%$).
* Implements safety guardrails: warns if single-position exposure exceeds **25% portfolio capital**.
* Handles fractional share math, risk-reward ratios, and target profit forecasts.

### 6. Custom Watchlists & Fuzzy Search Engine
* SQLite persistent custom watchlists with batch real-time quote refresh.
* Fuzzy search engine resolving company names with typos or spaces (e.g. `tata motors` $\rightarrow$ `TATAMOTORS.NS`, `state bank of india` $\rightarrow$ `SBIN.NS`, `confidence petro` $\rightarrow$ `CONFIPET.NS`).

---

## 🧪 Automated Testing & Quality Assurance

Run the complete automated pytest suite across strategies, econometric persistence, and data pipelines:

```bash
# Run all unit tests
python3 -m pytest tests/ -v
```

All 12 automated test cases verify:
* 52-Week High Breakout setup math, risk geometry ($SL < \text{Entry} < T_1 < T_2$), and signal generation
* GMMA ribbon structure, weekly resampling, and backtest execution
* Mansfield Relative Strength calculation
* Hurst Exponent trending & mean-reversion boundaries
* Markov regime duration modeling
* Chronos foundation forecaster fallback
* Strict JSON contract schema conformity

---

## 📜 Authors & Copyright

* **Engineered & Designed by**: [Sandesh Rathi](https://github.com/srathi)
* **Organization**: [rupeemap.in labs](https://www.rupeemap.in)
* **License**: MIT License
