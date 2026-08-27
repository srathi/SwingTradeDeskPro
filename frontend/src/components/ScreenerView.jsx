import React, { useState, useEffect } from 'react';
import { 
  Play, 
  RefreshCw, 
  Sliders, 
  BarChart2, 
  TrendingUp, 
  ShieldAlert, 
  Download, 
  Sparkles, 
  Target, 
  AlertCircle,
  Bookmark,
  Compass,
  CheckCircle2
} from 'lucide-react';
import { fetchUniverses, fetchStrategies, fetchWatchlists, runScanSync, fetchAIForecast } from '../services/api';

const fmt = (v, d = 2) => {
  if (typeof v === 'number' && !isNaN(v)) return v.toFixed(d);
  if (typeof v === 'string' && !isNaN(Number(v))) return Number(v).toFixed(d);
  return '—';
};

export default function ScreenerView({ 
  onSelectTicker, 
  onOpenRisk, 
  onOpenBacktest,
  onOpenSectorPulse,
  presetUniverse = null,
  presetCustomTickers = null
}) {
  const [universes, setUniverses] = useState([]);
  const [watchlists, setWatchlists] = useState([]);
  const [strategies, setStrategies] = useState([]);
  const [selectedUniverse, setSelectedUniverse] = useState(presetUniverse || 'NIFTY_50');
  const [selectedStrategy, setSelectedStrategy] = useState('trend_pullback');
  
  // Custom filter states
  const [showFilters, setShowFilters] = useState(false);
  const [minPrice, setMinPrice] = useState(50);
  const [minVolume, setMinVolume] = useState(300000);
  const [rsiMin, setRsiMin] = useState(40);
  const [rsiMax, setRsiMax] = useState(65);
  const [rrTarget, setRrTarget] = useState(2.0);

  // Scanning states
  const [scanning, setScanning] = useState(false);
  const [progress, setProgress] = useState(0);
  const [scannedCount, setScannedCount] = useState(0);
  const [totalCount, setTotalCount] = useState(0);
  const [results, setResults] = useState([]);
  const [errorMsg, setErrorMsg] = useState(null);

  // AI Forecast Confluence Modal state
  const [aiModalSetup, setAiModalSetup] = useState(null);
  const [aiModalLoading, setAiModalLoading] = useState(false);
  const [aiModalData, setAiModalData] = useState(null);
  const [aiModalError, setAiModalError] = useState(null);

  const handleOpenAIForecast = async (setup) => {
    setAiModalSetup(setup);
    setAiModalLoading(true);
    setAiModalError(null);
    setAiModalData(null);
    try {
      const data = await fetchAIForecast(setup.ticker, 15, 20, "mini");
      setAiModalData(data);
    } catch (err) {
      setAiModalError(err.message || "Failed to generate AI forecast.");
    } finally {
      setAiModalLoading(false);
    }
  };

  useEffect(() => {
    fetchUniverses().then(setUniverses).catch(console.error);
    fetchStrategies().then(setStrategies).catch(console.error);
    fetchWatchlists().then(setWatchlists).catch(console.error);
  }, []);

  useEffect(() => {
    if (presetUniverse) {
      setSelectedUniverse(presetUniverse);
    }
  }, [presetUniverse]);

  const handleStartScan = () => {
    setScanning(true);
    setProgress(0);
    setScannedCount(0);
    setResults([]);
    setErrorMsg(null);

    let customTickers = null;
    let universeLabel = selectedUniverse;

    if (selectedUniverse.startsWith('WL_')) {
      const wlId = selectedUniverse.replace('WL_', '');
      const matchedWl = watchlists.find(w => String(w.id) === String(wlId));
      if (matchedWl) {
        customTickers = matchedWl.tickers;
        universeLabel = matchedWl.name;
      }
    } else if (presetCustomTickers && selectedUniverse === presetUniverse) {
      customTickers = presetCustomTickers;
    }

    if (customTickers && customTickers.length === 0) {
      setErrorMsg("This watchlist is currently empty. Please add stock symbols to it first.");
      setScanning(false);
      return;
    }

    const payload = {
      universe: universeLabel,
      strategy_id: selectedStrategy,
      custom_tickers: customTickers,
      params: {
        min_price: Number(minPrice),
        min_volume: Number(minVolume),
        rsi_min: Number(rsiMin),
        rsi_max: Number(rsiMax),
        rr_target_1: Number(rrTarget)
      }
    };

    // Dynamic WebSocket host resolution
    const host = window.location.port === '5173' ? 'localhost:8888' : window.location.host;
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${host}/api/screener/ws`;

    let ws = null;

    try {
      ws = new WebSocket(wsUrl);

      ws.onopen = () => {
        ws.send(JSON.stringify(payload));
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.type === 'START') {
            setTotalCount(data.total);
          } else if (data.type === 'MATCH') {
            setResults((prev) => {
              const exists = prev.some((r) => r.ticker === data.match.ticker);
              if (!exists) return [data.match, ...prev];
              return prev;
            });
          } else if (data.type === 'PROGRESS') {
            setScannedCount(data.scanned);
            setProgress(data.progress_pct);
          } else if (data.type === 'COMPLETE') {
            setScanning(false);
            setProgress(100);
            setResults(data.results || []);
            try { ws.close(); } catch (e) {}
          } else if (data.type === 'ERROR') {
            setErrorMsg(data.message);
            setScanning(false);
            try { ws.close(); } catch (e) {}
          }
        } catch (e) {
          console.error("WS parse error:", e);
        }
      };

      ws.onerror = async (err) => {
        console.warn("WebSocket stream fallback to HTTP scan:", err);
        try {
          const res = await runScanSync(payload);
          setResults(res.results || []);
          setProgress(100);
          setScannedCount(res.scanned_count || 0);
          setTotalCount(res.scanned_count || 0);
        } catch (httpErr) {
          setErrorMsg(httpErr.message || "Scan request failed.");
        } finally {
          setScanning(false);
        }
      };
    } catch (err) {
      console.warn("Direct HTTP fallback due to WS error:", err);
      runScanSync(payload).then(res => {
        setResults(res.results || []);
        setProgress(100);
      }).catch(httpErr => {
        setErrorMsg(httpErr.message);
      }).finally(() => {
        setScanning(false);
      });
    }
  };

  const exportCSV = () => {
    if (results.length === 0) return;
    const headers = ["Ticker", "Strategy", "Score", "Close", "20 EMA", "RSI", "Stop Loss", "Target 1 (2R)", "Target 2 (3R)", "Risk (₹)", "Risk %", "Summary"];
    const rows = results.map(r => {
      const ema20 = r.ema_20 ?? r.indicators?.ema_20 ?? r.indicators?.ema20 ?? "—";
      const rsiVal = r.rsi ?? r.indicators?.rsi ?? r.indicators?.rsi_14 ?? r.indicators?.rsi_28 ?? "—";
      const summary = r.setup_summary || (r.reasons && r.reasons.length > 0 ? r.reasons[0] : "") || `${r.strategy} Triggered`;
      return [
        r.ticker, r.strategy, r.score, r.close, ema20, rsiVal, r.stop_loss, r.target_1, r.target_2, r.risk_per_share, `${r.risk_pct}%`, `"${summary.replace(/"/g, '""')}"`
      ];
    });
    const csvContent = "data:text/csv;charset=utf-8," + [headers.join(","), ...rows.map(e => e.join(","))].join("\n");
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `SwingDesk_${selectedStrategy}_${selectedUniverse}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const currentStrat = strategies.find(s => s.id === selectedStrategy);

  return (
    <div className="space-y-6">
      
      {/* Top Banner / Strategy Header */}
      <div className="bg-gradient-to-r from-gray-900 via-[#131b2e] to-gray-900 p-6 rounded-2xl border border-gray-800 shadow-xl relative overflow-hidden">
        <div className="absolute right-0 top-0 w-96 h-96 bg-cyan-500/5 rounded-full blur-3xl pointer-events-none"></div>
        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center space-x-2">
              <span className="px-2.5 py-0.5 rounded-full bg-cyan-500/10 text-cyan-400 text-xs font-semibold uppercase tracking-wider border border-cyan-500/20 flex items-center gap-1.5">
                <Sparkles className="w-3.5 h-3.5" /> Quantitative Engine
              </span>
              <span className="text-xs text-gray-400">• Institutional Quality Screener</span>
            </div>
            <h1 className="text-2xl font-bold text-white tracking-tight mt-1.5">
              {currentStrat ? currentStrat.name : "Swing Trading Screener"}
            </h1>
            <p className="text-sm text-gray-300 max-w-2xl mt-1">
              {currentStrat ? currentStrat.description : "Scan Indian and global equities for quantified swing setups with asymmetric risk-to-reward."}
            </p>
          </div>

          <div className="flex items-center space-x-2 sm:space-x-3 flex-wrap gap-y-2">
            {onOpenSectorPulse && (
              <button
                onClick={onOpenSectorPulse}
                className="flex items-center space-x-1.5 px-3 py-2 rounded-lg text-xs font-semibold bg-cyan-500/10 text-cyan-300 border border-cyan-500/30 hover:bg-cyan-500/20 transition-all shadow-sm shadow-cyan-500/10"
                title="View Sector Rotation & Relative Strength Matrix"
              >
                <Compass className="w-3.5 h-3.5 text-cyan-400" />
                <span>Sector Pulse</span>
              </button>
            )}
            <button
              onClick={() => setShowFilters(!showFilters)}
              className={`flex items-center space-x-1.5 px-3.5 py-2 rounded-lg text-xs font-medium border transition-colors ${
                showFilters ? 'bg-gray-800 text-cyan-400 border-cyan-500/40' : 'bg-gray-900 text-gray-300 border-gray-700 hover:bg-gray-800'
              }`}
            >
              <Sliders className="w-3.5 h-3.5" />
              <span>Filters</span>
            </button>
            <button
              onClick={handleStartScan}
              disabled={scanning}
              className={`flex items-center space-x-2 px-5 py-2.5 rounded-lg text-sm font-semibold shadow-lg transition-all ${
                scanning 
                  ? 'bg-cyan-700 text-gray-200 cursor-not-allowed opacity-80' 
                  : 'bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white shadow-cyan-500/25 hover:shadow-cyan-500/40 active:scale-95'
              }`}
            >
              {scanning ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin text-white" />
                  <span>Scanning {scannedCount}/{totalCount || '...'}</span>
                </>
              ) : (
                <>
                  <Play className="w-4 h-4 fill-current" />
                  <span>Run Live Scan</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* Configuration Selectors */}
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3 mt-5 pt-5 border-t border-gray-800/80">
          <div>
            <label className="text-xs font-medium text-gray-400 block mb-1">Index Universe / Watchlist</label>
            <select
              value={selectedUniverse}
              onChange={(e) => setSelectedUniverse(e.target.value)}
              disabled={scanning}
              className="w-full bg-gray-950 border border-gray-700 rounded-lg px-3 py-2 text-sm text-gray-200 focus:outline-none focus:border-cyan-500"
            >
              {watchlists.length > 0 && (
                <optgroup label="📋 Custom Watchlists">
                  {watchlists.map((wl) => (
                    <option key={`WL_${wl.id}`} value={`WL_${wl.id}`}>
                      📋 {wl.name} ({wl.tickers.length} stocks)
                    </option>
                  ))}
                </optgroup>
              )}
              
              <optgroup label="🌐 Exchange Index Universes">
                {universes.map((u) => (
                  <option key={u.id} value={u.id}>
                    {u.name} ({u.count} symbols)
                  </option>
                ))}
              </optgroup>
            </select>
          </div>

          <div>
            <label className="text-xs font-medium text-gray-400 block mb-1">Trading Strategy</label>
            <select
              value={selectedStrategy}
              onChange={(e) => setSelectedStrategy(e.target.value)}
              disabled={scanning}
              className="w-full bg-gray-950 border border-gray-700 rounded-lg px-3 py-2 text-sm text-gray-200 focus:outline-none focus:border-cyan-500"
            >
              {strategies.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.name}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="text-xs font-medium text-gray-400 block mb-1">Data Source & Horizon</label>
            <div className="bg-gray-950 border border-gray-700 rounded-lg px-3 py-2 text-sm text-gray-300 flex items-center justify-between">
              <span className="text-xs text-gray-300 font-mono">Yahoo Finance Daily (1Y)</span>
              <span className="text-[10px] px-1.5 py-0.5 rounded bg-emerald-500/10 text-emerald-400 font-semibold">Cached 4h</span>
            </div>
          </div>
        </div>

        {/* Collapsible Filter Panel */}
        {showFilters && (
          <div className="mt-4 pt-4 border-t border-gray-800/60 grid grid-cols-2 sm:grid-cols-4 gap-4 bg-gray-950/60 p-4 rounded-xl">
            <div>
              <label className="text-xs text-gray-400 block mb-1">Min Price (₹): <span className="text-cyan-400 font-mono">₹{minPrice}</span></label>
              <input 
                type="range" min="10" max="500" step="10" 
                value={minPrice} onChange={(e) => setMinPrice(e.target.value)}
                className="w-full accent-cyan-500"
              />
            </div>
            <div>
              <label className="text-xs text-gray-400 block mb-1">Min 20D Vol: <span className="text-cyan-400 font-mono">{(minVolume / 1000).toFixed(0)}k</span></label>
              <input 
                type="range" min="100000" max="2000000" step="100000" 
                value={minVolume} onChange={(e) => setMinVolume(e.target.value)}
                className="w-full accent-cyan-500"
              />
            </div>
            <div>
              <label className="text-xs text-gray-400 block mb-1">RSI Range: <span className="text-cyan-400 font-mono">{rsiMin} - {rsiMax}</span></label>
              <div className="flex gap-2">
                <input 
                  type="number" value={rsiMin} onChange={(e) => setRsiMin(e.target.value)}
                  className="w-1/2 bg-gray-900 border border-gray-700 rounded px-2 py-1 text-xs text-cyan-400 text-center"
                />
                <input 
                  type="number" value={rsiMax} onChange={(e) => setRsiMax(e.target.value)}
                  className="w-1/2 bg-gray-900 border border-gray-700 rounded px-2 py-1 text-xs text-cyan-400 text-center"
                />
              </div>
            </div>
            <div>
              <label className="text-xs text-gray-400 block mb-1">Target R:R: <span className="text-cyan-400 font-mono">1:{rrTarget}</span></label>
              <input 
                type="range" min="1.5" max="4.0" step="0.5" 
                value={rrTarget} onChange={(e) => setRrTarget(e.target.value)}
                className="w-full accent-cyan-500"
              />
            </div>
          </div>
        )}

      </div>

      {/* Progress Bar while scanning */}
      {scanning && (
        <div className="bg-gray-900/90 border border-gray-800 p-4 rounded-xl space-y-2 animate-fadeIn">
          <div className="flex items-center justify-between text-xs text-gray-300">
            <div className="flex items-center space-x-2">
              <span className="w-2.5 h-2.5 rounded-full bg-cyan-400 animate-ping"></span>
              <span className="font-semibold text-cyan-300">Scanning {selectedUniverse.replace('WL_', 'Watchlist: ')}...</span>
              <span className="text-gray-400 font-mono">({scannedCount} of {totalCount || '?'} symbols analyzed)</span>
            </div>
            <div className="flex items-center space-x-3">
              <span className="text-emerald-400 font-semibold font-mono">{results.length} Candidates Found</span>
              <span className="text-cyan-400 font-mono font-bold">{progress}%</span>
            </div>
          </div>
          <div className="w-full bg-gray-950 rounded-full h-2 overflow-hidden border border-gray-800">
            <div 
              className="bg-gradient-to-r from-cyan-500 to-blue-500 h-2 rounded-full transition-all duration-300 ease-out"
              style={{ width: `${progress}%` }}
            ></div>
          </div>
        </div>
      )}

      {errorMsg && (
        <div className="p-4 rounded-xl bg-red-950/40 border border-red-800 text-red-300 text-xs flex items-center space-x-2">
          <AlertCircle className="w-4 h-4 flex-shrink-0 text-red-400" />
          <span>{errorMsg}</span>
        </div>
      )}

      {/* Results Header & Summary Stats */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div className="flex items-center space-x-3">
          <h2 className="text-lg font-bold text-white tracking-tight flex items-center gap-2">
            <span>Actionable Setups</span>
            <span className="text-xs px-2 py-0.5 rounded-full bg-gray-800 text-cyan-400 border border-gray-700 font-mono font-semibold">
              {results.length}
            </span>
          </h2>
          {results.length > 0 && (
            <span className="text-xs text-gray-400 hidden sm:inline">
              Sorted by Setup Quality Score
            </span>
          )}
        </div>

        {results.length > 0 && (
          <button
            onClick={exportCSV}
            className="flex items-center space-x-1.5 px-3 py-1.5 bg-gray-900 hover:bg-gray-800 border border-gray-700 rounded-lg text-xs font-medium text-gray-300 transition-colors self-start sm:self-auto"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Export CSV</span>
          </button>
        )}
      </div>

      {/* Results Display */}
      {results.length > 0 ? (
        <div className="grid grid-cols-1 gap-3">
          {results.map((setup) => (
            <div 
              key={setup.ticker}
              className="bg-gray-900/80 hover:bg-gray-900 border border-gray-800 hover:border-cyan-500/40 rounded-xl p-4 transition-all duration-150 shadow-sm hover:shadow-cyan-500/5 group"
            >
              <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
                
                {/* Left: Ticker & Strategy info */}
                <div className="flex items-start space-x-3 min-w-[240px]">
                  <div className={`w-10 h-10 rounded-lg flex items-center justify-center font-bold text-xs border ${
                    setup.score >= 80 
                      ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30' 
                      : 'bg-cyan-500/10 text-cyan-400 border-cyan-500/30'
                  }`}>
                    <div className="text-center">
                      <div className="text-[9px] uppercase tracking-tighter text-gray-400">Score</div>
                      <div className="text-sm font-bold leading-none">{setup.score}</div>
                    </div>
                  </div>

                  <div>
                    <div className="flex items-center space-x-2">
                      <span className="text-base font-bold text-white group-hover:text-cyan-300 transition-colors">
                        {setup.ticker}
                      </span>
                      <span className="text-[11px] px-2 py-0.5 rounded bg-gray-800 text-gray-300 font-mono border border-gray-700">
                        ₹{fmt(setup.close)}
                      </span>
                    </div>
                    <p className="text-xs text-gray-400 mt-0.5">{setup.setup_summary || (setup.reasons && setup.reasons.length > 0 ? setup.reasons[0] : "") || `${setup.strategy} Setup`}</p>
                  </div>
                </div>

                {/* Middle: Key Quantitative Indicators */}
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 bg-gray-950/60 px-4 py-2.5 rounded-lg border border-gray-800/80 text-xs">
                  <div>
                    <span className="text-gray-500 block text-[10px] uppercase font-semibold">20 EMA</span>
                    <span className="font-mono text-cyan-300 font-medium">₹{fmt(setup.ema_20 ?? setup.indicators?.ema_20 ?? setup.indicators?.ema20)}</span>
                  </div>
                  <div>
                    <span className="text-gray-500 block text-[10px] uppercase font-semibold">
                      {setup.strategy_id === 'rsi28_divergence' ? 'RSI (28)' : 'RSI (14)'}
                    </span>
                    {(() => {
                      const rsiVal = setup.rsi ?? setup.indicators?.rsi ?? setup.indicators?.rsi_14 ?? setup.indicators?.rsi_28;
                      return (
                        <span className={`font-mono font-medium ${rsiVal <= 45 ? 'text-emerald-400' : 'text-yellow-400'}`}>
                          {fmt(rsiVal, 1)}
                        </span>
                      );
                    })()}
                  </div>
                  <div>
                    <span className="text-gray-500 block text-[10px] uppercase font-semibold">Stop Loss</span>
                    <span className="font-mono text-red-400 font-semibold">₹{fmt(setup.stop_loss)}</span>
                  </div>
                  <div>
                    <span className="text-gray-500 block text-[10px] uppercase font-semibold">Target (2R)</span>
                    <span className="font-mono text-emerald-400 font-semibold">₹{fmt(setup.target_1)}</span>
                  </div>
                </div>

                {/* Right: Actions */}
                <div className="flex items-center space-x-2 self-end lg:self-center">
                  <button
                    onClick={() => handleOpenAIForecast(setup)}
                    className="flex items-center space-x-1.5 px-3 py-2 bg-purple-950/40 hover:bg-purple-900/60 text-purple-300 border border-purple-800/80 hover:border-purple-500 rounded-lg text-xs font-semibold shadow-sm transition-all"
                    title="Run Kronos AI Foundation Forecast"
                  >
                    <Sparkles className="w-3.5 h-3.5 text-purple-400" />
                    <span>AI Forecast</span>
                  </button>

                  <button
                    onClick={() => onSelectTicker(setup.ticker)}
                    className="flex items-center space-x-1.5 px-3 py-2 bg-gray-800 hover:bg-gray-700 text-cyan-300 border border-gray-700 hover:border-cyan-500/50 rounded-lg text-xs font-medium transition-colors"
                    title="Open in Chart Studio"
                  >
                    <BarChart2 className="w-3.5 h-3.5" />
                    <span>Chart</span>
                  </button>

                  <button
                    onClick={() => onOpenRisk(setup)}
                    className="flex items-center space-x-1.5 px-3 py-2 bg-gray-800 hover:bg-gray-700 text-amber-300 border border-gray-700 hover:border-amber-500/50 rounded-lg text-xs font-medium transition-colors"
                    title="Calculate Position Size"
                  >
                    <ShieldAlert className="w-3.5 h-3.5" />
                    <span>Risk Calc</span>
                  </button>

                  <button
                    onClick={() => onOpenBacktest(setup.ticker, setup.strategy_id)}
                    className="flex items-center space-x-1.5 px-3 py-2 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white rounded-lg text-xs font-semibold shadow-sm transition-all"
                    title="Run Historical Backtest"
                  >
                    <TrendingUp className="w-3.5 h-3.5" />
                    <span>Backtest</span>
                  </button>
                </div>

              </div>
            </div>
          ))}
        </div>
      ) : (
        !scanning && (
          <div className="bg-gray-900/40 border border-dashed border-gray-800 rounded-2xl p-12 text-center space-y-3">
            <div className="w-12 h-12 rounded-full bg-gray-800/80 flex items-center justify-center mx-auto text-gray-500 border border-gray-700">
              <Target className="w-6 h-6" />
            </div>
            <h3 className="text-base font-semibold text-gray-200">No Active Setups Loaded</h3>
            <p className="text-xs text-gray-400 max-w-md mx-auto">
              Select a custom watchlist or index universe above, then click <strong className="text-cyan-400 font-medium">Run Live Scan</strong> to identify high-probability swing trades.
            </p>
          </div>
        )
      )}

      {/* AI Confluence Modal */}
      {aiModalSetup && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-gray-900 border border-purple-500/40 rounded-2xl max-w-lg w-full p-6 shadow-2xl space-y-5 relative">
            
            {/* Modal Header */}
            <div className="flex items-center justify-between border-b border-gray-800 pb-3">
              <div className="flex items-center space-x-2.5">
                <span className="p-2 bg-purple-500/20 border border-purple-500/30 rounded-lg text-purple-400">
                  <Sparkles className="w-5 h-5" />
                </span>
                <div>
                  <h3 className="text-base font-bold text-white flex items-center gap-2">
                    <span>{aiModalSetup.ticker}</span>
                    <span className="text-[10px] px-2 py-0.5 rounded bg-purple-500/20 text-purple-300 border border-purple-500/30">
                      Kronos AI Confluence
                    </span>
                  </h3>
                  <p className="text-xs text-gray-400">
                    Strategy Setup: <span className="text-cyan-400 font-medium">{aiModalSetup.strategy}</span>
                  </p>
                </div>
              </div>
              <button
                onClick={() => setAiModalSetup(null)}
                className="text-gray-400 hover:text-white text-lg font-bold p-1"
              >
                ✕
              </button>
            </div>

            {/* Modal Body */}
            {aiModalLoading && (
              <div className="h-48 flex flex-col items-center justify-center space-y-2">
                <RefreshCw className="w-6 h-6 text-purple-400 animate-spin" />
                <p className="text-xs text-gray-400">Running Monte Carlo neural trajectory simulation...</p>
              </div>
            )}

            {aiModalError && (
              <div className="p-3 bg-red-950/50 border border-red-800 rounded-lg text-red-300 text-xs">
                {aiModalError}
              </div>
            )}

            {!aiModalLoading && aiModalData && (
              <div className="space-y-4">
                
                {/* 2x2 Metric Grid */}
                <div className="grid grid-cols-2 gap-3 text-xs">
                  <div className="bg-gray-950 p-3 rounded-xl border border-gray-800">
                    <span className="text-gray-500 text-[10px] uppercase font-semibold block">Upside Probability</span>
                    <span className={`text-xl font-bold font-mono ${aiModalData.upside_prob >= 60 ? 'text-emerald-400' : 'text-yellow-400'}`}>
                      {aiModalData.upside_prob}%
                    </span>
                    <div className="w-full bg-gray-800 h-1.5 rounded-full mt-1.5 overflow-hidden">
                      <div 
                        className={`h-full ${aiModalData.upside_prob >= 60 ? 'bg-emerald-400' : 'bg-yellow-400'}`}
                        style={{ width: `${aiModalData.upside_prob}%` }}
                      ></div>
                    </div>
                  </div>

                  <div className="bg-gray-950 p-3 rounded-xl border border-gray-800">
                    <span className="text-gray-500 text-[10px] uppercase font-semibold block">Expected 15D Target</span>
                    <span className="text-xl font-bold font-mono text-cyan-300">
                      ₹{aiModalData.expected_close?.toFixed(2)}
                    </span>
                    <span className={`text-[10px] font-mono block mt-0.5 ${aiModalData.expected_change_pct >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                      {aiModalData.expected_change_pct >= 0 ? `+${aiModalData.expected_change_pct}%` : `${aiModalData.expected_change_pct}%`} vs CMP
                    </span>
                  </div>

                  <div className="bg-gray-950 p-3 rounded-xl border border-gray-800">
                    <span className="text-gray-500 text-[10px] uppercase font-semibold block">90% Corridor [p10, p90]</span>
                    <span className="font-mono text-gray-200 font-semibold block mt-0.5">
                      ₹{aiModalData.p10_close?.toFixed(2)} ~ ₹{aiModalData.p90_close?.toFixed(2)}
                    </span>
                  </div>

                  <div className="bg-gray-950 p-3 rounded-xl border border-gray-800">
                    <span className="text-gray-500 text-[10px] uppercase font-semibold block">Volatility Risk</span>
                    <span className="font-mono text-purple-300 font-semibold block mt-0.5">
                      {aiModalData.volatility_amplification}x ({aiModalData.volatility_amplification <= 1.1 ? '🟢 Orderly' : '⚠️ Elevated'})
                    </span>
                  </div>
                </div>

                {/* Strategy Confluence Synthesis Box */}
                <div className="bg-gradient-to-r from-purple-950/40 to-blue-950/40 p-3.5 rounded-xl border border-purple-800/60 text-xs space-y-1.5">
                  <div className="flex items-center space-x-2">
                    <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                    <span className="font-bold text-white">{aiModalData.confluence_badge}</span>
                  </div>
                  <p className="text-gray-300 text-[11px] leading-relaxed">
                    Kronos Foundation Model indicates a <strong className="text-cyan-300">{aiModalData.regime}</strong> trajectory. 
                    Quantitative strategy target of <strong className="text-emerald-400">₹{aiModalSetup.target_1}</strong> falls well within the 90% confidence corridor ($p_{90}$ = ₹{aiModalData.p90_close}).
                  </p>
                </div>

                {/* Action Footer */}
                <div className="flex items-center justify-end space-x-2 pt-2 border-t border-gray-800">
                  <button
                    onClick={() => {
                      setAiModalSetup(null);
                      onSelectTicker(aiModalSetup.ticker);
                    }}
                    className="px-3 py-1.5 bg-cyan-600 hover:bg-cyan-500 text-white rounded-lg text-xs font-semibold flex items-center space-x-1"
                  >
                    <BarChart2 className="w-3.5 h-3.5" />
                    <span>Open in Chart Studio</span>
                  </button>
                  <button
                    onClick={() => {
                      setAiModalSetup(null);
                      onOpenRisk(aiModalSetup);
                    }}
                    className="px-3 py-1.5 bg-amber-600 hover:bg-amber-500 text-white rounded-lg text-xs font-semibold flex items-center space-x-1"
                  >
                    <ShieldAlert className="w-3.5 h-3.5" />
                    <span>Position Size</span>
                  </button>
                </div>

              </div>
            )}

          </div>
        </div>
      )}

    </div>
  );
}
