import React, { useState, useEffect } from 'react';
import { 
  Sparkles, Search, TrendingUp, TrendingDown, ShieldAlert, 
  BarChart2, RefreshCw, Download, Layers, Activity, Cpu, 
  AlertTriangle, ArrowUpRight, ArrowDownRight, Compass, ShieldCheck,
  CheckCircle2, Gauge, Zap, Database, ArrowRight
} from 'lucide-react';
import { 
  fetchAIForecast, 
  fetchAIModelStatus, 
  searchStocks,
  fetchMacroFactors,
  runMacroAlignment
} from '../services/api';
import StockSearchInput from './StockSearchInput';

const QUICK_TICKERS = [
  { symbol: "RELIANCE.NS", name: "Reliance Ind." },
  { symbol: "TCS.NS", name: "TCS" },
  { symbol: "HDFCBANK.NS", name: "HDFC Bank" },
  { symbol: "INFY.NS", name: "Infosys" },
  { symbol: "ICICIBANK.NS", name: "ICICI Bank" },
  { symbol: "BHARTIARTL.NS", name: "Bharti Airtel" },
  { symbol: "TITAN.NS", name: "Titan Company" },
  { symbol: "KOTAKBANK.NS", name: "Kotak Bank" },
  { symbol: "BOSCHLTD.NS", name: "Bosch Ltd" }
];

