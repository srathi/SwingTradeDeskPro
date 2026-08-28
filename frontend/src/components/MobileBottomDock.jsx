import React from 'react';
import { Layers, Zap, Compass, BarChart2, MessageSquareCode } from 'lucide-react';

export default function MobileBottomDock({
  activeTab,
  setActiveTab,
  onToggleCopilot,
  isCopilotOpen
}) {
  const navItems = [
    { id: 'screener', label: 'Screener', icon: Layers },
    { id: 'deepscan', label: 'Deep Scan', icon: Zap },
    { id: 'sectors', label: 'Sectors', icon: Compass },
    { id: 'chart', label: 'Chart', icon: BarChart2 }
  ];

  return (
    <nav 
      className="lg:hidden fixed bottom-0 left-0 right-0 z-40 bg-gray-950/90 backdrop-blur-xl border-t border-gray-800/90 px-2 py-1.5 shadow-2xl safe-area-bottom"
      aria-label="Mobile Bottom Navigation"
    >
      <div className="flex items-center justify-around max-w-md mx-auto">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`flex flex-col items-center justify-center py-1 px-3 rounded-xl transition-all duration-150 relative min-w-[56px] min-h-[48px] ${
                isActive 
                  ? 'text-cyan-400 font-bold bg-cyan-950/40 border border-cyan-800/40 shadow-sm' 
                  : 'text-gray-400 hover:text-gray-200 hover:bg-gray-900/50'
              }`}
            >
              <Icon className={`w-5 h-5 transition-transform ${isActive ? 'scale-110 text-cyan-400' : ''}`} />
              <span className="text-[10px] mt-0.5 font-medium tracking-tight whitespace-nowrap">
                {item.label}
              </span>
              {isActive && (
                <span className="absolute -bottom-0.5 w-4 h-0.5 bg-cyan-400 rounded-full shadow-[0_0_8px_rgba(34,211,238,0.8)]" />
              )}
            </button>
          );
        })}

        {/* AlphaChanakya AI Quick Trigger */}
        <button
          onClick={onToggleCopilot}
          className={`flex flex-col items-center justify-center py-1 px-3 rounded-xl transition-all duration-150 relative min-w-[56px] min-h-[48px] ${
            isCopilotOpen
              ? 'text-amber-300 font-bold bg-amber-950/40 border border-amber-800/40 shadow-sm'
              : 'text-gray-400 hover:text-amber-300 hover:bg-gray-900/50'
          }`}
          title="Open AlphaChanakya AI Copilot"
        >
          <div className="relative">
            <MessageSquareCode className={`w-5 h-5 transition-transform ${isCopilotOpen ? 'scale-110 text-amber-300' : 'text-amber-400'}`} />
            <span className="absolute -top-0.5 -right-1 w-2 h-2 rounded-full bg-emerald-400 animate-pulse ring-2 ring-gray-950" />
          </div>
          <span className="text-[10px] mt-0.5 font-medium tracking-tight whitespace-nowrap text-amber-300/90">
            Chanakya
          </span>
          {isCopilotOpen && (
            <span className="absolute -bottom-0.5 w-4 h-0.5 bg-amber-400 rounded-full shadow-[0_0_8px_rgba(251,191,36,0.8)]" />
          )}
        </button>
      </div>
    </nav>
  );
}
