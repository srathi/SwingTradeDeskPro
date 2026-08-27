import React, { useState, useEffect } from 'react';
import { 
  Sparkles, Search, TrendingUp, TrendingDown, ShieldAlert, 
  BarChart2, RefreshCw, Download, Layers, Activity, Cpu, 
  CheckCircle2, AlertTriangle, ArrowUpRight, ArrowDownRight, Compass
} from 'lucide-react';
import { fetchAIForecast, fetchAIModelStatus } from '../services/api';

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
  const [tickerInput, setTickerInput] = useState(selectedTicker);
  const [activeTicker, setActiveTicker] = useState(selectedTicker);
  const [predLen, setPredLen] = useState(15);
  const [paths, setPaths] = useState(20);
  const [modelType, setModelType] = useState("mini");
  const [loading, setLoading] = useState(false);
  const [forecastData, setForecastData] = useState(null);
  const [errorMsg, setErrorMsg] = useState(null);
  const [modelStatus, setModelStatus] = useState(null);
  const [showGhostPaths, setShowGhostPaths] = useState(true);

  useEffect(() => {
    fetchAIModelStatus().then(setModelStatus).catch(() => {});
  }, []);

  useEffect(() => {
    if (selectedTicker && selectedTicker !== activeTicker) {
      setTickerInput(selectedTicker);
      setActiveTicker(selectedTicker);
      runForecast(selectedTicker, predLen, paths, modelType);
    }
  }, [selectedTicker]);

  useEffect(() => {
    runForecast(activeTicker, predLen, paths, modelType);
  }, [predLen, paths, modelType]);

  const runForecast = async (symbol, horizon, samplePaths, modelTier) => {
    if (!symbol) return;
    setLoading(true);
    setErrorMsg(null);
    try {
      const data = await fetchAIForecast(symbol, horizon, samplePaths, modelTier);
      setForecastData(data);
    } catch (err) {
      setErrorMsg(err.message || "Failed to generate AI forecast.");
      setForecastData(null);
    } finally {
      setLoading(false);
    }
  };

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    if (!tickerInput.trim()) return;
    setActiveTicker(tickerInput.trim().toUpperCase());
    runForecast(tickerInput.trim().toUpperCase(), predLen, paths, modelType);
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

      {/* Control & Search Bar */}
      <div className="bg-gray-900/90 p-4 rounded-xl border border-gray-800 flex flex-col md:flex-row md:items-center justify-between gap-4 shadow-lg">
        
        {/* Ticker Search */}
        <form onSubmit={handleSearchSubmit} className="flex items-center space-x-2 flex-1 max-w-md">
          <div className="relative flex-1">
            <Search className="w-4 h-4 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={tickerInput}
              onChange={(e) => setTickerInput(e.target.value)}
              placeholder="Enter symbol (e.g. RELIANCE.NS, TCS.NS)..."
              className="w-full bg-gray-950 text-white pl-9 pr-3 py-2 rounded-lg border border-gray-700 focus:border-cyan-500 focus:outline-none text-xs font-mono"
            />
          </div>
          <button
            type="submit"
            disabled={loading}
            className="px-4 py-2 bg-cyan-600 hover:bg-cyan-500 text-white rounded-lg text-xs font-semibold flex items-center space-x-1.5 transition-colors disabled:opacity-50"
          >
            {loading ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <Sparkles className="w-3.5 h-3.5" />}
            <span>Forecast</span>
          </button>
        </form>

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

      {/* Error Message */}
      {errorMsg && (
        <div className="p-4 bg-red-950/40 border border-red-800/80 rounded-xl text-red-300 text-xs flex items-center space-x-3">
          <AlertTriangle className="w-5 h-5 flex-shrink-0" />
          <span>{errorMsg}</span>
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
  );
}
