// knowledgeBase.js - Comprehensive Jargon Dictionary & Page Playbooks for SwingTradeDeskPro
// Copyright (c) rupeemap.in labs | by Sandesh Rathi (https://www.rupeemap.in)

export const UNIVERSAL_GLOSSARY = {
  // --- VOLUME & PRICE ACTION ---
  poc: {
    term: "Point of Control (POC)",
    acronym: "POC",
    category: "Volume Profile",
    short_def: "The exact price level where the absolute highest trading volume occurred over the selected lookback window.",
    formula: "POC = PriceBucket with max(Volume_traded)",
    importance: "Institutional buyers and algorithmic desks treat POC as 'fair value'. When price trades above POC, it acts as high-liquidity support; when below, it acts as strong resistance.",
    playbook: "Look for bullish setups that bounce directly off POC or break out above POC with expanding volume. Avoid buying stocks trading directly beneath an un-tested POC.",
    example: "If KOTAKBANK is trading at ₹423.70 and its 6-month POC is at ₹380.50, the stock has strong institutional volume support sitting at ₹380.50."
  },
  vah: {
    term: "Value Area High (VAH)",
    acronym: "VAH",
    category: "Volume Profile",
    short_def: "The upper price boundary containing 70% of all transacted session volume.",
    formula: "VAH = Upper limit of the 70% volume distribution integral",
    importance: "Represents the highest price market participants accepted as fair value. Breaking above VAH signals institutional expansion into price discovery.",
    playbook: "A breakout above VAH accompanied by high relative volume is a strong Stage-2 trend confirmation.",
    example: "If RELIANCE consolidates between ₹1,270 (VAL) and ₹1,310 (VAH), a daily close above ₹1,310 confirms a breakout out of the value area."
  },
  val: {
    term: "Value Area Low (VAL)",
    acronym: "VAL",
    category: "Volume Profile",
    short_def: "The lower price boundary containing 70% of all transacted session volume.",
    formula: "VAL = Lower limit of the 70% volume distribution integral",
    importance: "Represents the lowest price where major institutions accumulated shares. Often acts as a rock-solid swing trade demand floor.",
    playbook: "When a strong stock pulls back to VAL during a market dip with oversold RSI, it offers an asymmetric, low-risk swing entry.",
    example: "TCS pulling back to VAL at ₹3,450 with RSI(14) at 38 is an institutional value re-test setup."
  },
  avwap: {
    term: "Anchored VWAP (AVWAP)",
    acronym: "AVWAP",
    category: "Volume Profile",
    short_def: "Volume-Weighted Average Price calculated starting from a specific structural market event (e.g. 52-Week High, Swing Low, or Earnings Gap).",
    formula: "AVWAP = Σ(Price × Volume) / Σ(Volume) starting from Anchor Bar t_0",
    importance: "Reveals the true breakeven cost basis of all market participants who entered since that key anchor event.",
    playbook: "1. 52-Week High AVWAP acts as overhead institutional resistance.\n2. Swing Low AVWAP acts as the primary defense floor for bulls.\n3. Price reclaiming AVWAP from below signals institutional accumulation.",
    example: "If TATASTEEL made a 52-Week High at ₹180, the 52W-High AVWAP at ₹155 shows the average price of all sellers since that top."
  },

  // --- MULTI-TIMEFRAME & CONFLUENCE ---
  elder_triple_screen: {
    term: "Alexander Elder Triple-Screen Confluence",
    acronym: "Triple Screen",
    category: "Multi-Timeframe",
    short_def: "A 3-tier filtration framework created by Dr. Alexander Elder that combines the Weekly Macro Tide, Daily Wave, and Micro Execution Timing.",
    formula: "Score = (Weekly_Trend × 40%) + (Daily_Momentum × 40%) + (Micro_Trigger × 20%)",
    importance: "Prevents traders from buying daily pullbacks when the overarching weekly trend is bearish, drastically reducing false breakouts.",
    playbook: "• Screen 1 (Weekly Tide): 13/26 EMA slope + MACD Histogram.\n• Screen 2 (Daily Wave): 20/50 EMA structure + RSI pullback.\n• Screen 3 (Micro Timing): Entry trigger bar breaking prior day high with volume.",
    example: "A stock with ⭐⭐⭐ Triple Screen A+ (Score 90/100) has weekly MACD expanding upwards, daily price bouncing on the 20 EMA, and a breakout trigger."
  },
  alpha_fusion: {
    term: "Alpha Fusion Ensemble Engine",
    acronym: "Alpha Fusion",
    category: "Quantitative Ensemble",
    short_def: "A hybrid quantitative score (0–100) that fuses strategy mechanics, Kronos neural AI forecasts, multi-timeframe confluence, and volume profile, scaled by macro market regimes.",
    formula: "Alpha = [Strategy(30%) + AI_Upside(25%) + MTF(25%) + VolProfile(20%)] × Regime_Multiplier",
    importance: "Replaces single-indicator bias with an institutional ensemble model. Only setups with cross-domain quantitative agreement achieve Score > 75.",
    playbook: "• Score ≥ 80: High-Conviction Institutional Grade (Grade A+).\n• Score 65–79: Standard Quality Swing Trade (Grade B+).\n• Score < 65: Lower Conviction (Gated or requires smaller sizing).",
    example: "If INFY triggers a Trend-Pullback (30 pts), Kronos AI forecasts +4.2% (25 pts), MTF is bullish (25 pts), and POC is supportive (20 pts), Composite Alpha = 100 × 1.0 = 100."
  },
  ev_r: {
    term: "Statistical Expectancy (EV/R)",
    acronym: "EV/R",
    category: "Risk & Probability",
    short_def: "Expected Value per 1 Unit of Risk ($R$). Measures how much profit you can mathematically expect to make for every ₹1,000 risked.",
    formula: "EV/R = (Win_Rate × Avg_Win_R) - (Loss_Rate × 1.0R)",
    importance: "Positive expectancy ($EV/R > +0.20R$) is the mathematical foundation of profitable trading. Without positive expectancy, position sizing cannot save a strategy.",
    playbook: "• EV/R > +0.35R: Excellent statistical edge.\n• EV/R +0.15R to +0.35R: Good playable edge.\n• EV/R ≤ 0.00R: Negative edge (Do not trade).",
    example: "If a strategy has 60% win rate and 1.8R average win: EV/R = (0.60 × 1.8) - (0.40 × 1.0) = +0.68R. For every ₹10,000 risked, expected average profit is ₹6,800."
  },

  // --- RISK & EXIT MODELS ---
  chandelier_exit: {
    term: "Chandelier Trailing Stop",
    acronym: "Chandelier Exit",
    category: "Risk Management",
    short_def: "A volatility-adaptive trailing stop developed by Chuck LeBeau that hangs down from the highest high of the trade by a multiple of ATR(14).",
    formula: "Chandelier_Stop = Highest_High(22 bars) - (3.0 × ATR_14)",
    importance: "Allows massive Stage-2 winning trends to compound without getting shaken out by normal daily noise, while strictly locking in accrued profits when trend breaks.",
    playbook: "Trail your stop loss upward to the Chandelier level every session. Never move a Chandelier stop downward.",
    example: "If a stock reached a 22-day peak of ₹1,000 and ATR is ₹20: Chandelier Stop = ₹1,000 - (3.0 × ₹20) = ₹940."
  },
  half_kelly: {
    term: "Half-Kelly Position Sizing",
    acronym: "Half-Kelly",
    category: "Capital Sizing",
    short_def: "A fractional implementation of Ed Thorp and J.L. Kelly's optimal capital growth formula that cuts risk volatility by 50% while capturing 75% of max growth.",
    formula: "f* = 0.5 × [ p - ( (1 - p) / b ) ]  where p=Win Rate, b=Payoff Ratio",
    importance: "Prevents catastrophic drawdowns caused by full Kelly aggressive betting, while ensuring capital is dynamically allocated heavier to higher-edge setups.",
    playbook: "Use the calculated Half-Kelly % to size your trade allocation. If Half-Kelly recommends 4.2%, allocate 4.2% of total portfolio risk to this setup.",
    example: "With a 65% win rate and 2.0 reward ratio: Full Kelly = 47.5%, Half-Kelly = 23.75% portfolio capital allocation."
  },
  r_multiple: {
    term: "R-Multiple (Risk Unit)",
    acronym: "R",
    category: "Performance Tracking",
    short_def: "The normalized measure of return relative to the initial amount of capital risked on that trade.",
    formula: "R = (Exit_Price - Entry_Price) / (Entry_Price - Stop_Loss)",
    importance: "Standardizes trade performance across different stock prices. A +3R win is equally great whether trading a ₹50 penny stock or a ₹4,000 blue chip.",
    playbook: "Target swing setups offering at least 2.0R to 3.0R reward relative to your 1.0R risk.",
    example: "Bought at ₹500, Stop Loss at ₹480 (1R = ₹20). Exited at ₹560. Profit = ₹60 = +3.0R."
  },
  profit_factor: {
    term: "Profit Factor",
    acronym: "PF",
    category: "Performance Tracking",
    short_def: "The ratio of total gross profits to total gross losses over a trading history.",
    formula: "Profit_Factor = Σ(Gross Profits) / Σ(Gross Losses)",
    importance: "The single best metric for system robustness. A PF > 1.8 indicates an institutional-grade edge.",
    playbook: "• PF > 2.0: Exceptional system.\n• PF 1.5 – 2.0: Solid profitable trading.\n• PF < 1.0: Losing system.",
    example: "If total closed winning trades made ₹1,50,000 and total losing trades lost ₹50,000, Profit Factor = 3.00."
  },

  // --- MACRO & VOLATILITY ---
  market_regime: {
    term: "Macro Market Regime & Volatility Intelligence",
    acronym: "Regime",
    category: "Macro Regime",
    short_def: "An institutional risk-gating system that classifies the broader equity market into 4 distinct volatility states to dictate optimal strategy selection and position sizing.",
    formula: "Regime = f(Nifty Trend, India VIX, Market Breadth % > 200 EMA)",
    importance: "Prevents trend traders from buying false breakouts during volatile chop and alerts swing traders when risk-on expansion is active.",
    playbook: "• 🟢 Risk-On Expansion: Full 100% position sizing; trade Breakouts & Momentum.\n• 🟡 Selective Pullbacks: 75% sizing; buy 20/50 EMA dips on market leaders.\n• 🟠 High Chop Mean-Reversion: 50% sizing; Bollinger Band & RSI oversold bounces.\n• 🔴 Capital Preservation: 25% sizing or 100% cash; protect capital.",
    example: "When Nifty is above 20 EMA, VIX is 12.8, and Breadth is 68%, Market Regime is 🟢 Risk-On Expansion."
  },
  volume_profile: {
    term: "Volume Profile (VPVR)",
    acronym: "Volume Profile",
    category: "Volume Profile",
    short_def: "An advanced charting study that plots trading activity over a specified time period at specified price levels rather than over time.",
    formula: "Horizontal volume histogram decomposed into POC, VAH (Value Area High), and VAL (Value Area Low).",
    importance: "Reveals where large institutional participants actually traded their orders, creating high-probability support and resistance zones.",
    playbook: "Trade with the Value Area: Buy near VAL when trending upward; target POC and VAH.",
    example: "A stock consolidates inside the Value Area (₹450–₹480) with POC at ₹465. Buying at ₹452 offers an asymmetric 1:3 R/R setup."
  },
  india_vix: {
    term: "India VIX (Volatility Index)",
    acronym: "VIX",
    category: "Macro Regime",
    short_def: "NSE's gauge of annualized expected market volatility over the next 30 calendar days derived from NIFTY index option prices.",
    formula: "Implied Daily Move % = India_VIX / √252",
    importance: "VIX determines market regime: Low VIX (<14) signals smooth trend expansion; High VIX (>22) signals extreme chop, panic, and breakout failure.",
    playbook: "• VIX < 14: Risk-On (Trade full size breakouts).\n• VIX 14–18: Selective Pullbacks (Buy 20 EMA dips).\n• VIX 18–22: High Chop (Mean-reversion only).\n• VIX > 22: Capital Preservation (Cut sizing to 25%, raise cash).",
    example: "If India VIX is 12.6, implied daily NIFTY move is 12.6 / 15.87 = ±0.79% (ideal for momentum swing trades)."
  },
  market_breadth: {
    term: "Market Breadth (% > 200 EMA)",
    acronym: "Breadth",
    category: "Macro Regime",
    short_def: "The percentage of stocks across the NIFTY 500 trading above their long-term 200-day Exponential Moving Average.",
    formula: "Breadth % = (Count of Stocks with CMP > 200 EMA) / Total_Universe × 100",
    importance: "Leading indicator of macro health. Breadth > 60% indicates widespread institutional participation across sectors.",
    playbook: "When Breadth > 70%, aggressive Stage-2 swing trades thrive. When Breadth < 40%, preserve capital and trade defensives.",
    example: "If 340 out of 500 stocks are above their 200 EMA, Breadth is 68% (Strong Bullish Health)."
  },

  // --- TECHNICAL INDICATORS ---
  ema_20_50_200: {
    term: "Exponential Moving Averages (20 / 50 / 200 EMA)",
    acronym: "EMA Ribbon",
    category: "Technical Indicator",
    short_def: "Weighted moving averages that give higher weight to recent prices, defining short-term (20 EMA), intermediate (50 EMA), and institutional macro (200 EMA) trends.",
    formula: "EMA_t = (Price_t × (2 / (N + 1))) + (EMA_{t-1} × (1 - (2 / (N + 1))))",
    importance: "Institutional swing trades thrive in stacked bull alignment: Price > 20 EMA > 50 EMA > 200 EMA.",
    playbook: "• 20 EMA: Dynamic pullback support for momentum leaders.\n• 50 EMA: Core institutional swing base.\n• 200 EMA: Major bull/bear line in the sand.",
    example: "When a stock pulls back to test its 20 EMA from above and prints a bullish rejection hammer, it is a textbook Trend-Pullback entry."
  },
  rsi_14: {
    term: "Relative Strength Index (RSI 14)",
    acronym: "RSI(14)",
    category: "Technical Indicator",
    short_def: "Momentum oscillator measuring the speed and change of price movements between 0 and 100.",
    formula: "RSI = 100 - (100 / (1 + (Avg_Gain / Avg_Loss)))",
    importance: "Identifies whether an asset is overbought (>70) or oversold (<30), and spots hidden bullish momentum divergences.",
    playbook: "In an uptrend, look for RSI pullbacks into the 40–55 support zone, then bounce.",
    example: "RSI dropping to 42 while stock price holds above 20 EMA indicates a healthy cooling-off pullback within a strong uptrend."
  },
  kronos_neural_forecast: {
    term: "Kronos AI Foundation Neural Forecast",
    acronym: "Kronos AI",
    category: "AI Neural Model",
    short_def: "A neural time-series foundation model trained on multi-scale financial market data to forecast the next 15-day price trajectory with 90% confidence corridors.",
    formula: "Trajectory = E[Price_{t+k} | OHLCV_{0:t}], Corridor = [P10, P90]",
    importance: "Eliminates emotional guessing by providing mathematical probability bounds (P10/P90) and upside probability % for swing holding horizons.",
    playbook: "Verify that Kronos Upside Probability is ≥ 60% and the Expected Target falls cleanly within the 90% corridor before taking a trade.",
    example: "Kronos forecasts RELIANCE to reach ₹1,340 (+2.8%) over the next 15 sessions with 68% Upside Probability and 90% corridor of ₹1,290–₹1,365."
  },
  rsi_28: {
    term: "Relative Strength Index (RSI 28 Smoothed)",
    acronym: "RSI(28)",
    category: "Technical Indicator",
    short_def: "A 28-period smoothed momentum oscillator designed specifically to filter out high-frequency market noise and detect high-conviction macro swing divergence.",
    formula: "RSI_{28} = 100 - (100 / (1 + (AvgGain_{28} / AvgLoss_{28})))",
    importance: "Standard 14-period RSI generates false whipsaws in noisy chop. The 28-period lookback isolates genuine institutional divergence between swing lows/highs.",
    playbook: "Look for Bullish Divergence where Price forms a Lower Low while RSI(28) forms a distinctly Higher Low from below 45.",
    example: "HDFCBANK makes a lower low at ₹1,620 vs previous low at ₹1,650, while RSI(28) prints 38 vs previous 32. This triggers a high-probability macro divergence reversal."
  },
  mansfield_rs: {
    term: "Mansfield Relative Strength (MRS)",
    acronym: "MRS",
    category: "Sector & Relative Strength",
    short_def: "Standardized Stan Weinstein relative strength indicator measuring whether a sector or equity is outperforming the benchmark index (Nifty 50).",
    formula: "MRS = ((Price / Benchmark) / SMA_{52W}(Price / Benchmark) - 1) × 100",
    importance: "MRS > 0 and rising confirms that the stock/sector is an institutional market leader attracting capital inflows. MRS < 0 signals chronic underperformance.",
    playbook: "Only buy stocks in sectors where Mansfield RS is positive (> 0) and trending upward. Avoid bottom-fishing in negative RS sectors.",
    example: "NIFTY AUTO MRS is +4.8 and rising, while NIFTY FMCG is -3.2. Institutional capital is rotating heavily into Auto equities."
  },
  hurst_exponent: {
    term: "Hurst Exponent (H)",
    acronym: "Hurst",
    category: "Quantitative Statistics",
    short_def: "A mathematical metric ranging from 0 to 1 measuring the long-term memory and trending persistence of a financial time series.",
    formula: "H = \\log(R/S) / \\log(T)",
    importance: "• H > 0.5: Persistent Trending series (trend-following strategies work best).\n• H = 0.5: Geometric Random Walk.\n• H < 0.5: Mean-Reverting series (range-bound strategies work best).",
    playbook: "Deploy Trend-Pullback and Breakout strategies when Sector Hurst > 0.55. Switch to Mean-Reversion when Hurst < 0.45.",
    example: "NIFTY IT has a Hurst exponent of 0.64, indicating strong trend persistence suitable for trailing breakout rides."
  },
  max_drawdown: {
    term: "Maximum Drawdown (MDD)",
    acronym: "MDD",
    category: "Risk & Backtesting",
    short_def: "The maximum peak-to-trough equity percentage decline observed during a backtest or live trading period.",
    formula: "MDD = \\max_{t} ((Peak_t - Equity_t) / Peak_t) × 100",
    importance: "Measures downside portfolio pain and risk of ruin. Institutional swing desks cap system MDD at < 15%.",
    playbook: "Size positions so that system drawdown never exceeds the maximum capital risk tolerance threshold.",
    example: "A strategy with 45% annual return and 8.2% Max Drawdown provides exceptional risk-adjusted stability."
  },
  squeeze_momentum: {
    term: "John Carter Squeeze Momentum",
    acronym: "TTM Squeeze",
    category: "Momentum & Volatility",
    short_def: "Indicator detecting low-volatility consolidation when Bollinger Bands (20, 2.0) compress inside Keltner Channels (20, 1.5 ATR).",
    formula: "Squeeze On = BB_{width} < Keltner_{width}",
    importance: "Markets alternate between periods of low volatility (consolidation) and high volatility (explosive expansion). Squeeze signals coiled explosive energy.",
    playbook: "When Black Dot (Squeeze On) transitions to Green Dot (Squeeze Fired) with positive momentum histogram, enter in the direction of the momentum bar.",
    example: "TATASTEEL enters squeeze for 8 sessions; on Day 9, squeeze fires with cyan histogram bar, launching a 6% 3-day swing."
  },
  gmma: {
    term: "Guppy Multiple Moving Average (GMMA)",
    acronym: "GMMA",
    category: "Trend Strategy",
    short_def: "A set of 12 exponential moving averages split into Trader EMAs (3, 5, 8, 10, 12, 15) and Investor EMAs (30, 35, 40, 45, 50, 60).",
    formula: "Trader EMAs vs Investor EMAs ribbon spread",
    importance: "Separates short-term speculative sentiment from long-term institutional accumulation. Ribbon separation confirms trend strength.",
    playbook: "Buy when the Trader Ribbon expands and bounces off the Investor Ribbon in stacked upward alignment.",
    example: "All 6 Trader EMAs compress into the Investor Ribbon and bounce cleanly upward, confirming institutional support."
  },

  // --- SECTOR PULSE QUANTITATIVE INTELLIGENCE ---
  regime_forecast_memory: {
    term: "Regime Forecast & Memory (Hurst H & Markov Duration)",
    acronym: "Regime Memory",
    category: "Sector & Macro",
    short_def: "A quantitative forecasting framework combining Hurst Long-Memory ($H$) with Markov Chain state-transition duration models to predict how many days a sector trend will persist.",
    formula: "Expected Runway = E[Duration | Current State] - Current Regime Age",
    importance: "Prevents entering a sector right as its multi-month momentum run is mathematically exhausting, and highlights fresh breakouts with 20+ days of remaining runway.",
    playbook: "• High Runway (> 15 Days) + Hurst > 0.55: Deploy aggressive Breakout & Trend-Following strategies.\n• Low Runway (< 5 Days) or High Exhaustion: Tighten trailing stops and take profits on strength.",
    example: "NIFTY AUTO is on Day 12 of a Strong Uptrend with Expected Total Run of 28 Days. It has an Estimated Runway of 16 Days Remaining, making fresh swing pullback entries high-probability."
  },
  exhaustion_risk: {
    term: "Exhaustion & Volatility Risk (Weibull & ATR Gating)",
    acronym: "Exhaustion Risk",
    category: "Sector & Macro",
    short_def: "Multi-factor risk diagnostic measuring trend fatigue (Weibull hazard rate), overextension distance from the 50 EMA (> 3×ATR), and trailing stop floors.",
    formula: "Exhaustion Prob = 1 - e^{-(Age / \\eta)^\\beta}, Overextension = (Price - EMA_{50}) > 3.0 × ATR_{14}",
    importance: "When a sector becomes overextended (> 3 ATR) and exhaustion exceeds 65%, even strong news catalysts trigger sharp mean-reverting pullbacks rather than continued rallies.",
    playbook: "• Exhaustion < 30% & Normal Band: Safe for fresh breakout entries.\n• Exhaustion > 60% or Overextended Flag: Avoid initiating new positions; trail stops to lock in gains.",
    example: "NIFTY PHARMA is up 8 consecutive weeks, with Exhaustion Probability at 74% and Overextension Flag active. Swing traders should trail stops to the ₹21,400 floor rather than buying new breakouts."
  },
  regime_age_runway: {
    term: "Current Regime Age & Estimated Runway",
    acronym: "Runway",
    category: "Sector & Macro",
    short_def: "The exact number of trading sessions a sector has spent in its current trend regime compared against its historical Markov expected run length.",
    formula: "Estimated Runway = max(0, Expected_Total_Days - Current_Age_Days)",
    importance: "Identifies whether a sector trend is in its youth (early Stage 2), maturity (mid-run), or late-stage exhaustion.",
    playbook: "The best risk-to-reward swing entries occur in young trends with Age < 10 days and Runway > 15 days.",
    example: "NIFTY METAL just transitioned into 'Early Uptrend' on Day 3 with an Expected Run of 22 Days (19 Days Runway remaining) — optimal for fresh accumulation."
  },
  weibull_exhaustion: {
    term: "Trend Exhaustion Probability (Weibull Hazard Rate)",
    acronym: "Exhaustion %",
    category: "Quantitative Statistics",
    short_def: "The mathematical probability that the current price trend will terminate or experience a deep mean-reverting correction within the next 5 sessions.",
    formula: "h(t) = (\\beta / \\eta) × (t / \\eta)^{\\beta - 1}",
    importance: "Unlike static indicators, Weibull hazard models factor in time-decay of momentum trends. Older trends experience non-linear acceleration in failure risk.",
    playbook: "Scale down position sizing to 50% when Exhaustion Probability crosses 60%.",
    example: "Exhaustion Probability rising from 22% to 68% over 3 weeks warns of institutional profit-taking ahead."
  },
  overextension_risk: {
    term: "Overextension Flag (> 3x ATR Deviation)",
    acronym: "Overextended",
    category: "Volatility & Risk",
    short_def: "Quantitative alert triggered when price stretches more than 3.0 standard Daily Average True Ranges (ATR 14) above its 50-day Exponential Moving Average.",
    formula: "Overextension Flag = True if (Close - EMA_{50}) > 3.0 × ATR_{14}",
    importance: "Mean-reversion physics dictate that extreme elastic stretches from moving averages snap back aggressively toward the mean.",
    playbook: "Never initiate new long breakout positions when Overextension Flag is True. Wait for a pullback to the 20 EMA.",
    example: "TRENT surges 22% in 6 days and triggers Overextension Flag (+3.4 ATR). Buying here has poor R/R; wait for a retest of the 20 EMA."
  },
  merit_score: {
    term: "Constituent Merit Score (0–100)",
    acronym: "Merit",
    category: "Stock Scoring",
    short_def: "A composite ranking metric evaluating individual stocks inside a sector by relative strength against the sector index, volume surge, EMA alignment, and stage quality.",
    formula: "Merit = 0.35(RS_vs_Sector) + 0.25(Volume_Surge) + 0.25(EMA_Trend) + 0.15(RSI_Momentum)",
    importance: "Ensures you always pick the #1 or #2 market leaders in a winning sector rather than lagging sympathy plays.",
    playbook: "When trading a leading sector, exclusively pick stocks with Merit Score > 80.",
    example: "In NIFTY IT, COFORGE has a Merit Score of 91 while WIPRO has a Merit Score of 48. Allocate capital into COFORGE for maximum alpha."
  },
  weinstein_stage: {
    term: "Stan Weinstein 4-Stage Analysis",
    acronym: "Stage",
    category: "Technical Analysis",
    short_def: "Classical institutional market structure model classifying price cycles into 4 distinct phases based on the 30-week (150-day) moving average.",
    formula: "Stage 1 (Accumulation / Base) → Stage 2 (Bull Expansion / Markup) → Stage 3 (Distribution / Top) → Stage 4 (Decline / Markdown)",
    importance: "80% of all massive swing trade winners occur exclusively in Stage 2. Trading in Stage 4 causes chronic capital erosion.",
    playbook: "• Stage 2 (Bull): Buy breakouts and 20 EMA pullbacks.\n• Stage 1 (Base): Monitor for early breakout.\n• Stage 3/4: Avoid or exit immediately.",
    example: "A stock breaking out of a 6-month base above its rising 30-week SMA enters Stage 2 Bull Expansion."
  },
  avwap_multi_pivot: {
    term: "Multi-Pivot Anchored VWAP (AVWAP)",
    acronym: "AVWAP",
    category: "Volume Profile & Orderflow",
    short_def: "Volume-Weighted Average Price anchored from key psychological inflection points: 52-Week High, Recent Swing Low, and Earnings/Surge Bar.",
    formula: "AVWAP = \\frac{\\sum_{i=anchor}^{t} (Price_i \\times Volume_i)}{\\sum_{i=anchor}^{t} Volume_i}",
    importance: "Represents the aggregate breakeven price of all buyers and sellers who entered since that critical market event.",
    playbook: "• Price > Swing Low AVWAP: Institutional buyers from the bottom are in profit and defending their cost basis (Demand zone).\n• Price < 52W High AVWAP: Overhead trapped buyers create resistance.",
    example: "If a stock pulls back to its Swing Low AVWAP at ₹485 and prints a hammer candle, it represents a high-conviction institutional defense level."
  },
  alpha_fusion_interpretation: {
    term: "Alpha Fusion Composite Diagnostic Protocol",
    acronym: "Alpha Fusion Protocol",
    category: "Quantitative Synthesis",
    short_def: "The comprehensive interpretation methodology for the 4-Pillar Alpha Fusion engine to validate high-conviction swing setups.",
    formula: "Alpha Score = Regime_Mult × [0.30(Strategy) + 0.25(Kronos AI) + 0.25(MTF Confluence) + 0.20(Volume Profile)]",
    importance: "Eliminates single-indicator biases by requiring confluence across price action, neural forecasting, multi-timeframe trends, and institutional orderflow.",
    playbook: "• Score 80–100 (Triple Screen A+ / Strong Alpha): Full size entry (100% position).\n• Score 60–79 (Moderate Alpha): Standard size entry (75% position); verify EV/R > +0.30R.\n• Score < 60 (Weak Alpha): Pass or wait for better alignment.",
    example: "If a stock has an Alpha Fusion Score of 86, Kronos Upside Prob of 68%, Double Screen B+ confluence, and EV/R of +0.52R, it meets all institutional criteria for an immediate trade."
  }
};

