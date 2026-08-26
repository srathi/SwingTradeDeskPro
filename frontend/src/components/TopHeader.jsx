import React from 'react';
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
  BookOpen 
} from 'lucide-react';
import StockSearchInput from './StockSearchInput';

export default function TopHeader({ 
  activeTab, 
  onToggleMobileSidebar, 
  onSelectTicker 
}) {
  const tabMetadata = {
    screener: { category: "Discovery", label: "Live Screener", icon: Layers },
    deepscan: { category: "Discovery", label: "Deep Scan", icon: Zap },
    sectors: { category: "Discovery", label: "Sector Pulse", icon: Compass },
    chart: { category: "Execution", label: "Chart Studio", icon: BarChart2 },
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

      {/* Right: Quick Stock Search & Market Live Indicator */}
      <div className="flex items-center space-x-3">
        
        {/* Quick Ticker Search Bar */}
        <div className="w-44 sm:w-64">
          <StockSearchInput
            placeholder="Quick stock search (e.g. RELIANCE)..."
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
          <span className="text-emerald-400 font-medium">NSE/BSE Live</span>
        </div>

      </div>

    </header>
  );
}
