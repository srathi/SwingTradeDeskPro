import React, { useState } from 'react';
import Navbar from './components/Navbar';
import ScreenerView from './components/ScreenerView';
import ChartStudio from './components/ChartStudio';
import BacktestStudio from './components/BacktestStudio';
import RiskCalculator from './components/RiskCalculator';
import WatchlistView from './components/WatchlistView';
import SingleStockScanner from './components/SingleStockScanner';
import ErrorBoundary from './components/ErrorBoundary';

export default function App() {
  const [activeTab, setActiveTab] = useState('screener');
  const [selectedTicker, setSelectedTicker] = useState('RELIANCE.NS');
  const [deepScanTicker, setDeepScanTicker] = useState('');
  const [backtestStrategy, setBacktestStrategy] = useState('trend_pullback');
  const [riskSetup, setRiskSetup] = useState(null);
  const [presetUniverse, setPresetUniverse] = useState(null);
  const [presetCustomTickers, setPresetCustomTickers] = useState(null);

  // Cross-component navigation handlers
  const handleSelectTicker = (ticker) => {
    let sym = ticker;
    if (sym && !sym.includes('.') && !['AAPL', 'MSFT', 'NVDA', 'GOOGL', 'AMZN', 'TSLA'].includes(sym)) {
      sym += '.NS';
    }
    setSelectedTicker(sym);
    setActiveTab('chart');
  };

  const handleOpenDeepScan = (ticker) => {
    let sym = ticker;
    if (sym && !sym.includes('.') && !['AAPL', 'MSFT', 'NVDA', 'GOOGL', 'AMZN', 'TSLA'].includes(sym)) {
      sym += '.NS';
    }
    setDeepScanTicker(sym);
    setActiveTab('deepscan');
  };

  const handleOpenRisk = (setup) => {
    setRiskSetup(setup);
    setActiveTab('risk');
  };

  const handleOpenBacktest = (ticker, strategyId) => {
    let sym = ticker;
    if (sym && !sym.includes('.') && !['AAPL', 'MSFT', 'NVDA', 'GOOGL', 'AMZN', 'TSLA'].includes(sym)) {
      sym += '.NS';
    }
    setSelectedTicker(sym);
    setBacktestStrategy(strategyId || 'trend_pullback');
    setActiveTab('backtest');
  };

  const handleScanWatchlist = (watchlist) => {
    if (watchlist) {
      setPresetUniverse(`WL_${watchlist.id}`);
      setPresetCustomTickers(watchlist.tickers);
    }
    setActiveTab('screener');
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
        </ErrorBoundary>
      </main>

      {/* Institutional Footer */}
      <footer className="border-t border-gray-900/80 py-4 bg-[#0B0F19] text-center text-xs text-gray-400">
        <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-2">
          <span>SwingDesk Pro — Quantitative Swing Trading Platform for Indian & Global Markets</span>
          <span className="font-mono text-gray-400">Data powered by Yahoo Finance API</span>
        </div>
      </footer>
    </div>
  );
}
