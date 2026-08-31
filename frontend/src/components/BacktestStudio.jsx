import React, { useState, useEffect, useRef } from 'react';
import { createChart } from 'lightweight-charts';
import { 
  Play, 
  RefreshCw, 
  TrendingUp, 
  TrendingDown, 
  Award, 
  Percent, 
  ShieldCheck, 
  Activity, 
  Download, 
  Sliders,
  DollarSign,
  Clock,
  CheckCircle2,
  XCircle,
  BarChart3,
  AlertCircle,
  FileDown
} from 'lucide-react';
import { runBacktest, fetchStrategies, fetchUniverses } from '../services/api';
import StockSearchInput from './StockSearchInput';

export default function BacktestStudio({ initialTicker = "", initialStrategy = "trend_pullback" }) {
  const chartContainerRef = useRef(null);
  const chartRef = useRef(null);

  const [ticker, setTicker] = useState(initialTicker || "");
  const [strategyId, setStrategyId] = useState(initialStrategy || "trend_pullback");
  const [period, setPeriod] = useState("2y");
  const [initialCapital, setInitialCapital] = useState(500000);
  const [riskPct, setRiskPct] = useState(1.0);
  const [slippagePct, setSlippagePct] = useState(0.08);
  const [enableTaxes, setEnableTaxes] = useState(true);

  const [strategies, setStrategies] = useState([]);
  const [universes, setUniverses] = useState([]);
  const [loading, setLoading] = useState(false);
  const [metrics, setMetrics] = useState(null);
  const [errorMsg, setErrorMsg] = useState(null);
  const [tradeFilter, setTradeFilter] = useState('ALL'); // ALL, WIN, LOSS
  const [hoveredPoint, setHoveredPoint] = useState(null);

  useEffect(() => {
    fetchStrategies().then(setStrategies).catch(console.error);
    fetchUniverses().then(setUniverses).catch(console.error);
  }, []);

  useEffect(() => {
    if (initialTicker) setTicker(initialTicker);
    if (initialStrategy) setStrategyId(initialStrategy);
  }, [initialTicker, initialStrategy]);

  const handleRunBacktest = async (e) => {
    if (e) e.preventDefault();
    if (!ticker || !ticker.trim()) {
      setErrorMsg("Please enter or select a stock symbol to backtest.");
      return;
    }
    setLoading(true);
    setErrorMsg(null);
    setHoveredPoint(null);
    try {
      const res = await runBacktest({
        ticker: ticker.trim(),
        strategy_id: strategyId,
        period: period,
        initial_capital: Number(initialCapital),
        risk_pct: Number(riskPct),
        slippage_pct: Number(slippagePct),
        enable_indian_taxes: enableTaxes
      });
      setMetrics(res);
    } catch (err) {
      setErrorMsg(err.message || "Failed to execute backtest");
    } finally {
      setLoading(false);
    }
  };

  // Render Equity Curve via Lightweight Charts with strict deduplication & trade markers
  useEffect(() => {
    if (!chartContainerRef.current || !metrics || !metrics.equity_curve || metrics.equity_curve.length === 0) return;

    if (chartRef.current) {
      try { chartRef.current.remove(); } catch (e) {}
      chartRef.current = null;
    }

    const container = chartContainerRef.current;
    const initialWidth = container.clientWidth || 700;
    const isProfitable = metrics.net_profit >= 0;

    let chart = null;
    try {
      chart = createChart(container, {
        width: initialWidth,
        height: 290,
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
          timeVisible: true
        },
        rightPriceScale: {
          borderColor: '#374151',
          scaleMargins: { top: 0.1, bottom: 0.1 }
        },
        localization: {
          priceFormatter: (price) => '₹' + Math.round(price).toLocaleString('en-IN')
        }
      });
      chartRef.current = chart;

      // Deduplicate by date and ensure ascending sort
      const dateMap = new Map();
      metrics.equity_curve
        .filter(p => p.date && p.date !== 'Start' && p.date.includes('-'))
        .forEach(p => {
          const cleanDate = p.date.split(' ')[0].split('T')[0];
          dateMap.set(cleanDate, p.equity);
        });

      const equityData = Array.from(dateMap.entries())
        .map(([time, value]) => ({ time, value }))
        .sort((a, b) => (a.time > b.time ? 1 : -1));

      if (equityData.length > 0) {
        const areaSeries = chart.addAreaSeries({
          topColor: isProfitable ? 'rgba(16, 185, 129, 0.35)' : 'rgba(244, 63, 94, 0.35)',
          bottomColor: isProfitable ? 'rgba(16, 185, 129, 0.0)' : 'rgba(244, 63, 94, 0.0)',
          lineColor: isProfitable ? '#10B981' : '#F43F5E',
          lineWidth: 2,
          title: 'Portfolio Equity (₹)'
        });
        areaSeries.setData(equityData);

        // Initial capital baseline
        areaSeries.createPriceLine({
          price: metrics.initial_capital,
          color: '#6B7280',
          lineWidth: 1,
          lineStyle: 2,
          title: 'INITIAL CAPITAL (₹' + metrics.initial_capital.toLocaleString('en-IN') + ')'
        });

        // Add trade entry and exit markers on equity curve
        if (metrics.trades && metrics.trades.length > 0) {
          const markers = [];
          metrics.trades.forEach(t => {
            if (t.entry_date) {
              const d = t.entry_date.split(' ')[0].split('T')[0];
              markers.push({
                time: d,
                position: 'belowBar',
                color: '#38BDF8',
                shape: 'arrowUp',
                text: `#${t.trade_no} Buy`
              });
            }
            if (t.exit_date) {
              const d = t.exit_date.split(' ')[0].split('T')[0];
              markers.push({
                time: d,
                position: 'aboveBar',
                color: t.is_win ? '#34D399' : '#F87171',
                shape: t.is_win ? 'circle' : 'arrowDown',
                text: t.is_win ? `+₹${Math.round(t.net_pnl)}` : `-₹${Math.abs(Math.round(t.net_pnl))}`
              });
            }
          });

          markers.sort((a, b) => (a.time > b.time ? 1 : -1));
          // Deduplicate markers on same timestamp and shape
          const uniqueMarkers = [];
          const seen = new Set();
          markers.forEach(m => {
            const k = `${m.time}-${m.shape}`;
            if (!seen.has(k)) {
              seen.add(k);
              uniqueMarkers.push(m);
            }
          });

          if (uniqueMarkers.length > 0) {
            areaSeries.setMarkers(uniqueMarkers);
          }
        }

        // Crosshair hover listener for inspection
        chart.subscribeCrosshairMove((param) => {
          if (!param || !param.time || param.point === undefined || !param.seriesData) {
            setHoveredPoint(null);
            return;
          }
          const price = param.seriesData.get(areaSeries);
          if (price !== undefined) {
            const timeStr = typeof param.time === 'string' 
              ? param.time 
              : `${param.time.year}-${String(param.time.month).padStart(2, '0')}-${String(param.time.day).padStart(2, '0')}`;
            const pointData = metrics.equity_curve.find(p => (p.date || '').startsWith(timeStr));
            setHoveredPoint({
              date: timeStr,
              equity: price,
              inTrade: pointData ? pointData.in_trade : false,
              pnl: price - metrics.initial_capital,
              pnlPct: ((price - metrics.initial_capital) / metrics.initial_capital) * 100.0
            });
          }
        });
      }
    } catch (e) {
      console.error("Backtest chart render error:", e);
    }

    const handleResize = () => {
      if (chartRef.current && container) {
        chartRef.current.applyOptions({ width: container.clientWidth || 700 });
      }
    };
    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      if (chartRef.current) {
        try { chartRef.current.remove(); } catch (e) {}
        chartRef.current = null;
      }
    };
  }, [metrics]);

  const exportCSV = () => {
    if (!metrics || !metrics.trades || metrics.trades.length === 0) return;
    const headers = ["Trade #", "Ticker", "Entry Date", "Exit Date", "Entry Price", "Exit Price", "Shares", "Capital Deployed", "Gross PnL", "Net PnL", "Return %", "Exit Reason", "Days Held"];
    const rows = metrics.trades.map(t => [
      t.trade_no,
      t.ticker,
      t.entry_date,
      t.exit_date,
      t.entry_price,
      t.exit_price,
      t.shares,
      t.capital_deployed,
      t.gross_pnl,
      t.net_pnl,
      t.return_pct,
      `"${t.exit_reason}"`,
      t.bars_held
    ]);

    const csvContent = "data:text/csv;charset=utf-8," + [headers.join(","), ...rows.map(e => e.join(","))].join("\n");
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `Backtest_${metrics.ticker}_${metrics.strategy_id}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const [pdfLoading, setPdfLoading] = useState(false);

  const handleExportPdf = async () => {
    if (!metrics) return;
    setPdfLoading(true);
    try {
      const payload = {
        ticker: metrics.ticker?.startsWith('Basket') ? null : metrics.ticker,
        universe: metrics.ticker?.startsWith('Basket') ? metrics.ticker.replace('Basket: ', '') : null,
        strategy_id: metrics.strategy_id || strategyId,
        period: period,
        initial_capital: Number(initialCapital),
        risk_pct: Number(riskPct),
        slippage_pct: Number(slippagePct),
        enable_indian_taxes: enableTaxes
      };
      const res = await fetch('/api/backtest/export/pdf', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      if (!res.ok) throw new Error("Failed to generate PDF Factsheet");
      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      const cleanTarget = (metrics.ticker || "Backtest").replace('.NS', '').replace(':', '_').replace(' ', '_');
      a.download = `SwingTradeDesk_Factsheet_${cleanTarget}_${metrics.strategy_id}.pdf`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      alert("Error downloading Backtest PDF Factsheet: " + err.message);
    } finally {
      setPdfLoading(false);
    }
  };

  const filteredTrades = metrics && metrics.trades ? metrics.trades.filter(t => {
    if (tradeFilter === 'WIN') return t.is_win;
    if (tradeFilter === 'LOSS') return !t.is_win;
    return true;
  }) : [];

  return (
    <div className="space-y-6">
      
      {/* Control Panel Card */}
      <div className="bg-gray-900/80 border border-gray-800 rounded-2xl p-5 shadow-xl space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 border-b border-gray-800 pb-4">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center text-cyan-400">
              <TrendingUp className="w-5 h-5" />
            </div>
            <div>
              <h1 className="text-lg sm:text-xl font-bold text-white tracking-tight">Institutional Backtest Studio</h1>
              <p className="text-xs text-gray-400">Realistic bar-by-bar simulation with STT, GST, Brokerage, and Slippage models</p>
            </div>
          </div>

          <button
            onClick={handleRunBacktest}
            disabled={loading}
            className={`flex items-center space-x-2 px-6 py-2.5 rounded-xl text-sm font-semibold shadow-lg transition-all ${
              loading
                ? 'bg-cyan-700 text-gray-200 cursor-not-allowed opacity-80'
                : 'bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white shadow-cyan-500/25 active:scale-95'
            }`}
          >
            {loading ? <RefreshCw className="w-4 h-4 animate-spin text-white" /> : <Play className="w-4 h-4 fill-current" />}
            <span>{loading ? "Simulating..." : "Run Simulation"}</span>
          </button>
        </div>

        {/* Input Form */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-6 gap-3 pt-2">
          
          <div className="lg:col-span-2">
            <label className="text-xs font-medium text-gray-400 block mb-1">Target Symbol</label>
            <StockSearchInput
              value={ticker}
              onSelectStock={(sym) => setTicker(sym)}
              placeholder="Search symbol or company name..."
              className="w-full"
            />
          </div>

          <div className="lg:col-span-2">
            <label className="text-xs font-medium text-gray-400 block mb-1">Strategy</label>
            <select
              value={strategyId}
              onChange={(e) => setStrategyId(e.target.value)}
              className="w-full bg-gray-950 border border-gray-700 rounded-lg px-3 py-2 text-sm text-gray-200 focus:outline-none focus:border-cyan-500 font-mono"
            >
              {strategies.map((s) => (
                <option key={s.id} value={s.id}>{s.name}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="text-xs font-medium text-gray-400 block mb-1">Horizon</label>
            <select
              value={period}
              onChange={(e) => setPeriod(e.target.value)}
              className="w-full bg-gray-950 border border-gray-700 rounded-lg px-3 py-2 text-sm text-gray-200 focus:outline-none focus:border-cyan-500"
            >
              <option value="1y">1 Year</option>
              <option value="2y">2 Years</option>
              <option value="5y">5 Years</option>
              <option value="max">Max Data</option>
            </select>
          </div>

          <div>
            <label className="text-xs font-medium text-gray-400 block mb-1">Capital (₹)</label>
            <input
              type="number"
              value={initialCapital}
              onChange={(e) => setInitialCapital(e.target.value)}
              className="w-full bg-gray-950 border border-gray-700 rounded-lg px-3 py-2 text-sm text-gray-200 focus:outline-none focus:border-cyan-500 font-mono"
            />
          </div>

          <div>
            <label className="text-xs font-medium text-gray-400 block mb-1">Risk / Trade (%)</label>
            <input
              type="number"
              step="0.1"
              value={riskPct}
              onChange={(e) => setRiskPct(e.target.value)}
              className="w-full bg-gray-950 border border-gray-700 rounded-lg px-3 py-2 text-sm text-gray-200 focus:outline-none focus:border-cyan-500 font-mono"
            />
          </div>

          <div>
            <label className="text-xs font-medium text-gray-400 block mb-1">Slippage (%)</label>
            <input
              type="number"
              step="0.01"
              value={slippagePct}
              onChange={(e) => setSlippagePct(e.target.value)}
              className="w-full bg-gray-950 border border-gray-700 rounded-lg px-3 py-2 text-sm text-gray-200 focus:outline-none focus:border-cyan-500 font-mono"
            />
          </div>

          <div className="sm:col-span-2 lg:col-span-2 flex items-center space-x-2 pt-6">
            <input
              type="checkbox"
              id="taxToggle"
              checked={enableTaxes}
              onChange={(e) => setEnableTaxes(e.target.checked)}
              className="w-4 h-4 rounded text-cyan-500 bg-gray-950 border-gray-700 focus:ring-0 cursor-pointer"
            />
            <label htmlFor="taxToggle" className="text-xs text-gray-300 font-medium cursor-pointer">
              Enable Indian Taxes (STT, GST, Stamp Duty, Brokerage)
            </label>
          </div>
        </div>

        {errorMsg && (
          <div className="p-3 bg-rose-500/10 border border-rose-500/30 rounded-xl text-rose-400 text-xs flex items-center space-x-2">
            <AlertCircle className="w-4 h-4 flex-shrink-0" />
            <span>{errorMsg}</span>
          </div>
        )}
      </div>

      {/* Blank Initial State Prompt */}
      {!metrics && !loading && (
        <div className="bg-gray-900/50 border border-dashed border-gray-800 rounded-2xl p-16 text-center space-y-3 shadow-inner">
          <div className="w-14 h-14 rounded-full bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center mx-auto text-cyan-400 shadow-md">
            <TrendingUp className="w-7 h-7" />
          </div>
          <h3 className="text-lg font-bold text-white">No Simulation Loaded</h3>
          <p className="text-xs sm:text-sm text-gray-400 max-w-md mx-auto leading-relaxed">
            Search and select a target equity symbol above, choose your quantitative strategy, time horizon, and capital, then click <strong className="text-cyan-400 font-medium">Run Simulation</strong> to simulate bar-by-bar trade performance with realistic Indian market taxes and slippage.
          </p>
        </div>
      )}

      {/* Results View */}
      {metrics && (
        <div className="space-y-6">
          
          {/* Executive Results Header with One-Click PDF Export */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-gradient-to-r from-gray-900 via-gray-900/90 to-gray-900 border border-gray-800 p-4 rounded-2xl shadow-lg">
            <div>
              <div className="flex items-center space-x-2">
                <span className="text-[11px] uppercase font-mono text-cyan-400 font-bold px-2 py-0.5 rounded bg-cyan-500/10 border border-cyan-500/20">
                  {metrics.ticker}
                </span>
                <span className="text-xs text-gray-400 font-mono">Horizon: {period.toUpperCase()}</span>
              </div>
              <h2 className="text-base sm:text-lg font-bold text-white mt-1">
                {strategies.find(s => s.id === metrics.strategy_id)?.name || metrics.strategy_id}
              </h2>
            </div>

            <div className="flex items-center space-x-2 flex-wrap gap-y-2">
              <button
                onClick={handleExportPdf}
                disabled={pdfLoading}
                className="px-4 py-2 bg-gradient-to-r from-red-600 via-rose-600 to-red-700 hover:from-red-500 hover:to-rose-500 text-white font-bold rounded-xl text-xs flex items-center space-x-2 shadow-lg shadow-red-900/30 transition-all border border-red-500/40"
                title="Download 2-Page Institutional Strategy Factsheet (PDF)"
              >
                {pdfLoading ? (
                  <RefreshCw className="w-4 h-4 animate-spin" />
                ) : (
                  <FileDown className="w-4 h-4" />
                )}
                <span>{pdfLoading ? "Generating..." : "📄 Export Factsheet (PDF)"}</span>
              </button>

              <button
                onClick={exportCSV}
                className="px-3.5 py-2 rounded-xl bg-gray-800 hover:bg-gray-700 text-gray-200 border border-gray-700 text-xs font-mono flex items-center space-x-1.5 transition-colors"
              >
                <Download className="w-3.5 h-3.5 text-cyan-400" />
                <span>Export CSV</span>
              </button>
            </div>
          </div>

          {/* Top Scorecard KPIs */}
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
            <div className="bg-gray-900/80 border border-gray-800 rounded-xl p-3.5">
              <div className="text-[11px] text-gray-400 uppercase font-mono">Net Profit</div>
              <div className={`text-lg font-bold font-mono mt-0.5 ${metrics.net_profit >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                {metrics.net_profit >= 0 ? '+' : ''}₹{metrics.net_profit.toLocaleString()}
              </div>
              <div className={`text-xs font-mono ${metrics.net_profit_pct >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                {metrics.net_profit_pct >= 0 ? '+' : ''}{metrics.net_profit_pct}% Return
              </div>
            </div>

            <div className="bg-gray-900/80 border border-gray-800 rounded-xl p-3.5">
              <div className="text-[11px] text-gray-400 uppercase font-mono">Win Rate %</div>
              <div className="text-lg font-bold text-cyan-400 font-mono mt-0.5">
                {metrics.win_rate}%
              </div>
              <div className="text-xs text-gray-400 font-mono">
                {metrics.winning_trades}W / {metrics.losing_trades}L ({metrics.total_trades} total)
              </div>
            </div>

            <div className="bg-gray-900/80 border border-gray-800 rounded-xl p-3.5">
              <div className="text-[11px] text-gray-400 uppercase font-mono">Profit Factor</div>
              <div className="text-lg font-bold text-indigo-400 font-mono mt-0.5">
                {metrics.profit_factor}
              </div>
              <div className="text-xs text-gray-400 font-mono">
                Payoff: {metrics.payoff_ratio}x
              </div>
            </div>

            <div className="bg-gray-900/80 border border-gray-800 rounded-xl p-3.5">
              <div className="text-[11px] text-gray-400 uppercase font-mono">Max Drawdown</div>
              <div className="text-lg font-bold text-rose-400 font-mono mt-0.5">
                -{metrics.max_drawdown_pct}%
              </div>
              <div className="text-xs text-gray-400 font-mono">
                -₹{metrics.max_drawdown_val?.toLocaleString()}
              </div>
            </div>

            <div className="bg-gray-900/80 border border-gray-800 rounded-xl p-3.5">
              <div className="text-[11px] text-gray-400 uppercase font-mono">Sharpe Ratio</div>
              <div className="text-lg font-bold text-amber-400 font-mono mt-0.5">
                {metrics.sharpe_ratio}
              </div>
              <div className="text-xs text-gray-400 font-mono">
                Sortino: {metrics.sortino_ratio}
              </div>
            </div>

            <div className="bg-gray-900/80 border border-gray-800 rounded-xl p-3.5">
              <div className="text-[11px] text-gray-400 uppercase font-mono">Avg Holding</div>
              <div className="text-lg font-bold text-purple-400 font-mono mt-0.5">
                {metrics.avg_holding_days} Days
              </div>
              <div className="text-xs text-gray-400 font-mono">
                CAGR: {metrics.cagr_pct}%
              </div>
            </div>
          </div>

          {/* Equity Curve Chart */}
          <div className="bg-gray-900/80 border border-gray-800 rounded-2xl p-5 shadow-xl space-y-3">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-gray-800/80 pb-3">
              <div className="flex items-center space-x-2">
                <BarChart3 className="w-4 h-4 text-cyan-400" />
                <h3 className="text-sm font-bold text-gray-200 uppercase tracking-wider font-mono">
                  Portfolio Equity Curve ({metrics.ticker})
                </h3>
              </div>

              {/* Live Hover Inspection Bar */}
              {hoveredPoint ? (
                <div className="flex items-center space-x-3 bg-gray-950 px-3 py-1 rounded-lg border border-cyan-500/40 text-xs font-mono">
                  <span className="text-gray-400">{hoveredPoint.date}</span>
                  <span className="text-gray-600">|</span>
                  <span className="text-white font-bold">₹{Math.round(hoveredPoint.equity).toLocaleString('en-IN')}</span>
                  <span className="text-gray-600">|</span>
                  <span className={`font-bold ${hoveredPoint.pnl >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                    {hoveredPoint.pnl >= 0 ? '+' : ''}₹{Math.round(hoveredPoint.pnl).toLocaleString('en-IN')} ({hoveredPoint.pnlPct >= 0 ? '+' : ''}{hoveredPoint.pnlPct.toFixed(2)}%)
                  </span>
                  <span className="text-gray-600">|</span>
                  <span className={hoveredPoint.inTrade ? 'text-cyan-400 font-semibold' : 'text-gray-500'}>
                    {hoveredPoint.inTrade ? '⚡ In Position' : 'Cash'}
                  </span>
                </div>
              ) : (
                <div className="text-xs text-gray-400 font-mono">
                  Initial: ₹{metrics.initial_capital.toLocaleString('en-IN')} ➔ Final: ₹{metrics.final_capital.toLocaleString('en-IN')}
                </div>
              )}
            </div>

            {/* Visual Markers Legend */}
            <div className="flex items-center space-x-4 text-[11px] font-mono text-gray-400 px-1">
              <span className="flex items-center gap-1">
                <span className="w-2 h-2 rounded-full bg-cyan-400"></span>
                <span>🔵 Buy Entry</span>
              </span>
              <span className="flex items-center gap-1">
                <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
                <span>🟢 Win Exit</span>
              </span>
              <span className="flex items-center gap-1">
                <span className="w-2 h-2 rounded-full bg-rose-400"></span>
                <span>🔴 Stop Loss Exit</span>
              </span>
            </div>

            <div ref={chartContainerRef} className="w-full rounded-xl overflow-hidden" />
          </div>

          {/* Trade Execution Logs Table */}
          <div className="bg-gray-900/80 border border-gray-800 rounded-2xl p-5 shadow-xl space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
              <div className="flex items-center space-x-3">
                <h3 className="text-sm font-bold text-gray-200 uppercase tracking-wider font-mono">
                  Trade Execution Log ({filteredTrades.length} Trades)
                </h3>
                
                {/* Filter Tabs */}
                <div className="flex space-x-1 bg-gray-950 p-1 rounded-lg border border-gray-800 text-xs">
                  <button
                    onClick={() => setTradeFilter('ALL')}
                    className={`px-2.5 py-1 rounded-md transition-colors ${tradeFilter === 'ALL' ? 'bg-gray-800 text-white font-semibold' : 'text-gray-400 hover:text-gray-200'}`}
                  >
                    All ({metrics.total_trades})
                  </button>
                  <button
                    onClick={() => setTradeFilter('WIN')}
                    className={`px-2.5 py-1 rounded-md transition-colors ${tradeFilter === 'WIN' ? 'bg-emerald-500/20 text-emerald-300 font-semibold' : 'text-gray-400 hover:text-gray-200'}`}
                  >
                    Winners ({metrics.winning_trades})
                  </button>
                  <button
                    onClick={() => setTradeFilter('LOSS')}
                    className={`px-2.5 py-1 rounded-md transition-colors ${tradeFilter === 'LOSS' ? 'bg-rose-500/20 text-rose-300 font-semibold' : 'text-gray-400 hover:text-gray-200'}`}
                  >
                    Losers ({metrics.losing_trades})
                  </button>
                </div>
              </div>

              <div className="flex items-center space-x-2">
                <button
                  onClick={handleExportPdf}
                  disabled={pdfLoading}
                  className="px-3.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 hover:border-slate-500 text-xs font-mono flex items-center space-x-1.5 transition-colors shadow-sm"
                  title="Download 2-Page Institutional Strategy Factsheet (PDF)"
                >
                  {pdfLoading ? (
                    <RefreshCw className="w-3.5 h-3.5 animate-spin text-cyan-400" />
                  ) : (
                    <FileDown className="w-3.5 h-3.5 text-cyan-400" />
                  )}
                  <span>{pdfLoading ? "Generating..." : "Export Factsheet (PDF)"}</span>
                </button>

                <button
                  onClick={exportCSV}
                  className="px-3.5 py-1.5 rounded-lg bg-gray-800 hover:bg-gray-700 text-gray-200 border border-gray-700 text-xs font-mono flex items-center space-x-1.5 transition-colors"
                >
                  <Download className="w-3.5 h-3.5 text-cyan-400" />
                  <span>Export CSV</span>
                </button>
              </div>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-gray-950 text-gray-400 uppercase font-mono border-b border-gray-800">
                  <tr>
                    <th className="py-2.5 px-3">#</th>
                    <th className="py-2.5 px-3">Symbol</th>
                    <th className="py-2.5 px-3">Entry Date</th>
                    <th className="py-2.5 px-3">Exit Date</th>
                    <th className="py-2.5 px-3 text-right">Entry Price</th>
                    <th className="py-2.5 px-3 text-right">Exit Price</th>
                    <th className="py-2.5 px-3 text-right">Shares</th>
                    <th className="py-2.5 px-3 text-right">Net PnL (₹)</th>
                    <th className="py-2.5 px-3 text-right">Return %</th>
                    <th className="py-2.5 px-3">Exit Reason</th>
                    <th className="py-2.5 px-3 text-center">Held</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-800 text-gray-200 font-mono">
                  {filteredTrades.map((t) => (
                    <tr key={t.trade_no} className="hover:bg-gray-800/40 transition-colors">
                      <td className="py-2.5 px-3 text-gray-400">#{t.trade_no}</td>
                      <td className="py-2.5 px-3 font-semibold text-white">{t.ticker}</td>
                      <td className="py-2.5 px-3 text-gray-300">{t.entry_date}</td>
                      <td className="py-2.5 px-3 text-gray-300">{t.exit_date}</td>
                      <td className="py-2.5 px-3 text-right">₹{t.entry_price}</td>
                      <td className="py-2.5 px-3 text-right">₹{t.exit_price}</td>
                      <td className="py-2.5 px-3 text-right">{t.shares}</td>
                      <td className={`py-2.5 px-3 text-right font-bold ${t.net_pnl >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                        {t.net_pnl >= 0 ? '+' : ''}₹{t.net_pnl.toLocaleString()}
                      </td>
                      <td className={`py-2.5 px-3 text-right font-bold ${t.return_pct >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                        {t.return_pct >= 0 ? '+' : ''}{t.return_pct}%
                      </td>
                      <td className="py-2.5 px-3">
                        <span className={`px-2 py-0.5 rounded text-[10px] font-semibold ${
                          t.exit_reason.includes('Target') 
                            ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' 
                            : (t.exit_reason.includes('Stop') ? 'bg-rose-500/10 text-rose-400 border border-rose-500/20' : 'bg-gray-800 text-gray-300')
                        }`}>
                          {t.exit_reason}
                        </span>
                      </td>
                      <td className="py-2.5 px-3 text-center text-gray-400">{t.bars_held}d</td>
                    </tr>
                  ))}
                  {filteredTrades.length === 0 && (
                    <tr>
                      <td colSpan="11" className="text-center py-8 text-gray-500">
                        No trades triggered for this setup in the selected horizon.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>

        </div>
      )}

    </div>
  );
}
