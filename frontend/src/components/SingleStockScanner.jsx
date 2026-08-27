import React, { useState, useEffect } from 'react';
import { 
  RefreshCw, 
  TrendingUp, 
  ShieldCheck, 
  BarChart2, 
  Activity, 
  AlertCircle, 
  Sparkles, 
  Zap, 
  ArrowUpRight, 
  ArrowDownRight, 
  Clock, 
  Layers, 
  Award,
  Search,
  Building2
} from 'lucide-react';
import { fetchDeepScan, searchStocks, fetchAIForecast } from '../services/api';
import StockSearchInput from './StockSearchInput';

const fmt = (v, d = 2) => {
  if (typeof v === 'number' && !isNaN(v)) return v.toFixed(d);
  if (typeof v === 'string' && !isNaN(Number(v))) return Number(v).toFixed(d);
  return '—';
};

const POPULAR_STOCKS = [
  { symbol: "RELIANCE.NS", name: "Reliance Industries" },
  { symbol: "SBIN.NS", name: "State Bank of India" },
  { symbol: "HDFCBANK.NS", name: "HDFC Bank" },
  { symbol: "INFY.NS", name: "Infosys" },
  { symbol: "TCS.NS", name: "Tata Consultancy Services" },
  { symbol: "LT.NS", name: "Larsen & Toubro" },
  { symbol: "ITC.NS", name: "ITC Ltd" },
  { symbol: "BAJFINANCE.NS", name: "Bajaj Finance" }
];

