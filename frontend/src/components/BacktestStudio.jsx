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
  AlertCircle
} from 'lucide-react';
import { runBacktest, fetchStrategies, fetchUniverses } from '../services/api';
import StockSearchInput from './StockSearchInput';

export default function BacktestStudio({ initialTicker = "RELIANCE.NS", initialStrategy = "trend_pullback" }) {
  const chartContainerRef = useRef(null);
  const chartRef = useRef(null);

  const [ticker, setTicker] = useState(initialTicker);
  const [strategyId, setStrategyId] = useState(initialStrategy);
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
    setLoading(true);
    setErrorMsg(null);
    try {
      let sym = ticker.trim().toUpperCase();
      if (!sym.includes('.') && !sym.startsWith('BASKET') && !['AAPL', 'MSFT', 'NVDA', 'GOOGL', 'AMZN', 'TSLA'].includes(sym)) {
        sym += '.NS';
      }

      const res = await runBacktest({
        ticker: sym,
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

  // Render Equity Curve via Lightweight Charts
  useEffect(() => {
    if (!chartContainerRef.current || !metrics || !metrics.equity_curve || metrics.equity_curve.length === 0) return;

    if (chartRef.current) {
      try { chartRef.current.remove(); } catch (e) {}
      chartRef.current = null;
    }

    const container = chartContainerRef.current;
    const initialWidth = container.clientWidth || 700;

    let chart = null;
    try {
      chart = createChart(container, {
        width: initialWidth,
        height: 280,
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
        }
      });
      chartRef.current = chart;

      const equityData = metrics.equity_curve
        .filter(p => p.date !== 'Start' && p.date.includes('-'))
        .map(p => ({
          time: p.date,
          value: p.equity
        }));

      if (equityData.length > 0) {
        const areaSeries = chart.addAreaSeries({
          topColor: 'rgba(6, 182, 212, 0.4)',
          bottomColor: 'rgba(6, 182, 212, 0.0)',
          lineColor: '#06B6D4',
          lineWidth: 2,
          title: 'Portfolio Equity (₹)'
        });
        areaSeries.setData(equityData);

        areaSeries.createPriceLine({
          price: metrics.initial_capital,
          color: '#6B7280',
          lineWidth: 1,
          lineStyle: 2,
          title: 'INITIAL CAPITAL'
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

  const filteredTrades = metrics?.trades?.filter(t => {
    if (tradeFilter === 'WIN') return t.is_win;
    if (tradeFilter === 'LOSS') return !t.is_win;
    return true;
  }) || [];

  const exportTradeLogCSV = () => {
    if (!metrics || !metrics.trades || metrics.trades.length === 0) return;
    const headers = ["Trade #", "Ticker", "Entry Date", "Exit Date", "Entry Price", "Exit Price", "Shares", "Capital Deployed", "Gross PnL", "Net PnL", "Return %", "Exit Reason", "Bars Held"];
    const rows = metrics.trades.map(t => [
      t.trade_no, t.ticker, t.entry_date, t.exit_date, t.entry_price, t.exit_price, t.shares, t.capital_deployed, t.gross_pnl, t.net_pnl, `${t.return_pct}%`, `"${t.exit_reason}"`, t.bars_held
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

  return (
    <div className="space-y-6">
      
      {/* Control & Parameters Panel */}
      <div className="bg-gray-900/90 border border-gray-800 p-6 rounded-2xl shadow-xl space-y-4">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-gray-800 pb-4">
          <div>
            <span className="px-2.5 py-0.5 rounded-full bg-cyan-500/10 text-cyan-400 text-xs font-semibold uppercase tracking-wider border border-cyan-500/20">
              Institutional Simulation
            </span>
            <h1 className="text-xl font-bold text-white mt-1">Quantitative Backtest Studio</h1>
            <p className="text-xs text-gray-400">
              Simulates realistic trade lifecycle including STT, GST, brokerage, slippage, and fixed risk position sizing.
            </p>
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
              className="w-full bg-gray-950 border border-gray-700 rounded-lg px-3 py-2 text-sm text-gray-200 focus:outline-none focus:border-cyan-500"
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
              className="w-full bg-gray-950 border border-gray-700 rounded-lg px-3 py-2 text-sm text-gray-200 font-mono focus:outline-none focus:border-cyan-500"
            />
          </div>
        </div>

        {/* Frictions & Risk Settings */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-3 border-t border-gray-800/60 bg-gray-950/60 p-3.5 rounded-xl text-xs">
          <div className="flex items-center justify-between">
            <span className="text-gray-400">Risk per Trade (%):</span>
            <input
              type="number"
              step="0.5"
              min="0.5"
              max="5"
              value={riskPct}
              onChange={(e) => setRiskPct(e.target.value)}
              className="w-20 bg-gray-900 border border-gray-700 rounded px-2 py-1 text-cyan-300 font-mono text-center"
            />
          </div>

          <div className="flex items-center justify-between">
            <span className="text-gray-400">Estimated Slippage (%):</span>
            <input
              type="number"
              step="0.01"
              value={slippagePct}
              onChange={(e) => setSlippagePct(e.target.value)}
              className="w-20 bg-gray-900 border border-gray-700 rounded px-2 py-1 text-cyan-300 font-mono text-center"
            />
          </div>

          <div className="flex items-center justify-between">
            <span className="text-gray-400">Indian Taxes & Brokerage:</span>
            <button
              onClick={() => setEnableTaxes(!enableTaxes)}
              className={`px-3 py-1 rounded font-semibold transition-colors ${
                enableTaxes ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40' : 'bg-gray-800 text-gray-500'
              }`}
            >
              {enableTaxes ? "Enabled (STT+GST)" : "Zero Costs"}
            </button>
          </div>
        </div>

      </div>

      {errorMsg && (
        <div className="p-4 bg-red-950/40 border border-red-800 text-red-300 text-xs rounded-xl flex items-center space-x-2">
          <AlertCircle className="w-4 h-4 text-red-400 flex-shrink-0" />
          <span>{errorMsg}</span>
        </div>
      )}

      {/* Backtest Results Dashboard */}
      {metrics && (
        <div className="space-y-6">
          
          {/* Key Metric Scorecards */}
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
            
            <div className="bg-gray-900/80 border border-gray-800 p-4 rounded-xl space-y-1">
              <span className="text-[10px] uppercase font-bold text-gray-500">Net Profit</span>
              <div className={`text-lg font-bold font-mono ${metrics.net_profit >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                {metrics.net_profit >= 0 ? `+₹${metrics.net_profit.toLocaleString()}` : `-₹${Math.abs(metrics.net_profit).toLocaleString()}`}
              </div>
              <span className={`text-xs font-semibold ${metrics.net_profit_pct >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                {metrics.net_profit_pct >= 0 ? `+${metrics.net_profit_pct}%` : `${metrics.net_profit_pct}%`} Return
              </span>
            </div>

            <div className="bg-gray-900/80 border border-gray-800 p-4 rounded-xl space-y-1">
              <span className="text-[10px] uppercase font-bold text-gray-500">Win Rate</span>
              <div className="text-lg font-bold font-mono text-cyan-300">
                {metrics.win_rate}%
              </div>
              <span className="text-xs text-gray-400">
                {metrics.winning_trades}W / {metrics.losing_trades}L ({metrics.total_trades} total)
              </span>
            </div>

            <div className="bg-gray-900/80 border border-gray-800 p-4 rounded-xl space-y-1">
              <span className="text-[10px] uppercase font-bold text-gray-500">Profit Factor</span>
              <div className={`text-lg font-bold font-mono ${metrics.profit_factor >= 1.5 ? 'text-emerald-400' : 'text-yellow-400'}`}>
                {metrics.profit_factor}
              </div>
              <span className="text-xs text-gray-400">Gross Wins / Losses</span>
            </div>

            <div className="bg-gray-900/80 border border-gray-800 p-4 rounded-xl space-y-1">
              <span className="text-[10px] uppercase font-bold text-gray-500">Max Drawdown</span>
              <div className="text-lg font-bold font-mono text-red-400">
                -{metrics.max_drawdown_pct}%
              </div>
              <span className="text-xs text-gray-400">-₹{metrics.max_drawdown_amount.toLocaleString()}</span>
            </div>

            <div className="bg-gray-900/80 border border-gray-800 p-4 rounded-xl space-y-1">
              <span className="text-[10px] uppercase font-bold text-gray-500">Sharpe Ratio</span>
              <div className="text-lg font-bold font-mono text-purple-300">
                {metrics.sharpe_ratio}
              </div>
              <span className="text-xs text-gray-400">Sortino: {metrics.sortino_ratio}</span>
            </div>

            <div className="bg-gray-900/80 border border-gray-800 p-4 rounded-xl space-y-1">
              <span className="text-[10px] uppercase font-bold text-gray-500">Taxes & Friction</span>
              <div className="text-lg font-bold font-mono text-amber-400">
                ₹{metrics.total_taxes_paid.toLocaleString()}
              </div>
              <span className="text-xs text-gray-400">STT, GST, Brokerage</span>
            </div>

          </div>

          {/* Equity Curve Chart */}
          <div className="bg-gray-900/80 border border-gray-800 p-4 rounded-2xl space-y-3">
            <div className="flex items-center justify-between border-b border-gray-800 pb-3">
              <div className="flex items-center space-x-2">
                <BarChart3 className="w-4 h-4 text-cyan-400" />
                <h3 className="text-sm font-bold text-white">Portfolio Equity Curve (₹)</h3>
              </div>
              <span className="text-xs font-mono text-gray-400">
                Final Equity: <strong className="text-cyan-300">₹{metrics.final_equity.toLocaleString()}</strong>
              </span>
            </div>
            
            <div ref={chartContainerRef} className="w-full rounded-lg overflow-hidden" />
          </div>

          {/* Trade Execution Log Table */}
          <div className="bg-gray-900/80 border border-gray-800 rounded-2xl p-5 space-y-4">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-gray-800 pb-4">
              <div className="flex items-center space-x-3">
                <h3 className="text-base font-bold text-white">Trade-by-Trade Execution Log</h3>
                <div className="flex items-center space-x-1 bg-gray-950 p-1 rounded-lg border border-gray-800 text-xs">
                  {['ALL', 'WIN', 'LOSS'].map((f) => (
                    <button
                      key={f}
                      onClick={() => setTradeFilter(f)}
                      className={`px-2.5 py-1 rounded font-semibold text-xs ${
                        tradeFilter === f ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40' : 'text-gray-400 hover:text-gray-200'
                      }`}
                    >
                      {f}
                    </button>
                  ))}
                </div>
              </div>

              <button
                onClick={exportTradeLogCSV}
                className="flex items-center space-x-1.5 px-3 py-1.5 bg-gray-800 hover:bg-gray-700 border border-gray-700 rounded-lg text-xs font-medium text-gray-200 self-start sm:self-auto"
              >
                <Download className="w-3.5 h-3.5" />
                <span>Export Trades CSV</span>
              </button>
            </div>

            {filteredTrades.length > 0 ? (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs text-gray-300 font-mono">
                  <thead className="bg-gray-950/80 text-gray-400 uppercase text-[10px] font-semibold tracking-wider border-b border-gray-800">
                    <tr>
                      <th className="px-3 py-2.5">#</th>
                      <th className="px-3 py-2.5">Symbol</th>
                      <th className="px-3 py-2.5">Entry</th>
                      <th className="px-3 py-2.5">Exit</th>
                      <th className="px-3 py-2.5">Entry ₹</th>
                      <th className="px-3 py-2.5">Exit ₹</th>
                      <th className="px-3 py-2.5">Shares</th>
                      <th className="px-3 py-2.5">Capital</th>
                      <th className="px-3 py-2.5">Net PnL</th>
                      <th className="px-3 py-2.5">Return</th>
                      <th className="px-3 py-2.5">Exit Reason</th>
                      <th className="px-3 py-2.5">Held</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-800/60">
                    {filteredTrades.map((t) => (
                      <tr key={t.trade_no} className="hover:bg-gray-800/40 transition-colors">
                        <td className="px-3 py-2 text-gray-500 font-bold">{t.trade_no}</td>
                        <td className="px-3 py-2 text-white font-bold">{t.ticker}</td>
                        <td className="px-3 py-2 text-gray-400">{t.entry_date}</td>
                        <td className="px-3 py-2 text-gray-400">{t.exit_date}</td>
                        <td className="px-3 py-2 text-gray-200">₹{t.entry_price}</td>
                        <td className="px-3 py-2 text-gray-200">₹{t.exit_price}</td>
                        <td className="px-3 py-2 text-cyan-300">{t.shares}</td>
                        <td className="px-3 py-2 text-gray-300">₹{t.capital_deployed.toLocaleString()}</td>
                        <td className={`px-3 py-2 font-bold ${t.net_pnl >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                          {t.net_pnl >= 0 ? `+₹${t.net_pnl.toLocaleString()}` : `-₹${Math.abs(t.net_pnl).toLocaleString()}`}
                        </td>
                        <td className={`px-3 py-2 font-bold ${t.return_pct >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                          {t.return_pct >= 0 ? `+${t.return_pct}%` : `${t.return_pct}%`}
                        </td>
                        <td className="px-3 py-2 text-gray-400">
                          <span className={`px-2 py-0.5 rounded text-[10px] font-semibold ${
                            t.is_win ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 'bg-red-500/10 text-red-400 border border-red-500/20'
                          }`}>
                            {t.exit_reason}
                          </span>
                        </td>
                        <td className="px-3 py-2 text-gray-400">{t.bars_held} bars</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="text-center py-8 text-gray-500 text-xs">
                No trades match the selected filter.
              </div>
            )}

          </div>

        </div>
      )}

    </div>
  );
}
