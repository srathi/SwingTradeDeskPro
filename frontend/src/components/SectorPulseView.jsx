import React, { useState, useEffect } from 'react';
import { 
  Activity, 
  TrendingUp, 
  TrendingDown, 
  RefreshCw, 
  Compass, 
  ShieldAlert, 
  Target, 
  Clock, 
  BarChart3, 
  Zap, 
  Award, 
  CheckCircle2, 
  AlertTriangle,
  Layers,
  ArrowUpRight,
  ArrowDownRight,
  ChevronDown,
  ChevronUp,
  Sparkles,
  SlidersHorizontal,
  LineChart,
  DollarSign,
  ExternalLink,
  Flame
} from 'lucide-react';
import { fetchSectorPulse, fetchSectorConstituents } from '../services/api';

export default function SectorPulseView({ onScanSector, onSelectTicker, onOpenAIForecast, onOpenRisk, onOpenBacktest }) {
  const [market, setMarket] = useState('NSE');
  const [period, setPeriod] = useState('2y');
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState(null);
  const [selectedSector, setSelectedSector] = useState(null);
  const [filterRegime, setFilterRegime] = useState('ALL'); // ALL, UPTREND, DOWNTREND
  const [expandedSectors, setExpandedSectors] = useState(new Set());
  const [constituentsMap, setConstituentsMap] = useState({});
  const [loadingConstituents, setLoadingConstituents] = useState({});

  const loadPulse = async () => {
    setLoading(true);
    setErrorMsg(null);
    try {
      const res = await fetchSectorPulse(market, period);
      setData(res);
      if (res && res.sectors && res.sectors.length > 0) {
        setSelectedSector(res.sectors[0]);
        // Prefetch constituents for top sector
        loadConstituentsForSector(res.sectors[0].sector);
      }
    } catch (err) {
      setErrorMsg(err.message || "Failed to load sector pulse data");
    } finally {
      setLoading(false);
    }
  };

  const loadConstituentsForSector = async (sectorCode) => {
    if (!sectorCode || constituentsMap[sectorCode] || loadingConstituents[sectorCode]) return;
    setLoadingConstituents(prev => ({ ...prev, [sectorCode]: true }));
    try {
      const res = await fetchSectorConstituents(sectorCode);
      if (res && res.constituents) {
        setConstituentsMap(prev => ({ ...prev, [sectorCode]: res.constituents }));
      }
    } catch (e) {
      console.warn(`Could not load constituents for ${sectorCode}:`, e);
    } finally {
      setLoadingConstituents(prev => ({ ...prev, [sectorCode]: false }));
    }
  };

  useEffect(() => {
    loadPulse();
  }, [market, period]);

  useEffect(() => {
    if (selectedSector && selectedSector.sector) {
      loadConstituentsForSector(selectedSector.sector);
    }
  }, [selectedSector]);

  const toggleExpandSector = (sectorCode, e) => {
    e.stopPropagation();
    loadConstituentsForSector(sectorCode);
    setExpandedSectors(prev => {
      const next = new Set(prev);
      if (next.has(sectorCode)) {
        next.delete(sectorCode);
      } else {
        next.add(sectorCode);
      }
      return next;
    });
  };

  const filteredSectors = data && data.sectors ? data.sectors.filter(s => {
    if (filterRegime === 'UPTREND') return s.regime.trend_classification.includes('UPTREND');
    if (filterRegime === 'DOWNTREND') return s.regime.trend_classification.includes('DOWNTREND');
    return true;
  }) : [];

  const selectedConstituents = selectedSector ? (constituentsMap[selectedSector.sector] || selectedSector.top_constituents || []) : [];
  const isSelectedLoadingConstituents = selectedSector ? loadingConstituents[selectedSector.sector] : false;

  return (
    <div className="space-y-6">
      
      {/* Header Banner */}
      <div className="bg-gradient-to-r from-[#0c1427] via-[#091122] to-[#060a16] border border-cyan-500/20 rounded-2xl p-6 shadow-xl relative overflow-hidden">
        <div className="absolute -right-16 -top-16 w-64 h-64 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none"></div>
        <div className="relative z-10 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          
          <div className="flex items-center space-x-3.5">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-tr from-cyan-600/30 to-blue-500/20 border border-cyan-500/40 flex items-center justify-center text-cyan-400 shadow-lg shadow-cyan-500/10">
              <Compass className="w-6 h-6 animate-spin-slow" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-xl sm:text-2xl font-bold text-white tracking-tight">SectorPulse</h1>
                <span className="text-xs px-2.5 py-0.5 rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 font-mono font-semibold uppercase">
                  Regime & Relative Strength Forecaster
                </span>
              </div>
              <p className="text-xs sm:text-sm text-gray-400 mt-1">
                Top-Down Macro Rotation, Mansfield RS, Hurst Persistence ($H$), and Ranked Constituent Leaders by <a href="https://www.rupeemap.in" target="_blank" rel="noopener noreferrer" className="text-cyan-400 font-medium hover:underline hover:text-cyan-300 transition-colors">rupeemap.in labs</a>.
              </p>
            </div>
          </div>

          {/* Controls */}
          <div className="flex items-center gap-2.5 self-start md:self-auto flex-wrap">
            <div className="flex bg-gray-950 p-1 rounded-xl border border-gray-800 text-xs">
              <button
                onClick={() => setMarket('NSE')}
                className={`px-3 py-1.5 rounded-lg transition-colors font-medium ${
                  market === 'NSE' ? 'bg-cyan-600 text-white shadow-sm' : 'text-gray-400 hover:text-gray-200'
                }`}
              >
                NSE India
              </button>
              <button
                onClick={() => setMarket('US')}
                className={`px-3 py-1.5 rounded-lg transition-colors font-medium ${
                  market === 'US' ? 'bg-cyan-600 text-white shadow-sm' : 'text-gray-400 hover:text-gray-200'
                }`}
              >
                US Sectors
              </button>
            </div>

            <button
              onClick={loadPulse}
              disabled={loading}
              className="p-2 bg-gray-900 hover:bg-gray-800 border border-gray-700 text-gray-300 rounded-xl transition-all"
              title="Refresh Sector Feeds"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin text-cyan-400' : ''}`} />
            </button>
          </div>

        </div>
      </div>

      {/* Top Scorecard: Market Breadth */}
      {data && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3.5">
          <div className="bg-gray-900/80 border border-gray-800 rounded-xl p-4 shadow-md">
            <div className="text-[11px] text-gray-400 uppercase font-mono">Market Breadth Score</div>
            <div className={`text-2xl font-bold font-mono mt-1 ${data.market_breadth_score >= 60 ? 'text-emerald-400' : data.market_breadth_score <= 40 ? 'text-rose-400' : 'text-amber-400'}`}>
              {data.market_breadth_score}%
            </div>
            <div className="text-[11px] text-gray-500 mt-0.5">
              {data.market_breadth_score >= 60 ? 'Bullish Sector Alignment' : 'Mixed / Selective Market'}
            </div>
          </div>

          <div className="bg-gray-900/80 border border-gray-800 rounded-xl p-4 shadow-md">
            <div className="text-[11px] text-gray-400 uppercase font-mono">Uptrend Leading Sectors</div>
            <div className="text-2xl font-bold text-emerald-400 font-mono mt-1">
              {data.uptrend_sectors} <span className="text-xs text-gray-400 font-sans font-normal">/ {data.total_sectors}</span>
            </div>
            <div className="text-[11px] text-gray-500 mt-0.5">Positive Relative Strength</div>
          </div>

          <div className="bg-gray-900/80 border border-gray-800 rounded-xl p-4 shadow-md">
            <div className="text-[11px] text-gray-400 uppercase font-mono">Downtrend / Lagging</div>
            <div className="text-2xl font-bold text-rose-400 font-mono mt-1">
              {data.downtrend_sectors} <span className="text-xs text-gray-400 font-sans font-normal">/ {data.total_sectors}</span>
            </div>
            <div className="text-[11px] text-gray-500 mt-0.5">Underperforming Benchmark</div>
          </div>

          <div className="bg-gray-900/80 border border-gray-800 rounded-xl p-4 shadow-md">
            <div className="text-[11px] text-gray-400 uppercase font-mono">Benchmark Reference</div>
            <div className="text-2xl font-bold text-cyan-400 font-mono mt-1">
              {data.benchmark}
            </div>
            <div className="text-[11px] text-gray-500 mt-0.5">Anchor Index</div>
          </div>
        </div>
      )}

      {/* Main Sector Rotation Table & Detail Split View */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Left 2 Cols: Sector Rotation Grid */}
        <div className="lg:col-span-2 bg-gray-900/80 border border-gray-800 rounded-2xl shadow-xl overflow-hidden backdrop-blur-sm space-y-3 p-5">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 border-b border-gray-800 pb-3">
            <div className="flex items-center space-x-2">
              <BarChart3 className="w-4 h-4 text-cyan-400" />
              <h2 className="text-sm font-bold text-gray-200 uppercase tracking-wider font-mono">
                Sector Rotation & Relative Strength Matrix
              </h2>
            </div>

            {/* Filter Tabs */}
            <div className="flex space-x-1 bg-gray-950 p-1 rounded-lg border border-gray-800 text-xs">
              <button
                onClick={() => setFilterRegime('ALL')}
                className={`px-2.5 py-1 rounded-md transition-colors ${filterRegime === 'ALL' ? 'bg-gray-800 text-white font-semibold' : 'text-gray-400 hover:text-gray-200'}`}
              >
                All ({data?.total_sectors || 0})
              </button>
              <button
                onClick={() => setFilterRegime('UPTREND')}
                className={`px-2.5 py-1 rounded-md transition-colors ${filterRegime === 'UPTREND' ? 'bg-emerald-500/20 text-emerald-300 font-semibold' : 'text-gray-400 hover:text-gray-200'}`}
              >
                Uptrends ({data?.uptrend_sectors || 0})
              </button>
              <button
                onClick={() => setFilterRegime('DOWNTREND')}
                className={`px-2.5 py-1 rounded-md transition-colors ${filterRegime === 'DOWNTREND' ? 'bg-rose-500/20 text-rose-300 font-semibold' : 'text-gray-400 hover:text-gray-200'}`}
              >
                Downtrends ({data?.downtrend_sectors || 0})
              </button>
            </div>
          </div>

          {loading && (
            <div className="py-16 text-center text-gray-400 space-y-2">
              <RefreshCw className="w-6 h-6 animate-spin text-cyan-400 mx-auto" />
              <p className="text-xs font-mono">Computing Mansfield Relative Strength & Markov Regime models...</p>
            </div>
          )}

          {errorMsg && (
            <div className="p-4 bg-rose-500/10 border border-rose-500/30 rounded-xl text-rose-400 text-xs flex items-center gap-2">
              <ShieldAlert className="w-4 h-4 flex-shrink-0" />
              <span>{errorMsg}</span>
            </div>
          )}

          {!loading && data && (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-gray-950 text-gray-400 uppercase font-mono border-b border-gray-800">
                  <tr>
                    <th className="py-3 px-2 w-8 text-center"></th>
                    <th className="py-3 px-3">Sector</th>
                    <th className="py-3 px-3">Regime</th>
                    <th className="py-3 px-3 text-right">MRS Score</th>
                    <th className="py-3 px-3 text-right">5D Slope</th>
                    <th className="py-3 px-3 text-center">Hurst ($H$)</th>
                    <th className="py-3 px-3 text-center">Rem. Days</th>
                    <th className="py-3 px-3 text-right">Weight</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-800/60 font-mono">
                  {filteredSectors.map((s) => {
                    const isSelected = selectedSector && selectedSector.sector === s.sector;
                    const isExpanded = expandedSectors.has(s.sector);
                    const regime = s.regime.trend_classification;
                    const cList = constituentsMap[s.sector] || s.top_constituents || [];
                    const isRowLoading = loadingConstituents[s.sector];

                    return (
                      <React.Fragment key={s.sector}>
                        <tr
                          onClick={() => setSelectedSector(s)}
                          className={`cursor-pointer transition-all ${
                            isSelected
                              ? 'bg-cyan-500/15 text-white font-medium border-l-4 border-l-cyan-400'
                              : 'hover:bg-gray-800/40 text-gray-300'
                          }`}
                        >
                          <td className="py-3 px-2 text-center" onClick={(e) => toggleExpandSector(s.sector, e)}>
                            <button
                              className={`p-1 rounded hover:bg-gray-700/60 text-gray-400 hover:text-cyan-300 transition-transform ${isExpanded ? 'rotate-180 text-cyan-400' : ''}`}
                              title={isExpanded ? "Collapse constituents" : "Expand top constituents"}
                            >
                              <ChevronDown className="w-3.5 h-3.5" />
                            </button>
                          </td>

                          <td className="py-3 px-3">
                            <div className="font-bold text-white font-sans flex items-center gap-1.5">
                              <span>{s.name}</span>
                            </div>
                            <div className="text-[10px] text-gray-500 font-mono">{s.sector}</div>
                          </td>

                          <td className="py-3 px-3">
                            <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider ${
                              regime === 'STRONG_UPTREND'
                                ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                                : regime === 'EARLY_UPTREND'
                                ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/30'
                                : regime === 'STRONG_DOWNTREND'
                                ? 'bg-rose-500/20 text-rose-400 border border-rose-500/30'
                                : regime === 'EARLY_DOWNTREND'
                                ? 'bg-orange-500/20 text-orange-400 border border-orange-500/30'
                                : 'bg-gray-800 text-gray-400'
                            }`}>
                              {regime.replace('_', ' ')}
                            </span>
                          </td>

                          <td className={`py-3 px-3 text-right font-bold text-sm ${s.regime.mrs_score >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                            {s.regime.mrs_score >= 0 ? '+' : ''}{s.regime.mrs_score}%
                          </td>

                          <td className={`py-3 px-3 text-right ${s.regime.mrs_slope_5d >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                            <div className="flex items-center justify-end space-x-0.5">
                              {s.regime.mrs_slope_5d >= 0 ? <ArrowUpRight className="w-3.5 h-3.5" /> : <ArrowDownRight className="w-3.5 h-3.5" />}
                              <span>{s.regime.mrs_slope_5d >= 0 ? '+' : ''}{s.regime.mrs_slope_5d}</span>
                            </div>
                          </td>

                          <td className="py-3 px-3 text-center">
                            <span className={`px-1.5 py-0.5 rounded text-[11px] font-bold ${
                              s.regime.hurst_exponent > 0.55 ? 'text-purple-300 bg-purple-500/10' : 'text-gray-400'
                            }`}>
                              {s.regime.hurst_exponent}
                            </span>
                          </td>

                          <td className="py-3 px-3 text-center text-gray-200">
                            {s.duration_forecast.estimated_remaining_days}d
                          </td>

                          <td className="py-3 px-3 text-right">
                            <span className={`px-2 py-0.5 rounded text-[11px] font-bold ${
                              s.trade_recommendation.sector_weight_multiplier >= 1.0 ? 'text-emerald-400 bg-emerald-500/10' : 'text-gray-400 bg-gray-900'
                            }`}>
                              {s.trade_recommendation.sector_weight_multiplier}x
                            </span>
                          </td>
                        </tr>

                        {/* Inline Expandable Constituent Drawer */}
                        {isExpanded && (
                          <tr className="bg-gray-950/90 border-b border-gray-800/80">
                            <td colSpan={8} className="p-3 pl-8">
                              <div className="space-y-2">
                                <div className="text-[11px] text-gray-400 font-sans font-semibold flex items-center justify-between">
                                  <span className="flex items-center gap-1.5 text-cyan-400">
                                    <Sparkles className="w-3.5 h-3.5 text-amber-400" /> Top {s.name} Constituent Leaders (Ranked by Merit):
                                  </span>
                                  <span className="text-[10px] text-gray-500">Click any stock to open in Chart Studio</span>
                                </div>

                                {isRowLoading && (
                                  <div className="py-3 text-center text-gray-400 text-xs flex items-center justify-center gap-2 font-mono">
                                    <RefreshCw className="w-3.5 h-3.5 animate-spin text-cyan-400" />
                                    <span>Ranking {s.name} stocks...</span>
                                  </div>
                                )}

                                {!isRowLoading && cList.length > 0 && (
                                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2">
                                    {cList.map(c => (
                                      <div
                                        key={c.symbol}
                                        className="bg-gray-900/90 border border-gray-800 hover:border-cyan-500/50 p-2.5 rounded-xl transition-all group flex flex-col justify-between space-y-2 shadow-sm"
                                      >
                                        <div className="flex items-start justify-between">
                                          <div>
                                            <div className="font-bold text-gray-200 group-hover:text-cyan-300 transition-colors font-sans text-xs flex items-center gap-1.5">
                                              <span>{c.name}</span>
                                              <span className="text-[10px] text-gray-500 font-mono">({c.weight})</span>
                                            </div>
                                            <div className="text-[11px] font-mono text-gray-400 flex items-center gap-2 mt-0.5">
                                              <span>₹{c.close.toLocaleString()}</span>
                                              <span className={c.change_pct >= 0 ? 'text-emerald-400' : 'text-rose-400'}>
                                                {c.change_pct >= 0 ? '+' : ''}{c.change_pct}%
                                              </span>
                                            </div>
                                          </div>
                                          <div className="text-right flex flex-col items-end gap-1">
                                            <span className={`text-[10px] px-1.5 py-0.2 rounded font-semibold font-sans ${
                                              c.stage_type === 'bull'
                                                ? 'bg-emerald-500/20 text-emerald-300'
                                                : c.stage_type === 'early'
                                                ? 'bg-cyan-500/20 text-cyan-300'
                                                : 'bg-gray-800 text-gray-400'
                                            }`}>
                                              {c.stage}
                                            </span>
                                            <span className="text-[10px] text-purple-300 font-mono font-bold">
                                              Merit {c.merit_score}
                                            </span>
                                          </div>
                                        </div>

                                        <div className="flex items-center space-x-1.5 pt-1.5 border-t border-gray-800/80">
                                          <button
                                            onClick={(e) => {
                                              e.stopPropagation();
                                              onSelectTicker && onSelectTicker(c.symbol);
                                            }}
                                            className="flex-1 py-1 bg-gray-800 hover:bg-gray-700 text-[10px] font-semibold text-cyan-300 rounded border border-gray-700 hover:border-cyan-500/40 flex items-center justify-center gap-1 transition-colors"
                                          >
                                            <BarChart3 className="w-3 h-3" /> Chart
                                          </button>
                                          <button
                                            onClick={(e) => {
                                              e.stopPropagation();
                                              onOpenAIForecast && onOpenAIForecast(c.symbol);
                                            }}
                                            className="flex-1 py-1 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-[10px] font-bold text-white rounded flex items-center justify-center gap-1 shadow-sm transition-all"
                                          >
                                            <Sparkles className="w-3 h-3" /> 🔮 Forecast
                                          </button>
                                        </div>
                                      </div>
                                    ))}
                                  </div>
                                )}
                              </div>
                            </td>
                          </tr>
                        )}
                      </React.Fragment>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Right 1 Col: Selected Sector Deep Inspection & Ranked Leaders Card */}
        {selectedSector && (
          <div className="bg-gray-900/90 border border-cyan-500/30 rounded-2xl p-5 shadow-2xl space-y-5">
            
            <div className="border-b border-gray-800 pb-3">
              <div className="flex items-center justify-between">
                <span className="text-[10px] uppercase font-mono font-bold text-cyan-400 bg-cyan-500/10 px-2 py-0.5 rounded border border-cyan-500/30">
                  Sector Inspection
                </span>
                <span className="text-xs font-mono text-gray-400">₹{selectedSector.metadata.close.toLocaleString()}</span>
              </div>
              <h3 className="text-lg font-bold text-white mt-1">{selectedSector.name}</h3>
              <p className="text-xs text-gray-400 font-mono">{selectedSector.sector}</p>
            </div>

            {/* Action & Sizing Card */}
            <div className="p-3.5 bg-gray-950/90 rounded-xl border border-gray-800 space-y-2">
              <div className="flex justify-between items-center text-xs">
                <span className="text-gray-400 uppercase font-mono">Recommended Action</span>
                <span className="font-bold text-cyan-300 font-mono">{selectedSector.trade_recommendation.action}</span>
              </div>
              <div className="flex justify-between items-center text-xs">
                <span className="text-gray-400 uppercase font-mono">Allocation Weight</span>
                <span className="font-bold text-emerald-400 font-mono">{selectedSector.trade_recommendation.sector_weight_multiplier}x Multiplier</span>
              </div>
            </div>

            {/* Top Constituents & Leaders (Ranked by Merit) */}
            <div className="space-y-2.5">
              <div className="flex items-center justify-between border-b border-gray-800/80 pb-2">
                <div className="text-[11px] text-cyan-400 uppercase font-bold tracking-wider font-mono flex items-center gap-1.5">
                  <Award className="w-4 h-4 text-amber-400" />
                  <span>Top {selectedSector.name} Stocks (by Merit)</span>
                </div>
                <span className="text-[10px] text-gray-500 font-mono">Top Leaders</span>
              </div>

              {isSelectedLoadingConstituents && (
                <div className="py-6 text-center text-gray-400 text-xs flex items-center justify-center gap-2 font-mono">
                  <RefreshCw className="w-4 h-4 animate-spin text-cyan-400" />
                  <span>Loading {selectedSector.name} constituents...</span>
                </div>
              )}

              {!isSelectedLoadingConstituents && selectedConstituents.length === 0 && (
                <div className="py-4 text-center text-gray-500 text-xs font-mono">
                  Constituent profiling available on selection.
                </div>
              )}

              {!isSelectedLoadingConstituents && selectedConstituents.length > 0 && (
                <div className="space-y-2 max-h-[380px] overflow-y-auto pr-1">
                  {selectedConstituents.map((c, idx) => (
                    <div 
                      key={c.symbol}
                      className="bg-gray-950/90 border border-gray-800/80 hover:border-cyan-500/40 rounded-xl p-2.5 transition-all space-y-1.5 shadow-sm"
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-2">
                          <span className="w-5 h-5 rounded-md bg-gray-900 border border-gray-700 flex items-center justify-center text-[10px] font-mono font-bold text-cyan-400">
                            #{idx + 1}
                          </span>
                          <div>
                            <div className="text-xs font-bold text-white flex items-center gap-1.5">
                              <span>{c.name}</span>
                              <span className="text-[10px] text-gray-500 font-mono">({c.weight})</span>
                            </div>
                            <div className="text-[10px] text-gray-400 font-mono">
                              ₹{c.close.toLocaleString()} • <span className={c.change_pct >= 0 ? 'text-emerald-400' : 'text-rose-400'}>{c.change_pct >= 0 ? '+' : ''}{c.change_pct}%</span> • RSI: {c.rsi}
                            </div>
                          </div>
                        </div>

                        <div className="text-right">
                          <div className={`text-[10px] px-1.5 py-0.5 rounded font-bold uppercase ${
                            c.stage_type === 'bull'
                              ? 'bg-emerald-500/20 text-emerald-400'
                              : c.stage_type === 'early'
                              ? 'bg-cyan-500/20 text-cyan-300'
                              : 'bg-gray-800 text-gray-400'
                          }`}>
                            {c.stage}
                          </div>
                          <div className="text-[10px] font-mono text-purple-300 mt-0.5">
                            Merit: {c.merit_score}
                          </div>
                        </div>
                      </div>

                      {/* Active setup banner if present */}
                      {c.active_setup && (
                        <div className="text-[10px] px-2 py-0.5 rounded-md bg-amber-500/10 border border-amber-500/20 text-amber-300 flex items-center justify-between font-mono">
                          <span>⭐ Active Setup: {c.active_setup}</span>
                          <span>Score {c.setup_score}</span>
                        </div>
                      )}

                      {/* 1-Click Action Buttons */}
                      <div className="flex items-center gap-1.5 pt-1 border-t border-gray-900">
                        <button
                          onClick={() => onSelectTicker && onSelectTicker(c.symbol)}
                          className="flex-1 py-1 rounded bg-gray-900 hover:bg-cyan-600/20 border border-gray-800 hover:border-cyan-500/40 text-gray-300 hover:text-cyan-300 text-[10px] font-medium flex items-center justify-center gap-1 transition-all"
                          title="Open Chart in Chart Studio"
                        >
                          <LineChart className="w-3 h-3" /> Chart
                        </button>
                        <button
                          onClick={() => onOpenBacktest && onOpenBacktest(c.symbol)}
                          className="flex-1 py-1 rounded bg-gray-900 hover:bg-indigo-600/20 border border-gray-800 hover:border-indigo-500/40 text-gray-300 hover:text-indigo-300 text-[10px] font-medium flex items-center justify-center gap-1 transition-all"
                          title="Run Walk-Forward Backtest"
                        >
                          <SlidersHorizontal className="w-3 h-3" /> Backtest
                        </button>
                        <button
                          onClick={() => onOpenRisk && onOpenRisk({ close: c.close, stop_loss: Math.round(c.close * 0.95), target_1: Math.round(c.close * 1.10) })}
                          className="flex-1 py-1 rounded bg-gray-900 hover:bg-emerald-600/20 border border-gray-800 hover:border-emerald-500/40 text-gray-300 hover:text-emerald-300 text-[10px] font-medium flex items-center justify-center gap-1 transition-all"
                          title="Calculate Exact Position Sizing"
                        >
                          <DollarSign className="w-3 h-3" /> Risk
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Persistence & Regime Duration */}
            <div className="space-y-2 text-xs font-mono">
              <div className="text-[11px] text-gray-400 uppercase font-bold tracking-wider">
                Regime Forecast & Memory ($H$)
              </div>

              <div className="bg-gray-950/70 p-3 rounded-xl border border-gray-800/80 space-y-2">
                <div className="flex justify-between">
                  <span className="text-gray-400">Hurst Exponent ($H$):</span>
                  <span className="font-bold text-purple-400">{selectedSector.regime.hurst_exponent} (Persistent Memory)</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Current Regime Age:</span>
                  <span className="text-gray-200">{selectedSector.duration_forecast.current_regime_age_days} Days</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Expected Total Run:</span>
                  <span className="text-cyan-300 font-bold">{selectedSector.duration_forecast.expected_total_duration_days} Days</span>
                </div>
                <div className="flex justify-between border-t border-gray-800/80 pt-1.5">
                  <span className="text-gray-400">Estimated Runway:</span>
                  <span className="text-emerald-400 font-bold">{selectedSector.duration_forecast.estimated_remaining_days} Days Remaining</span>
                </div>
              </div>
            </div>

            {/* Exhaustion & Risk Alert */}
            <div className="space-y-2 text-xs font-mono">
              <div className="text-[11px] text-gray-400 uppercase font-bold tracking-wider">
                Exhaustion & Volatility Risk
              </div>

              <div className="bg-gray-950/70 p-3 rounded-xl border border-gray-800/80 space-y-2">
                <div className="flex justify-between">
                  <span className="text-gray-400">Exhaustion Probability:</span>
                  <span className={`font-bold ${selectedSector.duration_forecast.exhaustion_probability >= 0.60 ? 'text-rose-400' : 'text-emerald-400'}`}>
                    {Math.round(selectedSector.duration_forecast.exhaustion_probability * 100)}%
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Overextension Flag:</span>
                  <span className={selectedSector.risk_parameters.overextension_flag ? 'text-amber-400 font-bold' : 'text-gray-400'}>
                    {selectedSector.risk_parameters.overextension_flag ? '⚠️ Overextended (>3 ATR)' : 'Normal Band'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Trailing Stop Level:</span>
                  <span className="text-rose-400 font-bold">₹{selectedSector.risk_parameters.trailing_stop_level.toLocaleString()}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">ATR(14) Volatility:</span>
                  <span className="text-gray-300">₹{selectedSector.risk_parameters.atr_14.toLocaleString()}</span>
                </div>
              </div>
            </div>

            {/* Screener Link Button */}
            <button
              onClick={() => onScanSector && onScanSector(selectedSector.name)}
              className="w-full py-2.5 rounded-xl bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white font-medium text-xs flex items-center justify-center gap-2 shadow-lg shadow-cyan-600/25 transition-all active:scale-95"
            >
              <Zap className="w-4 h-4" />
              <span>Screen All {selectedSector.name} Stocks</span>
            </button>

          </div>
        )}

      </div>

    </div>
  );
}