export default function SingleStockScanner({ 
  initialTicker = "", 
  onOpenChart, 
  onOpenAIForecast,
  onOpenBacktest, 
  onOpenRisk 
}) {
  const [ticker, setTicker] = useState(initialTicker || "");
  const [capital, setCapital] = useState(500000);
  const [riskPct, setRiskPct] = useState(1.0);
  const [period, setPeriod] = useState("2y");
  
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState(null);
  const [reboundSuggestions, setReboundSuggestions] = useState([]);
  
  const [aiForecast, setAiForecast] = useState(null);
  const [aiLoading, setAiLoading] = useState(false);

  useEffect(() => {
    if (initialTicker && initialTicker.trim()) {
      setTicker(initialTicker);
      runScan(initialTicker, capital, riskPct);
    }
  }, [initialTicker]);

  const runScan = async (symToScan, capVal, riskVal) => {
    if (!symToScan || !symToScan.trim()) return;
    setLoading(true);
    setErrorMsg(null);
    setReboundSuggestions([]);
    setAiForecast(null);

    try {
      let sym = symToScan.trim();
      const res = await fetchDeepScan(sym, period, capVal, riskVal);
      setData(res);
      setTicker(res.ticker);

      // Auto-trigger Kronos Foundation Model forward pass
      setAiLoading(true);
      fetchAIForecast(res.ticker, 15, 20, "mini")
        .then(aiData => setAiForecast(aiData))
        .catch(() => setAiForecast(null))
        .finally(() => setAiLoading(false));

    } catch (err) {
      setErrorMsg(err.message || `Could not run deep scan on '${symToScan}'`);
      try {
        const suggestions = await searchStocks(symToScan);
        setReboundSuggestions(suggestions);
      } catch (e) {}
    } finally {
      setLoading(false);
    }
  };

  const handleSelectStock = (selectedSym, stockObj) => {
    setTicker(selectedSym);
    setErrorMsg(null);
    setReboundSuggestions([]);
    runScan(selectedSym, capital, riskPct);
  };

  const handleCapitalChange = (newCap, newRisk) => {
    setCapital(newCap);
    setRiskPct(newRisk);
    if (ticker) {
      runScan(ticker, newCap, newRisk);
    }
  };

  return (
    <div className="space-y-6">
      
      {/* Top Banner & Search - Note: overflow-visible allows autocomplete dropdown to float over everything */}
      <div className="bg-gradient-to-r from-gray-900 via-[#131b2e] to-gray-900 p-6 rounded-2xl border border-gray-800 shadow-xl relative overflow-visible">
        <div className="relative z-10 space-y-4">
          
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
              <div className="flex items-center space-x-2">
                <span className="px-2.5 py-0.5 rounded-full bg-cyan-500/10 text-cyan-400 text-xs font-semibold uppercase tracking-wider border border-cyan-500/20 flex items-center gap-1.5">
                  <Zap className="w-3.5 h-3.5" /> Quantitative Deep-Scan
                </span>
                <span className="text-xs text-gray-400">• Single Stock Technical Profiler</span>
              </div>
              <h1 className="text-2xl font-bold text-white tracking-tight mt-1.5">
                Single Stock Comprehensive Analyzer
              </h1>
              <p className="text-xs text-gray-300 max-w-2xl mt-1">
                Evaluate moving average alignment, volatility, RSI momentum, multi-strategy setup triggers, 2-year backtest stats, and exact position sizing for any stock.
              </p>
            </div>

            <div className="flex items-center space-x-2">
              {data && (
                <>
                  <button
                    onClick={() => onOpenChart && onOpenChart(data.ticker)}
                    className="flex items-center space-x-1.5 px-3.5 py-2 bg-gray-800 hover:bg-gray-700 text-cyan-300 border border-gray-700 hover:border-cyan-500/50 rounded-xl text-xs font-semibold transition-colors"
                  >
                    <BarChart2 className="w-4 h-4" />
                    <span>View Chart</span>
                  </button>

                  <button
                    onClick={() => onOpenAIForecast && onOpenAIForecast(data.ticker)}
                    className="flex items-center space-x-1.5 px-3.5 py-2 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white rounded-xl text-xs font-bold shadow-md transition-all"
                  >
                    <Sparkles className="w-4 h-4" />
                    <span>🔮 AI Forecast</span>
                  </button>

                  <button
                    onClick={() => onOpenBacktest && onOpenBacktest(data.ticker, data.active_setup?.strategy_id || 'trend_pullback')}
                    className="flex items-center space-x-1.5 px-3.5 py-2 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white rounded-xl text-xs font-semibold shadow-md transition-all"
                  >
                    <TrendingUp className="w-4 h-4" />
                    <span>Full Backtest</span>
                  </button>
                </>
              )}
            </div>
          </div>

          {/* Autocomplete Search Box */}
          <div className="pt-2 flex flex-col sm:flex-row gap-3">
            <StockSearchInput
              value={ticker}
              onSelectStock={handleSelectStock}
              placeholder="Search stock symbol or natural name (e.g. Reliance, Tata Motors, State Bank, HDFC)..."
              className="flex-1"
            />
            <button
              onClick={() => runScan(ticker, capital, riskPct)}
              disabled={loading || !ticker.trim()}
              className="px-6 py-2.5 bg-cyan-500 hover:bg-cyan-400 disabled:opacity-50 text-gray-950 font-bold text-xs rounded-xl shadow-lg transition-all flex items-center justify-center space-x-2 flex-shrink-0"
            >
              {loading ? <RefreshCw className="w-4 h-4 animate-spin text-gray-950" /> : <Sparkles className="w-4 h-4" />}
              <span>{loading ? "Analyzing..." : "Run Deep Scan"}</span>
            </button>
          </div>

        </div>
      </div>

      {/* Error & Rebound Suggestions Banner */}
      {errorMsg && (
        <div className="p-4 bg-red-950/40 border border-red-800/80 rounded-xl space-y-3">
          <div className="flex items-center space-x-2 text-red-300 text-xs font-semibold">
            <AlertCircle className="w-4 h-4 text-red-400 flex-shrink-0" />
            <span>{errorMsg}</span>
          </div>

          {reboundSuggestions.length > 0 && (
            <div className="pt-2 border-t border-red-900/40 space-y-2">
              <span className="text-xs font-semibold text-gray-300 flex items-center gap-1.5">
                <Sparkles className="w-3.5 h-3.5 text-cyan-400" /> Did you mean one of these stocks?
              </span>
              <div className="flex flex-wrap gap-2">
                {reboundSuggestions.map((stock) => (
                  <button
                    key={stock.symbol}
                    onClick={() => handleSelectStock(stock.symbol, stock)}
                    className="px-3.5 py-2 bg-gray-900 hover:bg-gray-850 border border-cyan-500/40 hover:border-cyan-400 rounded-xl text-xs text-white transition-all flex items-center space-x-2 shadow-sm text-left whitespace-normal"
                  >
                    <span className="font-mono font-bold text-cyan-300 flex-shrink-0">{stock.symbol}</span>
                    <span className="text-gray-300 font-medium whitespace-normal">{stock.name}</span>
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Loading State */}
      {loading && !data && (
        <div className="p-16 text-center space-y-3 bg-gray-900/40 border border-gray-800 rounded-2xl">
          <RefreshCw className="w-8 h-8 text-cyan-400 animate-spin mx-auto" />
          <h3 className="text-sm font-semibold text-gray-300">Computing Technical Matrix & Backtest for {ticker}...</h3>
        </div>
      )}

      {/* Initial Blank State with Quick Search Chips */}
      {!loading && !data && !errorMsg && (
        <div className="bg-gray-900/40 border border-dashed border-gray-800 rounded-2xl p-12 text-center space-y-4">
          <div className="w-12 h-12 rounded-2xl bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center mx-auto text-cyan-400">
            <Search className="w-6 h-6" />
          </div>
          <div>
            <h3 className="text-base font-bold text-white">No Stock Selected</h3>
            <p className="text-xs text-gray-400 max-w-md mx-auto mt-1">
              Search any NSE / BSE equity or natural company name above to view its technical moving averages, multi-strategy setup signals, 2-year backtest stats, and risk sizing.
            </p>
          </div>

          <div className="pt-3 border-t border-gray-800/80 max-w-2xl mx-auto space-y-2">
            <span className="text-[11px] font-semibold text-gray-500 uppercase tracking-wider block">
              Quick Scan Examples
            </span>
            <div className="flex flex-wrap justify-center gap-2">
              {POPULAR_STOCKS.map((stk) => (
                <button
                  key={stk.symbol}
                  onClick={() => handleSelectStock(stk.symbol, stk)}
                  className="px-3 py-1.5 bg-gray-950 hover:bg-gray-800 border border-gray-800 hover:border-cyan-500/40 rounded-lg text-xs text-gray-300 hover:text-cyan-300 font-mono transition-all flex items-center space-x-1.5"
                >
                  <span className="font-bold">{stk.symbol.replace('.NS', '')}</span>
                  <span className="text-gray-500 text-[11px]">({stk.name})</span>
                </button>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Main Quantitative Analysis Dashboard */}
      {data && (
        <div className="space-y-6">
          
          {/* Top Scorecard & Verdict Banner */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
            
            {/* Left 2 Cols: Stock Info & Ranges */}
            <div className="lg:col-span-2 bg-gray-900/90 border border-gray-800 rounded-2xl p-5 space-y-4">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-gray-800 pb-4">
                <div className="flex-1 min-w-0 pr-2">
                  <div className="flex items-center space-x-2.5 flex-wrap">
                    <h2 className="text-2xl sm:text-3xl font-extrabold text-white font-mono tracking-tight">{data.ticker}</h2>
                    <span className="text-xs px-2.5 py-0.5 rounded-full bg-cyan-500/10 text-cyan-400 font-bold border border-cyan-500/20 uppercase tracking-wider">
                      {data.ticker.endsWith('.NS') ? 'NSE' : data.ticker.endsWith('.BO') ? 'BSE' : 'US Market'}
                    </span>
                  </div>
                  <h3 className="text-sm sm:text-base font-semibold text-gray-200 mt-1 leading-snug whitespace-normal break-words">
                    {data.company_name}
                  </h3>
                </div>

                <div className="flex items-baseline space-x-2.5 flex-shrink-0">
                  <span className="text-2xl sm:text-3xl font-extrabold text-white font-mono">₹{fmt(data.cmp)}</span>
                  <span className={`text-sm sm:text-base font-bold font-mono flex items-center px-2 py-0.5 rounded-lg ${
                    data.change_pct >= 0 ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 'bg-red-500/10 text-red-400 border border-red-500/20'
                  }`}>
                    {data.change_pct >= 0 ? <ArrowUpRight className="w-4 h-4 mr-0.5" /> : <ArrowDownRight className="w-4 h-4 mr-0.5" />}
                    {data.change_pct >= 0 ? `+${data.change_pct}%` : `${data.change_pct}%`}
                  </span>
                </div>
              </div>

              {/* Range & Volatility Grid */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                <div className="bg-gray-950/60 p-3 rounded-xl border border-gray-800/80">
                  <span className="text-[10px] uppercase font-bold text-gray-500 block">52-Week Range</span>
                  <span className="text-xs font-mono font-bold text-gray-200 block mt-0.5">
                    ₹{fmt(data.range_52w.low)} – ₹{fmt(data.range_52w.high)}
                  </span>
                </div>

                <div className="bg-gray-950/60 p-3 rounded-xl border border-gray-800/80">
                  <span className="text-[10px] uppercase font-bold text-gray-500 block">20-Day Range</span>
                  <span className="text-xs font-mono font-bold text-gray-200 block mt-0.5">
                    ₹{fmt(data.range_20d.low)} – ₹{fmt(data.range_20d.high)}
                  </span>
                </div>

                <div className="bg-gray-950/60 p-3 rounded-xl border border-gray-800/80">
                  <span className="text-[10px] uppercase font-bold text-gray-500 block">Daily ATR (14)</span>
                  <span className="text-xs font-mono font-bold text-cyan-300 block mt-0.5">
                    ₹{fmt(data.atr_14)} ({data.atr_pct}%)
                  </span>
                </div>

                <div className="bg-gray-950/60 p-3 rounded-xl border border-gray-800/80">
                  <span className="text-[10px] uppercase font-bold text-gray-500 block">Volume Surge</span>
                  <span className={`text-xs font-mono font-bold block mt-0.5 ${
                    data.oscillators.vol_ratio >= 1.2 ? 'text-emerald-400' : 'text-gray-300'
                  }`}>
                    {data.oscillators.vol_ratio}x 20D Avg
                  </span>
                </div>
              </div>

              {/* Quick Action Navigation Bar */}
              <div className="flex flex-wrap items-center justify-between gap-2 pt-3 border-t border-gray-800/80">
                <div className="text-[11px] text-gray-400 font-medium">
                  Instant Navigation:
                </div>
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => onOpenChart && onOpenChart(data.ticker)}
                    className="px-3 py-1.5 bg-gray-800 hover:bg-gray-700 text-cyan-300 border border-gray-700 hover:border-cyan-500/50 rounded-lg text-xs font-semibold flex items-center space-x-1.5 transition-colors"
                  >
                    <BarChart2 className="w-3.5 h-3.5" />
                    <span>Interactive Chart</span>
                  </button>
                  <button
                    onClick={() => onOpenAIForecast && onOpenAIForecast(data.ticker)}
                    className="px-3 py-1.5 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white rounded-lg text-xs font-semibold flex items-center space-x-1.5 shadow-sm transition-all"
                  >
                    <Sparkles className="w-3.5 h-3.5" />
                    <span>🔮 AI Forecast</span>
                  </button>
                  <button
                    onClick={() => onOpenBacktest && onOpenBacktest(data.ticker, data.backtest_snapshot?.strategy_id || 'trend_pullback')}
                    className="px-3 py-1.5 bg-gray-800 hover:bg-gray-700 text-gray-200 border border-gray-700 hover:border-gray-500 rounded-lg text-xs font-semibold flex items-center space-x-1.5 transition-colors"
                  >
                    <TrendingUp className="w-3.5 h-3.5 text-emerald-400" />
                    <span>Backtest</span>
                  </button>
                </div>
              </div>
            </div>

            {/* Right: Automated Verdict Card */}
            <div className={`rounded-2xl p-5 border flex flex-col justify-between space-y-3 ${
              data.verdict.type === 'BULLISH' 
                ? 'bg-emerald-950/30 border-emerald-500/40 text-emerald-300'
                : (data.verdict.type === 'UPTREND'
                  ? 'bg-cyan-950/30 border-cyan-500/40 text-cyan-300'
                  : 'bg-gray-900/90 border-gray-800 text-gray-300')
            }`}>
              <div>
                <div className="flex items-center space-x-2">
                  <Award className="w-5 h-5 flex-shrink-0" />
                  <span className="text-[11px] uppercase font-bold tracking-wider">Trading Verdict</span>
                </div>
                <h3 className="text-base font-bold text-white mt-1">{data.verdict.title}</h3>
                <p className="text-xs leading-relaxed text-gray-300 mt-1.5">{data.verdict.text}</p>
              </div>

              {data.active_setup && (
                <div className="pt-2 border-t border-gray-800/60 flex items-center justify-between text-xs font-mono">
                  <span className="text-gray-400">Quality Score:</span>
                  <span className="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400 font-bold">
                    {data.active_setup.score}/100
                  </span>
                </div>
              )}
            </div>

          </div>

          {/* Section 2: Moving Averages Alignment & Momentum Oscillators */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            
            {/* Moving Averages Matrix */}
            <div className="bg-gray-900/90 border border-gray-800 rounded-2xl p-5 space-y-3">
              <div className="flex items-center justify-between border-b border-gray-800 pb-2.5">
                <div className="flex items-center space-x-2">
                  <Layers className="w-4 h-4 text-cyan-400" />
                  <h3 className="text-sm font-bold text-white">Moving Averages Matrix</h3>
                </div>
                <span className="text-xs text-gray-400 font-mono">Distance to CMP</span>
              </div>

              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs font-mono">
                  <thead className="bg-gray-950/60 text-gray-500 uppercase text-[10px]">
                    <tr>
                      <th className="px-3 py-2">Indicator</th>
                      <th className="px-3 py-2">Level Value</th>
                      <th className="px-3 py-2">Distance (%)</th>
                      <th className="px-3 py-2">Technical Status</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-800/60 text-gray-200">
                    <tr>
                      <td className="px-3 py-2 text-cyan-300 font-semibold">20 EMA</td>
                      <td className="px-3 py-2">₹{fmt(data.moving_averages.ema_20?.value)}</td>
                      <td className={`px-3 py-2 font-semibold ${(data.moving_averages.ema_20?.dist_pct || 0) >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                        {(data.moving_averages.ema_20?.dist_pct || 0) >= 0 ? `+${data.moving_averages.ema_20?.dist_pct}%` : `${data.moving_averages.ema_20?.dist_pct}%`}
                      </td>
                      <td className="px-3 py-2 text-[11px] text-gray-400">Dynamic Support</td>
                    </tr>
                    <tr>
                      <td className="px-3 py-2 text-amber-300 font-semibold">50 EMA</td>
                      <td className="px-3 py-2">₹{fmt(data.moving_averages.ema_50?.value)}</td>
                      <td className={`px-3 py-2 font-semibold ${(data.moving_averages.ema_50?.dist_pct || 0) >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                        {(data.moving_averages.ema_50?.dist_pct || 0) >= 0 ? `+${data.moving_averages.ema_50?.dist_pct}%` : `${data.moving_averages.ema_50?.dist_pct}%`}
                      </td>
                      <td className="px-3 py-2 text-[11px] text-gray-400">Intermediate Trend</td>
                    </tr>
                    <tr>
                      <td className="px-3 py-2 text-indigo-300 font-semibold">100 EMA</td>
                      <td className="px-3 py-2">₹{fmt(data.moving_averages.ema_100?.value)}</td>
                      <td className={`px-3 py-2 font-semibold ${(data.moving_averages.ema_100?.dist_pct || 0) >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                        {(data.moving_averages.ema_100?.dist_pct || 0) >= 0 ? `+${data.moving_averages.ema_100?.dist_pct}%` : `${data.moving_averages.ema_100?.dist_pct}%`}
                      </td>
                      <td className="px-3 py-2 text-[11px] text-gray-400">Medium Horizon</td>
                    </tr>
                    <tr>
                      <td className="px-3 py-2 text-purple-300 font-semibold">200 EMA</td>
                      <td className="px-3 py-2">₹{fmt(data.moving_averages.ema_200?.value)}</td>
                      <td className={`px-3 py-2 font-semibold ${(data.moving_averages.ema_200?.dist_pct || 0) >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                        {(data.moving_averages.ema_200?.dist_pct || 0) >= 0 ? `+${data.moving_averages.ema_200?.dist_pct}%` : `${data.moving_averages.ema_200?.dist_pct}%`}
                      </td>
                      <td className="px-3 py-2 text-[11px] text-gray-400">Macro Bull Baseline</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            {/* Momentum & Technical Oscillators */}
            <div className="bg-gray-900/90 border border-gray-800 rounded-2xl p-5 space-y-4">
              <div className="flex items-center justify-between border-b border-gray-800 pb-2.5">
                <div className="flex items-center space-x-2">
                  <Activity className="w-4 h-4 text-cyan-400" />
                  <h3 className="text-sm font-bold text-white">Momentum & Oscillators</h3>
                </div>
                <span className="text-xs text-gray-400 font-mono">Wilder / TV Specs</span>
              </div>

              <div className="grid grid-cols-2 gap-3 text-xs">
                <div className="bg-gray-950/60 p-3 rounded-xl border border-gray-800/80 space-y-1">
                  <span className="text-[10px] uppercase font-bold text-gray-500">RSI (14)</span>
                  <div className="flex items-center justify-between">
                    <span className="text-base font-bold font-mono text-white">{data.oscillators.rsi_14}</span>
                    <span className="text-[10px] px-2 py-0.5 rounded bg-cyan-500/10 text-cyan-300 font-semibold">
                      {data.oscillators.rsi_status}
                    </span>
                  </div>
                </div>

                <div className="bg-gray-950/60 p-3 rounded-xl border border-gray-800/80 space-y-1">
                  <span className="text-[10px] uppercase font-bold text-gray-500">MACD (12, 26, 9)</span>
                  <div className="flex items-center justify-between font-mono">
                    <span className="text-xs text-gray-300">{data.oscillators.macd}</span>
                    <span className={`text-xs font-bold ${data.oscillators.macd_hist >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                      Hist: {data.oscillators.macd_hist >= 0 ? `+${data.oscillators.macd_hist}` : data.oscillators.macd_hist}
                    </span>
                  </div>
                </div>

                <div className="bg-gray-950/60 p-3 rounded-xl border border-gray-800/80 space-y-1">
                  <span className="text-[10px] uppercase font-bold text-gray-500">Bollinger Bands</span>
                  <div className="text-[11px] font-mono text-gray-300 space-y-0.5">
                    <div>Upper: <span className="text-gray-100">₹{fmt(data.oscillators.bollinger.upper)}</span></div>
                    <div>Lower: <span className="text-gray-100">₹{fmt(data.oscillators.bollinger.lower)}</span></div>
                  </div>
                </div>

                <div className="bg-gray-950/60 p-3 rounded-xl border border-gray-800/80 space-y-1">
                  <span className="text-[10px] uppercase font-bold text-gray-500">Volume Analysis</span>
                  <div className="text-[11px] font-mono text-gray-300 space-y-0.5">
                    <div>Today: <span className="text-gray-100">{data.oscillators.volume_today.toLocaleString()}</span></div>
                    <div>20D Avg: <span className="text-gray-400">{data.oscillators.vol_sma20.toLocaleString()}</span></div>
                  </div>
                </div>
              </div>
            </div>

          </div>

          {/* Section 3: Multi-Strategy Setup Trigger Status */}
          <div className="bg-gray-900/90 border border-gray-800 rounded-2xl p-5 space-y-4">
            <div className="flex items-center justify-between border-b border-gray-800 pb-3">
              <div className="flex items-center space-x-2">
                <Sparkles className="w-4 h-4 text-cyan-400" />
                <h3 className="text-base font-bold text-white">Multi-Strategy Quantitative Setup Check</h3>
              </div>
              <span className="text-xs text-gray-400">Simultaneous scan across all 3 models</span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {data.strategy_evaluations.map((item) => (
                <div
                  key={item.strategy_id}
                  className={`p-4 rounded-xl border space-y-3 transition-all ${
                    item.is_active
                      ? 'bg-emerald-950/20 border-emerald-500/50 shadow-lg shadow-emerald-500/5'
                      : 'bg-gray-950/60 border-gray-800/80 opacity-70'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-white truncate">{item.name}</span>
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase font-mono ${
                      item.is_active ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' : 'bg-gray-800 text-gray-500'
                    }`}>
                      {item.is_active ? `Score ${item.setup?.score}/100` : "Inactive"}
                    </span>
                  </div>

                  {item.is_active && item.setup ? (
                    <div className="space-y-2 text-xs font-mono pt-1">
                      <div className="flex justify-between text-gray-300">
                        <span>Entry:</span>
                        <span className="text-cyan-300 font-bold">₹{fmt(item.setup.close)}</span>
                      </div>
                      <div className="flex justify-between text-gray-300">
                        <span>Stop Loss:</span>
                        <span className="text-red-400 font-bold">₹{fmt(item.setup.stop_loss)}</span>
                      </div>
                      <div className="flex justify-between text-gray-300">
                        <span>Target 1 (2R):</span>
                        <span className="text-emerald-400 font-bold">₹{fmt(item.setup.target_1)} (+{item.setup.reward_pct_t1}%)</span>
                      </div>
                      <div className="p-2 rounded bg-gray-900/80 text-[10px] text-gray-300 font-sans border border-gray-800 mt-2">
                        {item.setup.setup_summary}
                      </div>
                    </div>
                  ) : (
                    <p className="text-[11px] text-gray-500 leading-relaxed pt-1">
                      Current candle does not satisfy strict entry conditions for this model.
                    </p>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Section 3.5: Kronos AI Foundation Forecast & Neural Price Corridor */}
          <div className="bg-gradient-to-r from-purple-950/40 via-gray-900/90 to-blue-950/40 border border-purple-800/60 rounded-2xl p-5 space-y-4 shadow-xl">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-purple-900/50 pb-3">
              <div className="flex items-center space-x-2.5">
                <div className="w-8 h-8 rounded-lg bg-purple-500/20 border border-purple-500/30 flex items-center justify-center text-purple-300">
                  <Sparkles className="w-4 h-4 text-purple-400" />
                </div>
                <div>
                  <h3 className="text-base font-bold text-white flex items-center gap-2">
                    <span>Kronos AI Foundation Forecast</span>
                    <span className="text-[10px] px-2 py-0.5 rounded-full bg-purple-500/20 text-purple-300 border border-purple-500/40 font-mono uppercase font-semibold">
                      Monte Carlo Neural Engine
                    </span>
                  </h3>
                  <p className="text-xs text-gray-400">
                    Autoregressive 15-day forward projection &amp; 90% confidence corridor for {data.ticker}
                  </p>
                </div>
              </div>

              <button
                onClick={() => onOpenAIForecast && onOpenAIForecast(data.ticker)}
                className="px-3 py-1.5 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white rounded-lg text-xs font-semibold flex items-center space-x-1.5 shadow-sm transition-all self-start sm:self-auto"
              >
                <Sparkles className="w-3.5 h-3.5" />
                <span>Full AI Forecast Studio</span>
              </button>
            </div>

            {aiLoading && (
              <div className="py-8 flex flex-col items-center justify-center space-y-2 text-gray-400 text-xs font-mono">
                <RefreshCw className="w-6 h-6 animate-spin text-purple-400" />
                <span>Running parallel Monte Carlo forward pass (20 paths) on Kronos Foundation Model...</span>
              </div>
            )}

            {!aiLoading && aiForecast && (
              <div className="space-y-4">
                {/* 4 Metrics Grid */}
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
                  <div className="bg-gray-950/80 p-3 rounded-xl border border-gray-800">
                    <span className="text-gray-500 text-[10px] uppercase font-bold block">Upside Probability</span>
                    <span className={`text-xl font-extrabold font-mono ${aiForecast.upside_prob >= 60 ? 'text-emerald-400' : aiForecast.upside_prob >= 45 ? 'text-yellow-400' : 'text-rose-400'}`}>
                      {aiForecast.upside_prob}%
                    </span>
                    <div className="w-full bg-gray-800 h-1.5 rounded-full mt-1.5 overflow-hidden">
                      <div 
                        className={`h-full ${aiForecast.upside_prob >= 60 ? 'bg-emerald-400' : aiForecast.upside_prob >= 45 ? 'bg-yellow-400' : 'bg-rose-400'}`}
                        style={{ width: `${aiForecast.upside_prob}%` }}
                      ></div>
                    </div>
                  </div>

                  <div className="bg-gray-950/80 p-3 rounded-xl border border-gray-800">
                    <span className="text-gray-500 text-[10px] uppercase font-bold block">Expected 15D Target</span>
                    <span className="text-xl font-extrabold font-mono text-cyan-300">
                      ₹{aiForecast.expected_close?.toFixed(2)}
                    </span>
                    <span className={`text-[10px] font-mono block mt-0.5 ${aiForecast.expected_change_pct >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                      {aiForecast.expected_change_pct >= 0 ? `+${aiForecast.expected_change_pct}%` : `${aiForecast.expected_change_pct}%`} vs CMP
                    </span>
                  </div>

                  <div className="bg-gray-950/80 p-3 rounded-xl border border-gray-800">
                    <span className="text-gray-500 text-[10px] uppercase font-bold block">90% Corridor [p10, p90]</span>
                    <span className="font-mono text-gray-200 font-bold block mt-1">
                      ₹{aiForecast.p10_close?.toFixed(2)} ~ ₹{aiForecast.p90_close?.toFixed(2)}
                    </span>
                    <span className="text-[10px] text-gray-500 block mt-0.5">
                      Spread: ₹{(aiForecast.p90_close - aiForecast.p10_close).toFixed(2)}
                    </span>
                  </div>

                  <div className="bg-gray-950/80 p-3 rounded-xl border border-gray-800">
                    <span className="text-gray-500 text-[10px] uppercase font-bold block">Volatility Risk</span>
                    <span className="font-mono text-purple-300 font-bold block mt-1">
                      {aiForecast.volatility_amplification}x
                    </span>
                    <span className="text-[10px] text-gray-400 block mt-0.5">
                      {aiForecast.volatility_amplification <= 1.1 ? '🟢 Low/Orderly Risk' : '⚠️ Elevated Risk'}
                    </span>
                  </div>
                </div>

                {/* Synthesis Banner */}
                <div className="bg-purple-950/30 border border-purple-800/50 p-3 rounded-xl flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs">
                  <div className="flex items-center space-x-2">
                    <span className="px-2 py-0.5 rounded bg-purple-500/20 text-purple-300 font-bold text-[10px] uppercase border border-purple-500/30">
                      {aiForecast.confluence_badge}
                    </span>
                    <span className="text-gray-300 text-[11px]">
                      Regime: <strong className="text-white">{aiForecast.regime}</strong>. Historical price action indicates high-fidelity alignment with quantitative strategy setups.
                    </span>
                  </div>
                  <button
                    onClick={() => onOpenChart && onOpenChart(data.ticker)}
                    className="px-2.5 py-1 bg-gray-800 hover:bg-gray-700 text-cyan-300 rounded border border-gray-700 text-[11px] font-semibold whitespace-nowrap flex items-center space-x-1 self-start sm:self-auto"
                  >
                    <BarChart2 className="w-3 h-3" />
                    <span>View Forecast on Chart</span>
                  </button>
                </div>
              </div>
            )}
          </div>

          {/* Section 4: 2-Year Historical Strategy Performance & Position Sizing */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            
            {/* 2-Year Backtest Snapshot */}
            <div className="bg-gray-900/90 border border-gray-800 rounded-2xl p-5 space-y-4">
              <div className="flex items-center justify-between border-b border-gray-800 pb-3">
                <div className="flex items-center space-x-2">
                  <Clock className="w-4 h-4 text-cyan-400" />
                  <h3 className="text-sm font-bold text-white">2-Year Strategy Backtest Snapshot</h3>
                </div>
                <span className="text-xs text-cyan-300 font-mono font-semibold">
                  {data.backtest_snapshot.strategy_id.replace('_', ' ').toUpperCase()}
                </span>
              </div>

              <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 text-xs">
                <div className="bg-gray-950/60 p-3 rounded-xl border border-gray-800/80">
                  <span className="text-[10px] uppercase font-bold text-gray-500 block">Win Rate</span>
                  <span className="text-base font-bold font-mono text-cyan-300 block mt-0.5">
                    {data.backtest_snapshot.win_rate}%
                  </span>
                  <span className="text-[10px] text-gray-400">
                    {data.backtest_snapshot.winning_trades}W / {data.backtest_snapshot.losing_trades}L
                  </span>
                </div>

                <div className="bg-gray-950/60 p-3 rounded-xl border border-gray-800/80">
                  <span className="text-[10px] uppercase font-bold text-gray-500 block">Profit Factor</span>
                  <span className="text-base font-bold font-mono text-emerald-400 block mt-0.5">
                    {data.backtest_snapshot.profit_factor}
                  </span>
                  <span className="text-[10px] text-gray-400">Gross Win / Loss</span>
                </div>

                <div className="bg-gray-950/60 p-3 rounded-xl border border-gray-800/80">
                  <span className="text-[10px] uppercase font-bold text-gray-500 block">Max Drawdown</span>
                  <span className="text-base font-bold font-mono text-red-400 block mt-0.5">
                    -{data.backtest_snapshot.max_drawdown_pct}%
                  </span>
                  <span className="text-[10px] text-gray-400">Peak to trough</span>
                </div>
              </div>

              <div className="p-3 bg-gray-950/80 rounded-xl border border-gray-800 flex items-center justify-between text-xs font-mono">
                <span className="text-gray-400">Total 2Y Return:</span>
                <span className={`font-bold ${data.backtest_snapshot.net_profit_pct >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                  {data.backtest_snapshot.net_profit_pct >= 0 ? `+${data.backtest_snapshot.net_profit_pct}%` : `${data.backtest_snapshot.net_profit_pct}%`} (+₹{(data.backtest_snapshot.net_profit || 0).toLocaleString()})
                </span>
              </div>
            </div>

            {/* Position Sizer Calculator Card */}
            <div className="bg-gray-900/90 border border-gray-800 rounded-2xl p-5 space-y-4">
              <div className="flex items-center justify-between border-b border-gray-800 pb-3">
                <div className="flex items-center space-x-2">
                  <ShieldCheck className="w-4 h-4 text-cyan-400" />
                  <h3 className="text-sm font-bold text-white">Risk Sizing & Order Allocation</h3>
                </div>
                <span className="text-xs text-gray-400 font-mono">1% Risk Model</span>
              </div>

              <div className="grid grid-cols-2 gap-3 text-xs">
                <div>
                  <label className="text-[10px] uppercase font-bold text-gray-500 block mb-1">Account Capital (₹)</label>
                  <input
                    type="number"
                    value={capital}
                    onChange={(e) => handleCapitalChange(Number(e.target.value), riskPct)}
                    className="w-full bg-gray-950 border border-gray-700 rounded-lg px-2.5 py-1.5 text-xs text-gray-100 font-mono focus:outline-none focus:border-cyan-500"
                  />
                </div>
                <div>
                  <label className="text-[10px] uppercase font-bold text-gray-500 block mb-1">Risk Budget (%)</label>
                  <input
                    type="number"
                    step="0.5"
                    value={riskPct}
                    onChange={(e) => handleCapitalChange(capital, Number(e.target.value))}
                    className="w-full bg-gray-950 border border-gray-700 rounded-lg px-2.5 py-1.5 text-xs text-gray-100 font-mono focus:outline-none focus:border-cyan-500"
                  />
                </div>
              </div>

              <div className="bg-gray-950/80 p-3.5 rounded-xl border border-gray-800 space-y-2 text-xs font-mono">
                <div className="flex justify-between items-center text-gray-300">
                  <span>Recommended Order Size:</span>
                  <span className="text-sm font-bold text-cyan-300">{data.position_sizing.shares} Shares</span>
                </div>
                <div className="flex justify-between items-center text-gray-300">
                  <span>Capital Required:</span>
                  <span className="font-semibold text-gray-100">₹{(data.position_sizing?.capital_required || 0).toLocaleString()} ({data.position_sizing?.portfolio_allocation_pct || 0}% of account)</span>
                </div>
                <div className="flex justify-between items-center text-gray-300">
                  <span>Max Risk Budget:</span>
                  <span className="font-semibold text-red-400">₹{(data.position_sizing?.total_risk_amount || 0).toLocaleString()}</span>
                </div>
                <div className="flex justify-between items-center text-gray-300 pt-1 border-t border-gray-800">
                  <span>Target 1 Profit (2R):</span>
                  <span className="font-bold text-emerald-400">+₹{(data.position_sizing?.potential_profit_target_1 || 0).toLocaleString()}</span>
                </div>
              </div>
            </div>

          </div>

          {/* Section 5: Recent 10 Trading Sessions Table */}
          <div className="bg-gray-900/90 border border-gray-800 rounded-2xl p-5 space-y-3">
            <div className="flex items-center justify-between border-b border-gray-800 pb-3">
              <h3 className="text-sm font-bold text-white">Recent 10 Trading Sessions (Daily OHLCV)</h3>
              <span className="text-xs text-gray-400 font-mono">Historical Bar Feed</span>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs text-gray-300 font-mono">
                <thead className="bg-gray-950/80 text-gray-500 uppercase text-[10px]">
                  <tr>
                    <th className="px-3 py-2">Date</th>
                    <th className="px-3 py-2">Open</th>
                    <th className="px-3 py-2">High</th>
                    <th className="px-3 py-2">Low</th>
                    <th className="px-3 py-2">Close</th>
                    <th className="px-3 py-2">Volume</th>
                    <th className="px-3 py-2">20 EMA</th>
                    <th className="px-3 py-2">RSI (14)</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-800/60">
                  {data.recent_candles.map((c) => (
                    <tr key={c.date} className="hover:bg-gray-800/40 transition-colors">
                      <td className="px-3 py-2 text-gray-400 font-semibold">{c.date}</td>
                      <td className="px-3 py-2">₹{fmt(c.open)}</td>
                      <td className="px-3 py-2">₹{fmt(c.high)}</td>
                      <td className="px-3 py-2">₹{fmt(c.low)}</td>
                      <td className={`px-3 py-2 font-bold ${c.close >= c.open ? 'text-emerald-400' : 'text-red-400'}`}>
                        ₹{fmt(c.close)}
                      </td>
                      <td className="px-3 py-2 text-gray-400">{c.volume.toLocaleString()}</td>
                      <td className="px-3 py-2 text-cyan-300">₹{fmt(c.ema_20)}</td>
                      <td className={`px-3 py-2 font-semibold ${c.rsi_14 >= 50 ? 'text-emerald-400' : 'text-yellow-400'}`}>
                        {fmt(c.rsi_14, 1)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

        </div>
      )}

    </div>
  );
}
