import React, { useState, useEffect, useRef } from 'react';
import { Search, Building2, ArrowRight } from 'lucide-react';
import { searchStocks } from '../services/api';

export default function StockSearchInput({
  value,
  onSelectStock,
  placeholder = "Search symbol or company (e.g. Reliance, Tata Motors, SBI, HDFC)...",
  className = ""
}) {
  const [query, setQuery] = useState(value || '');
  const [suggestions, setSuggestions] = useState([]);
  const [isOpen, setIsOpen] = useState(false);
  const [highlightIdx, setHighlightIdx] = useState(0);
  
  const containerRef = useRef(null);
  const isSelectingRef = useRef(false);

  useEffect(() => {
    if (value !== query) {
      isSelectingRef.current = true;
      setQuery(value || '');
      setSuggestions([]);
      setIsOpen(false);
    }
  }, [value]);

  useEffect(() => {
    // If the change came from clicking a dropdown selection or prop update, do not re-fetch and re-open dropdown
    if (isSelectingRef.current) {
      isSelectingRef.current = false;
      return;
    }

    if (!query || query.trim().length < 1) {
      setSuggestions([]);
      setIsOpen(false);
      return;
    }

    const timer = setTimeout(async () => {
      try {
        const results = await searchStocks(query);
        // Only open if the user hasn't just selected a stock
        if (!isSelectingRef.current) {
          setSuggestions(results);
          setIsOpen(results.length > 0);
          setHighlightIdx(0);
        }
      } catch (err) {
        console.error("Search error:", err);
      }
    }, 120);

    return () => clearTimeout(timer);
  }, [query]);

  // Click outside to close
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (containerRef.current && !containerRef.current.contains(e.target)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSelect = (stock) => {
    isSelectingRef.current = true;
    setQuery(stock.symbol);
    setIsOpen(false);
    setSuggestions([]);
    onSelectStock(stock.symbol, stock);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setHighlightIdx((prev) => (prev + 1) % (suggestions.length || 1));
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setHighlightIdx((prev) => (prev - 1 + (suggestions.length || 1)) % (suggestions.length || 1));
    } else if (e.key === 'Enter') {
      e.preventDefault();
      if (isOpen && suggestions.length > 0) {
        handleSelect(suggestions[highlightIdx]);
      } else if (query.trim()) {
        isSelectingRef.current = true;
        setIsOpen(false);
        setSuggestions([]);
        let sym = query.trim().toUpperCase();
        if (!sym.includes('.') && !['AAPL', 'MSFT', 'NVDA', 'GOOGL', 'AMZN', 'TSLA'].includes(sym)) {
          sym += '.NS';
        }
        onSelectStock(sym, { symbol: sym, name: query.trim() });
      }
    } else if (e.key === 'Escape') {
      setIsOpen(false);
    }
  };

  return (
    <div ref={containerRef} className={`relative ${className}`}>
      <div className="relative flex items-center">
        <Search className="w-4 h-4 text-gray-400 absolute left-3.5 pointer-events-none" />
        <input
          type="text"
          value={query}
          onChange={(e) => {
            isSelectingRef.current = false;
            setQuery(e.target.value);
          }}
          onFocus={() => {
            if (suggestions.length > 0 && !isSelectingRef.current) {
              setIsOpen(true);
            }
          }}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          className="w-full bg-gray-950 border border-gray-700 focus:border-cyan-500 rounded-xl pl-10 pr-4 py-2.5 text-xs sm:text-sm text-gray-100 placeholder-gray-500 font-mono focus:outline-none transition-colors shadow-inner"
        />
      </div>

      {/* Autocomplete Dropdown */}
      {isOpen && suggestions.length > 0 && (
        <div className="absolute left-0 right-0 top-full mt-1.5 bg-[#0e1422] border border-cyan-500/30 rounded-xl shadow-2xl z-[100] max-h-80 overflow-y-auto divide-y divide-gray-800/80">
          <div className="px-3.5 py-2 bg-gray-950/90 text-[10px] uppercase font-bold text-gray-400 tracking-wider flex justify-between items-center border-b border-gray-800">
            <span className="text-cyan-400 font-mono">Select Matching Stock ({suggestions.length})</span>
            <span className="text-gray-500 hidden sm:inline">Use ↑↓ keys & Enter</span>
          </div>
          {suggestions.map((stock, idx) => (
            <div
              key={stock.symbol}
              onMouseDown={(e) => {
                e.preventDefault();
                handleSelect(stock);
              }}
              onMouseEnter={() => setHighlightIdx(idx)}
              className={`px-4 py-3 flex items-center justify-between cursor-pointer transition-colors ${
                idx === highlightIdx ? 'bg-cyan-500/15 text-cyan-200' : 'text-gray-200 hover:bg-gray-800/60'
              }`}
            >
              <div className="flex items-center space-x-3 min-w-0 flex-1 pr-3">
                <div className="w-8 h-8 rounded-lg bg-gray-800/80 border border-gray-700 flex items-center justify-center text-cyan-400 flex-shrink-0">
                  <Building2 className="w-4 h-4" />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center space-x-2">
                    <span className="font-mono font-bold text-sm text-white tracking-wide">
                      {stock.symbol}
                    </span>
                    <span className="text-[10px] px-1.5 py-0.2 rounded bg-gray-800 text-cyan-400 font-semibold border border-cyan-500/20 uppercase">
                      {stock.exchange}
                    </span>
                  </div>
                  <div className="text-xs text-gray-300 font-normal whitespace-normal break-words leading-snug mt-0.5">
                    {stock.name}
                  </div>
                </div>
              </div>
              <ArrowRight className="w-4 h-4 text-cyan-400 flex-shrink-0" />
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
