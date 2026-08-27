import React, { useState } from 'react';
import { 
  BookOpen, 
  ExternalLink, 
  TrendingUp, 
  Layers, 
  Award, 
  ShieldCheck, 
  Clock, 
  Zap, 
  Target,
  BarChart3,
  CheckCircle2,
  Info
} from 'lucide-react';

const STRATEGIES_DATA = [
  {
    id: "connors_rsi2",
    name: "Connors RSI(2) Ultra-Mean Reversion",
    research_basis: "Larry Connors & Cesar Alvarez (2009) — Short Term Trading Strategies That Work",
    empirical_edge: "Exploits short-term 2-day panic pullbacks (RSI_2 < 10) in verified >200 SMA macro uptrends for sharp, high-probability snapbacks.",
    win_rate: "74% – 81%",
    win_rate_val: 78,
    sharpe: "1.5 – 1.9",
    holding: "3 – 7 Days",
    rr_target: "1:1.5 – 1:2.0",
    trend_filter: "Price > 200 SMA (Strict macro uptrend filter)",
    entry_trigger: "RSI(2) < 10 with 2+ consecutive down days and bullish reversal bounce",
    stop_loss: "Close - 2.0 x ATR(14) or recent swing low",
    profit_exit: "First close above 5-period SMA or 1:2 R:R target",
    color: "from-emerald-500/20 to-teal-500/10",
    badge_color: "text-emerald-400 bg-emerald-500/10 border-emerald-500/30"
  },
  {
    id: "volatility_squeeze",
    name: "TTM Volatility Squeeze Expansion",
    research_basis: "John Carter (2007) — Mastering the Trade / Volatility Regime Models",
    empirical_edge: "Bollinger Bands contract inside Keltner Channels (coiled spring) before explosive directional momentum expansion with accelerating MACD.",
    win_rate: "65% – 72%",
    win_rate_val: 68,
    sharpe: "1.4 – 1.8",
    holding: "5 – 15 Days",
    rr_target: "1:2.5 – 1:3.5",
    trend_filter: "Price > 200 EMA and 20 EMA > 50 EMA",
    entry_trigger: "Bollinger Bands expand outside Keltner Channels + MACD Histogram > 0 and increasing",
    stop_loss: "Lowest low of the squeeze base or Close - 1.5 x ATR(14)",
    profit_exit: "Target 1 = 2.0R (1:2), Target 2 = 3.5R (1:3.5)",
    color: "from-cyan-500/20 to-blue-500/10",
    badge_color: "text-cyan-400 bg-cyan-500/10 border-cyan-500/30"
  },
  {
    id: "mean_reversion",
    name: "Mean Reversion (Bollinger + RSI)",
    research_basis: "John Bollinger (2001) / Statistical Arbitrage Literature",
    empirical_edge: "Extreme 2-sigma statistical price deviation beyond lower Bollinger Band snaps back to historical moving average equilibrium.",
    win_rate: "60% – 68%",
    win_rate_val: 64,
    sharpe: "1.2 – 1.4",
    holding: "3 – 7 Days",
    rr_target: "1:1.5 – 1:2.0",
    trend_filter: "Liquid universe with active ATR volatility",
    entry_trigger: "Price pierces Lower Bollinger Band with RSI(14) <= 35 and bullish rejection candle",
    stop_loss: "Candle Low - 0.5 x ATR(14)",
    profit_exit: "Target 1 = 20 SMA Middle Band, Target 2 = Upper Bollinger Band",
    color: "from-blue-500/20 to-indigo-500/10",
    badge_color: "text-blue-400 bg-blue-500/10 border-blue-500/30"
  },
  {
    id: "relative_strength_leader",
    name: "Mansfield Relative Strength Stage-2 Leader",
    research_basis: "Stan Weinstein (1988) — Stage Analysis / Gary Antonacci — Dual Momentum (2014)",
    empirical_edge: "Institutional capital concentration in market leaders outperforming the Nifty 50 benchmark breaking out to new 20D/52W highs.",
    win_rate: "58% – 66%",
    win_rate_val: 62,
    sharpe: "1.6 – 2.1",
    holding: "10 – 30 Days",
    rr_target: "1:2.5 – 1:4.0+",
    trend_filter: "Close > 20 EMA > 50 EMA > 200 EMA (Stage-2 Markup)",
    entry_trigger: "20-Day / 52-Week High Breakout on >= 1.3x institutional volume surge",
    stop_loss: "20 EMA or 10-day swing low",
    profit_exit: "Target 1 = +12%, Target 2 = Trailing 20 EMA",
    color: "from-purple-500/20 to-pink-500/10",
    badge_color: "text-purple-400 bg-purple-500/10 border-purple-500/30"
  },
  {
    id: "trend_pullback",
    name: "Trend-Pullback (20/50 EMA)",
    research_basis: "Moving Average Envelopes & Trend Following (Fama-French, Moskowitz)",
    empirical_edge: "Entering high-momentum macro uptrends during temporary low-volume pullbacks to rising 20 EMA offers low risk entries with 1:2+ payout.",
    win_rate: "48% – 56%",
    win_rate_val: 52,
    sharpe: "1.2 – 1.5",
    holding: "5 – 12 Days",
    rr_target: "1:2.0 – 1:3.0",
    trend_filter: "Price > 200 EMA and 20 EMA > 50 EMA",
    entry_trigger: "Pullback within 1% of 20 EMA with bullish candlestick and 40 <= RSI <= 65",
    stop_loss: "Below 50 EMA or recent swing low",
    profit_exit: "Target 1 = 2.0R (1:2), Target 2 = 3.0R (1:3)",
    color: "from-amber-500/20 to-orange-500/10",
    badge_color: "text-amber-400 bg-amber-500/10 border-amber-500/30"
  },
  {
    id: "vcp_breakout",
    name: "VCP & Base Breakout",
    research_basis: "Mark Minervini — Trade Like a Stock Market Wizard (SEPA Model)",
    empirical_edge: "Progressive reduction in volatility dries up overhead supply float before institutional demand creates explosive upward re-rating.",
    win_rate: "38% – 46%",
    win_rate_val: 42,
    sharpe: "1.3 – 1.6",
    holding: "7 – 20 Days",
    rr_target: "1:2.5 – 1:3.5",
    trend_filter: "Contraction volatility <= 75% across 2 to 4 consecutive tighter price waves",
    entry_trigger: "20-day high resistance breakout on >= 1.4x volume surge",
    stop_loss: "Pivot low of final contraction wave",
    profit_exit: "Target 1 = 2.5R, Target 2 = 3.5R",
    color: "from-rose-500/20 to-red-500/10",
    badge_color: "text-rose-400 bg-rose-500/10 border-rose-500/30"
  },
  {
    id: "gmma_breakout",
    name: "GMMA Weekly Multi-Timeframe Breakout",
    research_basis: "Daryl Guppy (2004) — Trend Trading / Guppy Multiple Moving Averages",
    empirical_edge: "Aligns Weekly institutional investor ribbon (30-60 EMA) expansion with daily volume-backed breakouts to ride high-momentum multi-week Stage 2 markup runners.",
    win_rate: "54% – 62%",
    win_rate_val: 58,
    sharpe: "1.5 – 1.9",
    holding: "10 – 30 Days",
    rr_target: "1:2.5 – 1:4.0",
    trend_filter: "Weekly Slow Investor Ribbon (30, 35, 40, 45, 50, 60 EMA) expanding upward + Fast Ribbon above Slow",
    entry_trigger: "Daily breakout above 20D pivot on >= 1.3x institutional volume surge",
    stop_loss: "Below top of Slow Investor Ribbon or 10-day swing low",
    profit_exit: "Target 1 = 2.5R, Target 2 = 4.0R (Trailing Slow Ribbon)",
    color: "from-cyan-500/20 to-purple-500/10",
    badge_color: "text-cyan-300 bg-cyan-500/10 border-cyan-500/30"
  },
  {
    id: "high_52w_breakout",
    name: "52-Week High Breakout (George & Hwang / SEPA)",
    research_basis: "Thomas J. George & Chuan-Yang Hwang (2004) — Journal of Finance / Mark Minervini SEPA",
    empirical_edge: "Exploits the 52-week high anomaly where zero overhead supply allows leading equities emerging from tight consolidation bases to enter unconstrained price discovery.",
    win_rate: "52% – 60%",
    win_rate_val: 56,
    sharpe: "1.6 – 2.0",
    holding: "10 – 45 Days",
    rr_target: "1:2.5 – 1:4.0+",
    trend_filter: "Stage-2 Bull Structure: Close > 50 EMA > 200 EMA with tight base (<= 15% depth)",
    entry_trigger: "Daily close breaking prior 52-Week High resistance on >= 1.4x institutional volume surge",
    stop_loss: "Pivot low of the consolidation base or 20 EMA - 0.5 ATR",
    profit_exit: "Target 1 = 2.5R, Target 2 = 4.0R (Trailing 20/50 EMA)",
    color: "from-emerald-500/20 to-blue-500/10",
    badge_color: "text-emerald-300 bg-emerald-500/10 border-emerald-500/30"
  },
  {
    id: "rsi28_divergence",
    name: "RSI(28) Momentum Divergence Reversal",
    research_basis: "J. Welles Wilder (1978) Lunar Cycle Model / Quantitative Divergence Studies",
    empirical_edge: "Filters out false short-term noise with a smoothed 28-period oscillator. When price creates lower lows while RSI(28) builds distinct higher lows, it marks structural multi-week selling exhaustion.",
    win_rate: "56% – 64%",
    win_rate_val: 60,
    sharpe: "1.4 – 1.8",
    holding: "7 – 25 Days",
    rr_target: "1:2.0 – 1:3.5",
    trend_filter: "Oversold/neutral value zone (RSI_28 <= 52) with confirmed double swing low pivot",
    entry_trigger: "Bullish reversal bounce candle confirming higher low on RSI(28) while price tests lower low",
    stop_loss: "Below the second swing low pivot - 0.5 x ATR(14)",
    profit_exit: "Target 1 = 2.0R (50 EMA mean reversion), Target 2 = 3.5R",
    color: "from-indigo-500/20 to-teal-500/10",
    badge_color: "text-indigo-300 bg-indigo-500/10 border-indigo-500/30"
  },
  {
    id: "pocket_pivot",
    name: "Institutional Pocket Pivot (Morales & Kacher)",
    research_basis: "Gil Morales & Chris Kacher (2010) — Trade Like an O'Neil Disciple",
    empirical_edge: "Identifies early inside-the-base volume accumulation where volume on an upward bounce off the 10/20/50 EMA exceeds the maximum down-volume of the prior 10 sessions, entering before classical 52W/VCP breakouts.",
    win_rate: "55% – 63%",
    win_rate_val: 59,
    sharpe: "1.7 – 2.2",
    holding: "7 – 25 Days",
    rr_target: "1:2.5 – 1:4.5+",
    trend_filter: "Stage-2 Bull Base: Price > 50 EMA inside constructive base (<= 22% depth)",
    entry_trigger: "Volume > max down-volume of past 10 days on bounce off 10/20/50 EMA with green candle",
    stop_loss: "Lowest low of past 5 days or 20 EMA - 0.4 ATR",
    profit_exit: "Target 1 = 2.5R (Base resistance), Target 2 = 4.5R (Breakout runner)",
    color: "from-emerald-500/20 to-cyan-500/10",
    badge_color: "text-emerald-400 bg-emerald-500/10 border-emerald-500/30"
  },
  {
    id: "wyckoff_spring",
    name: "Wyckoff Spring Shakeout (VPA)",
    research_basis: "Richard D. Wyckoff (1931) / Tom Williams — Master the Markets (Volume Spread Analysis)",
    empirical_edge: "Exploits institutional liquidity sweeps and stop hunts. Price briefly pierces 20-day support to trap bears before immediately rejecting with a hammer tail back inside the trading range.",
    win_rate: "58% – 66%",
    win_rate_val: 62,
    sharpe: "1.5 – 1.9",
    holding: "5 – 15 Days",
    rr_target: "1:2.0 – 1:3.5",
    trend_filter: "Consolidation trading range with clear 20-day support floor",
    entry_trigger: "Daily low pierces support floor but closes in upper 50%+ of candle with bullish absorption",
    stop_loss: "Spring Low tail - 0.5 x ATR(14)",
    profit_exit: "Target 1 = 2.0R (Range ceiling), Target 2 = 3.5R (Stage 2 continuation)",
    color: "from-amber-500/20 to-rose-500/10",
    badge_color: "text-amber-400 bg-amber-500/10 border-amber-500/30"
  },
  {
    id: "nr7_expansion",
    name: "Toby Crabel NR7 Volatility Expansion",
    research_basis: "Toby Crabel (1990) — Day Trading with Short Term Price Patterns",
    empirical_edge: "Captures explosive directional momentum out of extreme 7-day narrow range compression (NR7) coils within confirmed Stage 2 uptrends.",
    win_rate: "62% – 68%",
    win_rate_val: 65,
    sharpe: "1.4 – 1.8",
    holding: "3 – 8 Days",
    rr_target: "1:2.0 – 1:3.0",
    trend_filter: "Stage-2 Trend: Close > 50 EMA and Close > 20 EMA",
    entry_trigger: "Daily High-Low range is narrowest of last 7 days (<= 0.85 ATR) with bullish close",
    stop_loss: "Below low of NR7 compression bar - 0.35 x ATR(14)",
    profit_exit: "Target 1 = 2.0R, Target 2 = 3.0R (Rapid volatility expansion)",
    color: "from-violet-500/20 to-blue-500/10",
    badge_color: "text-violet-400 bg-violet-500/10 border-violet-500/30"
  }
];

