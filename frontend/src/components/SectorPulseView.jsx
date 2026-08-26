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
  ArrowDownRight
} from 'lucide-react';
import { fetchSectorPulse } from '../services/api';

export default function SectorPulseView({ onScanSector }) {
  const [market, setMarket] = useState('NSE');
  const [period, setPeriod] = useState('2y');
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState(null);
  const [selectedSector, setSelectedSector] = useState(null);
  const [filterRegime, setFilterRegime] = useState('ALL'); // ALL, UPTREND, DOWNTREND

  const loadPulse = async () => {
    setLoading(true);
    setErrorMsg(null);
    try {
      const res = await fetchSectorPulse(market, period);
      setData(res);
      if (res && res.sectors && res.sectors.length > 0) {
        setSelectedSector(res.sectors[0]);
      }
    } catch (err) {
      setErrorMsg(err.message || "Failed to load sector pulse data");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadPulse();
  }, [market, period]);

  const filteredSectors = data && data.sectors ? data.sectors.filter(s => {
    if (filterRegime === 'UPTREND') return s.regime.trend_classification.includes('UPTREND');
    if (filterRegime === 'DOWNTREND') return s.regime.trend_classification.includes('DOWNTREND');
    return true;
  }) : [];

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
                Top-Down Macro Rotation, Mansfield RS, Hurst Persistence ($H$), and Markov Regime Duration Modeling by <a href="https://www.rupeemap.in" target="_blank" rel="noopener noreferrer" className="text-cyan-400 font-medium hover:underline hover:text-cyan-300 transition-colors">rupeemap.in labs</a>.
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
            <div className="text-[11px] text-gray-500 mt-0.5">Nifty 50 Equal Anchor</div>
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
                    const regime = s.regime.trend_classification;
                    const isUptrend = regime.includes('UPTREND');
                    const isDowntrend = regime.includes('DOWNTREND');

                    return (
                      <tr
                        key={s.sector}
                        onClick={() => setSelectedSector(s)}
                        className={`cursor-pointer transition-all ${
                          isSelected
                            ? 'bg-cyan-500/15 text-white font-medium border-l-4 border-l-cyan-400'
                            : 'hover:bg-gray-800/40 text-gray-300'
                        }`}
                      >
                        <td className="py-3 px-3">
                          <div className="font-bold text-white font-sans">{s.name}</div>
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
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Right 1 Col: Selected Sector Deep Inspection Card */}
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
              <span>Screen {selectedSector.name} Stocks</span>
            </button>

          </div>
        )}

      </div>

    </div>
  );
}
