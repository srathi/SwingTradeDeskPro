import React, { useState, useEffect } from 'react';
import { 
  Menu, 
  ChevronRight, 
  Search, 
  Activity, 
  Compass, 
  Layers, 
  Zap, 
  BarChart2, 
  TrendingUp,
  ShieldAlert,
  Bookmark, 
  BookOpen,
  Sparkles,
  BookMarked,
  ShieldCheck,
  AlertTriangle
} from 'lucide-react';
import { fetchMarketRegime } from '../services/api';
import StockSearchInput from './StockSearchInput';

export default function TopHeader({ 
  activeTab, 
  onToggleMobileSidebar, 
  onSelectTicker 
}) {
  const [regimeData, setRegimeData] = useState(null);
  const [isRegimeModalOpen, setIsRegimeModalOpen] = useState(false);

  useEffect(() => {
    const fetchRegime = async () => {
      try {
        const data = await fetchMarketRegime('NSE');
        setRegimeData(data);
      } catch (e) {
        // quiet fallback
      }
    };
    fetchRegime();
    const interval = setInterval(fetchRegime, 180000); // 3 mins
    return () => clearInterval(interval);
  }, []);

  const tabMetadata = {
    screener: { category: "Discovery", label: "Live Screener", icon: Layers },
    deepscan: { category: "Discovery", label: "Deep Scan", icon: Zap },
    sectors: { category: "Discovery", label: "Sector Pulse", icon: Compass },
    chart: { category: "Execution", label: "Chart Studio", icon: BarChart2 },
    aiforecast: { category: "Execution", label: "Kronos AI Forecaster", icon: Sparkles },
    journal: { category: "Execution", label: "Paper Journal", icon: BookMarked },
    risk: { category: "Execution", label: "Risk & Position Sizer", icon: ShieldAlert },
    backtester: { category: "Validation", label: "Backtest Studio", icon: TrendingUp },
    docs: { category: "Documentation", label: "Trading Handbook", icon: BookOpen }
  };

  const meta = tabMetadata[activeTab] || { category: "Overview", label: "Dashboard", icon: Activity };
  const TabIcon = meta.icon;

  return (
    <>
      <header className="h-16 bg-gray-900/90 backdrop-blur-md border-b border-gray-800/80 px-4 sm:px-6 flex items-center justify-between sticky top-0 z-30 shadow-md">
        
        {/* Left: Mobile Toggle & Breadcrumbs */}
        <div className="flex items-center space-x-3">
          <button
            onClick={onToggleMobileSidebar}
            className="lg:hidden p-2 rounded-lg text-gray-400 hover:text-white hover:bg-gray-800 focus:outline-none transition-colors"
            aria-label="Toggle navigation menu"
          >
            <Menu className="w-5 h-5" />
          </button>

          {/* Breadcrumb Navigation */}
          <div className="flex items-center space-x-2 text-xs font-mono">
            <span className="text-gray-400 font-semibold">{meta.category}</span>
            <ChevronRight className="w-3.5 h-3.5 text-gray-600" />
            <div className="flex items-center space-x-1.5 font-bold text-white bg-gray-800/60 px-2.5 py-1 rounded-md border border-gray-700/50">
              <TabIcon className="w-3.5 h-3.5 text-cyan-400" />
              <span>{meta.label}</span>
            </div>
          </div>
        </div>

        {/* Right: Macro Regime Pill, Quick Stock Search & Market Live Indicator */}
        <div className="flex items-center space-x-2.5">
          
          {/* Macro Market Regime Badge (Clickable) */}
          {regimeData && (
            <button
              onClick={() => setIsRegimeModalOpen(true)}
              className="flex items-center space-x-2 bg-gray-950/90 hover:bg-gray-900 border border-gray-800 hover:border-cyan-500/50 px-2.5 py-1 rounded-lg text-xs font-mono transition-all cursor-pointer shadow-sm group"
              title="Click to view full Macro Market Regime & Volatility Intelligence Report"
            >
              {/* Benchmark Nifty */}
              <div className="flex items-center space-x-1">
                <span className="text-gray-400 font-bold">NIFTY</span>
                <span className="text-white font-bold">₹{regimeData.benchmark?.close?.toLocaleString('en-IN')}</span>
                <span className={`text-[10px] ${regimeData.benchmark?.change_pct >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                  ({regimeData.benchmark?.change_pct >= 0 ? '+' : ''}{regimeData.benchmark?.change_pct}%)
                </span>
              </div>

              <span className="text-gray-700 hidden sm:inline">|</span>

              {/* India VIX */}
              <div className="hidden sm:flex items-center space-x-1">
                <span className="text-gray-400">VIX:</span>
                <span className={`font-bold ${regimeData.volatility?.value < 14 ? 'text-emerald-400' : regimeData.volatility?.value <= 18 ? 'text-cyan-400' : regimeData.volatility?.value <= 22 ? 'text-amber-400' : 'text-rose-400'}`}>
                  {regimeData.volatility?.value}
                </span>
              </div>

              <span className="text-gray-700 hidden md:inline">|</span>

              {/* Regime Verdict Badge */}
              <div className={`px-2 py-0.5 rounded text-[10px] font-bold border hidden md:flex items-center gap-1 ${regimeData.verdict?.code === 'RISK_ON_EXPANSION' ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' : regimeData.verdict?.code === 'SELECTIVE_PULLBACKS' ? 'bg-cyan-500/10 text-cyan-400 border-cyan-500/20' : regimeData.verdict?.code === 'HIGH_CHOP_MEAN_REVERSION' ? 'bg-amber-500/10 text-amber-400 border-amber-500/20' : 'bg-rose-500/10 text-rose-400 border-rose-500/20'}`}>
                <ShieldCheck className="w-3 h-3" />
                <span>{regimeData.verdict?.title}</span>
              </div>
            </button>
          )}

          {/* Quick Ticker Search Bar */}
          <div className="w-36 sm:w-56">
            <StockSearchInput
              placeholder="Quick search..."
              onSelectStock={(sym) => onSelectTicker && onSelectTicker(sym)}
              className="w-full text-xs"
            />
          </div>

          {/* Live Market Indicator Badge */}
          <div className="hidden lg:flex items-center space-x-2 bg-gray-950 border border-gray-800/90 px-2.5 py-1 rounded-lg text-[11px] font-mono text-gray-300">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
            </span>
            <span className="text-emerald-400 font-medium">Live</span>
          </div>

        </div>

      </header>

      {/* Macro Market Regime Intelligence Modal */}
      {isRegimeModalOpen && regimeData && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-fadeIn">
          <div className="bg-gray-900 border border-gray-800 rounded-2xl w-full max-w-2xl overflow-hidden shadow-2xl space-y-4 p-6">
            
            {/* Modal Header */}
            <div className="flex items-center justify-between border-b border-gray-800 pb-4">
              <div className="flex items-center space-x-2.5">
                <div className="w-9 h-9 rounded-xl bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center text-cyan-400">
                  <ShieldCheck className="w-5 h-5" />
                </div>
                <div>
                  <h2 className="text-lg font-bold text-white tracking-tight">Macro Market Regime & Volatility Intelligence</h2>
                  <p className="text-xs text-gray-400">Lopez de Prado & Campbell Harvey Institutional Risk Gating</p>
                </div>
              </div>
              <button
                onClick={() => setIsRegimeModalOpen(false)}
                className="text-gray-400 hover:text-white p-1 rounded-lg hover:bg-gray-800 transition-colors"
              >
                ✕
              </button>
            </div>

            {/* Current Active Regime Banner */}
            <div className={`p-4 rounded-xl border flex flex-col sm:flex-row sm:items-center justify-between gap-3 ${
              regimeData.verdict?.code === 'RISK_ON_EXPANSION' ? 'bg-emerald-950/40 border-emerald-500/40 text-emerald-300' :
              regimeData.verdict?.code === 'SELECTIVE_PULLBACKS' ? 'bg-cyan-950/40 border-cyan-500/40 text-cyan-300' :
              regimeData.verdict?.code === 'HIGH_CHOP_MEAN_REVERSION' ? 'bg-amber-950/40 border-amber-500/40 text-amber-300' :
              'bg-rose-950/40 border-rose-500/40 text-rose-300'
            }`}>
              <div>
                <span className="text-[10px] uppercase font-bold tracking-wider opacity-80 block">Current Active Regime</span>
                <h3 className="text-base font-extrabold text-white mt-0.5">{regimeData.verdict?.title}</h3>
                <p className="text-xs mt-1 text-gray-300 leading-relaxed">{regimeData.verdict?.description}</p>
              </div>
              <div className="bg-gray-950/80 p-3 rounded-lg border border-gray-800 text-center flex-shrink-0">
                <span className="text-[10px] text-gray-400 uppercase block font-bold">Recommended Capital</span>
                <span className="text-lg font-black font-mono text-cyan-300">{Math.round((regimeData.verdict?.recommended_allocation_multiplier || 1.0) * 100)}% Risk</span>
              </div>
            </div>

            {/* Metrics Breakdown Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 font-mono text-xs">
              
              {/* Benchmark Nifty */}
              <div className="bg-gray-950/70 p-3.5 rounded-xl border border-gray-800 space-y-1.5">
                <span className="text-[10px] text-gray-400 uppercase font-bold block">{regimeData.benchmark?.name}</span>
                <div className="text-base font-bold text-white">₹{regimeData.benchmark?.close?.toLocaleString('en-IN')}</div>
                <div className={`text-xs ${regimeData.benchmark?.change_pct >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                  {regimeData.benchmark?.change_pct >= 0 ? '+' : ''}{regimeData.benchmark?.change_pct}% Today
                </div>
                <div className="pt-2 border-t border-gray-800 text-[11px] text-gray-400">
                  Trend: <span className="text-cyan-300 font-bold">{regimeData.benchmark?.trend_status?.replace(/_/g, ' ')}</span>
                </div>
              </div>

              {/* Volatility Index */}
              <div className="bg-gray-950/70 p-3.5 rounded-xl border border-gray-800 space-y-1.5">
                <span className="text-[10px] text-gray-400 uppercase font-bold block">India VIX Volatility</span>
                <div className="text-base font-bold text-white">{regimeData.volatility?.value}</div>
                <div className={`text-xs ${regimeData.volatility?.change_pct <= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                  {regimeData.volatility?.change_pct >= 0 ? '+' : ''}{regimeData.volatility?.change_pct}% Today
                </div>
                <div className="pt-2 border-t border-gray-800 text-[11px] text-gray-400">
                  Implied Daily Move: <span className="text-amber-300 font-bold">±{regimeData.volatility?.implied_daily_move_pct}%</span>
                </div>
              </div>

              {/* Market Breadth */}
              <div className="bg-gray-950/70 p-3.5 rounded-xl border border-gray-800 space-y-1.5">
                <span className="text-[10px] text-gray-400 uppercase font-bold block">Market Breadth</span>
                <div className="text-base font-bold text-white">{regimeData.breadth?.pct_above_200_ema}%</div>
                <div className="text-xs text-gray-400">Above 200 EMA</div>
                <div className="pt-2 border-t border-gray-800 text-[11px] text-gray-400">
                  Breadth Quality: <span className="text-emerald-300 font-bold">{regimeData.breadth?.rating}</span>
                </div>
              </div>

            </div>

            {/* The 4 Regime Playbook Guide */}
            <div className="bg-gray-950/60 p-4 rounded-xl border border-gray-800 space-y-2">
              <span className="text-[11px] uppercase font-bold text-gray-400 tracking-wider block">The 4 Regime Playbooks:</span>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs">
                <div className="p-2 rounded-lg bg-emerald-950/20 border border-emerald-500/20 text-gray-300">
                  <span className="font-bold text-emerald-400 block">🟢 Risk-On Expansion (100% Risk)</span>
                  <p className="text-[11px] text-gray-400 mt-0.5">Aggressive breakouts & momentum leaders enabled.</p>
                </div>
                <div className="p-2 rounded-lg bg-cyan-950/20 border border-cyan-500/20 text-gray-300">
                  <span className="font-bold text-cyan-400 block">🟡 Selective Pullbacks (75% Risk)</span>
                  <p className="text-[11px] text-gray-400 mt-0.5">Stage 2 leaders on 20/50 EMA dips only.</p>
                </div>
                <div className="p-2 rounded-lg bg-amber-950/20 border border-amber-500/20 text-gray-300">
                  <span className="font-bold text-amber-400 block">🟠 High Chop (50% Risk)</span>
                  <p className="text-[11px] text-gray-400 mt-0.5">Mean-reversion oscillators only; breakouts gated.</p>
                </div>
                <div className="p-2 rounded-lg bg-rose-950/20 border border-rose-500/20 text-gray-300">
                  <span className="font-bold text-rose-400 block">🔴 Capital Preservation (25% Risk)</span>
                  <p className="text-[11px] text-gray-400 mt-0.5">Defensive cash holding; ultra-tight trailing stops.</p>
                </div>
              </div>
            </div>

            {/* Modal Footer */}
            <div className="flex justify-end pt-2">
              <button
                onClick={() => setIsRegimeModalOpen(false)}
                className="px-4 py-2 bg-gray-800 hover:bg-gray-700 text-white rounded-lg text-xs font-semibold transition-colors"
              >
                Close Report
              </button>
            </div>

          </div>
        </div>
      )}
    </>
  );
}
