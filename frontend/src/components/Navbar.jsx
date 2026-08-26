import React from 'react';
import { 
  TrendingUp, 
  BarChart2, 
  Layers, 
  ShieldAlert, 
  Bookmark, 
  Activity, 
  Zap,
  BookOpen,
  Compass
} from 'lucide-react';

export default function Navbar({ activeTab, setActiveTab }) {
  const navItems = [
    { id: 'screener', label: 'Screener', fullLabel: 'Live Screener', icon: Layers },
    { id: 'deepscan', label: 'Deep Scan', fullLabel: 'Deep Scan', icon: Zap },
    { id: 'sectors', label: 'Sector Pulse', fullLabel: '🧭 Sector Pulse', icon: Compass, isSectorBadge: true },
    { id: 'chart', label: 'Charts', fullLabel: 'Chart Studio', icon: BarChart2 },
    { id: 'backtest', label: 'Backtest', fullLabel: 'Backtest Studio', icon: TrendingUp },
    { id: 'risk', label: 'Risk', fullLabel: 'Risk Calculator', icon: ShieldAlert },
    { id: 'watchlists', label: 'Watchlists', fullLabel: 'Watchlists', icon: Bookmark },
    { id: 'matrix', label: 'Matrix', fullLabel: 'Strategy Matrix', icon: BookOpen, isHighlight: true },
  ];

  return (
    <header className="border-b border-gray-800 bg-[#0B0F19]/95 backdrop-blur-md sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-2 sm:px-4 lg:px-6">
        <div className="flex items-center justify-between h-16 gap-1 sm:gap-3">
          
          {/* Brand Logo */}
          <div className="flex items-center space-x-2 sm:space-x-2.5 cursor-pointer flex-shrink-0" onClick={() => setActiveTab('screener')}>
            <div className="w-8 h-8 sm:w-9 sm:h-9 rounded-lg bg-gradient-to-tr from-cyan-600 to-blue-500 flex items-center justify-center shadow-lg shadow-cyan-500/20 border border-cyan-400/30">
              <Activity className="w-4 h-4 sm:w-5 sm:h-5 text-white" />
            </div>
            <div>
              <div className="flex items-center space-x-1 sm:space-x-1.5">
                <span className="font-bold text-sm sm:text-base md:text-lg text-white tracking-tight">SwingDesk</span>
                <span className="text-[9px] sm:text-[10px] font-semibold px-1 sm:px-1.5 py-0.2 rounded bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">PRO</span>
              </div>
              <p className="text-[8px] sm:text-[9px] text-cyan-400/90 tracking-wide font-mono font-medium truncate max-w-[130px] sm:max-w-none">
                <a href="https://www.rupeemap.in" target="_blank" rel="noopener noreferrer" onClick={(e) => e.stopPropagation()} className="hover:underline hover:text-cyan-300 transition-colors">rupeemap.in labs</a> <span className="text-gray-500 font-sans hidden sm:inline">• by Sandesh Rathi</span>
              </p>
            </div>
          </div>

          {/* Navigation Links with smooth touch scrolling and no truncation */}
          <nav className="flex items-center space-x-1 sm:space-x-1.5 overflow-x-auto py-1 flex-1 justify-start md:justify-end no-scrollbar">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => setActiveTab(item.id)}
                  className={`flex items-center space-x-1 sm:space-x-1.5 px-2 sm:px-2.5 py-1.5 rounded-lg text-xs sm:text-xs md:text-sm font-medium whitespace-nowrap transition-all duration-150 flex-shrink-0 ${
                    isActive
                      ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 shadow-sm shadow-cyan-500/20 font-semibold'
                      : item.isSectorBadge
                      ? 'text-cyan-400 hover:text-cyan-200 bg-cyan-500/10 hover:bg-cyan-500/20 border border-cyan-500/30 font-semibold'
                      : item.isHighlight
                      ? 'text-purple-400 hover:text-purple-200 bg-purple-500/10 hover:bg-purple-500/20 border border-purple-500/20'
                      : 'text-gray-400 hover:text-gray-200 hover:bg-gray-800/60 border border-transparent'
                  }`}
                >
                  <Icon className={`w-3.5 h-3.5 sm:w-4 sm:h-4 ${isActive ? 'text-cyan-400' : item.isSectorBadge ? 'text-cyan-300' : 'text-gray-400'}`} />
                  <span className="hidden xl:inline">{item.fullLabel}</span>
                  <span className="inline xl:hidden">{item.label}</span>
                </button>
              );
            })}
          </nav>

        </div>
      </div>
    </header>
  );
}
