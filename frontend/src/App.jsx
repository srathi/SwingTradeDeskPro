import React, { useState } from 'react';
import Navbar from './components/Navbar';
import ScreenerView from './components/ScreenerView';
import SingleStockScanner from './components/SingleStockScanner';
import SectorPulseView from './components/SectorPulseView';
import ChartStudio from './components/ChartStudio';
import BacktestStudio from './components/BacktestStudio';
import RiskCalculator from './components/RiskCalculator';
import WatchlistView from './components/WatchlistView';
import StrategyGuideView from './components/StrategyGuideView';
import ErrorBoundary from './components/ErrorBoundary';

export default function App() {
  const [activeTab, setActiveTab] = useState('screener');
  const [selectedTicker, setSelectedTicker] = useState('RELIANCE.NS');
  const [deepScanTicker, setDeepScanTicker] = useState('');
  const [backtestStrategy, setBacktestStrategy] = useState('trend_pullback');
  const [riskSetup, setRiskSetup] = useState(null);
  const [presetUniverse, setPresetUniverse] = useState(null);
  const [presetCustomTickers, setPresetCustomTickers] = useState(null);

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

  const handleScanWatchlist = (watchlistName, tickers) => {
    setPresetUniverse('custom');
    setPresetCustomTickers(tickers);
    setActiveTab('screener');
  };

  const handleScanSector = (sectorName) => {
    // Map sector to appropriate universe or custom tickers
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
    <div className="min-h-screen bg-[#0B0F19] text-gray-100 flex flex-col">
      <Navbar activeTab={activeTab} setActiveTab={setActiveTab} />
      
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
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
              onOpenBacktest={handleOpenBacktest}
              onOpenRisk={handleOpenRisk}
            />
          )}

          {activeTab === 'sectors' && (
            <SectorPulseView
              onScanSector={handleScanSector}
            />
          )}

          {activeTab === 'chart' && (
            <ChartStudio
              initialTicker={selectedTicker}
              onOpenRisk={handleOpenRisk}
            />
          )}

          {activeTab === 'backtest' && (
            <BacktestStudio
              initialTicker={selectedTicker}
              initialStrategy={backtestStrategy}
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
      </main>

      {/* Institutional Footer with Sandesh Rathi & rupeemap.in labs Copyright */}
      <footer className="border-t border-gray-900/90 py-5 bg-[#080C14] text-xs text-gray-400">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-3">
          <div className="flex items-center space-x-2 flex-wrap">
            <span className="font-semibold text-gray-200">SwingDesk Pro</span>
            <span className="text-gray-600">|</span>
            <span>© 2026 <strong className="text-cyan-400 font-medium">rupeemap.in labs</strong> (by <strong className="text-gray-200 font-medium">Sandesh Rathi</strong>). All rights reserved.</span>
          </div>
          <div className="flex items-center space-x-4 text-[11px] text-gray-400 font-mono">
            <span>Quantitative Market Intelligence</span>
            <span className="text-gray-700">•</span>
            <span>NSE & BSE Indian Equities</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