export const PAGE_GUIDES = {
  screener: {
    title: "Live Screener & Batch Scanning",
    subtitle: "Real-time algorithmic scanner filtering thousands of stocks across 12 quantitative strategies.",
    summary: "The Live Screener scans custom watchlists or entire index universes (NIFTY 50, NIFTY 500, MidCap 150) in parallel batches to uncover high-probability swing trade setups.",
    sections: [
      {
        heading: "1. Scanner Controls & Universe Selection",
        description: "Select which universe to scan (e.g. NIFTY_50, NIFTY_MIDCAP_150, or your Custom Watchlists) and pick a target quantitative strategy.",
        tips: "Use 'All Active Strategies' to discover every valid setup across all 12 quantitative models simultaneously."
      },
      {
        heading: "2. Screener Setup Cards Breakdown",
        description: "Each match card contains institutional data points designed for rapid visual verification:",
        bullets: [
          "Score (0–100): Composite quantitative rating based on strategy criteria alignment and trend strength.",
          "⭐⭐ Confluence Badge: Alexander Elder Triple-Screen rating (Screen 1 Weekly Macro, Screen 2 Daily Wave, Screen 3 Timing).",
          "POC: ₹... Pill: The Point of Control (highest institutional volume node) for that stock.",
          "20 EMA: Short-term trend support level.",
          "RSI (14): Current momentum oscillator reading.",
          "Stop Loss: Exact price where setup is invalidated.",
          "Target (2R): Primary 1:2 Risk-to-Reward profit target."
        ]
      },
      {
        heading: "3. Action Buttons on Match Cards",
        description: "Quick 1-click tools on every card:",
        bullets: [
          "🔮 AI Forecast: Runs instant Kronos neural 15-day time-series forecast.",
          "📊 Chart: Opens the stock inside the Interactive Chart Studio with all indicators overlayed.",
          "🛡️ Risk Calc: Pre-fills stock entry and stop loss into the position size and capital risk calculator.",
          "📝 Log Trade: Instantly logs the setup into your Simulated Paper Trading Journal with 1 click."
        ]
      }
    ],
    example: {
      title: "Real-World Screener Workflow",
      text: "You run a scan on NIFTY_MIDCAP_150 for 'Trend-Pullback'. The scanner finds KOTAKBANK at ₹423.70 with a Score of 85, ⭐⭐ Double Screen B+ confluence, 20 EMA at ₹584.50, Stop Loss at ₹573.13, and Target at ₹712.54. You click 'Log Trade' to track it in your paper journal, then click 'Chart' to view the volume profile."
    }
  },

  deepscan: {
    title: "Single Stock Comprehensive Deep Scan",
    subtitle: "360-degree quantitative diagnostic combining Alpha Fusion, Triple Screen, Volume Profile, and Risk Models.",
    summary: "Deep Scan runs a comprehensive institutional diagnostic on any individual equity (NSE/BSE/Global) in under 2 seconds. It synthesizes technical rules, multi-timeframe trends, volume orderflow, neural forecasting, and mathematical position sizing into an actionable trade verdict.",
    sections: [
      {
        heading: "1. The 5-Step Diagnostic Protocol (How to Interpret Deep Scan)",
        description: "Follow this systematic 5-step institutional routine to evaluate any stock in seconds:",
        bullets: [
          "Step 1: Check Alexander Elder MTF Confluence (Hero Banner) — Look for ⭐⭐⭐ Triple Screen A+ or ⭐⭐ Double Screen B+. Ensure Screen 1 (Weekly Tide) is bullish before taking daily swing trades.",
          "Step 2: Read Alpha Fusion Composite Score & EV/R (Section 3.6) — Verify Score ≥ 75 and Statistical Expectancy EV/R ≥ +0.35R for high-conviction trades.",
          "Step 3: Analyze Volume Profile & AVWAPs (Section 3.8) — Confirm price is trading above the Volume POC (Point of Control) and bouncing near the Swing Low AVWAP (demand zone).",
          "Step 4: Check Kronos AI Neural 15-Day Corridor (Section 3.5) — Verify Upside Probability ≥ 60% and ensure the expected target is within the 90% confidence corridor [P10, P90].",
          "Step 5: Apply Risk Sizing & Chandelier Exit (Section 4) — Enter your account capital to generate the exact share count. Use the ATR Chandelier Stop (3x) to let winners run."
        ]
      },
      {
        heading: "2. Alpha Fusion Ensemble Interpretation Matrix (Section 3.6)",
        description: "The platform's flagship 4-pillar alpha synthesis engine ($0–100$):",
        bullets: [
          "🟢 Score 80–100 (Strong Alpha / Triple Screen A+): Exceptional institutional alignment across all 4 pillars. Full 100% position size. Highest statistical win rates.",
          "🟡 Score 60–79 (Moderate Alpha / Double Screen B+): Solid trade setup with favorable risk/reward. Allocate standard 75% position sizing. Verify EV/R > +0.25R.",
          "🟠 Score 45–59 (Speculative / Neutral): Mixed signals (e.g. Daily trend bullish but Weekly Tide flat or POC resistance overhead). Half 50% sizing or wait for confirmation.",
          "🔴 Score < 45 (Invalidated / High Risk): Trend broken, heavy overhead supply, or negative AI expectancy. Avoid long entries or cut existing positions."
        ]
      },
      {
        heading: "3. Alexander Elder Triple-Screen Confluence Matrix (Section 3.7)",
        description: "Audits market structure across 3 independent time horizons to eliminate whipsaws:",
        bullets: [
          "Screen 1 (Weekly Tide): 13/26 EMA slope + Weekly MACD Histogram. Dictates the macro trade direction. (Rule: Only buy when Tide is Bullish).",
          "Screen 2 (Daily Wave): 20/50 EMA alignment + Daily RSI(14) cooling. Identifies healthy pullbacks against the tide.",
          "Screen 3 (Micro Trigger): Intraday breakout above previous day's high to confirm the wave has turned back into the tide."
        ]
      },
      {
        heading: "4. Volume Profile & Multi-Pivot AVWAPs (Section 3.8)",
        description: "Identifies the exact breakeven cost bases of institutional participants:",
        bullets: [
          "POC (Gold Line): Highest volume node. Acts as high-liquidity bedrock support when price is above.",
          "Value Area (VAH / VAL): 70% volume containment zone. A close above VAH signals Stage-2 price discovery.",
          "Swing Low AVWAP (Green Dotted): Cost basis of buyers from the major bottom. Strong institutional defense zone.",
          "52W High AVWAP (Yellow Dotted): Cost basis of trapped top buyers. Represents critical overhead resistance to clear."
        ]
      },
      {
        heading: "5. Position Sizing & ATR Chandelier Stop (Section 4)",
        description: "Mathematical risk management and trailing stop parameters:",
        bullets: [
          "1% Risk Allocation Model: Calculates exact shares so you never risk more than 1% of equity if stop is hit.",
          "ATR Chandelier Stop (3x): Trailing exit placed 3.0 × ATR below the highest high of the swing to capture full trends."
        ]
      }
    ],
    example: {
      title: "Real-World Deep Scan Case Study",
      text: "RELIANCE trades at ₹1,305. Deep Scan reveals: Alpha Fusion Score = 86/100, MTF Rating = ⭐⭐ Double Screen B+, Kronos AI Upside = 68% (Expected Target ₹1,345), Price is resting right above 6-month POC (₹1,280) and Swing Low AVWAP (₹1,295), EV/R = +0.48R. Interpretation: Textbook high-conviction swing buy with ₹1,270 stop loss and ₹1,375 (2.5R) profit target."
    }
  },

  chart: {
    title: "Interactive Chart Studio",
    subtitle: "High-resolution TradingView Lightweight Charts with dynamic volume and mathematical overlays.",
    summary: "The Interactive Chart Studio lets you visualize price action with real-time indicators, Volume Profile horizontal lines, Multi-Pivot AVWAPs, and neural AI forecast funnels.",
    sections: [
      {
        heading: "1. Candlestick & Real Dynamic Volume Histogram",
        description: "High-performance canvas rendering OHLC candlesticks with dynamic session volume bars (green on up days, red on down days).",
        tips: "Zoom in/out with mouse scroll or touchpad pinch. Drag left/right to pan through historical price action."
      },
      {
        heading: "2. Indicator Overlays Toolbar",
        description: "Toggle indicators on/off instantly without page reloads:",
        bullets: [
          "20 EMA (Cyan): Short-term momentum support line.",
          "50 EMA (Amber): Intermediate trend support line.",
          "200 EMA (Purple): Long-term institutional trend line.",
          "Vol Profile: Renders Gold solid POC line + Cyan dashed VAH line + Blue dashed VAL line.",
          "AVWAP: Renders Yellow dotted 52W-High AVWAP + Green dotted Swing-Low AVWAP.",
          "AI Forecast: Overlays Kronos neural 15-day cyan trajectory and 90% confidence corridor."
        ]
      },
      {
        heading: "3. Full-Screen Maximize Mode",
        description: "Click [ ⛶ Full Screen ] to expand both the stock chart and the RSI momentum graph across your entire display. Press 'Esc' or click 'Exit Fullscreen' to return.",
        tips: "In fullscreen mode, all indicator toggles and timeframe selectors remain directly accessible on the top floating bar."
      },
      {
        heading: "4. RSI(14) Momentum Subchart",
        description: "Synchronized subchart showing Relative Strength Index with Overbought (70), Midline (50), and Oversold (30) reference levels."
      }
    ],
    example: {
      title: "Chart Studio Overlay Playbook",
      text: "When analyzing a stock, toggle 'Vol Profile' and 'AVWAP'. If price is holding above the Gold POC line and bouncing off the Green Swing-Low AVWAP, the bulls have full control."
    }
  },

  journal: {
    title: "Simulated Paper Trading Journal",
    subtitle: "Professional trade management, live mark-to-market P&L, and R-multiple performance analytics.",
    summary: "The Paper Journal allows you to simulate and track swing trades in real-time with zero risk to actual capital. It automatically computes your Mark-to-Market P&L, Win Rate %, Profit Factor, and R-Multiple distribution.",
    sections: [
      {
        heading: "1. Portfolio Performance Header",
        description: "Live summary cards reflecting your overall simulated portfolio health:",
        bullets: [
          "Net Combined P&L: Total ₹ returns across closed and active open positions.",
          "Realized vs Unrealized P&L: Locked-in profits vs active floating returns.",
          "Win Rate %: Percentage of closed trades that hit profit targets.",
          "Profit Factor: Ratio of gross profits to gross losses (Target: > 1.8).",
          "Average R-Multiple: Average return generated per 1 unit of risk."
        ]
      },
      {
        heading: "2. Active Open Positions Table",
        description: "Tracks all live swing trades with real-time CMP updates, current P&L (₹ and %), progress toward Target 1 (2R) / Target 2 (3R), and Target/Stop Hit alert badges.",
        tips: "Click '[Close]' on any active trade to record your exit price and reason (Target 1, Target 2, Trailing Stop, or Manual Exit)."
      },
      {
        heading: "3. 1-Click Logging from Screener & Deep Scan",
        description: "You can log trades directly from the Live Screener match cards or Deep Scan hero cards with 1 click."
      }
    ],
    example: {
      title: "Paper Journal Best Practice",
      text: "Log 20 consecutive swing trades without altering your stop loss or exiting prematurely. Review your Profit Factor and Average R-Multiple after 20 trades to verify your quantitative edge."
    }
  },

  regime: {
    title: "Macro Market Regime & Volatility Intelligence",
    subtitle: "Market-wide gating engine protecting capital against high-volatility chop and downtrends.",
    summary: "The Macro Regime Engine evaluates NIFTY 50 moving averages, India VIX implied volatility, and market breadth to determine the optimal capital allocation across 4 distinct market regimes.",
    sections: [
      {
        heading: "1. The 4 Market Regimes",
        bullets: [
          "🟢 Risk-On Expansion (VIX < 14): Full 100% position sizing. Momentum breakouts and Stage-2 leader breakouts thrive.",
          "🟡 Selective Pullbacks (VIX 14–18): 75% standard sizing. Focus on 20/50 EMA pullbacks in high-relative-strength leaders.",
          "🟠 High Chop Mean-Reversion (VIX 18–22): 50% half sizing. Breakouts frequently fail; focus strictly on oversold Bollinger/RSI bounces.",
          "🔴 Capital Preservation (VIX > 22 or Downtrend): 25% defensive sizing or 100% cash. Strict trailing stops."
        ]
      },
      {
        heading: "2. India VIX Implied Daily Move",
        description: "Calculates the expected daily percentage fluctuation in the Nifty index (VIX / √252) to set proper stop loss buffer distances."
      },
      {
        heading: "3. Regime Capital Multiplier in Alpha Fusion",
        description: "When the market shifts into defensive regimes, the platform automatically scales down composite swing trade scores to keep you safe."
      }
    ],
    example: {
      title: "How to trade the regime",
      text: "If Top Header shows '🔴 Capital Preservation / Defensive', reduce your trade size to 25% of standard capital and avoid buying breakout setups until VIX cools down."
    }
  },

  risk: {
    title: "Risk & Position Sizing Calculator",
    subtitle: "Ed Thorp Half-Kelly and Fixed Fractional position sizing calculations.",
    summary: "Calculates the exact number of shares to purchase based on your total account capital, maximum risk percentage (e.g. 1%), entry price, and stop loss.",
    sections: [
      {
        heading: "1. Golden Rule of Capital Preservation",
        description: "Never risk more than 1% to 2% of your total account equity on a single swing trade.",
        tips: "Position Size = (Account Equity × Risk %) / (Entry Price - Stop Loss)"
      },
      {
        heading: "2. Half-Kelly Capital Sizing",
        description: "Dynamically sizes positions larger on high-probability, high-reward setups and smaller on speculative setups."
      }
    ],
    example: {
      title: "Position Sizing Example",
      text: "On a ₹10,00,000 account with 1% risk (₹10,000 max risk): Buying a stock at ₹500 with Stop Loss at ₹480 (₹20 risk/share) means you should buy exactly 500 shares (₹10,000 / ₹20)."
    }
  },

  backtest: {
    title: "Historical Backtest Studio",
    subtitle: "Institutional backtesting engine verifying empirical win rates and Sharpe ratios.",
    summary: "Simulates historical performance across 1–5 years of data for any stock and strategy combination, factoring in entry triggers, stop losses, and target exits.",
    sections: [
      {
        heading: "1. Key Performance Metrics",
        bullets: [
          "Win Rate %: Percentage of historical trades that reached target.",
          "Profit Factor: Gross profits divided by gross losses.",
          "Max Drawdown %: The deepest peak-to-trough decline experienced.",
          "Sharpe Ratio: Risk-adjusted return metric (> 1.2 is good)."
        ]
      }
    ],
    example: {
      title: "Backtest interpretation",
      text: "A strategy with 68% win rate, 2.4 Profit Factor, and 7% Max Drawdown indicates an institutional-grade quantitative edge."
    }
  },

  sectors: {
    title: "Sector Pulse & Rotation Matrix",
    subtitle: "Top-down institutional sector rotation, Mansfield RS, Hurst Memory ($H$), Markov Durations, and Constituent Merit Leaders.",
    summary: "Sector Pulse provides macroeconomic alpha by tracking institutional money flows across all NSE/US sectors. Over 70% of a stock's individual swing move is driven by its underlying sector trend.",
    sections: [
      {
        heading: "1. Mansfield Relative Strength (MRS & 5D Slope)",
        description: "Stan Weinstein's mathematical benchmark comparison vs Nifty 50:",
        bullets: [
          "Positive MRS (> 0%): Sector is outperforming the benchmark and attracting institutional capital inflows.",
          "5D Slope (Arrow Up/Down): Rate of change in relative strength over the past 5 sessions. An accelerating positive slope (+0.4) confirms fresh momentum rotation.",
          "Golden Rule: Exclusively initiate swing trades in sectors with Positive & Rising Mansfield RS. Never bottom-fish in sectors with negative MRS."
        ]
      },
      {
        heading: "2. Regime Forecast & Memory ($H$) (Deep Breakdown)",
        description: "Statistical time-series physics quantifying sector trend persistence and runway:",
        bullets: [
          "Hurst Exponent (H): Quantifies time-series memory. H > 0.55 indicates persistent trending behavior (breakout/trend strategies work with high win rates); H < 0.45 indicates noisy mean-reversion.",
          "Current Regime Age (Days): Number of consecutive sessions the sector has remained in its current trend state.",
          "Expected Total Run (Markov Duration): The mathematical expected run length calculated from historical Markov chain state-transition matrices.",
          "Estimated Runway (Days Remaining): Expected Total Days minus Current Age. Represents the remaining momentum runway before the sector is statistically expected to pause or rotate.",
          "Runway Interpretation: Runway > 15 Days = Fresh young trend (Green Light for aggressive trades); Runway < 5 Days = Late-stage trend (tighten stops, avoid new breakouts)."
        ]
      },
      {
        heading: "3. Exhaustion & Volatility Risk (Deep Breakdown)",
        description: "Multi-variable quantitative risk audit protecting capital from buying market tops:",
        bullets: [
          "Exhaustion Probability (Weibull Hazard Rate): The mathematical likelihood that the trend will terminate or correct sharply within 5 sessions. < 30% = Fresh/Safe; > 60% = High Fatigue Warning.",
          "Overextension Flag (> 3x ATR): Triggered when price extends > 3.0 standard ATRs away from the 50 EMA. Flags extreme elastic stretch where new entries have poor risk/reward.",
          "Trailing Stop Level: Volatility-adjusted floor price protecting accumulated sector gains. A daily close below this line invalidates the uptrend.",
          "ATR(14) Volatility: Daily Average True Range in index points used to size protective buffers."
        ]
      },
      {
        heading: "4. Ranked Constituent Leaders & Merit Score (0–100)",
        description: "Ranks every individual stock in the sector to surface true market leaders:",
        bullets: [
          "Merit Score (> 80): Combines stock-vs-sector relative strength, volume surge, and EMA stack. Pick top #1 or #2 ranked stocks.",
          "Stage 2 Bull Expansion: Exclusively buy stocks in Stan Weinstein Stage 2 markup.",
          "Active Setup Pill: Highlights stocks that currently trigger a verified quantitative strategy (e.g. Trend-Pullback, VCP Breakout)."
        ]
      }
    ],
    example: {
      title: "Real-World Sector Rotation Playbook",
      text: "NIFTY AUTO shows: Strong Uptrend, Mansfield RS = +4.8% (Rising), Hurst H = 0.62 (Persistent Memory), Age = 11 Days, Expected Run = 28 Days (17 Days Runway Remaining), Exhaustion = 24% (Low Risk), Normal Band. Interpretation: Top-priority sector for capital allocation. Expand constituent drawer, select #1 ranked COFORGE (Merit 92, Stage 2), and click 'Screen' to enter pullback setups."
    }
  },

  aiforecast: {
    title: "Kronos AI Forecaster Studio",
    subtitle: "Autoregressive neural time-series model predicting 15-day price trajectories and 90% confidence corridors.",
    summary: "Kronos AI uses state-of-the-art neural architecture to generate 20 Monte Carlo forward paths, calculating probability of upside and expected price corridors for any stock.",
    sections: [
      {
        heading: "1. Upside Probability % & Expected Target",
        description: "Calculates the mathematical likelihood of price trading higher over the next 15 sessions."
      },
      {
        heading: "2. 90% Confidence Corridor [P10, P90]",
        description: "Projects the outer volatility boundaries. If CMP trades near P10 with high Upside Probability, it signals an asymmetric risk/reward dip buy."
      },
      {
        heading: "3. Volatility Amplification & Risk Gating",
        description: "Measures whether the forecasted price path exhibits orderly or erratic dispersion."
      }
    ],
    example: {
      title: "AI Forecaster Example",
      text: "RELIANCE shows 72% Upside Probability with an expected 15-day target of ₹1,345 and a 90% corridor of ₹1,290–₹1,370."
    }
  },

  watchlists: {
    title: "Custom Watchlists Studio",
    subtitle: "Organize, monitor, and batch-scan custom stock universes.",
    summary: "Create and manage custom thematic watchlists (e.g. 'High-Growth Tech', 'Breakout Candidates', 'PSU Momentum') and scan them with 1 click.",
    sections: [
      {
        heading: "1. Create & Manage Watchlists",
        description: "Add or remove NSE/BSE tickers with instant autocomplete lookup."
      },
      {
        heading: "2. 1-Click Screener Launch",
        description: "Click 'Scan this Watchlist' to feed your custom tickers directly into the Live Screener."
      }
    ],
    example: {
      title: "Watchlist Workflow",
      text: "Add 15 momentum favorites into a 'Weekly Watch' list, then click 'Scan Watchlist' on Monday morning to find actionable setups."
    }
  },

  matrix: {
    title: "Strategy Guide & Matrix",
    subtitle: "Comprehensive playbook for all 12 quantitative swing trading strategies.",
    summary: "Detailed rules, indicators, mathematical formulas, and historical benchmarks for all 12 quantitative strategies built into SwingTradeDesk Pro.",
    sections: [
      {
        heading: "1. Strategy Categories",
        bullets: [
          "Trend Following: Trend-Pullback (20/50 EMA), GMMA Trend, VWAP Cross.",
          "Momentum Breakouts: VCP Breakout, 52-Week High Breakout, Squeeze Momentum.",
          "Mean Reversion: Bollinger Band Oversold, RSI(28) Macro Divergence, Elder Confluence."
        ]
      },
      {
        heading: "2. Direct Launch Buttons",
        description: "Click 'Launch Screener' or 'Run Backtest' on any strategy card to test it immediately."
      }
    ],
    example: {
      title: "Strategy Selection",
      text: "In Risk-On regimes, select VCP Breakout or 52W High Breakout. In Chop regimes, select RSI(28) Divergence or Mean Reversion."
    }
  }
};