export default function AIForecastStudio({ 
  selectedTicker = "RELIANCE.NS", 
  onSelectTicker, 
  onOpenRisk, 
  onOpenBacktest 
}) {
  // Navigation tab: 'kline' (K-Line Candlestick Forecast) | 'macro' (Macro-Factor Alignment)
  const [activeAiTab, setActiveAiTab] = useState('kline');

  // K-Line Forecast State
  const [tickerInput, setTickerInput] = useState(selectedTicker);
  const [activeTicker, setActiveTicker] = useState(selectedTicker);
  const [predLen, setPredLen] = useState(15);
  const [paths, setPaths] = useState(20);
  const [modelType, setModelType] = useState("mini");
  const [loading, setLoading] = useState(false);
  const [forecastData, setForecastData] = useState(null);
  const [errorMsg, setErrorMsg] = useState(null);
  const [reboundSuggestions, setReboundSuggestions] = useState([]);
  const [modelStatus, setModelStatus] = useState(null);
  const [showGhostPaths, setShowGhostPaths] = useState(true);

  // Macro-Factor Alignment State
  const [macroFactors, setMacroFactors] = useState(null);
  const [macroResult, setMacroResult] = useState(null);
  const [macroLoading, setMacroLoading] = useState(false);
  const [macroError, setMacroError] = useState(null);
  const [forwardHorizon, setForwardHorizon] = useState(5);
  const [targetThresholdPct, setTargetThresholdPct] = useState(0.5);

  useEffect(() => {
    fetchAIModelStatus().then(setModelStatus).catch(() => {});
    fetchMacroFactors().then(setMacroFactors).catch(() => {});
  }, []);

  useEffect(() => {
    if (selectedTicker && selectedTicker !== activeTicker) {
      setTickerInput(selectedTicker);
      setActiveTicker(selectedTicker);
      if (activeAiTab === 'kline') {
        runForecast(selectedTicker, predLen, paths, modelType);
      } else {
        runMacroPipeline(selectedTicker, forwardHorizon, targetThresholdPct);
      }
    }
  }, [selectedTicker]);

  useEffect(() => {
    if (activeAiTab === 'kline') {
      runForecast(activeTicker, predLen, paths, modelType);
    }
  }, [predLen, paths, modelType]);

  const runMacroPipeline = async (symbol, horizon, threshold) => {
    if (!symbol) return;
    setMacroLoading(true);
    setMacroError(null);
    try {
      const data = await runMacroAlignment({
        ticker: symbol.trim(),
        forward_horizon: Number(horizon),
        target_threshold_pct: Number(threshold)
      });
      setMacroResult(data);
      if (data.ticker && data.ticker !== activeTicker) {
        setActiveTicker(data.ticker);
        setTickerInput(data.ticker);
      }
    } catch (err) {
      setMacroError(err.message || "Failed to execute macro-factor alignment.");
      setMacroResult(null);
    } finally {
      setMacroLoading(false);
    }
  };

  const runForecast = async (symbol, horizon, samplePaths, modelTier) => {
    if (!symbol) return;
    setLoading(true);
    setErrorMsg(null);
    setReboundSuggestions([]);
    try {
      const data = await fetchAIForecast(symbol, horizon, samplePaths, modelTier);
      setForecastData(data);
      if (data.ticker && data.ticker !== activeTicker) {
        setActiveTicker(data.ticker);
        setTickerInput(data.ticker);
      }
    } catch (err) {
      setErrorMsg(err.message || "Failed to generate AI forecast.");
      setForecastData(null);
      try {
        const suggestions = await searchStocks(symbol);
        setReboundSuggestions(suggestions);
      } catch (sugErr) {}
    } finally {
      setLoading(false);
    }
  };

  const handleSelectStock = (symbol, stockObj) => {
    setTickerInput(symbol);
    setActiveTicker(symbol);
    if (activeAiTab === 'kline') {
      runForecast(symbol, predLen, paths, modelType);
    } else {
      runMacroPipeline(symbol, forwardHorizon, targetThresholdPct);
    }
  };

  const exportForecastCSV = () => {
    if (!forecastData || !forecastData.forecast_candles) return;
    const headers = ["Day", "Date", "Predicted Open", "Predicted High", "Predicted Low", "Predicted Close", "10th Pct Low", "90th Pct High"];
    const rows = forecastData.forecast_candles.map((c, i) => [
      `T+${i + 1}`, c.date, c.open, c.high, c.low, c.close, c.band_low, c.band_high
    ]);
    const csvContent = "data:text/csv;charset=utf-8," + [headers.join(","), ...rows.map(e => e.join(","))].join("\n");
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `Kronos_Forecast_${forecastData.ticker}_${predLen}d.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="space-y-6">
      
      {/* Top Banner / Hero */}
      <div className="bg-gradient-to-r from-gray-900 via-[#131b2e] to-gray-900 p-6 rounded-2xl border border-gray-800 shadow-xl relative overflow-hidden">
        <div className="absolute right-0 top-0 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none"></div>
        <div className="relative z-10 flex flex-col lg:flex-row lg:items-center justify-between gap-4">
          <div>
            <div className="flex items-center space-x-3 mb-2">
              <span className="p-2 bg-gradient-to-br from-cyan-500/20 to-blue-600/20 border border-cyan-500/30 rounded-xl text-cyan-400">
                <Sparkles className="w-6 h-6" />
              </span>
              <div>
                <h1 className="text-xl font-extrabold text-white tracking-tight flex items-center gap-2">
                  Kronos AI Foundation Model Forecaster
                  <span className="text-[10px] uppercase font-semibold tracking-wider px-2 py-0.5 rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/30">
                    AAAI 2026 Foundation Model
                  </span>
                </h1>
                <p className="text-xs text-gray-400">
                  Autoregressive neural K-line forecasting trained on 12B+ global candles with parallel Monte Carlo probability density simulation.
                </p>
              </div>
            </div>
          </div>

          {/* Model Status & Device Badge */}
          <div className="flex items-center space-x-3 bg-gray-950/80 px-4 py-2.5 rounded-xl border border-gray-800 text-xs">
            <Cpu className="w-4 h-4 text-cyan-400" />
            <div>
              <div className="text-[10px] uppercase text-gray-500 font-semibold">Compute Device</div>
              <div className="font-mono text-cyan-300 font-bold uppercase">{modelStatus?.device || "CPU"} Accelerated</div>
            </div>
            <div className="h-6 w-px bg-gray-800"></div>
            <div>
              <div className="text-[10px] uppercase text-gray-500 font-semibold">Model Engine</div>
              <div className="font-mono text-emerald-400 font-bold">Kronos-{modelType}</div>
            </div>
          </div>
        </div>
      </div>

      {/* Workflow Navigation Switcher */}
      <div className="flex items-center space-x-2 bg-gray-950 p-1.5 rounded-xl border border-gray-800 w-fit shadow-md">
        <button
          onClick={() => setActiveAiTab('kline')}
          className={`px-4 py-2 rounded-lg text-xs font-bold transition-all flex items-center space-x-2 ${
            activeAiTab === 'kline'
              ? 'bg-gradient-to-r from-cyan-600 to-blue-600 text-white shadow-lg'
              : 'text-gray-400 hover:text-white'
          }`}
        >
          <Sparkles className="w-4 h-4" />
          <span>🔮 K-Line Candlestick Forecast</span>
        </button>
        <button
          onClick={() => {
            setActiveAiTab('macro');
            if (!macroResult && activeTicker) {
              runMacroPipeline(activeTicker, forwardHorizon, targetThresholdPct);
            }
          }}
          className={`px-4 py-2 rounded-lg text-xs font-bold transition-all flex items-center space-x-2 ${
            activeAiTab === 'macro'
              ? 'bg-gradient-to-r from-indigo-600 via-purple-600 to-cyan-600 text-white shadow-lg'
              : 'text-gray-400 hover:text-white'
          }`}
        >
          <Compass className="w-4 h-4" />
          <span>🏛️ Macro-Factor Alignment (Kronos + RBI)</span>
        </button>
      </div>

      {/* ========================================================================= */}
      {/* TAB 1: K-LINE CANDLESTICK FORECAST (100% PRESERVED)                      */}
      {/* ========================================================================= */}
      {activeAiTab === 'kline' && (
        <div className="space-y-6 animate-fadeIn">
          
          {/* Control & Search Bar */}
          <div className="bg-gray-900/90 p-4 rounded-xl border border-gray-800 flex flex-col md:flex-row md:items-center justify-between gap-4 shadow-lg">
            
            {/* Ticker Search with Live Autocomplete */}
            <div className="flex-1 max-w-md">
              <StockSearchInput
                value={tickerInput}
                onSelectStock={handleSelectStock}
                placeholder="Search ticker or company (e.g. Piccadily, Reliance, TCS, HDFC)..."
              />
            </div>

            {/* Forecast Parameters */}
            <div className="flex flex-wrap items-center gap-3 text-xs">
              
              {/* Horizon */}
              <div className="flex items-center space-x-1.5 bg-gray-950 px-2.5 py-1.5 rounded-lg border border-gray-800">
                <span className="text-gray-400 font-medium">Horizon:</span>
                <select
                  value={predLen}
                  onChange={(e) => setPredLen(Number(e.target.value))}
                  className="bg-transparent text-cyan-300 font-semibold focus:outline-none cursor-pointer"
                >
                  <option value={5} className="bg-gray-900">5 Days (Fast Swing)</option>
                  <option value={15} className="bg-gray-900">15 Days (Standard)</option>
                  <option value={30} className="bg-gray-900">30 Days (Multi-Week)</option>
                </select>
              </div>

              {/* Paths */}
              <div className="flex items-center space-x-1.5 bg-gray-950 px-2.5 py-1.5 rounded-lg border border-gray-800">
                <span className="text-gray-400 font-medium">MC Paths:</span>
                <select
                  value={paths}
                  onChange={(e) => setPaths(Number(e.target.value))}
                  className="bg-transparent text-amber-300 font-semibold focus:outline-none cursor-pointer"
                >
                  <option value={10} className="bg-gray-900">10 Paths</option>
                  <option value={20} className="bg-gray-900">20 Paths (Balanced)</option>
                  <option value={30} className="bg-gray-900">30 Paths (Deep Density)</option>
                </select>
              </div>

              {/* Model Tier */}
              <div className="flex items-center space-x-1.5 bg-gray-950 px-2.5 py-1.5 rounded-lg border border-gray-800">
                <span className="text-gray-400 font-medium">Model:</span>
                <select
                  value={modelType}
                  onChange={(e) => setModelType(e.target.value)}
                  className="bg-transparent text-emerald-300 font-semibold focus:outline-none cursor-pointer"
                >
                  <option value="mini" className="bg-gray-900">Kronos-mini (4.1M)</option>
                  <option value="small" className="bg-gray-900">Kronos-small (24.7M)</option>
                </select>
              </div>

              {/* Ghost Paths Toggle */}
              <button
                onClick={() => setShowGhostPaths(!showGhostPaths)}
                className={`px-3 py-1.5 rounded-lg border text-xs font-medium transition-colors flex items-center space-x-1.5 ${
                  showGhostPaths 
                    ? 'bg-cyan-500/20 text-cyan-300 border-cyan-500/40' 
                    : 'bg-gray-950 text-gray-400 border-gray-800 hover:text-white'
                }`}
              >
                <Layers className="w-3.5 h-3.5" />
                <span>Scenario Paths</span>
              </button>
            </div>
          </div>

          {/* Quick Ticker Chips */}
          <div className="flex items-center space-x-2 overflow-x-auto pb-1 text-xs">
            <span className="text-gray-500 text-[11px] font-semibold uppercase tracking-wider whitespace-nowrap">Nifty Leaders:</span>
            {QUICK_TICKERS.map((t) => (
              <button
                key={t.symbol}
                onClick={() => {
                  setTickerInput(t.symbol);
                  setActiveTicker(t.symbol);
                  runForecast(t.symbol, predLen, paths, modelType);
                }}
                className={`px-2.5 py-1 rounded-lg border font-mono whitespace-nowrap transition-all ${
                  activeTicker === t.symbol 
                    ? 'bg-cyan-600/30 text-cyan-300 border-cyan-500 font-semibold' 
                    : 'bg-gray-900/60 text-gray-400 border-gray-800 hover:bg-gray-800 hover:text-white'
                }`}
              >
                {t.name}
              </button>
            ))}
          </div>

          {/* Error Message & Rebound Suggestions */}
          {errorMsg && (
            <div className="p-4 bg-red-950/40 border border-red-800/80 rounded-xl space-y-3">
              <div className="flex items-center space-x-3 text-red-300 text-xs">
                <AlertTriangle className="w-5 h-5 flex-shrink-0" />
                <span>{errorMsg}</span>
              </div>

              {reboundSuggestions.length > 0 && (
                <div className="pt-2 border-t border-red-900/40 space-y-2">
                  <span className="text-xs font-semibold text-gray-300 flex items-center gap-1.5">
                    <Sparkles className="w-3.5 h-3.5 text-cyan-400" /> Did you mean one of these?
                  </span>
                  <div className="flex flex-wrap gap-2">
                    {reboundSuggestions.map((stock) => (
                      <button
                        key={stock.symbol}
                        onClick={() => handleSelectStock(stock.symbol, stock)}
                        className="px-3 py-1.5 bg-gray-900 hover:bg-gray-800 border border-cyan-500/40 hover:border-cyan-400 rounded-lg text-xs text-white transition-all flex items-center space-x-2 shadow-sm"
                      >
                        <span className="font-mono font-bold text-cyan-300">{stock.symbol}</span>
                        <span className="text-gray-400 truncate max-w-xs">{stock.name}</span>
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Loading Skeleton */}
          {loading && (
            <div className="h-64 bg-gray-900/40 border border-gray-800 rounded-2xl flex flex-col items-center justify-center space-y-3">
              <RefreshCw className="w-8 h-8 text-cyan-400 animate-spin" />
              <p className="text-xs text-gray-400 font-medium">Running parallel Monte Carlo forward pass ({paths} paths) on Kronos Foundation Model...</p>
            </div>
          )}

          {/* Results View */}
          {!loading && forecastData && (
            <div className="space-y-6">
              
              {/* Key Metrics Cards */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                
                {/* Upside Probability Gauge */}
                <div className="bg-gray-900/90 p-4 rounded-xl border border-gray-800 shadow-md">
                  <span className="text-gray-400 text-[10px] font-semibold uppercase tracking-wider block mb-1">
                    Upside Probability ({predLen}D)
                  </span>
                  <div className="flex items-baseline space-x-2">
                    <span className={`text-2xl font-black font-mono ${forecastData.upside_prob >= 60 ? 'text-emerald-400' : forecastData.upside_prob >= 45 ? 'text-amber-400' : 'text-red-400'}`}>
                      {forecastData.upside_prob}%
                    </span>
                    <span className="text-xs text-gray-400 font-medium">P(Close &gt; CMP)</span>
                  </div>
                  <div className="mt-2 w-full bg-gray-800 h-1.5 rounded-full overflow-hidden">
                    <div 
                      className={`h-full transition-all duration-500 ${forecastData.upside_prob >= 60 ? 'bg-emerald-400' : forecastData.upside_prob >= 45 ? 'bg-amber-400' : 'bg-red-400'}`}
                      style={{ width: `${forecastData.upside_prob}%` }}
                    ></div>
                  </div>
                  <span className="text-[10px] text-gray-500 mt-1.5 block font-medium">
                    {forecastData.confluence_badge}
                  </span>
                </div>

                {/* Expected Target Price */}
                <div className="bg-gray-900/90 p-4 rounded-xl border border-gray-800 shadow-md">
                  <span className="text-gray-400 text-[10px] font-semibold uppercase tracking-wider block mb-1">
                    Expected Close (Mean Path)
                  </span>
                  <div className="flex items-baseline space-x-2">
                    <span className="text-2xl font-black font-mono text-cyan-300">
                      ₹{forecastData.expected_close?.toLocaleString('en-IN')}
                    </span>
                    <span className={`text-xs font-mono font-bold flex items-center ${forecastData.expected_change_pct >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                      {forecastData.expected_change_pct >= 0 ? <ArrowUpRight className="w-3.5 h-3.5 mr-0.5" /> : <ArrowDownRight className="w-3.5 h-3.5 mr-0.5" />}
                      {forecastData.expected_change_pct > 0 ? `+${forecastData.expected_change_pct}%` : `${forecastData.expected_change_pct}%`}
                    </span>
                  </div>
                  <span className="text-[10px] text-gray-500 mt-1.5 block">
                    Last Close: ₹{forecastData.last_close?.toLocaleString('en-IN')}
                  </span>
                </div>

                {/* 90% Confidence Corridor */}
                <div className="bg-gray-900/90 p-4 rounded-xl border border-gray-800 shadow-md">
                  <span className="text-gray-400 text-[10px] font-semibold uppercase tracking-wider block mb-1">
                    90% Confidence Corridor [p10, p90]
                  </span>
                  <div className="text-sm font-black font-mono text-gray-200 mt-1">
                    ₹{forecastData.p10_close?.toLocaleString('en-IN')} <span className="text-gray-500 font-normal">to</span> ₹{forecastData.p90_close?.toLocaleString('en-IN')}
                  </div>
                  <span className="text-[10px] text-gray-500 mt-2 block">
                    Dispersion Spread: ₹{(forecastData.p90_close - forecastData.p10_close).toFixed(2)}
                  </span>
                </div>

                {/* Volatility Amplification */}
                <div className="bg-gray-900/90 p-4 rounded-xl border border-gray-800 shadow-md">
                  <span className="text-gray-400 text-[10px] font-semibold uppercase tracking-wider block mb-1">
                    Volatility Amplification
                  </span>
                  <div className="flex items-baseline space-x-2">
                    <span className="text-2xl font-black font-mono text-purple-300">
                      {forecastData.volatility_amplification}x
                    </span>
                    <span className="text-xs text-gray-400 font-medium">vs Trailing 30D</span>
                  </div>
                  <span className="text-[10px] text-gray-500 mt-1.5 block">
                    {forecastData.volatility_amplification <= 1.1 ? '🟢 Low/Orderly Swing Risk' : '⚠️ Elevated Volatility Risk'}
                  </span>
                </div>

              </div>

              {/* Interactive Trajectory Visualization Card */}
              <div className="bg-gray-900/90 p-6 rounded-2xl border border-gray-800 shadow-xl space-y-4">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-gray-800/80 pb-4">
                  <div>
                    <h3 className="text-base font-bold text-white flex items-center gap-2">
                      <Activity className="w-4 h-4 text-cyan-400" />
                      <span>Autoregressive Trajectory &amp; 90% Confidence Funnel</span>
                    </h3>
                    <p className="text-xs text-gray-400">
                      Mean trajectory (cyan) surrounded by shaded 90% confidence corridor ($p_{10}$ to $p_{90}$).
                    </p>
                  </div>

                  {/* Action Buttons */}
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => onSelectTicker(forecastData.ticker)}
                      className="flex items-center space-x-1.5 px-3 py-1.5 bg-gray-800 hover:bg-gray-700 text-cyan-300 border border-gray-700 hover:border-cyan-500/50 rounded-lg text-xs font-medium transition-colors"
                    >
                      <BarChart2 className="w-3.5 h-3.5" />
                      <span>Chart Studio</span>
                    </button>
                    <button
                      onClick={exportForecastCSV}
                      className="flex items-center space-x-1.5 px-3 py-1.5 bg-gray-800 hover:bg-gray-700 text-gray-300 border border-gray-700 hover:border-gray-500 rounded-lg text-xs font-medium transition-colors"
                    >
                      <Download className="w-3.5 h-3.5" />
                      <span>Export CSV</span>
                    </button>
                  </div>
                </div>

                {/* Custom SVG Candlestick & Funnel Chart */}
                <div className="w-full bg-gray-950 p-4 rounded-xl border border-gray-800/80 overflow-x-auto">
                  <div className="min-w-[600px] h-64 relative flex items-end">
                    
                    {/* SVG Visualizer */}
                    <svg className="w-full h-full" viewBox="0 0 800 240" preserveAspectRatio="none">
                      <defs>
                        <linearGradient id="funnelGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                          <stop offset="0%" stopColor="#06b6d4" stopOpacity="0.25" />
                          <stop offset="100%" stopColor="#06b6d4" stopOpacity="0.03" />
                        </linearGradient>
                      </defs>

                      {/* Horizontal Grid lines */}
                      <line x1="0" y1="60" x2="800" y2="60" stroke="#1f2937" strokeDasharray="3,3" />
                      <line x1="0" y1="120" x2="800" y2="120" stroke="#1f2937" strokeDasharray="3,3" />
                      <line x1="0" y1="180" x2="800" y2="180" stroke="#1f2937" strokeDasharray="3,3" />

                      {/* Reference line: Last Close */}
                      <line x1="0" y1="120" x2="800" y2="120" stroke="#4b5563" strokeWidth="1" strokeDasharray="4,4" />
                      <text x="10" y="115" fill="#9ca3af" fontSize="10" fontFamily="monospace">
                        Base: ₹{forecastData.last_close}
                      </text>

                      {(() => {
                        const candles = forecastData.forecast_candles || [];
                        if (candles.length === 0) return null;

                        const allVals = [
                          forecastData.last_close,
                          ...candles.map(c => c.high),
                          ...candles.map(c => c.low),
                          ...candles.map(c => c.band_high),
                          ...candles.map(c => c.band_low)
                        ];
                        const minVal = Math.min(...allVals) * 0.99;
                        const maxVal = Math.max(...allVals) * 1.01;
                        const range = maxVal - minVal || 1;

                        const getY = (val) => 220 - ((val - minVal) / range) * 200;
                        const stepX = 760 / (candles.length);

                        // Build Shaded Funnel Polygon
                        const upperPoints = candles.map((c, i) => `${40 + i * stepX},${getY(c.band_high)}`).join(" ");
                        const lowerPoints = candles.slice().reverse().map((c, i) => `${40 + (candles.length - 1 - i) * stepX},${getY(c.band_low)}`).join(" ");
                        const funnelPoly = `${upperPoints} ${lowerPoints}`;

                        // Mean Line Path
                        const meanPathStr = candles.map((c, i) => `${i === 0 ? 'M' : 'L'} ${40 + i * stepX} ${getY(c.close)}`).join(" ");

                        return (
                          <>
                            {/* Shaded 90% Confidence Corridor */}
                            <polygon points={funnelPoly} fill="url(#funnelGradient)" stroke="#0891b2" strokeWidth="0.8" strokeDasharray="2,2" />

                            {/* Ghost Scenario Paths */}
                            {showGhostPaths && forecastData.sample_paths?.map((path, pIdx) => {
                              const pathStr = path.map((pt, i) => `${i === 0 ? 'M' : 'L'} ${40 + i * stepX} ${getY(pt.close)}`).join(" ");
                              return (
                                <path
                                  key={pIdx}
                                  d={pathStr}
                                  fill="none"
                                  stroke="#6b7280"
                                  strokeWidth="0.7"
                                  strokeOpacity="0.4"
                                />
                              );
                            })}

                            {/* Mean Forecast Path */}
                            <path d={meanPathStr} fill="none" stroke="#22d3ee" strokeWidth="2.5" />

                            {/* Candle Bars */}
                            {candles.map((c, i) => {
                              const cx = 40 + i * stepX;
                              const isUp = c.close >= c.open;
                              const topY = getY(Math.max(c.open, c.close));
                              const botY = getY(Math.min(c.open, c.close));
                              const hY = getY(c.high);
                              const lY = getY(c.low);
                              const bodyHeight = Math.max(3, botY - topY);

                              return (
                                <g key={i}>
                                  {/* Wick */}
                                  <line x1={cx} y1={hY} x2={cx} y2={lY} stroke={isUp ? '#34d399' : '#f87171'} strokeWidth="1.2" />
                                  {/* Body */}
                                  <rect
                                    x={cx - 5}
                                    y={topY}
                                    width="10"
                                    height={bodyHeight}
                                    fill={isUp ? '#059669' : '#dc2626'}
                                    stroke={isUp ? '#34d399' : '#f87171'}
                                    strokeWidth="0.8"
                                    rx="1"
                                  />
                                  {/* Date label */}
                                  <text x={cx} y="235" fill="#6b7280" fontSize="8" textAnchor="middle" fontFamily="monospace">
                                    T+{i + 1}
                                  </text>
                                </g>
                              );
                            })}
                          </>
                        );
                      })()}
                    </svg>
                  </div>
                </div>

                {/* Trajectory Table */}
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs">
                    <thead>
                      <tr className="border-b border-gray-800 text-[10px] text-gray-500 uppercase font-semibold">
                        <th className="pb-2">Session</th>
                        <th className="pb-2">Date</th>
                        <th className="pb-2">Open</th>
                        <th className="pb-2">High</th>
                        <th className="pb-2">Low</th>
                        <th className="pb-2">Expected Close</th>
                        <th className="pb-2">10th Pct Low</th>
                        <th className="pb-2">90th Pct High</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-800/60 font-mono">
                      {forecastData.forecast_candles?.map((c, i) => (
                        <tr key={i} className="hover:bg-gray-800/30 transition-colors">
                          <td className="py-2 text-cyan-400 font-semibold">T+{i + 1}</td>
                          <td className="py-2 text-gray-400">{c.date}</td>
                          <td className="py-2 text-gray-300">₹{c.open.toFixed(2)}</td>
                          <td className="py-2 text-emerald-400">₹{c.high.toFixed(2)}</td>
                          <td className="py-2 text-red-400">₹{c.low.toFixed(2)}</td>
                          <td className="py-2 text-white font-bold">₹{c.close.toFixed(2)}</td>
                          <td className="py-2 text-gray-500">₹{c.band_low.toFixed(2)}</td>
                          <td className="py-2 text-gray-500">₹{c.band_high.toFixed(2)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>

              </div>

            </div>
          )}

        </div>
      )}

      {/* ========================================================================= */}
      {/* TAB 2: MACRO-FACTOR ALIGNMENT STUDIO (KRONOS + RBI) (NEW INDEPENDENT TOOL) */}
      {/* ========================================================================= */}
      {activeAiTab === 'macro' && (
        <div className="space-y-6 animate-fadeIn">
          
          {/* Indian Macro HUD Banner */}
          {macroFactors && (
            <div className="bg-gradient-to-r from-gray-900 via-indigo-950/40 to-gray-900 p-5 rounded-2xl border border-indigo-900/40 shadow-xl space-y-4">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-gray-800/80 pb-3">
                <div className="flex items-center space-x-2">
                  <Database className="w-4 h-4 text-cyan-400" />
                  <h3 className="text-sm font-bold text-white uppercase tracking-wider font-mono">
                    Indian Macroeconomic Factors HUD (Zero-Lookahead Synchronized)
                  </h3>
                </div>
                <div className="flex items-center space-x-2 text-[11px] font-mono text-emerald-400 bg-emerald-950/40 px-2.5 py-1 rounded-lg border border-emerald-500/30">
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  <span>Statutory 12-Day Publication Lag Enforced</span>
                </div>
              </div>

              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 font-mono text-xs">
                
                {/* RBI Repo Rate */}
                <div className="bg-gray-950/80 p-3.5 rounded-xl border border-gray-800 space-y-1">
                  <span className="text-[10px] text-gray-400 uppercase font-bold block">{macroFactors.rbi_repo_rate?.label}</span>
                  <div className="text-xl font-black text-cyan-300">{macroFactors.rbi_repo_rate?.value}%</div>
                  <div className="text-[11px] text-emerald-400 font-sans">{macroFactors.rbi_repo_rate?.stance}</div>
                  <div className="text-[10px] text-gray-500 pt-1 border-t border-gray-800/60">
                    Effective: {macroFactors.rbi_repo_rate?.effective_date}
                  </div>
                </div>

                {/* MoSPI CPI Inflation */}
                <div className="bg-gray-950/80 p-3.5 rounded-xl border border-gray-800 space-y-1">
                  <span className="text-[10px] text-gray-400 uppercase font-bold block">{macroFactors.india_cpi_inflation?.label}</span>
                  <div className="text-xl font-black text-emerald-300">{macroFactors.india_cpi_inflation?.value}%</div>
                  <div className="text-[11px] text-gray-300 font-sans">{macroFactors.india_cpi_inflation?.status}</div>
                  <div className="text-[10px] text-gray-500 pt-1 border-t border-gray-800/60">
                    Released: {macroFactors.india_cpi_inflation?.release_date}
                  </div>
                </div>

                {/* 10Y Sovereign Yield */}
                <div className="bg-gray-950/80 p-3.5 rounded-xl border border-gray-800 space-y-1">
                  <span className="text-[10px] text-gray-400 uppercase font-bold block">10Y Sovereign Yield</span>
                  <div className="text-xl font-black text-amber-300">{macroFactors.india_10y_yield?.value}%</div>
                  <div className="text-[11px] text-gray-400 font-sans">Benchmark Spread</div>
                  <div className="text-[10px] text-gray-500 pt-1 border-t border-gray-800/60">
                    Change: {macroFactors.india_10y_yield?.change_bps} bps
                  </div>
                </div>

                {/* USD / INR Forex */}
                <div className="bg-gray-950/80 p-3.5 rounded-xl border border-gray-800 space-y-1">
                  <span className="text-[10px] text-gray-400 uppercase font-bold block">USD / INR Parity</span>
                  <div className="text-xl font-black text-purple-300">₹{macroFactors.usdinr?.value}</div>
                  <div className="text-[11px] text-gray-400 font-sans">Forex Capital Flow</div>
                  <div className="text-[10px] text-gray-500 pt-1 border-t border-gray-800/60">
                    Day Change: +{macroFactors.usdinr?.change_pct}%
                  </div>
                </div>

              </div>
            </div>
          )}

          {/* Alignment Control & Parameter Bar */}
          <div className="bg-gray-900/90 p-4 rounded-xl border border-gray-800 flex flex-col md:flex-row md:items-center justify-between gap-4 shadow-lg">
            
            {/* Ticker Search */}
            <div className="flex-1 max-w-md">
              <StockSearchInput
                value={tickerInput}
                onSelectStock={(sym) => {
                  setTickerInput(sym);
                  setActiveTicker(sym);
                  runMacroPipeline(sym, forwardHorizon, targetThresholdPct);
                }}
                placeholder="Search equity symbol (e.g. RELIANCE, HDFCBANK, TCS)..."
              />
            </div>

            {/* Pipeline Parameters */}
            <div className="flex flex-wrap items-center gap-3 text-xs">
              
              {/* Forecast Horizon */}
              <div className="flex items-center space-x-1.5 bg-gray-950 px-2.5 py-1.5 rounded-lg border border-gray-800">
                <span className="text-gray-400 font-medium">Forward Horizon:</span>
                <select
                  value={forwardHorizon}
                  onChange={(e) => {
                    const h = Number(e.target.value);
                    setForwardHorizon(h);
                    runMacroPipeline(activeTicker, h, targetThresholdPct);
                  }}
                  className="bg-transparent text-cyan-300 font-semibold focus:outline-none cursor-pointer font-mono"
                >
                  <option value={2} className="bg-gray-900">2 Days (Momentum Scalp)</option>
                  <option value={5} className="bg-gray-900">5 Days (Standard Swing)</option>
                  <option value={10} className="bg-gray-900">10 Days (Multi-Session)</option>
                  <option value={20} className="bg-gray-900">20 Days (Monthly Trend)</option>
                </select>
              </div>

              {/* Breakout Target Threshold */}
              <div className="flex items-center space-x-1.5 bg-gray-950 px-2.5 py-1.5 rounded-lg border border-gray-800">
                <span className="text-gray-400 font-medium">Target Threshold:</span>
                <select
                  value={targetThresholdPct}
                  onChange={(e) => {
                    const th = Number(e.target.value);
                    setTargetThresholdPct(th);
                    runMacroPipeline(activeTicker, forwardHorizon, th);
                  }}
                  className="bg-transparent text-emerald-300 font-semibold focus:outline-none cursor-pointer font-mono"
                >
                  <option value={0.5} className="bg-gray-900">&gt; +0.5% Breakout</option>
                  <option value={1.0} className="bg-gray-900">&gt; +1.0% Expansion</option>
                  <option value={2.0} className="bg-gray-900">&gt; +2.0% High Alpha</option>
                </select>
              </div>

              {/* Run Pipeline Button */}
              <button
                onClick={() => runMacroPipeline(activeTicker, forwardHorizon, targetThresholdPct)}
                disabled={macroLoading}
                className="px-4 py-2 rounded-lg bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white text-xs font-bold transition-all shadow-md flex items-center space-x-1.5 disabled:opacity-50"
              >
                {macroLoading ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <Zap className="w-3.5 h-3.5" />}
                <span>{macroLoading ? "Aligning..." : "Run Macro Alignment"}</span>
              </button>
            </div>
          </div>

          {/* Quick Ticker Chips for Macro */}
          <div className="flex items-center space-x-2 overflow-x-auto pb-1 text-xs">
            <span className="text-gray-500 text-[11px] font-semibold uppercase tracking-wider whitespace-nowrap">Nifty Leaders:</span>
            {QUICK_TICKERS.map((t) => (
              <button
                key={t.symbol}
                onClick={() => {
                  setTickerInput(t.symbol);
                  setActiveTicker(t.symbol);
                  runMacroPipeline(t.symbol, forwardHorizon, targetThresholdPct);
                }}
                className={`px-2.5 py-1 rounded-lg border font-mono whitespace-nowrap transition-all ${
                  activeTicker === t.symbol 
                    ? 'bg-indigo-600/30 text-indigo-300 border-indigo-500 font-semibold' 
                    : 'bg-gray-900/60 text-gray-400 border-gray-800 hover:bg-gray-800 hover:text-white'
                }`}
              >
                {t.name}
              </button>
            ))}
          </div>

          {/* Macro Error Message */}
          {macroError && (
            <div className="p-4 bg-red-950/40 border border-red-800/80 rounded-xl flex items-center space-x-3 text-red-300 text-xs">
              <AlertTriangle className="w-5 h-5 flex-shrink-0" />
              <span>{macroError}</span>
            </div>
          )}

          {/* Macro Loading Skeleton */}
          {macroLoading && (
            <div className="h-64 bg-gray-900/40 border border-gray-800 rounded-2xl flex flex-col items-center justify-center space-y-3">
              <RefreshCw className="w-8 h-8 text-indigo-400 animate-spin" />
              <p className="text-xs text-gray-400 font-medium">
                Extracting 64D Kronos Causal Transformer Embeddings &amp; Aligning Zero-Lookahead Macro Factors for {activeTicker}...
              </p>
            </div>
          )}

          {/* Macro Results View */}
          {!macroLoading && macroResult && (
            <div className="space-y-6">
              
              {/* Primary Prediction Verdict Card */}
              <div className={`p-6 rounded-2xl border shadow-xl space-y-4 ${
                macroResult.live_prediction?.verdict_color === 'emerald' ? 'bg-emerald-950/30 border-emerald-500/40' :
                macroResult.live_prediction?.verdict_color === 'cyan' ? 'bg-cyan-950/30 border-cyan-500/40' :
                macroResult.live_prediction?.verdict_color === 'amber' ? 'bg-amber-950/30 border-amber-500/40' :
                'bg-rose-950/30 border-rose-500/40'
              }`}>
                <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
                  <div className="space-y-1">
                    <div className="flex items-center space-x-2">
                      <span className={`text-[10px] uppercase font-bold tracking-wider px-2.5 py-0.5 rounded-full border ${
                        macroResult.live_prediction?.verdict_color === 'emerald' ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40' :
                        macroResult.live_prediction?.verdict_color === 'cyan' ? 'bg-cyan-500/20 text-cyan-300 border-cyan-500/40' :
                        macroResult.live_prediction?.verdict_color === 'amber' ? 'bg-amber-500/20 text-amber-300 border-amber-500/40' :
                        'bg-rose-500/20 text-rose-300 border-rose-500/40'
                      }`}>
                        Stage 3 Ensemble Verdict • {macroResult.ticker}
                      </span>
                      <span className="text-xs text-gray-400 font-mono">As of {macroResult.live_prediction?.as_of_date}</span>
                    </div>

                    <h2 className="text-xl sm:text-2xl font-black text-white tracking-tight">
                      {macroResult.live_prediction?.verdict_title}
                    </h2>
                    <p className="text-xs text-gray-300 max-w-3xl leading-relaxed">
                      {macroResult.live_prediction?.action_summary}
                    </p>
                  </div>

                  {/* Probability KPI Box */}
                  <div className="bg-gray-950/90 p-4 rounded-xl border border-gray-800 text-center flex-shrink-0 min-w-[200px] space-y-1">
                    <span className="text-[10px] uppercase font-bold text-gray-400 block">Forward {macroResult.horizon_days}D Breakout Prob</span>
                    <div className={`text-3xl font-black font-mono ${
                      macroResult.live_prediction?.bullish_probability_pct >= 60 ? 'text-emerald-400' :
                      macroResult.live_prediction?.bullish_probability_pct >= 50 ? 'text-cyan-400' :
                      macroResult.live_prediction?.bullish_probability_pct >= 40 ? 'text-amber-400' :
                      'text-rose-400'
                    }`}>
                      {macroResult.live_prediction?.bullish_probability_pct}%
                    </div>
                    <div className="text-[11px] text-gray-400 font-mono">
                      Target: &gt; +{macroResult.target_threshold_pct}% | Confidence: {macroResult.live_prediction?.confidence_score}%
                    </div>
                  </div>
                </div>

                {/* Quick Action Workflow Links */}
                <div className="flex flex-wrap items-center gap-2 pt-3 border-t border-gray-800/80 text-xs">
                  <span className="text-gray-400 text-[11px] font-semibold uppercase">Action Workflows:</span>
                  <button
                    onClick={() => onSelectTicker(macroResult.ticker)}
                    className="px-3 py-1.5 bg-gray-900 hover:bg-gray-800 text-cyan-300 border border-gray-800 hover:border-cyan-500/40 rounded-lg font-medium transition-colors flex items-center space-x-1.5"
                  >
                    <BarChart2 className="w-3.5 h-3.5" />
                    <span>View in Chart Studio</span>
                  </button>
                  <button
                    onClick={() => onOpenBacktest && onOpenBacktest(macroResult.ticker)}
                    className="px-3 py-1.5 bg-gray-900 hover:bg-gray-800 text-purple-300 border border-gray-800 hover:border-purple-500/40 rounded-lg font-medium transition-colors flex items-center space-x-1.5"
                  >
                    <TrendingUp className="w-3.5 h-3.5" />
                    <span>Backtest Strategy</span>
                  </button>
                  <button
                    onClick={() => onOpenRisk && onOpenRisk(macroResult.ticker)}
                    className="px-3 py-1.5 bg-gray-900 hover:bg-gray-800 text-emerald-300 border border-gray-800 hover:border-emerald-500/40 rounded-lg font-medium transition-colors flex items-center space-x-1.5"
                  >
                    <ShieldAlert className="w-3.5 h-3.5" />
                    <span>1% Risk Sizing</span>
                  </button>
                </div>
              </div>

              {/* 2-Column Analytics Grid */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                
                {/* Left Column: Feature Attribution & Category Weights */}
                <div className="bg-gray-900/90 p-5 rounded-2xl border border-gray-800 shadow-xl space-y-4">
                  <div className="flex items-center space-x-2 border-b border-gray-800/80 pb-3">
                    <Activity className="w-4 h-4 text-cyan-400" />
                    <h3 className="text-sm font-bold text-white uppercase tracking-wider font-mono">
                      Multi-Factor Attribution &amp; Feature Importance
                    </h3>
                  </div>

                  {/* Category Attribution Weight Bars */}
                  <div className="space-y-2.5">
                    <span className="text-[11px] uppercase font-bold text-gray-400 tracking-wider block">
                      Factor Category Contribution Breakdown:
                    </span>
                    {Object.entries(macroResult.feature_attribution?.category_breakdown || {}).map(([cat, weight]) => (
                      <div key={cat} className="space-y-1">
                        <div className="flex justify-between text-xs font-mono">
                          <span className="text-gray-300">{cat}</span>
                          <span className="text-cyan-300 font-bold">{weight}%</span>
                        </div>
                        <div className="w-full bg-gray-950 h-2 rounded-full overflow-hidden border border-gray-800">
                          <div
                            className={`h-full ${
                              cat === 'Market Embedding' ? 'bg-cyan-400' :
                              cat === 'Monetary Policy' ? 'bg-indigo-400' :
                              cat === 'Inflation Environment' ? 'bg-emerald-400' :
                              cat === 'Bond Market' ? 'bg-amber-400' : 'bg-purple-400'
                            }`}
                            style={{ width: `${weight}%` }}
                          ></div>
                        </div>
                      </div>
                    ))}
                  </div>

                  {/* Top 10 Features List */}
                  <div className="pt-3 border-t border-gray-800/80 space-y-2">
                    <span className="text-[11px] uppercase font-bold text-gray-400 tracking-wider block">
                      Top 10 Downstream Ensemble Drivers:
                    </span>
                    <div className="space-y-1.5 font-mono text-xs max-h-48 overflow-y-auto pr-1">
                      {macroResult.feature_attribution?.top_features?.map((f, i) => (
                        <div key={i} className="flex items-center justify-between p-2 rounded-lg bg-gray-950/60 border border-gray-800/60">
                          <div className="flex items-center space-x-2">
                            <span className="text-gray-500 text-[10px]">#{i + 1}</span>
                            <span className="text-gray-200 font-semibold">{f.display_name}</span>
                          </div>
                          <span className="text-cyan-400 font-bold">{f.importance}%</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>

                {/* Right Column: Model Performance & 3-Stage Pipeline Architecture */}
                <div className="space-y-6">
                  
                  {/* Model Validation Scorecard */}
                  <div className="bg-gray-900/90 p-5 rounded-2xl border border-gray-800 shadow-xl space-y-4">
                    <div className="flex items-center space-x-2 border-b border-gray-800/80 pb-3">
                      <Gauge className="w-4 h-4 text-emerald-400" />
                      <h3 className="text-sm font-bold text-white uppercase tracking-wider font-mono">
                        Out-of-Sample Performance Scorecard
                      </h3>
                    </div>

                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 font-mono text-center">
                      <div className="bg-gray-950/80 p-3 rounded-xl border border-gray-800">
                        <span className="text-[10px] text-gray-500 uppercase block font-semibold">Accuracy</span>
                        <span className="text-lg font-black text-cyan-300">{macroResult.model_performance?.out_of_sample_accuracy_pct}%</span>
                      </div>
                      <div className="bg-gray-950/80 p-3 rounded-xl border border-gray-800">
                        <span className="text-[10px] text-gray-500 uppercase block font-semibold">Precision</span>
                        <span className="text-lg font-black text-emerald-300">{macroResult.model_performance?.precision_pct}%</span>
                      </div>
                      <div className="bg-gray-950/80 p-3 rounded-xl border border-gray-800">
                        <span className="text-[10px] text-gray-500 uppercase block font-semibold">Recall</span>
                        <span className="text-lg font-black text-indigo-300">{macroResult.model_performance?.recall_pct}%</span>
                      </div>
                      <div className="bg-gray-950/80 p-3 rounded-xl border border-gray-800">
                        <span className="text-[10px] text-gray-500 uppercase block font-semibold">F1-Score</span>
                        <span className="text-lg font-black text-amber-300">{macroResult.model_performance?.f1_score_pct}%</span>
                      </div>
                    </div>

                    <div className="text-xs text-gray-400 space-y-1 bg-gray-950/60 p-3 rounded-xl border border-gray-800 font-mono">
                      <div className="flex justify-between">
                        <span>Total Historical Samples:</span>
                        <span className="text-white font-bold">{macroResult.model_performance?.total_samples} bars</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Train / Test Split:</span>
                        <span className="text-cyan-300 font-bold">{macroResult.model_performance?.train_samples} Train / {macroResult.model_performance?.test_samples} Test</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Time-Series Shuffling:</span>
                        <span className="text-emerald-400 font-bold">Strictly Disabled (Zero Leakage)</span>
                      </div>
                    </div>
                  </div>

                  {/* 3-Stage Pipeline Architecture Infographic */}
                  <div className="bg-gray-900/90 p-5 rounded-2xl border border-gray-800 shadow-xl space-y-3 text-xs">
                    <span className="text-[11px] uppercase font-bold text-gray-400 tracking-wider block font-mono">
                      Two-Stage Alignment Pipeline Architecture:
                    </span>
                    
                    <div className="space-y-2">
                      <div className="p-3 rounded-xl bg-cyan-950/20 border border-cyan-500/30 text-gray-300 space-y-1">
                        <span className="font-bold text-cyan-300 flex items-center gap-1.5">
                          <span>1️⃣ Stage 1: Dense Temporal Market Embedding</span>
                        </span>
                        <p className="text-[11px] text-gray-400">
                          2-Layer Causal Transformer encodes 20-day [20, 6] OHLCVA sequences into 64-dimensional latent state embeddings (h_t).
                        </p>
                      </div>

                      <div className="p-3 rounded-xl bg-indigo-950/20 border border-indigo-500/30 text-gray-300 space-y-1">
                        <span className="font-bold text-indigo-300 flex items-center gap-1.5">
                          <span>2️⃣ Stage 2: Zero-Lookahead Macro Synchronization</span>
                        </span>
                        <p className="text-[11px] text-gray-400">
                          Calendar-aware backward as-of merge enforcing statutory 12-day MoSPI CPI lags and RBI MPC rate updates.
                        </p>
                      </div>

                      <div className="p-3 rounded-xl bg-emerald-950/20 border border-emerald-500/30 text-gray-300 space-y-1">
                        <span className="font-bold text-emerald-300 flex items-center gap-1.5">
                          <span>3️⃣ Stage 3: Chronological Ensemble Downstream</span>
                        </span>
                        <p className="text-[11px] text-gray-400">
                          Random Forest Classifier fuses latent market embeddings with macro factors (Repo Rate, CPI Inflation, Sovereign Yield, USD/INR) to predict forward swing probabilities.
                        </p>
                      </div>
                    </div>
                  </div>

                </div>

              </div>

            </div>
          )}

        </div>
      )}

    </div>
  );
}
