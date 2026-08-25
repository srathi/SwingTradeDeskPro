import React, { useState, useEffect } from 'react';
import { 
  Bookmark, 
  Plus, 
  Trash2, 
  Play, 
  BarChart2, 
  Layers, 
  Check, 
  X, 
  Sparkles,
  Zap
} from 'lucide-react';
import { fetchWatchlists, createWatchlist, updateWatchlist, deleteWatchlist } from '../services/api';
import StockSearchInput from './StockSearchInput';

export default function WatchlistView({ onSelectTicker, onScanWatchlist }) {
  const [watchlists, setWatchlists] = useState([]);
  const [activeWlId, setActiveWlId] = useState(null);
  const [newWlName, setNewWlName] = useState("");
  const [loading, setLoading] = useState(false);
  const [showCreateModal, setShowCreateModal] = useState(false);

  useEffect(() => {
    loadWatchlists();
  }, []);

  const loadWatchlists = async () => {
    setLoading(true);
    try {
      const data = await fetchWatchlists();
      setWatchlists(data);
      if (data.length > 0 && !activeWlId) {
        setActiveWlId(data[0].id);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateWatchlist = async (e) => {
    e.preventDefault();
    if (!newWlName.trim()) return;
    try {
      const res = await createWatchlist(newWlName.trim(), ["CONFIPET.NS", "RELIANCE.NS", "TCS.NS", "INFY.NS"]);
      setNewWlName("");
      setShowCreateModal(false);
      await loadWatchlists();
      setActiveWlId(res.id);
    } catch (err) {
      alert(err.message);
    }
  };

  const handleAddStock = async (selectedSym) => {
    if (!selectedSym || !activeWlId) return;
    let sym = selectedSym.trim().toUpperCase();
    if (!sym.includes('.') && !['AAPL', 'MSFT', 'NVDA', 'GOOGL', 'AMZN', 'TSLA'].includes(sym)) {
      sym += '.NS';
    }

    const currentWl = watchlists.find(w => w.id === activeWlId);
    if (!currentWl) return;

    if (currentWl.tickers.includes(sym)) {
      alert(`Symbol ${sym} is already in this watchlist.`);
      return;
    }

    const updatedTickers = [...currentWl.tickers, sym];
    await updateWatchlist(activeWlId, updatedTickers);
    loadWatchlists();
  };

  const handleRemoveTicker = async (symToRemove) => {
    const currentWl = watchlists.find(w => w.id === activeWlId);
    if (!currentWl) return;
    const updatedTickers = currentWl.tickers.filter(t => t !== symToRemove);
    await updateWatchlist(activeWlId, updatedTickers);
    loadWatchlists();
  };

  const handleDeleteWl = async (id) => {
    if (!confirm("Are you sure you want to delete this watchlist?")) return;
    await deleteWatchlist(id);
    setActiveWlId(null);
    loadWatchlists();
  };

  const activeWl = watchlists.find(w => w.id === activeWlId);

  return (
    <div className="space-y-6">
      
      {/* Top Banner */}
      <div className="bg-gray-900/90 border border-gray-800 p-6 rounded-2xl shadow-xl flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <span className="px-2.5 py-0.5 rounded-full bg-cyan-500/10 text-cyan-400 text-xs font-semibold uppercase tracking-wider border border-cyan-500/20">
            Portfolio Baskets
          </span>
          <h1 className="text-xl font-bold text-white mt-1">Custom Watchlists Manager</h1>
          <p className="text-xs text-gray-400">
            Create and organize customized equity baskets for focused high-frequency quantitative scanning.
          </p>
        </div>

        <button
          onClick={() => setShowCreateModal(true)}
          className="flex items-center space-x-2 px-4 py-2.5 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white text-xs font-semibold rounded-xl shadow-lg transition-all self-start md:self-auto"
        >
          <Plus className="w-4 h-4" />
          <span>New Watchlist</span>
        </button>
      </div>

      {/* Main Grid: Watchlists Tabs & Ticker Manager */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        
        {/* Left: Watchlist Baskets List */}
        <div className="space-y-2">
          <span className="text-xs font-bold uppercase text-gray-400 tracking-wider block px-1">
            My Baskets ({watchlists.length})
          </span>
          
          <div className="space-y-1.5">
            {watchlists.map((wl) => (
              <div
                key={wl.id}
                onClick={() => setActiveWlId(wl.id)}
                className={`p-3 rounded-xl border flex items-center justify-between cursor-pointer transition-all ${
                  activeWlId === wl.id
                    ? 'bg-gray-800/90 border-cyan-500/50 shadow-md text-cyan-300'
                    : 'bg-gray-900/60 border-gray-800 text-gray-300 hover:bg-gray-850'
                }`}
              >
                <div className="flex items-center space-x-2.5 truncate">
                  <Bookmark className={`w-4 h-4 ${activeWlId === wl.id ? 'text-cyan-400' : 'text-gray-500'}`} />
                  <span className="text-xs font-semibold truncate">{wl.name}</span>
                </div>
                <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-gray-950 text-gray-400 border border-gray-800">
                  {wl.tickers.length}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Right: Active Watchlist Content */}
        <div className="md:col-span-3 space-y-4">
          {activeWl ? (
            <div className="bg-gray-900/90 border border-gray-800 rounded-2xl p-6 space-y-6">
              
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-gray-800 pb-4">
                <div>
                  <h2 className="text-lg font-bold text-white flex items-center gap-2">
                    <span>{activeWl.name}</span>
                    <span className="text-xs text-gray-400 font-mono font-normal">({activeWl.tickers.length} symbols)</span>
                  </h2>
                  <p className="text-xs text-gray-400">Manage constituents or launch instant screener scan.</p>
                </div>

                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => onScanWatchlist(activeWl)}
                    disabled={activeWl.tickers.length === 0}
                    className="flex items-center space-x-1.5 px-4 py-2 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white rounded-lg text-xs font-semibold shadow-md transition-all active:scale-95 disabled:opacity-50"
                  >
                    <Play className="w-3.5 h-3.5 fill-current" />
                    <span>Scan this Basket</span>
                  </button>

                  <button
                    onClick={() => handleDeleteWl(activeWl.id)}
                    className="p-2 bg-gray-800 hover:bg-red-900/30 text-gray-400 hover:text-red-400 rounded-lg border border-gray-700 transition-colors"
                    title="Delete Watchlist"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>

              {/* Add Symbol Input with Autocomplete */}
              <div className="space-y-1.5">
                <label className="text-xs font-medium text-gray-400 block">Add Equity to {activeWl.name}</label>
                <StockSearchInput
                  value=""
                  onSelectStock={handleAddStock}
                  placeholder="Search stock symbol or company to add (e.g. CONFIPET, Tata Motors, Reliance)..."
                  className="w-full"
                />
              </div>

              {/* Tickers Chips Grid */}
              <div className="space-y-2">
                <span className="text-xs font-semibold text-gray-400 block">Current Constituents</span>
                {activeWl.tickers.length > 0 ? (
                  <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-2.5">
                    {activeWl.tickers.map((sym) => (
                      <div
                        key={sym}
                        className="bg-gray-950 border border-gray-800 hover:border-cyan-500/40 rounded-xl p-3 flex items-center justify-between group transition-all"
                      >
                        <div className="min-w-0 pr-2">
                          <span className="font-mono font-bold text-xs text-white group-hover:text-cyan-300 transition-colors block truncate">
                            {sym}
                          </span>
                        </div>
                        <div className="flex items-center space-x-1">
                          <button
                            onClick={() => onSelectTicker(sym)}
                            className="p-1 text-gray-500 hover:text-cyan-400 transition-colors"
                            title="Open Chart"
                          >
                            <BarChart2 className="w-3.5 h-3.5" />
                          </button>
                          <button
                            onClick={() => handleRemoveTicker(sym)}
                            className="p-1 text-gray-500 hover:text-red-400 transition-colors"
                            title="Remove"
                          >
                            <X className="w-3.5 h-3.5" />
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="p-8 text-center border border-dashed border-gray-800 rounded-xl text-gray-500 text-xs">
                    This watchlist is currently empty. Use the search box above to add equities.
                  </div>
                )}
              </div>

            </div>
          ) : (
            <div className="bg-gray-900/60 border border-dashed border-gray-800 rounded-2xl p-12 text-center text-gray-500 text-xs">
              Select or create a watchlist basket on the left.
            </div>
          )}
        </div>

      </div>

      {/* Create Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-gray-900 border border-gray-700 rounded-2xl p-6 max-w-md w-full space-y-4 shadow-2xl">
            <h3 className="text-base font-bold text-white">Create New Watchlist</h3>
            <form onSubmit={handleCreateWatchlist} className="space-y-4">
              <div>
                <label className="text-xs font-medium text-gray-400 block mb-1">Basket Name</label>
                <input
                  type="text"
                  value={newWlName}
                  onChange={(e) => setNewWlName(e.target.value)}
                  placeholder="e.g. Momentum Breakouts, PSU Champions"
                  className="w-full bg-gray-950 border border-gray-700 rounded-lg px-3 py-2 text-sm text-gray-100 focus:outline-none focus:border-cyan-500"
                  autoFocus
                />
              </div>
              <div className="flex justify-end space-x-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="px-4 py-2 bg-gray-800 hover:bg-gray-700 text-gray-300 rounded-lg text-xs font-medium"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-cyan-500 hover:bg-cyan-400 text-gray-950 rounded-lg text-xs font-bold shadow-md"
                >
                  Create
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

    </div>
  );
}
