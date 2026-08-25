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
  Sparkles
} from 'lucide-react';
import { fetchChartData, searchStocks } from '../services/api';
import StockSearchInput from './StockSearchInput';

const fmt = (v, d = 2) => {
  if (typeof v === 'number' && !isNaN(v)) return v.toFixed(d);
  if (typeof v === 'string' && !isNaN(Number(v))) return Number(v).toFixed(d);
  return '—';
};

export default function ChartStudio({ initialTicker = "RELIANCE.NS", onOpenRisk }) {
  const chartContainerRef = useRef(null);
  const rsiContainerRef = useRef(null);
  const chartRef = useRef(null);
  const rsiChartRef = useRef(null);

  const [ticker, setTicker] = useState(initialTicker);
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
    if (initialTicker) {
      setTicker(initialTicker);
    }
  }, [initialTicker]);

  useEffect(() => {
    loadData(ticker, period, strategyId);
  }, [ticker, period, strategyId]);

  const loadData = async (sym, prd, strat) => {
    setLoading(true);
    setErrorMsg(null);
    setReboundSuggestions([]);

    try {
      let cleanSym = sym.trim().toUpperCase();
      const data = await fetchChartData(cleanSym, prd, strat);
      setChartData(data);
    } catch (err) {
      setErrorMsg(err.message || `No price data available for ticker '${sym}'`);
      // Fetch rebound suggestions for typo or natural name
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

    // Clear previous charts safely
    if (chartRef.current) {
      try { chartRef.current.remove(); } catch (e) {}
      chartRef.current = null;
    }
    if (rsiChartRef.current) {
      try { rsiChartRef.current.remove(); } catch (e) {}
      rsiChartRef.current = null;
    }

    const container = chartContainerRef.current;
    const initialWidth = container.clientWidth || 700;

    let chart = null;
    let rsiChart = null;

    try {
      chart = createChart(container, {
        width: initialWidth,
        height: 420,
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
        crosshair: {
          mode: 1,
          vertLine: { color: '#06b6d4', width: 1, style: 3 },
          horzLine: { color: '#06b6d4', width: 1, style: 3 }
        },
        timeScale: {
          borderColor: '#374151',
          timeVisible: true
        },
        rightPriceScale: {
          borderColor: '#374151',
          scaleMargins: { top: 0.1, bottom: 0.2 }
        }
      });
      chartRef.current = chart;

      // Candlestick series
      const candleSeries = chart.addCandlestickSeries({
        upColor: '#10B981',
        downColor: '#EF4444',
        borderUpColor: '#10B981',
        borderDownColor: '#EF4444',
        wickUpColor: '#10B981',
        wickDownColor: '#EF4444'
      });
      candleSeries.setData(chartData.candles);

      // Volume series
      if (chartData.volume && chartData.volume.length > 0) {
        const volumeSeries = chart.addHistogramSeries({
          priceFormat: { type: 'volume' },
          priceScaleId: '',
          scaleMargins: { top: 0.8, bottom: 0 }
        });
        volumeSeries.setData(chartData.volume);
      }

      // EMAs
      if (showEMA20 && chartData.ema20 && chartData.ema20.length > 0) {
        const ema20 = chart.addLineSeries({ color: '#06B6D4', lineWidth: 1.5, title: '20 EMA' });
        ema20.setData(chartData.ema20);
      }
      if (showEMA50 && chartData.ema50 && chartData.ema50.length > 0) {
        const ema50 = chart.addLineSeries({ color: '#F59E0B', lineWidth: 1.5, title: '50 EMA' });
        ema50.setData(chartData.ema50);
      }
      if (showEMA200 && chartData.ema200 && chartData.ema200.length > 0) {
        const ema200 = chart.addLineSeries({ color: '#A855F7', lineWidth: 1.5, title: '200 EMA' });
        ema200.setData(chartData.ema200);
      }

      // Trade Setup Price Lines Overlay
      if (showSetupLines && chartData.active_setup) {
        const s = chartData.active_setup;
        if (s.close) {
          candleSeries.createPriceLine({
            price: Number(s.close),
            color: '#06b6d4',
            lineWidth: 1.5,
            lineStyle: 2,
            axisLabelVisible: true,
            title: 'ENTRY'
          });
        }
        if (s.stop_loss) {
          candleSeries.createPriceLine({
            price: Number(s.stop_loss),
            color: '#EF4444',
            lineWidth: 2,
            lineStyle: 0,
            axisLabelVisible: true,
            title: 'STOP LOSS'
          });
        }
        if (s.target_1) {
          candleSeries.createPriceLine({
            price: Number(s.target_1),
            color: '#10B981',
            lineWidth: 1.5,
            lineStyle: 0,
            axisLabelVisible: true,
            title: 'TARGET 1 (2R)'
          });
        }
        if (s.target_2) {
          candleSeries.createPriceLine({
            price: Number(s.target_2),
            color: '#34D399',
            lineWidth: 1.5,
            lineStyle: 2,
            axisLabelVisible: true,
            title: 'TARGET 2 (3R)'
          });
        }
      }

      // Sub-chart: RSI Chart
      if (rsiContainerRef.current && chartData.rsi && chartData.rsi.length > 0) {
        const rsiContainer = rsiContainerRef.current;
        rsiChart = createChart(rsiContainer, {
          width: rsiContainer.clientWidth || initialWidth,
          height: 140,
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
          color: '#F59E0B',
          lineWidth: 1.5,
          title: 'RSI(14)'
        });
        rsiSeries.setData(chartData.rsi);

        rsiSeries.createPriceLine({ price: 70, color: '#EF4444', lineStyle: 2, axisLabelVisible: false });
        rsiSeries.createPriceLine({ price: 50, color: '#6B7280', lineStyle: 3, axisLabelVisible: false });
        rsiSeries.createPriceLine({ price: 30, color: '#10B981', lineStyle: 2, axisLabelVisible: false });

        chart.timeScale().subscribeVisibleTimeRangeChange(range => {
          if (range && rsiChartRef.current) {
            try { rsiChartRef.current.timeScale().setVisibleRange(range); } catch (e) {}
          }
        });
      }
    } catch (chartErr) {
      console.error("TradingView Chart render exception:", chartErr);
    }

    const handleResize = () => {
      if (chartRef.current && container) {
        chartRef.current.applyOptions({ width: container.clientWidth || 700 });
      }
      if (rsiChartRef.current && rsiContainerRef.current) {
        rsiChartRef.current.applyOptions({ width: rsiContainerRef.current.clientWidth || 700 });
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

  const setup = chartData?.active_setup;

  return (
    <div className="space-y-4">
      
      {/* Top Header & Autocomplete Search Controls */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 bg-gray-900/90 p-4 rounded-xl border border-gray-800">
        
        {/* Autocomplete Search & Active Stock Info */}
        <div className="flex flex-wrap items-center gap-3 flex-1">
          <StockSearchInput
            value={ticker}
            onSelectStock={handleSelectStock}
            placeholder="Search stock or company (e.g. CONFIPET, Tata Motors, Reliance)..."
            className="w-full sm:w-80"
          />

          {chartData && (
            <div className="flex items-center space-x-3 pl-1">
              <span className="text-lg font-bold text-white font-mono">{chartData.ticker}</span>
              <div className="flex items-center space-x-1.5">
                <span className="text-base font-bold text-gray-100 font-mono">₹{fmt(chartData.latest_close)}</span>
                <span className={`text-xs font-semibold font-mono flex items-center ${
                  chartData.change_pct >= 0 ? 'text-emerald-400' : 'text-red-400'
                }`}>
                  {chartData.change_pct >= 0 ? <ArrowUpRight className="w-3.5 h-3.5" /> : <ArrowDownRight className="w-3.5 h-3.5" />}
                  {chartData.change_pct >= 0 ? `+${chartData.change_pct}%` : `${chartData.change_pct}%`}
                </span>
              </div>
            </div>
          )}
        </div>

        {/* Timeframe & Overlay Switches */}
        <div className="flex flex-wrap items-center gap-2 text-xs">
          
          {/* Period selector */}
          <div className="flex bg-gray-950 p-1 rounded-lg border border-gray-800">
            {['6mo', '1y', '2y', '5y'].map((p) => (
              <button
                key={p}
                onClick={() => setPeriod(p)}
                className={`px-2.5 py-1 rounded font-medium uppercase ${
                  period === p ? 'bg-cyan-500 text-gray-950 font-bold' : 'text-gray-400 hover:text-gray-200'
                }`}
              >
                {p}
              </button>
            ))}
          </div>

          {/* Indicator toggles */}
          <div className="flex items-center space-x-1 bg-gray-950 p-1 rounded-lg border border-gray-800 text-gray-300">
            <button
              onClick={() => setShowEMA20(!showEMA20)}
              className={`px-2 py-1 rounded font-mono text-[11px] ${showEMA20 ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40' : 'text-gray-500'}`}
            >
              20 EMA
            </button>
            <button
              onClick={() => setShowEMA50(!showEMA50)}
              className={`px-2 py-1 rounded font-mono text-[11px] ${showEMA50 ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40' : 'text-gray-500'}`}
            >
              50 EMA
            </button>
            <button
              onClick={() => setShowEMA200(!showEMA200)}
              className={`px-2 py-1 rounded font-mono text-[11px] ${showEMA200 ? 'bg-purple-500/20 text-purple-300 border border-purple-500/40' : 'text-gray-500'}`}
            >
              200 EMA
            </button>
          </div>

          {setup && (
            <button
              onClick={() => setShowSetupLines(!showSetupLines)}
              className={`px-2.5 py-1.5 rounded-lg border font-medium text-xs flex items-center space-x-1 ${
                showSetupLines ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30' : 'bg-gray-950 text-gray-500 border-gray-800'
              }`}
            >
              <Eye className="w-3.5 h-3.5" />
              <span>Setup Levels</span>
            </button>
          )}

          <button
            onClick={() => loadData(ticker, period, strategyId)}
            disabled={loading}
            className="p-1.5 bg-gray-800 hover:bg-gray-700 text-gray-300 rounded-lg border border-gray-700"
            title="Refresh Data"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin text-cyan-400' : ''}`} />
          </button>
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

      {/* Main Chart Area with Active Trade Setup Overlay Card */}
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
                onClick={() => onOpenRisk(setup)}
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
                The latest bar for {ticker} does not currently meet all entry criteria for the <strong className="text-cyan-400 font-medium">Trend Pullback</strong> model.
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

    </div>
  );
}
