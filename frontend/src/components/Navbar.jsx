import React from 'react';
import { 
  TrendingUp, 
  BarChart2, 
  Layers, 
  ShieldAlert, 
  Bookmark, 
  Activity, 
  Cpu,
  Zap
} from 'lucide-react';

export default function Navbar({ activeTab, setActiveTab }) {
  const navItems = [
    { id: 'screener', label: 'Live Screener', icon: Layers },
    { id: 'deepscan', label: 'Deep Scan', icon: Zap },
    { id: 'chart', label: 'Chart Studio', icon: BarChart2 },
    { id: 'backtest', label: 'Backtest Studio', icon: TrendingUp },
    { id: 'risk', label: 'Risk Calculator', icon: ShieldAlert },
    { id: 'watchlists', label: 'Watchlists', icon: Bookmark },
  ];

  return (
    <header className="border-b border-gray-800 bg-[#0B0F19]/90 backdrop-blur-md sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          
          {/* Brand Logo */}
          <div className="flex items-center space-x-3 cursor-pointer" onClick={() => setActiveTab('screener')}>
            <div className="w-9 h-9 rounded-lg bg-gradient-to-tr from-cyan-600 to-blue-500 flex items-center justify-center shadow-lg shadow-cyan-500/20 border border-cyan-400/30">
              <Activity className="w-5 h-5 text-white" />
            </div>
            <div>
              <div className="flex items-center space-x-1.5">
                <span className="font-bold text-lg text-white tracking-tight">SwingDesk</span>
                <span className="text-xs font-semibold px-1.5 py-0.5 rounded bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">PRO</span>
              </div>
              <p className="text-[10px] text-gray-400 tracking-wider uppercase font-medium">NSE & BSE Quantitative Suite</p>
            </div>
          </div>

          {/* Navigation Links */}
          <nav className="flex space-x-1 sm:space-x-2">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => setActiveTab(item.id)}
                  className={`flex items-center space-x-2 px-3 py-2 rounded-lg text-xs sm:text-sm font-medium transition-all duration-150 ${
                    isActive
                      ? 'bg-cyan-500/10 text-cyan-300 border border-cyan-500/30 shadow-sm shadow-cyan-500/10'
                      : 'text-gray-400 hover:text-gray-200 hover:bg-gray-800/50 border border-transparent'
                  }`}
                >
                  <Icon className={`w-4 h-4 ${isActive ? 'text-cyan-400' : 'text-gray-400'}`} />
                  <span>{item.label}</span>
                </button>
              );
            })}
          </nav>

          {/* System Status Indicators */}
          <div className="hidden lg:flex items-center space-x-3 text-xs">
            <div className="flex items-center space-x-2 px-2.5 py-1 rounded-md bg-gray-900/80 border border-gray-800 text-gray-300">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
              <span className="text-[11px] font-medium text-emerald-400">YF Feed Active</span>
            </div>
            <div className="flex items-center space-x-1.5 px-2.5 py-1 rounded-md bg-gray-900/80 border border-gray-800 text-gray-400">
              <Cpu className="w-3.5 h-3.5 text-cyan-400" />
              <span className="text-[11px] font-mono">v1.0.0-PRO</span>
            </div>
          </div>

        </div>
      </div>
    </header>
  );
}
