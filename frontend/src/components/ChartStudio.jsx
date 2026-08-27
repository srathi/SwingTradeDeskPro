import React, { useEffect, useRef, useState } from 'react';
import { createChart } from 'lightweight-charts';
import { 
  RefreshCw, 
  TrendingUp, 
  Eye, 
  Sliders, 
  ShieldAlert, 
  ArrowUpRight, 
  ArrowDownRight, 
  Info,
  AlertCircle,
  Sparkles,
  BarChart2
} from 'lucide-react';
import { fetchChartData, searchStocks } from '../services/api';
import StockSearchInput from './StockSearchInput';

const fmt = (v, d = 2) => {
  if (typeof v === 'number' && !isNaN(v)) return v.toFixed(d);
  if (typeof v === 'string' && !isNaN(Number(v))) return Number(v).toFixed(d);
  return '—';
};

export default function ChartStudio({ initialTicker = "", onOpenRisk }) {
  const chartContainerRef = useRef(null);
  const rsiContainerRef = useRef(null);
  const chartRef = useRef(null);
  const rsiChartRef = useRef(null);

  const [ticker, setTicker] = useState(initialTicker || "");
  const [period, setPeriod] = useState("1y");
  const [strategyId, setStrategyId] = useState("trend_pullback");
  const [chartData, setChartData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState(null);
  const [reboundSuggestions, setReboundSuggestions] = useState([]);

  // Overlay toggles
  const [showEMA20, setShowEMA20] = useState(true);
  const [showEMA50, setShowEMA50] = useState(true);
  const [showEMA200, setShowEMA200] = useState(true);
  const [showSetupLines, setShowSetupLines] = useState(true);

  useEffect(() => {
    if (initialTicker !== undefined) {
      setTicker(initialTicker);
    }
  }, [initialTicker]);

  useEffect(() => {
    if (!ticker || ticker.trim().length === 0) {
      setChartData(null);
      setLoading(false);
      setErrorMsg(null);
      return;
    }
    loadData(ticker, period, strategyId);
  }, [ticker, period, strategyId]);

  const loadData = async (sym, prd, strat) => {
    if (!sym || sym.trim().length === 0) return;
    setLoading(true);
    setErrorMsg(null);
    setReboundSuggestions([]);

    try {
      let cleanSym = sym.trim().toUpperCase();
      const data = await fetchChartData(cleanSym, prd, strat);
      setChartData(data);
    } catch (err) {
      setErrorMsg(err.message || `No price data available for ticker '${sym}'`);
      try {
        const suggestions = await searchStocks(sym);
        setReboundSuggestions(suggestions);
      } catch (sugErr) {}
    } finally {
      setLoading(false);
    }
  };

  const handleSelectStock = (selectedSym, stockObj) => {
    setTicker(selectedSym);
    setErrorMsg(null);
    setReboundSuggestions([]);
  };

  useEffect(() => {
    if (!chartContainerRef.current || !chartData || !chartData.candles || chartData.candles.length === 0) return;

    if (chartRef.current) {
      try { chartRef.current.remove(); } catch (e) {}
      chartRef.current = null;
    }
    if (rsiChartRef.current) {
      try { rsiChartRef.current.remove(); } catch (e) {}
      rsiChartRef.current = null;
    }

    const container = chartContainerRef.current;
    const rsiContainer = rsiContainerRef.current;

    const initialWidth = container.clientWidth || 800;

    let chart = null;
    let rsiChart = null;

    try {
      chart = createChart(container, {
        width: initialWidth,
        height: 400,
        layout: {
          background: { color: '#0B0F19' },
          textColor: '#9CA3AF',
          fontSize: 11,
          fontFamily: 'Inter, sans-serif'
        },
        grid: {
          vertLines: { color: '#1F2937' },
          horzLines: { color: '#1F2937' }
        },
        timeScale: {
          borderColor: '#374151',
          timeVisible: true,
          secondsVisible: false
        },
        rightPriceScale: {
          borderColor: '#374151',
          scaleMargins: { top: 0.1, bottom: 0.2 }
        }
      });
      chartRef.current = chart;

      const candleSeries = chart.addCandlestickSeries({
        upColor: '#10B981',
        downColor: '#EF4444',
        borderUpColor: '#10B981',
        borderDownColor: '#EF4444',
        wickUpColor: '#10B981',
        wickDownColor: '#EF4444'
      });

      const dateMap = new Map();
      chartData.candles.forEach(c => {
        dateMap.set(c.time, {
          time: c.time,
          open: c.open,
          high: c.high,
          low: c.low,
          close: c.close
        });
      });
      const candleData = Array.from(dateMap.values()).sort((a, b) => (a.time > b.time ? 1 : -1));
      candleSeries.setData(candleData);

      // Volume Series
      const volumeSeries = chart.addHistogramSeries({
        priceFormat: { type: 'volume' },
        priceScaleId: '',
        scaleMargins: { top: 0.8, bottom: 0 }
      });
      const volumeData = chartData.candles.map(c => ({
        time: c.time,
        value: c.volume || 1000,
        color: c.close >= c.open ? 'rgba(16, 185, 129, 0.25)' : 'rgba(239, 68, 68, 0.25)'
      }));
      volumeSeries.setData(volumeData);      // EMAs
      const ema20Data = chartData.indicators?.ema_20 || chartData.ema20;
      if (showEMA20 && ema20Data && ema20Data.length > 0) {
        const ema20Series = chart.addLineSeries({
          color: '#06B6D4',
          lineWidth: 1.5,
          title: '20 EMA'
        });
        ema20Series.setData(ema20Data.filter(p => p.value !== null && !isNaN(p.value)));
      }

      const ema50Data = chartData.indicators?.ema_50 || chartData.ema50;
      if (showEMA50 && ema50Data && ema50Data.length > 0) {
        const ema50Series = chart.addLineSeries({
          color: '#F59E0B',
          lineWidth: 1.5,
          title: '50 EMA'
        });
        ema50Series.setData(ema50Data.filter(p => p.value !== null && !isNaN(p.value)));
      }

      const ema200Data = chartData.indicators?.ema_200 || chartData.ema200;
      if (showEMA200 && ema200Data && ema200Data.length > 0) {
        const ema200Series = chart.addLineSeries({
          color: '#A855F7',
          lineWidth: 1.5,
          title: '200 EMA'
        });
        ema200Series.setData(ema200Data.filter(p => p.value !== null && !isNaN(p.value)));
      }

      // Setup Price Lines (Entry, Stop Loss, Target 1, Target 2)
      const currentSetup = chartData.setup || chartData.active_setup;
      if (showSetupLines && currentSetup) {
        const s = currentSetup;
        if (s.close) {
          candleSeries.createPriceLine({
            price: s.close,
            color: '#06B6D4',
            lineWidth: 1,
            lineStyle: 0,
            title: 'ENTRY'
          });
        }
        if (s.stop_loss) {
          candleSeries.createPriceLine({
            price: s.stop_loss,
            color: '#EF4444',
            lineWidth: 1,
            lineStyle: 2,
            title: 'STOP LOSS'
          });
        }
        if (s.target_1) {
          candleSeries.createPriceLine({
            price: s.target_1,
            color: '#10B981',
            lineWidth: 1,
            lineStyle: 2,
            title: 'TARGET 1 (2R)'
          });
        }
        if (s.target_2) {
          candleSeries.createPriceLine({
            price: s.target_2,
            color: '#34D399',
            lineWidth: 1,
            lineStyle: 2,
            title: 'TARGET 2 (3R)'
          });
        }
      }

      // RSI Subchart
      const rsiData = chartData.indicators?.rsi_14 || chartData.rsi;
      if (rsiContainer && rsiData && rsiData.length > 0) {
        rsiChart = createChart(rsiContainer, {
          width: initialWidth,
          height: 120,
          layout: {
            background: { color: '#0B0F19' },
            textColor: '#9CA3AF',
            fontSize: 10,
            fontFamily: 'Inter, sans-serif'
          },
          grid: {
            vertLines: { color: '#1F2937' },
            horzLines: { color: '#1F2937' }
          },
          timeScale: {
            borderColor: '#374151',
            timeVisible: true
          },
          rightPriceScale: {
            borderColor: '#374151',
            scaleMargins: { top: 0.1, bottom: 0.1 }
          }
        });
        rsiChartRef.current = rsiChart;

        const rsiSeries = rsiChart.addLineSeries({
          color: '#EAB308',
          lineWidth: 1.5,
          title: 'RSI(14)'
        });
        rsiSeries.setData(rsiData.filter(p => p.value !== null && !isNaN(p.value)));

        rsiSeries.createPriceLine({ price: 70, color: '#EF4444', lineWidth: 1, lineStyle: 2, title: '70' });
        rsiSeries.createPriceLine({ price: 30, color: '#10B981', lineWidth: 1, lineStyle: 2, title: '30' });
        rsiSeries.createPriceLine({ price: 50, color: '#6B7280', lineWidth: 1, lineStyle: 3, title: '50' });

        // Synchronize timescale between main and RSI subchart
        chart.timeScale().subscribeVisibleLogicalRangeChange(range => {
          if (range && rsiChartRef.current) {
            rsiChartRef.current.timeScale().setVisibleLogicalRange(range);
          }
        });
        rsiChart.timeScale().subscribeVisibleLogicalRangeChange(range => {
          if (range && chartRef.current) {
            chartRef.current.timeScale().setVisibleLogicalRange(range);
          }
        });
      }

    } catch (e) {
      console.error("TradingView Lightweight Charts render error:", e);
    }

    const handleResize = () => {
      if (chartRef.current && container) {
        chartRef.current.applyOptions({ width: container.clientWidth || 800 });
      }
      if (rsiChartRef.current && rsiContainer) {
        rsiChartRef.current.applyOptions({ width: rsiContainer.clientWidth || 800 });
      }
    };
    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      if (chartRef.current) {
        try { chartRef.current.remove(); } catch (e) {}
        chartRef.current = null;
      }
      if (rsiChartRef.current) {
        try { rsiChartRef.current.remove(); } catch (e) {}
        rsiChartRef.current = null;
      }
    };
  }, [chartData, showEMA20, showEMA50, showEMA200, showSetupLines]);

  const setup = chartData ? (chartData.setup || chartData.active_setup) : null;

  return (
    <div className="space-y-6">
      
      {/* Top Search & Configuration Header Card */}
      <div className="bg-gray-900/80 border border-gray-800 rounded-2xl p-5 shadow-xl space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
          
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center text-cyan-400">
              <BarChart2 className="w-5 h-5" />
            </div>
            <div>
              <h1 className="text-lg sm:text-xl font-bold text-white tracking-tight">Interactive Chart Studio</h1>
              <p className="text-xs text-gray-400">TradingView candlesticks with EMA support bands, RSI momentum, and trade overlays</p>
            </div>
          </div>

          {chartData && (
            <div className="flex items-center space-x-3 bg-gray-950 px-4 py-2 rounded-xl border border-gray-800">
              <div>
                <span className="text-[10px] text-gray-500 uppercase font-mono block">Latest Close</span>
                <span className="font-mono text-base font-bold text-white">₹{fmt(chartData.latest_close)}</span>
              </div>
              <div className="border-l border-gray-800 pl-3">
                <span className="text-[10px] text-gray-500 uppercase font-mono block">RSI(14)</span>
                <span className={`font-mono text-base font-bold ${chartData.latest_rsi <= 40 ? 'text-emerald-400' : 'text-yellow-400'}`}>
                  {fmt(chartData.latest_rsi, 1)}
                </span>
              </div>
            </div>
          )}
        </div>

        {/* Input Bar */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-6 gap-3 pt-2">
          <div className="lg:col-span-2">
            <label className="text-xs font-medium text-gray-400 block mb-1">Select Target Symbol</label>
            <StockSearchInput
              value={ticker}
              onSelectStock={handleSelectStock}
              placeholder="Type ticker (e.g. RELIANCE, SBIN, PICCADIL)..."
              className="w-full"
            />
          </div>

          <div className="lg:col-span-2">
            <label className="text-xs font-medium text-gray-400 block mb-1">Quantitative Strategy Overlay</label>
            <select
              value={strategyId}
              onChange={(e) => setStrategyId(e.target.value)}
              className="w-full bg-gray-950 border border-gray-700 rounded-lg px-3 py-2 text-sm text-gray-200 focus:outline-none focus:border-cyan-500 font-mono"
            >
              <option value="trend_pullback">Trend-Pullback (20/50 EMA)</option>
              <option value="vcp_breakout">VCP & Base Breakout</option>
              <option value="mean_reversion">Mean Reversion (Bollinger + RSI)</option>
              <option value="volatility_squeeze">TTM Volatility Squeeze</option>
              <option value="connors_rsi2">Connors RSI(2) Mean Reversion</option>
              <option value="relative_strength_leader">Mansfield RS Stage-2 Leader</option>
            </select>
          </div>

          <div>
            <label className="text-xs font-medium text-gray-400 block mb-1">Time Horizon</label>
            <select
              value={period}
              onChange={(e) => setPeriod(e.target.value)}
              className="w-full bg-gray-950 border border-gray-700 rounded-lg px-3 py-2 text-sm text-gray-200 focus:outline-none focus:border-cyan-500"
            >
              <option value="6mo">6 Months</option>
              <option value="1y">1 Year</option>
              <option value="2y">2 Years</option>
              <option value="5y">5 Years</option>
            </select>
          </div>

          {/* Indicator toggles */}
          <div className="flex items-end space-x-1">
            <div className="flex items-center space-x-1 bg-gray-950 p-1 rounded-lg border border-gray-800 text-gray-300 w-full h-[38px] justify-around">
              <button
                onClick={() => setShowEMA20(!showEMA20)}
                className={`px-1.5 py-1 rounded font-mono text-[10px] sm:text-[11px] ${showEMA20 ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40' : 'text-gray-500'}`}
              >
                20 EMA
              </button>
              <button
                onClick={() => setShowEMA50(!showEMA50)}
                className={`px-1.5 py-1 rounded font-mono text-[10px] sm:text-[11px] ${showEMA50 ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40' : 'text-gray-500'}`}
              >
                50 EMA
              </button>
              <button
                onClick={() => setShowEMA200(!showEMA200)}
                className={`px-1.5 py-1 rounded font-mono text-[10px] sm:text-[11px] ${showEMA200 ? 'bg-purple-500/20 text-purple-300 border border-purple-500/40' : 'text-gray-500'}`}
              >
                200 EMA
              </button>
            </div>
          </div>
        </div>

      </div>

      {/* Error & Rebound Suggestions Banner */}
      {errorMsg && (
        <div className="p-4 bg-red-950/40 border border-red-800/80 rounded-xl space-y-3">
          <div className="flex items-center space-x-2 text-red-300 text-xs font-semibold">
            <AlertCircle className="w-4 h-4 text-red-400 flex-shrink-0" />
            <span>{errorMsg}</span>
          </div>

          {reboundSuggestions.length > 0 && (
            <div className="pt-2 border-t border-red-900/40 space-y-2">
              <span className="text-xs font-semibold text-gray-300 flex items-center gap-1.5">
                <Sparkles className="w-3.5 h-3.5 text-cyan-400" /> Did you mean one of these?
              </span>
              <div className="flex flex-wrap gap-2">
                {reboundSuggestions.map((stock) => (
                  <button
                    key={stock.symbol}
                    onClick={() => handleSelectStock(stock.symbol, stock)}
                    className="px-3 py-1.5 bg-gray-900 hover:bg-gray-800 border border-cyan-500/40 hover:border-cyan-400 rounded-lg text-xs text-white transition-all flex items-center space-x-2 shadow-sm"
                  >
                    <span className="font-mono font-bold text-cyan-300">{stock.symbol}</span>
                    <span className="text-gray-400 truncate max-w-xs">{stock.name}</span>
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Blank Initial State Prompt */}
      {(!ticker || !chartData) && !loading && (
        <div className="bg-gray-900/50 border border-dashed border-gray-800 rounded-2xl p-16 text-center space-y-3 shadow-inner">
          <div className="w-14 h-14 rounded-full bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center mx-auto text-cyan-400 shadow-md">
            <BarChart2 className="w-7 h-7" />
          </div>
          <h3 className="text-lg font-bold text-white">No Stock Selected</h3>
          <p className="text-xs sm:text-sm text-gray-400 max-w-md mx-auto leading-relaxed">
            Search and select any Indian equity (NSE/BSE) or global stock in the search box above to load high-resolution TradingView candlesticks, EMA support bands, and quantitative swing trade triggers.
          </p>
        </div>
      )}

      {/* Main Chart Area when Data is Loaded */}
      {chartData && (
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-4">
          
          {/* TradingView Chart Container (3 cols) */}
          <div className="lg:col-span-3 bg-gray-900/80 border border-gray-800 rounded-xl p-3 space-y-2">
            
            <div className="relative min-h-[420px]">
              {loading && (
                <div className="absolute inset-0 bg-[#0B0F19]/60 backdrop-blur-sm flex items-center justify-center z-20 rounded-lg">
                  <div className="flex items-center space-x-2 text-cyan-400 text-sm font-medium">
                    <RefreshCw className="w-5 h-5 animate-spin" />
                    <span>Loading Candlesticks...</span>
                  </div>
                </div>
              )}
              
              {/* Candlestick & Volume Chart */}
              <div ref={chartContainerRef} className="w-full rounded-lg overflow-hidden" />
            </div>

            {/* RSI Sub-Chart */}
            <div className="border-t border-gray-800 pt-2 min-h-[140px]">
              <div className="flex items-center justify-between text-[11px] text-gray-400 px-2 pb-1 font-mono">
                <span className="font-semibold text-yellow-400">RSI(14) Momentum</span>
                <span>Levels: Overbought (70) | Mid (50) | Oversold (30)</span>
              </div>
              <div ref={rsiContainerRef} className="w-full rounded-lg overflow-hidden" />
            </div>

          </div>

          {/* Right Sidebar: Active Strategy Signal Analysis */}
          <div className="space-y-3">
            {setup ? (
              <div className="bg-gray-900/90 border border-cyan-500/30 rounded-xl p-4 space-y-4 shadow-lg shadow-cyan-500/5">
                
                <div className="flex items-center justify-between border-b border-gray-800 pb-3">
                  <div>
                    <span className="text-[10px] uppercase font-bold tracking-wider text-cyan-400">Triggered Setup</span>
                    <h3 className="text-sm font-bold text-white">{setup.strategy}</h3>
                  </div>
                  <div className="px-2.5 py-1 rounded-lg bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 text-xs font-bold font-mono">
                    Score {setup.score}/100
                  </div>
                </div>

                <div className="space-y-2.5 text-xs">
                  <div className="flex justify-between items-center py-1 border-b border-gray-800/60">
                    <span className="text-gray-400">Entry Price</span>
                    <span className="font-mono text-cyan-400 font-bold">₹{fmt(setup.close)}</span>
                  </div>
                  <div className="flex justify-between items-center py-1 border-b border-gray-800/60">
                    <span className="text-gray-400">Stop Loss</span>
                    <span className="font-mono text-red-400 font-bold">₹{fmt(setup.stop_loss)}</span>
                  </div>
                  <div className="flex justify-between items-center py-1 border-b border-gray-800/60">
                    <span className="text-gray-400">Target 1 (1:2 R:R)</span>
                    <span className="font-mono text-emerald-400 font-bold">₹{fmt(setup.target_1)}</span>
                  </div>
                  <div className="flex justify-between items-center py-1 border-b border-gray-800/60">
                    <span className="text-gray-400">Target 2 (1:3 R:R)</span>
                    <span className="font-mono text-emerald-300 font-bold">₹{fmt(setup.target_2)}</span>
                  </div>
                  <div className="flex justify-between items-center py-1 border-b border-gray-800/60">
                    <span className="text-gray-400">Risk per Share</span>
                    <span className="font-mono text-gray-200">₹{fmt(setup.risk_per_share)} ({setup.risk_pct}%)</span>
                  </div>
                  <div className="flex justify-between items-center py-1 border-b border-gray-800/60">
                    <span className="text-gray-400">Reward (Target 1)</span>
                    <span className="font-mono text-emerald-400">+{setup.reward_pct_t1}%</span>
                  </div>
                </div>

                <div className="p-2.5 rounded-lg bg-gray-950 text-[11px] text-gray-300 border border-gray-800">
                  <span className="font-semibold text-cyan-300 block mb-0.5">Execution Rule:</span>
                  {setup.setup_summary}
                </div>

                <button
                  onClick={() => onOpenRisk && onOpenRisk(setup)}
                  className="w-full py-2.5 rounded-lg bg-gradient-to-r from-amber-500 to-orange-600 hover:from-amber-400 hover:to-orange-500 text-gray-950 font-bold text-xs shadow-md transition-all flex items-center justify-center space-x-1.5"
                >
                  <ShieldAlert className="w-4 h-4" />
                  <span>Calculate Sizing & Capital</span>
                </button>

              </div>
            ) : (
              <div className="bg-gray-900/60 border border-gray-800 rounded-xl p-5 text-center space-y-2">
                <div className="w-9 h-9 rounded-full bg-gray-800 mx-auto flex items-center justify-center text-gray-400">
                  <Info className="w-5 h-5" />
                </div>
                <h4 className="text-xs font-semibold text-gray-200">No Active Setup On This Bar</h4>
                <p className="text-[11px] text-gray-400 leading-relaxed">
                  The latest bar for {ticker} does not currently meet all entry criteria for the selected strategy.
                </p>
              </div>
            )}

            {/* Quick Indicator Legend */}
            <div className="bg-gray-900/60 border border-gray-800 rounded-xl p-3.5 space-y-2 text-xs">
              <h4 className="text-[11px] font-bold text-gray-400 uppercase tracking-wider">Indicator Colors</h4>
              <div className="space-y-1.5 text-[11px]">
                <div className="flex items-center space-x-2">
                  <span className="w-2.5 h-2.5 rounded-full bg-cyan-400"></span>
                  <span className="text-gray-300">20 EMA (Primary Dynamic Support)</span>
                </div>
                <div className="flex items-center space-x-2">
                  <span className="w-2.5 h-2.5 rounded-full bg-amber-400"></span>
                  <span className="text-gray-300">50 EMA (Intermediate Trend)</span>
                </div>
                <div className="flex items-center space-x-2">
                  <span className="w-2.5 h-2.5 rounded-full bg-purple-400"></span>
                  <span className="text-gray-300">200 EMA (Macro Institutional Line)</span>
                </div>
              </div>
            </div>

          </div>

        </div>
      )}

    </div>
  );
}