export const STRATEGIES_PLAYBOOK = [
  {
    id: "trend_pullback",
    name: "Trend-Pullback (20/50 EMA)",
    category: "Trend Following",
    win_rate: "68% – 76%",
    holding: "5 – 12 Days",
    rr_target: "1:2.0 – 1:2.5",
    summary: "Buys orderly pullbacks to the rising 20 or 50 EMA in established Stage-2 uptrending market leaders.",
    entry_rule: "Price in strong uptrend (> 200 EMA) pulls back to touch 20/50 EMA with RSI(14) in 40–55 zone and prints a bullish reversal candle.",
    stop_rule: "Placed just below recent swing low or 1.5 × ATR(14) below entry.",
    target_rule: "Target 1 = 2.0R (Prior Swing High), Target 2 = 3.0R (Trailing Chandelier Exit)."
  },
  {
    id: "vcp_breakout",
    name: "Volatility Contraction Pattern (VCP)",
    category: "Momentum Breakout",
    win_rate: "64% – 72%",
    holding: "7 – 20 Days",
    rr_target: "1:2.5 – 1:3.5",
    summary: "Mark Minervini's signature institutional pattern where price swings contract progressively (e.g. 15% -> 8% -> 3%) before explosive breakout on volume.",
    entry_rule: "Daily close breaking above the final pivot resistance on volume > 150% of 20-day average.",
    stop_rule: "Below the low of the final tight contraction pivot (usually 3%–5% risk).",
    target_rule: "Target 1 = 2.5R, Target 2 = 3.5R."
  },
  {
    id: "high_52w_breakout",
    name: "52-Week High Breakout",
    category: "Momentum Breakout",
    win_rate: "62% – 70%",
    holding: "10 – 30 Days",
    rr_target: "1:2.5 – 1:4.0",
    summary: "Exploits the '52-week high effect' documented in empirical finance literature. Stocks crossing 52-week highs have zero overhead supply resistance.",
    entry_rule: "Daily close breaking above 52-week high with volume > 1.5x 20-day average.",
    stop_rule: "Close below breakout pivot or -2.0 × ATR(14).",
    target_rule: "Target 1 = 2.5R, Target 2 = Chandelier Trailing Exit."
  },
  {
    id: "connors_rsi2",
    name: "Connors RSI(2) Ultra-Mean Reversion",
    category: "Mean Reversion",
    win_rate: "74% – 81%",
    holding: "3 – 7 Days",
    rr_target: "1:1.5 – 1:2.0",
    summary: "Larry Connors' statistical edge capturing 2-day extreme panic drops (RSI_2 < 10) in verified macro uptrends (> 200 SMA).",
    entry_rule: "Price > 200 SMA + 2 consecutive down days + RSI(2) < 10 with bullish reversal intraday.",
    stop_rule: "Close - 2.0 × ATR(14) or recent swing low.",
    target_rule: "First close above 5-period SMA or 1:2 R:R."
  },
  {
    id: "volatility_squeeze",
    name: "TTM Volatility Squeeze Expansion",
    category: "Volatility Expansion",
    win_rate: "65% – 72%",
    holding: "5 – 15 Days",
    rr_target: "1:2.5 – 1:3.5",
    summary: "John Carter's coiled-spring setup where Bollinger Bands contract inside Keltner Channels before explosive directional momentum firing.",
    entry_rule: "Bollinger Bands expand outside Keltner Channels + MACD Histogram > 0 and expanding.",
    stop_rule: "Lowest low of the squeeze base.",
    target_rule: "Target 1 = 2.0R, Target 2 = 3.5R."
  },
  {
    id: "relative_strength_leader",
    name: "Mansfield Relative Strength Stage-2 Leader",
    category: "Relative Strength",
    win_rate: "67% – 74%",
    holding: "10 – 30 Days",
    rr_target: "1:2.5 – 1:4.0",
    summary: "Stan Weinstein Stage-2 breakout in stocks exhibiting severe positive relative strength outperformance compared to the NIFTY 500.",
    entry_rule: "Mansfield RS > 0 and rising + Price breaking out of a 4-week base with volume surge.",
    stop_rule: "Below base support level.",
    target_rule: "Target 1 = 2.5R, Target 2 = Chandelier Trailing Stop."
  },
  {
    id: "pocket_pivot",
    name: "Institutional Pocket Pivot",
    category: "Institutional Footprint",
    win_rate: "66% – 73%",
    holding: "5 – 15 Days",
    rr_target: "1:2.0 – 1:3.0",
    summary: "Gil Morales & Chris Kacher's early-entry footprint where volume on an up day exceeds the highest down-day volume of the prior 10 sessions while resting on 10/20 EMA.",
    entry_rule: "Price bounces off 10 or 20 EMA with volume higher than any down-volume day in past 10 sessions.",
    stop_rule: "Low of the pocket pivot candle.",
    target_rule: "Target 1 = 2.0R, Target 2 = 3.0R."
  },
  {
    id: "wyckoff_spring",
    name: "Wyckoff Spring Shakeout",
    category: "Smart Money Accumulation",
    win_rate: "65% – 72%",
    holding: "5 – 15 Days",
    rr_target: "1:2.5 – 1:3.5",
    summary: "Richard Wyckoff's classic smart-money trap where price briefly pierces support to trigger retail stop losses, then immediately reclaims the range.",
    entry_rule: "Price breaks below support level and closes back inside the trading range on the same or next bar.",
    stop_rule: "Low of the spring candle.",
    target_rule: "Target 1 = Middle of range, Target 2 = Upper range resistance."
  },
  {
    id: "nr7_expansion",
    name: "Toby Crabel NR7 Volatility Expansion",
    category: "Range Contraction",
    win_rate: "62% – 69%",
    holding: "3 – 8 Days",
    rr_target: "1:2.0 – 1:2.5",
    summary: "Toby Crabel's day of narrowest range of the last 7 sessions, signaling extreme volatility compression ready to expand.",
    entry_rule: "Buy stop order placed 1 tick above the high of the NR7 candle in an established uptrend.",
    stop_rule: "1 tick below the low of the NR7 candle.",
    target_rule: "Target 1 = 2.0R, Target 2 = 2.5R."
  },
  {
    id: "gmma_breakout",
    name: "Guppy Multiple Moving Average (GMMA)",
    category: "Trend Following",
    win_rate: "65% – 71%",
    holding: "7 – 20 Days",
    rr_target: "1:2.5 – 1:3.5",
    summary: "Daryl Guppy's 12-EMA system separating short-term trader sentiment (3,5,8,10,12,15 EMAs) from long-term institutional investors (30,35,40,45,50,60 EMAs).",
    entry_rule: "Short-term trader group expands and breaks cleanly above the long-term investor group.",
    stop_rule: "Lowest EMA of the investor group (60 EMA).",
    target_rule: "Target 1 = 2.5R, Target 2 = 3.5R."
  },
  {
    id: "rsi28_divergence",
    name: "RSI(28) Momentum Divergence",
    category: "Momentum Reversal",
    win_rate: "64% – 70%",
    holding: "5 – 12 Days",
    rr_target: "1:2.0 – 1:3.0",
    summary: "Identifies hidden institutional accumulation where price makes an equal or lower low while RSI(28) forms a distinct higher low.",
    entry_rule: "Bullish divergence confirmed by price reclaiming 10 EMA with expanding volume.",
    stop_rule: "Lowest price low of the divergence pattern.",
    target_rule: "Target 1 = 20 SMA, Target 2 = 2.0R."
  },
  {
    id: "mean_reversion",
    name: "Mean Reversion (Bollinger + RSI)",
    category: "Mean Reversion",
    win_rate: "60% – 68%",
    holding: "3 – 7 Days",
    rr_target: "1:1.5 – 1:2.0",
    summary: "Extreme 2-sigma statistical price deviation beyond the Lower Bollinger Band snapping back to equilibrium moving averages.",
    entry_rule: "Price pierces Lower Bollinger Band with RSI(14) <= 35 and prints a bullish rejection candle.",
    stop_rule: "Low of the rejection candle - 0.5 × ATR(14).",
    target_rule: "Target 1 = 20 SMA Middle Band, Target 2 = Upper Bollinger Band."
  }
];
