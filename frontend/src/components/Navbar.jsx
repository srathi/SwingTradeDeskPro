import React from 'react';
import { 
  TrendingUp, 
  BarChart2, 
  Layers, 
  ShieldAlert, 
  Bookmark, 
  Activity, 
  Zap,
  BookOpen
} from 'lucide-react';

export default function Navbar({ activeTab, setActiveTab }) {
  const navItems = [
    { id: 'screener', label: 'Live Screener', icon: Layers },
    { id: 'deepscan', label: 'Deep Scan', icon: Zap },
    { id: 'chart', label: 'Chart Studio', icon: BarChart2 },
    { id: 'backtest', label: 'Backtest Studio', icon: TrendingUp },
    { id: 'risk', label: 'Risk Calculator', icon: ShieldAlert },
    { id: 'watchlists', label: 'Watchlists', icon: Bookmark },
    { id: 'matrix', label: 'Strategy Matrix', icon: BookOpen, isHighlight: true },
  ];

  return (
    <header className="border-b border-gray-800 bg-[#0B0F19]/95 backdrop-blur-md sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-2 sm:px-4 lg:px-8">
        <div className="flex items-center justify-between h-16 gap-2">
          
          {/* Brand Logo */}
          <div className="flex items-center space-x-2.5 cursor-pointer flex-shrink-0" onClick={() => setActiveTab('screener')}>
            <div className="w-8 h-8 sm:w-9 sm:h-9 rounded-lg bg-gradient-to-tr from-cyan-600 to-blue-500 flex items-center justify-center shadow-lg shadow-cyan-500/20 border border-cyan-400/30">
              <Activity className="w-4 h-4 sm:w-5 sm:h-5 text-white" />
            </div>
            <div>
              <div className="flex items-center space-x-1.5">
                <span className="font-bold text-base sm:text-lg text-white tracking-tight">SwingDesk</span>
                <span className="text-[10px] font-semibold px-1.5 py-0.5 rounded bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">PRO</span>
              </div>
              <p className="text-[9px] sm:text-[10px] text-cyan-400/90 tracking-wide font-mono font-medium">
                rupeemap.in labs <span className="text-gray-500 font-sans">• by Sandesh Rathi</span>
              </p>
            </div>
          </div>

          {/* Navigation Links */}
          <nav className="flex items-center space-x-1 overflow-x-auto py-1 scrollbar-none flex-1 justify-end lg:justify-center">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => setActiveTab(item.id)}
                  className={`flex items-center space-x-1.5 px-2 sm:px-2.5 py-1.5 rounded-lg text-xs sm:text-sm font-medium whitespace-nowrap transition-all duration-150 flex-shrink-0 ${
                    isActive
                      ? 'bg-cyan-500/15 text-cyan-300 border border-cyan-500/40 shadow-sm shadow-cyan-500/20 font-semibold'
                      : item.isHighlight
                      ? 'text-cyan-400 hover:text-cyan-200 bg-cyan-500/5 hover:bg-cyan-500/10 border border-cyan-500/20'
                      : 'text-gray-400 hover:text-gray-200 hover:bg-gray-800/60 border border-transparent'
                  }`}
                >
                  <Icon className={`w-3.5 h-3.5 sm:w-4 sm:h-4 ${isActive ? 'text-cyan-400' : item.isHighlight ? 'text-cyan-400' : 'text-gray-400'}`} />
                  <span>{item.label}</span>
                </button>
              );
            })}
          </nav>

          {/* Status Indicator */}
          <div className="hidden 2xl:flex items-center space-x-2 bg-gray-900/60 border border-gray-800 px-3 py-1.5 rounded-full flex-shrink-0">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
            </span>
            <span className="text-[11px] font-mono text-gray-300 font-medium">NSE/BSE Active</span>
          </div>

        </div>
      </div>
    </header>
  );
}
