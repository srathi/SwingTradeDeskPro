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
    backtest: { category: "Execution", label: "Backtest Studio", icon: TrendingUp },
    risk: { category: "Execution", label: "Risk Calculator", icon: ShieldAlert },
    watchlists: { category: "Research", label: "Watchlists", icon: Bookmark },
    matrix: { category: "Research", label: "Strategy Matrix", icon: BookOpen },
  };

  const meta = tabMetadata[activeTab] || { category: "Workspace", label: "Dashboard", icon: Layers };
  const TabIcon = meta.icon;

  return (
    <header className="h-14 border-b border-gray-800/90 bg-[#080C14]/90 backdrop-blur-md px-3 sm:px-6 flex items-center justify-between gap-3 sticky top-0 z-30 flex-shrink-0">
      
      {/* Left: Mobile Menu Button & Breadcrumb */}
      <div className="flex items-center space-x-3">
        <button
          onClick={onToggleMobileSidebar}
          className="p-1.5 rounded-lg text-gray-400 hover:text-white hover:bg-gray-800/60 md:hidden"
          title="Open Navigation Menu"
        >
          <Menu className="w-5 h-5" />
        </button>

        {/* Dynamic Breadcrumbs */}
        <div className="flex items-center space-x-2 text-xs font-mono">
          <span className="text-gray-400 hidden sm:inline">SwingDesk</span>
          <ChevronRight className="w-3.5 h-3.5 text-gray-400 hidden sm:inline" />
          <span className="text-gray-400 font-medium">{meta.category}</span>
          <ChevronRight className="w-3.5 h-3.5 text-gray-400" />
          <div className="flex items-center space-x-1.5 text-cyan-300 font-bold bg-cyan-500/10 px-2 py-0.5 rounded border border-cyan-500/20">
            <TabIcon className="w-3.5 h-3.5 text-cyan-400" />
            <span>{meta.label}</span>
          </div>
        </div>
      </div>

      {/* Right: Macro Regime Pill, Quick Stock Search & Market Live Indicator */}
      <div className="flex items-center space-x-2.5">
        
        {/* Macro Market Regime Badge */}
        {regimeData && (
          <div className="hidden md:flex items-center space-x-2 bg-gray-950/90 border border-gray-800 px-2.5 py-1 rounded-lg text-xs font-mono">
            {/* Benchmark Nifty */}
            <div className="flex items-center space-x-1">
              <span className="text-gray-400 font-bold">NIFTY</span>
              <span className="text-white font-bold">₹{regimeData.benchmark?.close?.toLocaleString('en-IN')}</span>
              <span className={`text-[10px] ${regimeData.benchmark?.change_pct >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                ({regimeData.benchmark?.change_pct >= 0 ? '+' : ''}{regimeData.benchmark?.change_pct}%)
              </span>
            </div>

            <span className="text-gray-700">|</span>

            {/* India VIX */}
            <div className="flex items-center space-x-1">
              <span className="text-gray-400">VIX:</span>
              <span className={`font-bold ${regimeData.volatility?.value < 14 ? 'text-emerald-400' : regimeData.volatility?.value <= 18 ? 'text-cyan-400' : regimeData.volatility?.value <= 22 ? 'text-amber-400' : 'text-rose-400'}`}>
                {regimeData.volatility?.value}
              </span>
            </div>

            <span className="text-gray-700">|</span>

            {/* Regime Verdict Badge */}
            <div className={`px-2 py-0.5 rounded text-[10px] font-bold border flex items-center gap-1 ${regimeData.verdict?.code === 'RISK_ON_EXPANSION' ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' : regimeData.verdict?.code === 'SELECTIVE_PULLBACKS' ? 'bg-cyan-500/10 text-cyan-400 border-cyan-500/20' : regimeData.verdict?.code === 'HIGH_CHOP_MEAN_REVERSION' ? 'bg-amber-500/10 text-amber-400 border-amber-500/20' : 'bg-rose-500/10 text-rose-400 border-rose-500/20'}`}>
              <ShieldCheck className="w-3 h-3" />
              <span>{regimeData.verdict?.title}</span>
            </div>
          </div>
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
  );
}
