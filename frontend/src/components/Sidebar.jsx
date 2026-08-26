import React, { useState } from 'react';
import { 
  TrendingUp, 
  BarChart2, 
  Layers, 
  ShieldAlert, 
  Bookmark, 
  Activity, 
  Zap,
  BookOpen,
  Compass,
  ChevronLeft,
  ChevronRight,
  X
} from 'lucide-react';

export default function Sidebar({ 
  activeTab, 
  setActiveTab, 
  isCollapsed, 
  setIsCollapsed, 
  mobileOpen, 
  setMobileOpen 
}) {
  const navSections = [
    {
      title: "Discovery & Regime",
      items: [
        { id: 'screener', label: 'Live Screener', icon: Layers, badge: 'Realtime' },
        { id: 'deepscan', label: 'Deep Scan', icon: Zap },
        { id: 'sectors', label: 'Sector Pulse', icon: Compass, isSectorBadge: true, badge: 'Regime' },
      ]
    },
    {
      title: "Execution & Analysis",
      items: [
        { id: 'chart', label: 'Chart Studio', icon: BarChart2 },
        { id: 'backtest', label: 'Backtest Studio', icon: TrendingUp },
        { id: 'risk', label: 'Risk Calculator', icon: ShieldAlert },
      ]
    },
    {
      title: "Workspace & Research",
      items: [
        { id: 'watchlists', label: 'Watchlists', icon: Bookmark },
        { id: 'matrix', label: 'Strategy Matrix', icon: BookOpen, isHighlight: true },
      ]
    }
  ];

  const handleTabClick = (tabId) => {
    setActiveTab(tabId);
    if (mobileOpen) setMobileOpen(false);
  };

  return (
    <>
      {/* Mobile Backdrop Overlay */}
      {mobileOpen && (
        <div 
          onClick={() => setMobileOpen(false)}
          className="fixed inset-0 bg-black/70 backdrop-blur-sm z-40 md:hidden transition-opacity"
        />
      )}

      {/* Sidebar Container */}
      <aside className={`
        fixed md:static inset-y-0 left-0 z-50
        flex flex-col bg-[#070b14] border-r border-gray-800/90
        transition-all duration-300 ease-in-out
        ${mobileOpen ? 'translate-x-0 w-64' : '-translate-x-full md:translate-x-0'}
        ${isCollapsed ? 'md:w-16' : 'md:w-60'}
      `}>
        
        {/* Brand Header */}
        <div className={`h-16 flex items-center border-b border-gray-800/80 px-3.5 ${isCollapsed ? 'justify-center' : 'justify-between'}`}>
          <div 
            onClick={() => handleTabClick('screener')}
            className="flex items-center space-x-2.5 cursor-pointer overflow-hidden"
          >
            <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-cyan-600 to-blue-500 flex items-center justify-center shadow-lg shadow-cyan-500/20 border border-cyan-400/30 flex-shrink-0">
              <Activity className="w-4 h-4 text-white" />
            </div>

            {!isCollapsed && (
              <div className="transition-opacity duration-200">
                <div className="flex items-center space-x-1.5">
                  <span className="font-bold text-base text-white tracking-tight leading-none">SwingDesk</span>
                  <span className="text-[9px] font-semibold px-1.5 py-0.2 rounded bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 font-mono">PRO</span>
                </div>
                <p className="text-[9px] text-cyan-400/90 font-mono font-medium tracking-wide mt-0.5">
                  <a 
                    href="https://www.rupeemap.in" 
                    target="_blank" 
                    rel="noopener noreferrer" 
                    onClick={(e) => e.stopPropagation()} 
                    className="hover:underline hover:text-cyan-300 transition-colors"
                  >
                    rupeemap.in labs
                  </a>
                </p>
              </div>
            )}
          </div>

          {/* Mobile Close Button */}
          <button 
            onClick={() => setMobileOpen(false)}
            className="p-1 rounded-lg text-gray-400 hover:text-white md:hidden"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Navigation Sections */}
        <div className="flex-1 overflow-y-auto py-3 px-2 space-y-5 scrollbar-none">
          {navSections.map((section, idx) => (
            <div key={idx} className="space-y-1">
              {!isCollapsed && (
                <div className="px-2 pb-1 text-[10px] uppercase font-mono font-bold tracking-wider text-gray-400">
                  {section.title}
                </div>
              )}

              <div className="space-y-0.5">
                {section.items.map((item) => {
                  const Icon = item.icon;
                  const isActive = activeTab === item.id;

                  return (
                    <button
                      key={item.id}
                      onClick={() => handleTabClick(item.id)}
                      title={isCollapsed ? item.label : undefined}
                      className={`
                        w-full flex items-center rounded-xl transition-all duration-150 relative group
                        ${isCollapsed ? 'justify-center p-2.5' : 'space-x-2.5 px-3 py-2 text-xs sm:text-sm'}
                        ${isActive
                          ? 'bg-cyan-500/15 text-cyan-300 font-semibold border border-cyan-500/30 shadow-sm shadow-cyan-500/10'
                          : item.isSectorBadge
                          ? 'text-cyan-400 hover:text-cyan-200 hover:bg-cyan-500/10 border border-transparent'
                          : item.isHighlight
                          ? 'text-purple-300 hover:text-purple-100 hover:bg-purple-500/10 border border-transparent'
                          : 'text-gray-400 hover:text-gray-200 hover:bg-gray-800/60 border border-transparent'
                        }
                      `}
                    >
                      <Icon className={`
                        flex-shrink-0 transition-colors
                        ${isCollapsed ? 'w-5 h-5' : 'w-4 h-4'}
                        ${isActive ? 'text-cyan-400' : item.isSectorBadge ? 'text-cyan-400' : item.isHighlight ? 'text-purple-400' : 'text-gray-400 group-hover:text-gray-200'}
                      `} />

                      {!isCollapsed && (
                        <div className="flex-1 flex items-center justify-between overflow-hidden">
                          <span className="truncate">{item.label}</span>
                          {item.badge && (
                            <span className={`text-[9px] px-1.5 py-0.2 rounded font-mono font-bold uppercase tracking-wider ${
                              isActive ? 'bg-cyan-400/20 text-cyan-200' : 'bg-gray-800/80 text-gray-400'
                            }`}>
                              {item.badge}
                            </span>
                          )}
                        </div>
                      )}

                      {/* Tooltip for collapsed mode */}
                      {isCollapsed && (
                        <div className="fixed left-16 ml-2 px-2.5 py-1 bg-gray-900 text-gray-100 text-xs rounded-md shadow-xl border border-gray-700 opacity-0 pointer-events-none group-hover:opacity-100 group-hover:pointer-events-auto transition-opacity z-50 whitespace-nowrap">
                          {item.label}
                        </div>
                      )}
                    </button>
                  );
                })}
              </div>
            </div>
          ))}
        </div>

        {/* Sidebar Footer Controls */}
        <div className="p-2 border-t border-gray-800/80 bg-[#060912] space-y-2">
          
          {/* Market Status Pill */}
          {!isCollapsed ? (
            <div className="flex items-center justify-between px-2.5 py-1.5 rounded-lg bg-gray-900/80 border border-gray-800 text-[11px] font-mono">
              <div className="flex items-center space-x-1.5">
                <span className="relative flex h-2 w-2">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                </span>
                <span className="text-gray-300 font-medium">NSE/BSE</span>
              </div>
              <span className="text-emerald-400 font-semibold">Active</span>
            </div>
          ) : (
            <div className="flex justify-center py-1">
              <span className="relative flex h-2.5 w-2.5">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500"></span>
              </span>
            </div>
          )}

          {/* Desktop Collapse Toggle Button */}
          <button
            onClick={() => setIsCollapsed(!isCollapsed)}
            className="hidden md:flex w-full items-center justify-center p-1.5 rounded-lg text-gray-400 hover:text-white hover:bg-gray-800/60 border border-transparent hover:border-gray-700 transition-all text-xs font-mono"
            title={isCollapsed ? "Expand Sidebar" : "Collapse Sidebar"}
          >
            {isCollapsed ? (
              <ChevronRight className="w-4 h-4 text-cyan-400" />
            ) : (
              <div className="flex items-center space-x-1.5">
                <ChevronLeft className="w-4 h-4 text-gray-400" />
                <span className="text-[11px] text-gray-400">Collapse Panel</span>
              </div>
            )}
          </button>

          {/* Attribution */}
          {!isCollapsed && (
            <div className="px-2 pt-1 text-[9px] text-gray-400 font-mono text-center">
              <a 
                href="https://www.rupeemap.in" 
                target="_blank" 
                rel="noopener noreferrer" 
                className="hover:underline hover:text-cyan-400 transition-colors"
              >
                rupeemap.in labs
              </a> • by <strong className="text-gray-400 font-medium">Sandesh Rathi</strong>
            </div>
          )}

        </div>

      </aside>
    </>
  );
}
