import React, { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import TopHeader from './components/TopHeader';
import ScreenerView from './components/ScreenerView';
import SingleStockScanner from './components/SingleStockScanner';
import SectorPulseView from './components/SectorPulseView';
import ChartStudio from './components/ChartStudio';
import BacktestStudio from './components/BacktestStudio';
import RiskCalculator from './components/RiskCalculator';
import WatchlistView from './components/WatchlistView';
import StrategyGuideView from './components/StrategyGuideView';
import AIForecastStudio from './components/AIForecastStudio';
import TradeJournalView from './components/TradeJournalView';
import ContextualHelpDrawer from './components/ContextualHelpDrawer';
import AlphaChanakyaDrawer from './components/AlphaChanakyaDrawer';
import ErrorBoundary from './components/ErrorBoundary';

export default function App() {
  const [activeTab, setActiveTab] = useState('screener');
  const [selectedTicker, setSelectedTicker] = useState('');
  const [deepScanTicker, setDeepScanTicker] = useState('');
  const [backtestStrategy, setBacktestStrategy] = useState('trend_pullback');
  const [riskSetup, setRiskSetup] = useState(null);
  const [presetUniverse, setPresetUniverse] = useState(null);
  const [presetCustomTickers, setPresetCustomTickers] = useState(null);

  // Global Contextual Help & Jargon Drawer states
  const [helpDrawerOpen, setHelpDrawerOpen] = useState(false);
  const [helpDrawerTerm, setHelpDrawerTerm] = useState(null);

  useEffect(() => {
    const handleKeyDown = (e) => {
      // Toggle help drawer on '?' key if not in form input
      if (e.key === '?' && !['INPUT', 'TEXTAREA', 'SELECT'].includes(e.target.tagName)) {
        e.preventDefault();
        setHelpDrawerOpen(prev => !prev);
      }
    };
    const handleCustomOpen = (e) => {
      if (e.detail?.term) {
        setHelpDrawerTerm(e.detail.term);
      }
      setHelpDrawerOpen(true);
    };

    window.addEventListener('keydown', handleKeyDown);
    window.addEventListener('open-help-drawer', handleCustomOpen);
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
      window.removeEventListener('open-help-drawer', handleCustomOpen);
    };
  }, []);

  // Sidebar responsive states
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
  const [mobileSidebarOpen, setMobileSidebarOpen] = useState(false);

  const handleSelectTicker = (ticker) => {
    setSelectedTicker(ticker);
    setActiveTab('chart');
  };

  const handleOpenRisk = (setup) => {
    setRiskSetup(setup);
    setActiveTab('risk');
  };

  const handleOpenBacktest = (ticker, strategyId) => {
    setSelectedTicker(ticker);
    if (strategyId) {
      setBacktestStrategy(strategyId);
    }
    setActiveTab('backtest');
  };

  const handleOpenAIForecast = (ticker) => {
    setSelectedTicker(ticker);
    setActiveTab('aiforecast');
  };

  const handleScanWatchlist = (watchlistName, tickers) => {
    setPresetUniverse('custom');
    setPresetCustomTickers(tickers);
    setActiveTab('screener');
  };

  const handleScanSector = (sectorName) => {
    if (sectorName.includes('Bank')) {
      setPresetUniverse('NIFTY_BANK');
    } else if (sectorName.includes('IT')) {
      setPresetUniverse('NIFTY_IT');
    } else {
      setPresetUniverse('NIFTY_500');
    }
    setActiveTab('screener');
  };

  const handleLaunchScreenerWithStrategy = (strategyId) => {
    setActiveTab('screener');
  };

  const handleLaunchBacktestWithStrategy = (strategyId) => {
    setBacktestStrategy(strategyId);
    setActiveTab('backtest');
  };

  return (
    <div className="flex h-screen bg-[#0B0F19] text-gray-100 overflow-hidden">
      
      {/* Institutional Vertical Sidebar */}
      <Sidebar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        isCollapsed={isSidebarCollapsed}
        setIsCollapsed={setIsSidebarCollapsed}
        mobileOpen={mobileSidebarOpen}
        setMobileOpen={setMobileSidebarOpen}
      />

      {/* Main Workspace Column */}
      <div className="flex-1 flex flex-col min-w-0 h-screen overflow-hidden">
        
        {/* Top Minimal Header */}
        <TopHeader
          activeTab={activeTab}
          onToggleMobileSidebar={() => setMobileSidebarOpen(!mobileSidebarOpen)}
          onSelectTicker={handleSelectTicker}
          onOpenHelpDrawer={() => { setHelpDrawerTerm(null); setHelpDrawerOpen(true); }}
        />

        {/* Scrollable Canvas View */}
        <main className="flex-1 overflow-y-auto px-4 sm:px-6 lg:px-8 py-5 pb-6">
          <div className="max-w-7xl mx-auto space-y-6">
            <ErrorBoundary>
              {activeTab === 'screener' && (
                <ScreenerView
                  onSelectTicker={handleSelectTicker}
                  onOpenRisk={handleOpenRisk}
                  onOpenBacktest={handleOpenBacktest}
                  onOpenSectorPulse={() => setActiveTab('sectors')}
                  presetUniverse={presetUniverse}
                  presetCustomTickers={presetCustomTickers}
                />
              )}

              {activeTab === 'deepscan' && (
                <SingleStockScanner
                  initialTicker={deepScanTicker}
                  onOpenChart={handleSelectTicker}
                  onOpenAIForecast={handleOpenAIForecast}
                  onOpenBacktest={handleOpenBacktest}
                  onOpenRisk={handleOpenRisk}
                />
              )}

              {activeTab === 'sectors' && (
                <SectorPulseView
                  onScanSector={handleScanSector}
                  onSelectTicker={handleSelectTicker}
                  onOpenAIForecast={handleOpenAIForecast}
                  onOpenRisk={handleOpenRisk}
                  onOpenBacktest={handleOpenBacktest}
                />
              )}

              {activeTab === 'chart' && (
                <ChartStudio
                  initialTicker={selectedTicker}
                  onOpenRisk={handleOpenRisk}
                />
              )}

              {activeTab === 'aiforecast' && (
                <AIForecastStudio
                  selectedTicker={selectedTicker}
                  onSelectTicker={handleSelectTicker}
                  onOpenRisk={handleOpenRisk}
                  onOpenBacktest={handleOpenBacktest}
                />
              )}

              {activeTab === 'backtest' && (
                <BacktestStudio
                  initialTicker={selectedTicker}
                  initialStrategy={backtestStrategy}
                />
              )}

              {activeTab === 'journal' && (
                <TradeJournalView
                  onOpenChart={handleSelectTicker}
                  onOpenDeepScan={(t) => {
                    setDeepScanTicker(t);
                    setActiveTab('deepscan');
                  }}
                  onOpenAIForecast={handleOpenAIForecast}
                />
              )}

              {activeTab === 'risk' && (
                <RiskCalculator
                  prefillSetup={riskSetup}
                />
              )}

              {activeTab === 'watchlists' && (
                <WatchlistView
                  onSelectTicker={handleSelectTicker}
                  onOpenAIForecast={handleOpenAIForecast}
                  onScanWatchlist={handleScanWatchlist}
                />
              )}

              {activeTab === 'matrix' && (
                <StrategyGuideView
                  onLaunchScreener={handleLaunchScreenerWithStrategy}
                  onLaunchBacktest={handleLaunchBacktestWithStrategy}
                />
              )}
            </ErrorBoundary>

            {/* Institutional Footer */}
            <footer className="border-t border-gray-900/90 py-5 text-xs text-gray-500">
              <div className="flex flex-col sm:flex-row items-center justify-between gap-3">
                <div className="flex items-center space-x-2 flex-wrap">
                  <span className="font-semibold text-gray-300">SwingDesk Pro</span>
                  <span className="text-gray-700">|</span>
                  <span>© 2026 <a href="https://www.rupeemap.in" target="_blank" rel="noopener noreferrer" className="text-cyan-400 font-medium hover:underline hover:text-cyan-300 transition-colors">rupeemap.in labs</a> (by <strong className="text-gray-300 font-medium">Sandesh Rathi</strong>). All rights reserved.</span>
                </div>
                <div className="flex items-center space-x-4 text-[11px] text-gray-400 font-mono">
                  <span>Quantitative Terminal</span>
                  <span className="text-gray-700">•</span>
                  <span>NSE & BSE Indian Equities</span>
                </div>
              </div>
            </footer>

          </div>
        </main>

      </div>

      {/* Global Contextual Page Guide & Jargon Drawer */}
      <ContextualHelpDrawer
        isOpen={helpDrawerOpen}
        onClose={() => { setHelpDrawerOpen(false); setHelpDrawerTerm(null); }}
        activeTab={activeTab}
        initialTerm={helpDrawerTerm}
      />

      {/* AlphaChanakya AI Financial Copilot Interactive Widget */}
      <AlphaChanakyaDrawer
        activeTab={activeTab}
        selectedTicker={selectedTicker || deepScanTicker}
      />

    </div>
  );
}