export default function StrategyGuideView({ onLaunchScreener, onLaunchBacktest }) {
  const [selectedStrategy, setSelectedStrategy] = useState(STRATEGIES_DATA[0]);

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="bg-gradient-to-r from-[#0e172a] via-[#0b1324] to-[#080d1a] border border-cyan-500/20 rounded-2xl p-6 shadow-xl relative overflow-hidden">
        <div className="absolute -right-12 -top-12 w-64 h-64 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none"></div>
        <div className="relative z-10 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div>
            <div className="flex items-center space-x-2.5">
              <div className="w-10 h-10 rounded-xl bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center text-cyan-400 shadow-md">
                <BookOpen className="w-5 h-5" />
              </div>
              <div>
                <h1 className="text-xl sm:text-2xl font-bold text-white tracking-tight flex items-center gap-2">
                  Quantitative Strategy Matrix
                  <span className="text-xs px-2 py-0.5 rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 font-mono font-semibold uppercase">
                    Research Lab
                  </span>
                </h1>
                <p className="text-xs sm:text-sm text-gray-400 mt-0.5">
                  Academic foundations, mathematical rules, statistical win rates, and holding parameters by <a href="https://www.rupeemap.in" target="_blank" rel="noopener noreferrer" className="text-cyan-400 font-medium hover:underline hover:text-cyan-300 transition-colors">rupeemap.in labs</a> (by <strong className="text-gray-300 font-medium">Sandesh Rathi</strong>).
                </p>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className="bg-gray-900/80 border border-gray-800 rounded-xl px-4 py-2 text-right">
              <div className="text-[10px] text-gray-400 uppercase font-mono tracking-wider">Implemented Models</div>
              <div className="text-lg font-bold text-cyan-400 font-mono">{STRATEGIES_DATA.length} Strategies Active</div>
            </div>
          </div>
        </div>
      </div>

      {/* Main Research Comparison Table Card */}
      <div className="bg-gray-900/70 border border-gray-800 rounded-2xl shadow-xl overflow-hidden backdrop-blur-sm">
        <div className="px-6 py-4 border-b border-gray-800 bg-gray-950/60 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Award className="w-4 h-4 text-cyan-400" />
            <h2 className="text-sm font-bold text-gray-200 uppercase tracking-wider font-mono">
              Academic & Empirical Performance Comparison
            </h2>
          </div>
          <span className="text-xs text-gray-500 hidden sm:inline font-mono">Click any row to view deep rules</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs sm:text-sm">
            <thead className="bg-gray-950/80 text-[11px] text-gray-400 uppercase font-mono border-b border-gray-800 tracking-wider">
              <tr>
                <th className="py-3.5 px-5 font-semibold">Strategy</th>
                <th className="py-3.5 px-5 font-semibold">Research Basis</th>
                <th className="py-3.5 px-5 font-semibold hidden md:table-cell">Empirical Edge</th>
                <th className="py-3.5 px-5 font-semibold text-center">Win Rate</th>
                <th className="py-3.5 px-5 font-semibold text-center">Sharpe</th>
                <th className="py-3.5 px-5 font-semibold text-center">Holding</th>
                <th className="py-3.5 px-5 font-semibold text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-800/60 text-gray-300">
              {STRATEGIES_DATA.map((item) => {
                const isSelected = selectedStrategy.id === item.id;
                return (
                  <tr 
                    key={item.id}
                    onClick={() => setSelectedStrategy(item)}
                    className={`cursor-pointer transition-all duration-150 ${
                      isSelected 
                        ? 'bg-cyan-500/10 text-white font-medium border-l-4 border-l-cyan-400' 
                        : 'hover:bg-gray-800/40 hover:text-gray-100'
                    }`}
                  >
                    <td className="py-4 px-5">
                      <div className="font-semibold text-gray-100 flex items-center gap-2">
                        <span>{item.name}</span>
                        {item.id === "connors_rsi2" && (
                          <span className="text-[10px] px-1.5 py-0.2 rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 font-mono">
                            Highest Win Rate
                          </span>
                        )}
                        {item.id === "relative_strength_leader" && (
                          <span className="text-[10px] px-1.5 py-0.2 rounded bg-purple-500/20 text-purple-300 border border-purple-500/30 font-mono">
                            Highest Sharpe
                          </span>
                        )}
                      </div>
                      <div className="text-[11px] text-gray-400 font-mono mt-0.5">{item.id}</div>
                    </td>

                    <td className="py-4 px-5 text-xs text-gray-300 max-w-xs">
                      {item.research_basis}
                    </td>

                    <td className="py-4 px-5 text-xs text-gray-400 max-w-sm hidden md:table-cell leading-relaxed">
                      {item.empirical_edge}
                    </td>

                    <td className="py-4 px-5 text-center font-mono">
                      <span className="inline-block px-2 py-0.5 rounded-md font-bold text-xs bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                        {item.win_rate}
                      </span>
                    </td>

                    <td className="py-4 px-5 text-center font-mono font-bold text-cyan-400">
                      {item.sharpe}
                    </td>

                    <td className="py-4 px-5 text-center font-mono text-xs text-gray-300 whitespace-nowrap">
                      {item.holding}
                    </td>

                    <td className="py-4 px-5 text-right whitespace-nowrap" onClick={(e) => e.stopPropagation()}>
                      <div className="flex items-center justify-end space-x-1.5">
                        <button
                          onClick={() => onLaunchScreener && onLaunchScreener(item.id)}
                          title="Scan market with this strategy"
                          className="px-2.5 py-1 rounded-lg bg-gray-800 hover:bg-cyan-500/20 hover:text-cyan-300 text-gray-300 border border-gray-700 text-xs font-mono transition-colors flex items-center gap-1"
                        >
                          <Layers className="w-3.5 h-3.5 text-cyan-400" />
                          <span>Scan</span>
                        </button>
                        <button
                          onClick={() => onLaunchBacktest && onLaunchBacktest(item.id)}
                          title="Backtest this strategy"
                          className="px-2.5 py-1 rounded-lg bg-gray-800 hover:bg-indigo-500/20 hover:text-indigo-300 text-gray-300 border border-gray-700 text-xs font-mono transition-colors flex items-center gap-1"
                        >
                          <BarChart3 className="w-3.5 h-3.5 text-indigo-400" />
                          <span>Backtest</span>
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Selected Strategy Deep-Dive Details Card */}
      {selectedStrategy && (
        <div className="bg-gray-900/80 border border-cyan-500/30 rounded-2xl p-6 shadow-2xl space-y-6">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-4 border-b border-gray-800">
            <div>
              <div className="flex items-center space-x-2">
                <span className={`text-xs px-2.5 py-0.5 rounded-full border font-mono font-bold uppercase ${selectedStrategy.badge_color}`}>
                  Selected Strategy Profile
                </span>
                <span className="text-xs text-gray-400 font-mono">{selectedStrategy.id}</span>
              </div>
              <h3 className="text-xl font-bold text-white mt-1">{selectedStrategy.name}</h3>
              <p className="text-xs sm:text-sm text-gray-300 mt-1">{selectedStrategy.research_basis}</p>
            </div>

            <div className="flex items-center gap-3">
              <button
                onClick={() => onLaunchScreener && onLaunchScreener(selectedStrategy.id)}
                className="px-4 py-2 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white font-medium text-xs sm:text-sm flex items-center gap-2 shadow-lg shadow-cyan-600/20 transition-all"
              >
                <Zap className="w-4 h-4" />
                <span>⚡ Run Live Screener</span>
              </button>
              <button
                onClick={() => onLaunchBacktest && onLaunchBacktest(selectedStrategy.id)}
                className="px-4 py-2 rounded-xl bg-gray-800 hover:bg-gray-700 text-gray-200 border border-gray-700 font-medium text-xs sm:text-sm flex items-center gap-2 transition-all"
              >
                <TrendingUp className="w-4 h-4 text-cyan-400" />
                <span>Simulate in Backtester</span>
              </button>
            </div>
          </div>

          {/* Quick Metrics Grid */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3.5">
            <div className="bg-gray-950/70 border border-gray-800 rounded-xl p-3.5">
              <div className="text-[11px] text-gray-400 uppercase font-mono">Statistical Win Rate</div>
              <div className="text-lg font-bold text-emerald-400 font-mono mt-0.5">{selectedStrategy.win_rate}</div>
              <div className="text-[10px] text-gray-500 mt-0.5">Empirical historical tests</div>
            </div>

            <div className="bg-gray-950/70 border border-gray-800 rounded-xl p-3.5">
              <div className="text-[11px] text-gray-400 uppercase font-mono">Sharpe Ratio</div>
              <div className="text-lg font-bold text-cyan-400 font-mono mt-0.5">{selectedStrategy.sharpe}</div>
              <div className="text-[10px] text-gray-500 mt-0.5">Risk-adjusted return</div>
            </div>

            <div className="bg-gray-950/70 border border-gray-800 rounded-xl p-3.5">
              <div className="text-[11px] text-gray-400 uppercase font-mono">Target R:R Ratio</div>
              <div className="text-lg font-bold text-indigo-400 font-mono mt-0.5">{selectedStrategy.rr_target}</div>
              <div className="text-[10px] text-gray-500 mt-0.5">Reward to Risk payout</div>
            </div>

            <div className="bg-gray-950/70 border border-gray-800 rounded-xl p-3.5">
              <div className="text-[11px] text-gray-400 uppercase font-mono">Average Holding</div>
              <div className="text-lg font-bold text-amber-400 font-mono mt-0.5">{selectedStrategy.holding}</div>
              <div className="text-[10px] text-gray-500 mt-0.5">Swing trade lifecycle</div>
            </div>
          </div>

          {/* Detailed Rules & Logic */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="bg-gray-950/60 border border-gray-800/80 rounded-xl p-4 space-y-3">
              <div className="flex items-center space-x-2 text-cyan-400 text-xs font-bold uppercase font-mono">
                <Target className="w-4 h-4" />
                <span>Entry Rules & Setup Criteria</span>
              </div>
              
              <div className="space-y-2.5 text-xs text-gray-300">
                <div>
                  <span className="text-gray-400 font-mono block text-[11px] uppercase">Macro Trend Filter:</span>
                  <p className="font-mono text-gray-200 mt-0.5">{selectedStrategy.trend_filter}</p>
                </div>
                <div>
                  <span className="text-gray-400 font-mono block text-[11px] uppercase">Trigger Condition:</span>
                  <p className="font-mono text-cyan-300 mt-0.5">{selectedStrategy.entry_trigger}</p>
                </div>
                <div>
                  <span className="text-gray-400 font-mono block text-[11px] uppercase">Empirical Rationale:</span>
                  <p className="text-gray-300 mt-0.5 leading-relaxed">{selectedStrategy.empirical_edge}</p>
                </div>
              </div>
            </div>

            <div className="bg-gray-950/60 border border-gray-800/80 rounded-xl p-4 space-y-3">
              <div className="flex items-center space-x-2 text-rose-400 text-xs font-bold uppercase font-mono">
                <ShieldCheck className="w-4 h-4" />
                <span>Risk Management & Exits</span>
              </div>
              
              <div className="space-y-2.5 text-xs text-gray-300">
                <div>
                  <span className="text-gray-400 font-mono block text-[11px] uppercase">Stop Loss Placement:</span>
                  <p className="font-mono text-rose-300 mt-0.5">{selectedStrategy.stop_loss}</p>
                </div>
                <div>
                  <span className="text-gray-400 font-mono block text-[11px] uppercase">Profit Targets & Exits:</span>
                  <p className="font-mono text-emerald-300 mt-0.5">{selectedStrategy.profit_exit}</p>
                </div>
                <div>
                  <span className="text-gray-400 font-mono block text-[11px] uppercase">Execution Note:</span>
                  <p className="text-gray-400 mt-0.5 leading-relaxed">
                    Positions are automatically sized using Fixed Fractional 1.0% equity risk per trade.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
