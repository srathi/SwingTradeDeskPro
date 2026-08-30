import React, { useState, useEffect } from 'react';
import { 
  TrendingUp, 
  TrendingDown, 
  PlusCircle, 
  CheckCircle, 
  XCircle, 
  Trash2, 
  RefreshCw, 
  ShieldAlert, 
  Clock, 
  BarChart2, 
  Target, 
  Layers, 
  Sparkles,
  DollarSign,
  AlertTriangle
} from 'lucide-react';
import { 
  fetchJournalSummary, 
  logJournalTrade, 
  closeJournalTrade, 
  deleteJournalTrade 
} from '../services/api';
import JargonTooltip from './JargonTooltip';

export default function TradeJournalView({ onOpenChart, onOpenDeepScan, onOpenAIForecast }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // New Trade Modal state
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [newTicker, setNewTicker] = useState('');
  const [newStrategy, setNewStrategy] = useState('Trend Pullback (20/50 EMA)');
  const [newEntryPrice, setNewEntryPrice] = useState('');
  const [newShares, setNewShares] = useState('');
  const [newStopLoss, setNewStopLoss] = useState('');
  const [newTarget1, setNewTarget1] = useState('');
  const [newTarget2, setNewTarget2] = useState('');
  const [newNotes, setNewNotes] = useState('');

  // Close Trade Modal state
  const [closeModalTrade, setCloseModalTrade] = useState(null);
  const [closeExitPrice, setCloseExitPrice] = useState('');
  const [closeExitReason, setCloseExitReason] = useState('TARGET_1');
  const [closeNotes, setCloseNotes] = useState('');

  const fetchJournalData = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await fetchJournalSummary();
      setData(res);
    } catch (err) {
      console.error("Error fetching journal data:", err);
      setError("Failed to load simulated paper trading journal.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchJournalData();
  }, []);

  const handleAddTrade = async (e) => {
    e.preventDefault();
    if (!newTicker || !newEntryPrice || !newShares || !newStopLoss || !newTarget1) {
      alert("Please fill all required fields.");
      return;
    }

    try {
      await logJournalTrade({
        ticker: newTicker.trim().toUpperCase(),
        strategy: newStrategy,
        entry_price: parseFloat(newEntryPrice),
        shares: parseInt(newShares, 10),
        stop_loss: parseFloat(newStopLoss),
        target_1: parseFloat(newTarget1),
        target_2: newTarget2 ? parseFloat(newTarget2) : null,
        notes: newNotes
      });
      setIsModalOpen(false);
      // Reset form
      setNewTicker('');
      setNewEntryPrice('');
      setNewShares('');
      setNewStopLoss('');
      setNewTarget1('');
      setNewTarget2('');
      setNewNotes('');
      fetchJournalData();
    } catch (err) {
      alert("Failed to log trade: " + err.message);
    }
  };

  const handleExecuteClose = async (e) => {
    e.preventDefault();
    if (!closeModalTrade || !closeExitPrice) return;

    try {
      await closeJournalTrade(closeModalTrade.id, {
        exit_price: parseFloat(closeExitPrice),
        exit_reason: closeExitReason,
        notes: closeNotes
      });
      setCloseModalTrade(null);
      setCloseExitPrice('');
      setCloseNotes('');
      fetchJournalData();
    } catch (err) {
      alert("Failed to close trade: " + err.message);
    }
  };

  const handleDelete = async (tradeId) => {
    if (!window.confirm("Are you sure you want to delete this trade record?")) return;
    try {
      await deleteJournalTrade(tradeId);
      fetchJournalData();
    } catch (err) {
      alert("Failed to delete trade: " + err.message);
    }
  };

  const summary = data?.portfolio_summary || {
    total_trades: 0,
    open_trades_count: 0,
    closed_trades_count: 0,
    win_rate_pct: 0,
    profit_factor: 0,
    total_realized_pnl: 0,
    total_unrealized_pnl: 0,
    net_combined_pnl: 0,
    avg_r_multiple: 0
  };

  const openPositions = data?.open_positions || [];
  const closedTrades = data?.closed_trades || [];

  return (
    <div className="min-h-full bg-[#080C14] text-gray-100 p-4 sm:p-6 lg:p-8 space-y-6">
      
      {/* Top Header & Actions */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-gray-800/80 pb-5">
        <div>
          <div className="flex items-center space-x-2.5">
            <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
              <Layers className="w-6 h-6 text-cyan-400" />
              Simulated Paper Trading & Journal Studio
            </h1>
            <span className="bg-cyan-500/10 text-cyan-400 text-xs font-mono font-semibold px-2.5 py-0.5 rounded border border-cyan-500/20">
              Forward Testing
            </span>
          </div>
          <p className="text-sm text-gray-400 mt-1 font-mono">
            Institutional trade logging, live mark-to-market P&L tracking, R-multiple attribution, and behavioral analytics by <a href="https://www.rupeemap.in" target="_blank" rel="noopener noreferrer" className="text-cyan-400 hover:underline">rupeemap.in labs</a> (by Sandesh Rathi).
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={fetchJournalData}
            disabled={loading}
            className="flex items-center space-x-1.5 px-3 py-2 rounded-lg bg-gray-900 border border-gray-800 text-xs font-mono text-gray-300 hover:text-white hover:bg-gray-800/80 transition shadow-sm"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin text-cyan-400' : ''}`} />
            <span>Refresh Live CMP</span>
          </button>

          <button
            onClick={() => setIsModalOpen(true)}
            className="flex items-center space-x-1.5 px-4 py-2 rounded-lg bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white font-mono text-xs font-bold transition shadow-lg shadow-cyan-900/20"
          >
            <PlusCircle className="w-4 h-4" />
            <span>Log New Trade</span>
          </button>
        </div>
      </div>

      {/* Portfolio Performance KPI Matrix */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
        
        {/* Net Combined P&L */}
        <div className="bg-gray-950/80 border border-gray-800/90 rounded-xl p-3.5 shadow-sm">
          <span className="text-[11px] font-mono text-gray-400 uppercase tracking-wider block">Net Combined P&L</span>
          <div className={`text-lg font-bold font-mono mt-1 ${summary.net_combined_pnl >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
            {summary.net_combined_pnl >= 0 ? '+' : ''}₹{summary.net_combined_pnl.toLocaleString('en-IN')}
          </div>
          <span className="text-[10px] font-mono text-gray-400 block mt-0.5">Realized + Unrealized</span>
        </div>

        {/* Unrealized P&L */}
        <div className="bg-gray-950/80 border border-gray-800/90 rounded-xl p-3.5 shadow-sm">
          <span className="text-[11px] font-mono text-gray-400 uppercase tracking-wider block">Unrealized Open P&L</span>
          <div className={`text-lg font-bold font-mono mt-1 ${summary.total_unrealized_pnl >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
            {summary.total_unrealized_pnl >= 0 ? '+' : ''}₹{summary.total_unrealized_pnl.toLocaleString('en-IN')}
          </div>
          <span className="text-[10px] font-mono text-gray-400 block mt-0.5">{summary.open_trades_count} active position(s)</span>
        </div>

        {/* Realized P&L */}
        <div className="bg-gray-950/80 border border-gray-800/90 rounded-xl p-3.5 shadow-sm">
          <span className="text-[11px] font-mono text-gray-400 uppercase tracking-wider block">Realized Closed P&L</span>
          <div className={`text-lg font-bold font-mono mt-1 ${summary.total_realized_pnl >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
            {summary.total_realized_pnl >= 0 ? '+' : ''}₹{summary.total_realized_pnl.toLocaleString('en-IN')}
          </div>
          <span className="text-[10px] font-mono text-gray-400 block mt-0.5">{summary.closed_trades_count} closed trade(s)</span>
        </div>

        {/* Win Rate */}
        <div className="bg-gray-950/80 border border-gray-800/90 rounded-xl p-3.5 shadow-sm">
          <span className="text-[11px] font-mono text-gray-400 uppercase tracking-wider block">Historical Win Rate</span>
          <div className="text-lg font-bold font-mono text-cyan-300 mt-1">
            {summary.win_rate_pct}%
          </div>
          <span className="text-[10px] font-mono text-gray-400 block mt-0.5">On closed setups</span>
        </div>

        {/* Profit Factor */}
        <div className="bg-gray-950/80 border border-gray-800/90 rounded-xl p-3.5 shadow-sm">
          <JargonTooltip termKey="profit_factor">
            <span className="text-[11px] font-mono text-gray-400 uppercase tracking-wider block">Profit Factor</span>
          </JargonTooltip>
          <div className="text-lg font-bold font-mono text-purple-300 mt-1">
            {summary.profit_factor}
          </div>
          <span className="text-[10px] font-mono text-gray-400 block mt-0.5">Gross Win / Gross Loss</span>
        </div>

        {/* Avg R-Multiple */}
        <div className="bg-gray-950/80 border border-gray-800/90 rounded-xl p-3.5 shadow-sm">
          <JargonTooltip termKey="r_multiple">
            <span className="text-[11px] font-mono text-gray-400 uppercase tracking-wider block">Avg R-Multiple</span>
          </JargonTooltip>
          <div className="text-lg font-bold font-mono text-amber-300 mt-1">
            {summary.avg_r_multiple > 0 ? '+' : ''}{summary.avg_r_multiple} R
          </div>
          <span className="text-[10px] font-mono text-gray-400 block mt-0.5">Payoff ratio efficiency</span>
        </div>

      </div>

      {/* SECTION 1: Active Open Simulated Positions */}
      <div className="bg-gray-950/90 border border-gray-800 rounded-xl overflow-hidden shadow-lg">
        <div className="px-5 py-4 border-b border-gray-800/90 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <div className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse"></div>
            <h2 className="text-base font-bold text-white font-mono">
              Active Open Positions ({openPositions.length})
            </h2>
          </div>
          <span className="text-xs font-mono text-gray-400">Live mark-to-market prices</span>
        </div>

        {openPositions.length === 0 ? (
          <div className="p-12 text-center text-gray-400 font-mono">
            <Layers className="w-10 h-10 mx-auto text-gray-400 mb-2 opacity-50" />
            <p className="text-sm">No simulated trades currently open.</p>
            <button
              onClick={() => setIsModalOpen(true)}
              className="mt-3 px-3 py-1.5 rounded-lg bg-cyan-600/20 text-cyan-300 border border-cyan-500/30 text-xs hover:bg-cyan-600/30 font-mono"
            >
              + Log Your First Setup
            </button>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left font-mono text-xs">
              <thead className="bg-gray-900/60 text-gray-400 border-b border-gray-800">
                <tr>
                  <th className="py-3 px-4">Ticker / Strategy</th>
                  <th className="py-3 px-4">Entry / Shares</th>
                  <th className="py-3 px-4">Live CMP</th>
                  <th className="py-3 px-4">Stop Loss</th>
                  <th className="py-3 px-4">Target 1 & 2</th>
                  <th className="py-3 px-4">Current R-Multiple</th>
                  <th className="py-3 px-4">Unrealized P&L</th>
                  <th className="py-3 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-800/60">
                {openPositions.map((pos) => {
                  const isProfit = pos.unrealized_pnl >= 0;
                  return (
                    <tr key={pos.id} className="hover:bg-gray-900/40 transition">
                      
                      {/* Ticker & Strategy */}
                      <td className="py-3 px-4">
                        <div className="flex items-center space-x-2">
                          <button 
                            onClick={() => onOpenChart && onOpenChart(pos.ticker)}
                            className="font-bold text-cyan-300 hover:underline text-sm"
                          >
                            {pos.ticker}
                          </button>
                          <span className="text-[10px] px-1.5 py-0.5 rounded bg-gray-800 text-gray-300 border border-gray-700">
                            {pos.direction}
                          </span>
                        </div>
                        <span className="text-[11px] text-gray-400 block truncate max-w-[200px]">{pos.strategy}</span>
                      </td>

                      {/* Entry & Shares */}
                      <td className="py-3 px-4 text-gray-300">
                        <div>₹{pos.entry_price.toLocaleString('en-IN')}</div>
                        <span className="text-[11px] text-gray-400">{pos.shares} shares (₹{pos.capital_invested?.toLocaleString('en-IN')})</span>
                      </td>

                      {/* Live CMP */}
                      <td className="py-3 px-4">
                        <div className="font-bold text-white">₹{pos.cmp?.toLocaleString('en-IN')}</div>
                        {pos.is_stop_loss_hit && (
                          <span className="text-[10px] px-1.5 py-0.5 rounded bg-rose-500/20 text-rose-300 border border-rose-500/30 flex items-center gap-1 mt-0.5 w-max">
                            <AlertTriangle className="w-3 h-3" /> Stop Hit!
                          </span>
                        )}
                        {pos.is_target_1_hit && (
                          <span className="text-[10px] px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 flex items-center gap-1 mt-0.5 w-max">
                            <CheckCircle className="w-3 h-3" /> Target 1 Hit!
                          </span>
                        )}
                      </td>

                      {/* Stop Loss */}
                      <td className="py-3 px-4 text-rose-400 font-semibold">
                        ₹{pos.stop_loss?.toLocaleString('en-IN')}
                        <span className="text-[10px] text-gray-400 block">Risk: ₹{pos.risk_per_share}/sh</span>
                      </td>

                      {/* Targets */}
                      <td className="py-3 px-4">
                        <div className="text-emerald-400 font-semibold">T1: ₹{pos.target_1?.toLocaleString('en-IN')}</div>
                        {pos.target_2 && <div className="text-emerald-500/80 text-[11px]">T2: ₹{pos.target_2?.toLocaleString('en-IN')}</div>}
                      </td>

                      {/* R Multiple */}
                      <td className="py-3 px-4">
                        <span className={`font-bold px-2 py-0.5 rounded text-xs ${pos.current_r_multiple >= 1.0 ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30' : pos.current_r_multiple < 0 ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30' : 'bg-gray-800 text-gray-300'}`}>
                          {pos.current_r_multiple > 0 ? '+' : ''}{pos.current_r_multiple} R
                        </span>
                      </td>

                      {/* Unrealized P&L */}
                      <td className="py-3 px-4">
                        <div className={`font-bold ${isProfit ? 'text-emerald-400' : 'text-rose-400'}`}>
                          {isProfit ? '+' : ''}₹{pos.unrealized_pnl?.toLocaleString('en-IN')}
                        </div>
                        <span className={`text-[10px] ${isProfit ? 'text-emerald-500/80' : 'text-rose-500/80'}`}>
                          {isProfit ? '+' : ''}{pos.unrealized_pnl_pct}%
                        </span>
                      </td>

                      {/* Actions */}
                      <td className="py-3 px-4 text-right space-x-2">
                        <button
                          onClick={() => {
                            setCloseModalTrade(pos);
                            setCloseExitPrice(pos.cmp || pos.entry_price);
                          }}
                          className="px-2.5 py-1 rounded bg-blue-600/20 hover:bg-blue-600/30 text-blue-300 border border-blue-500/30 text-xs font-bold transition"
                        >
                          Close Trade
                        </button>
                        <button
                          onClick={() => handleDelete(pos.id)}
                          className="p-1 rounded text-gray-400 hover:text-rose-400 transition"
                          title="Delete trade"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      </td>

                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* SECTION 2: Closed Trades History & Attribution */}
      <div className="bg-gray-950/90 border border-gray-800 rounded-xl overflow-hidden shadow-lg">
        <div className="px-5 py-4 border-b border-gray-800/90 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Clock className="w-4 h-4 text-gray-400" />
            <h2 className="text-base font-bold text-white font-mono">
              Closed Trade History ({closedTrades.length})
            </h2>
          </div>
          <span className="text-xs font-mono text-gray-400">Post-trade statistical attribution</span>
        </div>

        {closedTrades.length === 0 ? (
          <div className="p-8 text-center text-gray-400 font-mono text-xs">
            No completed trades yet in this journal.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left font-mono text-xs">
              <thead className="bg-gray-900/60 text-gray-400 border-b border-gray-800">
                <tr>
                  <th className="py-3 px-4">Date / Ticker</th>
                  <th className="py-3 px-4">Strategy</th>
                  <th className="py-3 px-4">Entry → Exit</th>
                  <th className="py-3 px-4">Exit Reason</th>
                  <th className="py-3 px-4">R-Multiple</th>
                  <th className="py-3 px-4">Realized P&L</th>
                  <th className="py-3 px-4 text-right">Delete</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-800/60">
                {closedTrades.map((pos) => {
                  const isProfit = pos.realized_pnl >= 0;
                  return (
                    <tr key={pos.id} className="hover:bg-gray-900/40 transition">
                      <td className="py-3 px-4">
                        <span className="font-bold text-cyan-300">{pos.ticker}</span>
                        <span className="text-[10px] text-gray-400 block">{pos.exit_date?.slice(0, 10)}</span>
                      </td>
                      <td className="py-3 px-4 text-gray-400 truncate max-w-[180px]">
                        {pos.strategy}
                      </td>
                      <td className="py-3 px-4 text-gray-300">
                        ₹{pos.entry_price} → <span className="font-bold text-white">₹{pos.exit_price}</span> ({pos.shares} sh)
                      </td>
                      <td className="py-3 px-4">
                        <span className="px-2 py-0.5 rounded text-[11px] bg-gray-800 text-gray-300 border border-gray-700">
                          {pos.exit_reason}
                        </span>
                      </td>
                      <td className="py-3 px-4">
                        <span className={`font-bold px-2 py-0.5 rounded text-xs ${pos.realized_r_multiple >= 1.0 ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30' : pos.realized_r_multiple < 0 ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30' : 'bg-gray-800 text-gray-300'}`}>
                          {pos.realized_r_multiple > 0 ? '+' : ''}{pos.realized_r_multiple} R
                        </span>
                      </td>
                      <td className="py-3 px-4">
                        <div className={`font-bold ${isProfit ? 'text-emerald-400' : 'text-rose-400'}`}>
                          {isProfit ? '+' : ''}₹{pos.realized_pnl?.toLocaleString('en-IN')}
                        </div>
                        <span className={`text-[10px] ${isProfit ? 'text-emerald-500/80' : 'text-rose-500/80'}`}>
                          {isProfit ? '+' : ''}{pos.realized_pnl_pct}%
                        </span>
                      </td>
                      <td className="py-3 px-4 text-right">
                        <button
                          onClick={() => handleDelete(pos.id)}
                          className="p-1 rounded text-gray-400 hover:text-rose-400 transition"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* MODAL: Log New Trade */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
          <div className="bg-gray-950 border border-gray-800 rounded-xl max-w-lg w-full p-6 space-y-4 shadow-2xl font-mono">
            <div className="flex items-center justify-between border-b border-gray-800 pb-3">
              <h3 className="text-lg font-bold text-white flex items-center gap-2">
                <PlusCircle className="w-5 h-5 text-cyan-400" />
                Log Simulated Swing Trade
              </h3>
              <button onClick={() => setIsModalOpen(false)} className="text-gray-400 hover:text-white">
                <XCircle className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleAddTrade} className="space-y-3.5 text-xs">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-gray-400 mb-1">Ticker Symbol *</label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. RELIANCE.NS"
                    value={newTicker}
                    onChange={(e) => setNewTicker(e.target.value)}
                    className="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-cyan-500 uppercase"
                  />
                </div>
                <div>
                  <label className="block text-gray-400 mb-1">Strategy Used *</label>
                  <input
                    type="text"
                    required
                    value={newStrategy}
                    onChange={(e) => setNewStrategy(e.target.value)}
                    className="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-cyan-500"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-gray-400 mb-1">Entry Price (₹) *</label>
                  <input
                    type="number"
                    step="any"
                    required
                    placeholder="1250.00"
                    value={newEntryPrice}
                    onChange={(e) => setNewEntryPrice(e.target.value)}
                    className="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-cyan-500"
                  />
                </div>
                <div>
                  <label className="block text-gray-400 mb-1">Number of Shares *</label>
                  <input
                    type="number"
                    required
                    placeholder="100"
                    value={newShares}
                    onChange={(e) => setNewShares(e.target.value)}
                    className="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-cyan-500"
                  />
                </div>
              </div>

              <div className="grid grid-cols-3 gap-3">
                <div>
                  <label className="block text-rose-400 mb-1">Stop Loss (₹) *</label>
                  <input
                    type="number"
                    step="any"
                    required
                    placeholder="1190.00"
                    value={newStopLoss}
                    onChange={(e) => setNewStopLoss(e.target.value)}
                    className="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-rose-500"
                  />
                </div>
                <div>
                  <label className="block text-emerald-400 mb-1">Target 1 (₹) *</label>
                  <input
                    type="number"
                    step="any"
                    required
                    placeholder="1340.00"
                    value={newTarget1}
                    onChange={(e) => setNewTarget1(e.target.value)}
                    className="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-emerald-500"
                  />
                </div>
                <div>
                  <label className="block text-emerald-500/80 mb-1">Target 2 (₹)</label>
                  <input
                    type="number"
                    step="any"
                    placeholder="1400.00"
                    value={newTarget2}
                    onChange={(e) => setNewTarget2(e.target.value)}
                    className="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-emerald-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-gray-400 mb-1">Trade Notes / Thesis</label>
                <textarea
                  rows="2"
                  placeholder="e.g. 20 EMA pullback with volume dry-up, Stage 2 leader..."
                  value={newNotes}
                  onChange={(e) => setNewNotes(e.target.value)}
                  className="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-cyan-500"
                ></textarea>
              </div>

              <div className="flex justify-end space-x-3 pt-2">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="px-4 py-2 rounded-lg bg-gray-800 text-gray-300 hover:bg-gray-700 transition"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 rounded-lg bg-gradient-to-r from-cyan-600 to-blue-600 text-white font-bold hover:from-cyan-500 hover:to-blue-500 transition"
                >
                  Save & Track
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* MODAL: Close Trade */}
      {closeModalTrade && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
          <div className="bg-gray-950 border border-gray-800 rounded-xl max-w-md w-full p-6 space-y-4 shadow-2xl font-mono">
            <div className="flex items-center justify-between border-b border-gray-800 pb-3">
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                <CheckCircle className="w-5 h-5 text-blue-400" />
                Close Trade: {closeModalTrade.ticker}
              </h3>
              <button onClick={() => setCloseModalTrade(null)} className="text-gray-400 hover:text-white">
                <XCircle className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleExecuteClose} className="space-y-3 text-xs">
              <div>
                <label className="block text-gray-400 mb-1">Exit Execution Price (₹) *</label>
                <input
                  type="number"
                  step="any"
                  required
                  value={closeExitPrice}
                  onChange={(e) => setCloseExitPrice(e.target.value)}
                  className="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-cyan-500"
                />
              </div>

              <div>
                <label className="block text-gray-400 mb-1">Exit Reason *</label>
                <select
                  value={closeExitReason}
                  onChange={(e) => setCloseExitReason(e.target.value)}
                  className="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-cyan-500"
                >
                  <option value="TARGET_1">Target 1 Hit (Profit)</option>
                  <option value="TARGET_2">Target 2 Hit (Profit Runner)</option>
                  <option value="STOP_LOSS">Stop Loss Hit (Loss Controlled)</option>
                  <option value="TRAILING_STOP">Trailing Stop Hit (Lock Profit)</option>
                  <option value="TIME_EXPIRATION">15-Day Time Barrier Reallocation</option>
                  <option value="MANUAL">Manual Discretionary Exit</option>
                </select>
              </div>

              <div>
                <label className="block text-gray-400 mb-1">Post-Trade Review Notes</label>
                <textarea
                  rows="2"
                  placeholder="Lessons learned, discipline remarks..."
                  value={closeNotes}
                  onChange={(e) => setCloseNotes(e.target.value)}
                  className="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-cyan-500"
                ></textarea>
              </div>

              <div className="flex justify-end space-x-3 pt-2">
                <button
                  type="button"
                  onClick={() => setCloseModalTrade(null)}
                  className="px-4 py-2 rounded-lg bg-gray-800 text-gray-300 hover:bg-gray-700 transition"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 rounded-lg bg-blue-600 text-white font-bold hover:bg-blue-500 transition"
                >
                  Confirm Exit
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

    </div>
  );
}
