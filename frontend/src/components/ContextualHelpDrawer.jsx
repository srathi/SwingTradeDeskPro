// ContextualHelpDrawer.jsx - Interactive Slide-Over Page Guide & Jargon Dictionary
// Copyright (c) rupeemap.in labs | by Sandesh Rathi (https://www.rupeemap.in)

import React, { useState, useEffect, useMemo } from 'react';
import { 
  X, 
  Search, 
  BookOpen, 
  Sparkles, 
  HelpCircle, 
  ChevronRight, 
  Layers, 
  Award, 
  ShieldCheck, 
  TrendingUp, 
  Activity, 
  ExternalLink,
  Info,
  CheckCircle2,
  Lightbulb
} from 'lucide-react';
import { PAGE_GUIDES, UNIVERSAL_GLOSSARY, STRATEGIES_PLAYBOOK } from '../data/knowledgeBase';

export default function ContextualHelpDrawer({ 
  isOpen, 
  onClose, 
  activeTab = 'screener',
  initialTerm = null 
}) {
  const [selectedDrawerTab, setSelectedDrawerTab] = useState('page'); // 'page', 'glossary', 'strategies'
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('ALL');
  const [selectedTermKey, setSelectedTermKey] = useState(null);

  // Sync initial term if provided
  useEffect(() => {
    if (initialTerm) {
      setSelectedTermKey(initialTerm);
      setSelectedDrawerTab('glossary');
    }
  }, [initialTerm]);

  // Listen for Escape key to close
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };
    if (isOpen) {
      window.addEventListener('keydown', handleKeyDown);
    }
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  // Map app activeTab to page guide key
  const pageGuideKey = useMemo(() => {
    if (activeTab === 'screener') return 'screener';
    if (activeTab === 'deepscan') return 'deepscan';
    if (activeTab === 'chart') return 'chart';
    if (activeTab === 'journal') return 'journal';
    if (activeTab === 'risk') return 'risk';
    if (activeTab === 'backtest') return 'backtest';
    if (activeTab === 'regime') return 'regime';
    return 'screener';
  }, [activeTab]);

  const currentGuide = PAGE_GUIDES[pageGuideKey] || PAGE_GUIDES.screener;

  // Filter glossary terms by search & category
  const filteredGlossary = useMemo(() => {
    let list = Object.entries(UNIVERSAL_GLOSSARY).map(([key, item]) => ({ key, ...item }));
    if (selectedCategory !== 'ALL') {
      list = list.filter(item => item.category === selectedCategory);
    }
    if (searchQuery.trim().length > 0) {
      const q = searchQuery.toLowerCase();
      list = list.filter(item => 
        item.term.toLowerCase().includes(q) ||
        (item.acronym && item.acronym.toLowerCase().includes(q)) ||
        item.short_def.toLowerCase().includes(q) ||
        item.category.toLowerCase().includes(q)
      );
    }
    return list;
  }, [searchQuery, selectedCategory]);

  // Categories list for chips
  const categories = useMemo(() => {
    const set = new Set();
    Object.values(UNIVERSAL_GLOSSARY).forEach(item => {
      if (item.category) set.add(item.category);
    });
    return ['ALL', ...Array.from(set)];
  }, []);

  // Filter strategies by search
  const filteredStrategies = useMemo(() => {
    if (!searchQuery.trim()) return STRATEGIES_PLAYBOOK;
    const q = searchQuery.toLowerCase();
    return STRATEGIES_PLAYBOOK.filter(s => 
      s.name.toLowerCase().includes(q) ||
      s.summary.toLowerCase().includes(q) ||
      s.category.toLowerCase().includes(q)
    );
  }, [searchQuery]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-hidden select-text">
      {/* Backdrop */}
      <div 
        onClick={onClose}
        className="absolute inset-0 bg-black/70 backdrop-blur-sm transition-opacity animate-fadeIn"
      />

      {/* Drawer Panel */}
      <div className="absolute inset-y-0 right-0 max-w-full flex pl-10">
        <div className="w-screen max-w-xl bg-[#090D16] border-l border-gray-800 shadow-2xl flex flex-col justify-between overflow-hidden animate-slideLeft">
          
          {/* Top Header */}
          <div className="p-5 border-b border-gray-800/80 bg-gray-950/80 space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2.5">
                <div className="w-8 h-8 rounded-lg bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center text-cyan-400">
                  <BookOpen className="w-4 h-4" />
                </div>
                <div>
                  <h2 className="text-base font-bold text-white tracking-wide">
                    Page Guide & Jargon Playbook
                  </h2>
                  <span className="text-[11px] text-gray-400 font-mono">
                    Contextual Intelligence for <strong className="text-cyan-300">{currentGuide.title}</strong>
                  </span>
                </div>
              </div>

              <button
                onClick={onClose}
                className="p-1.5 rounded-lg text-gray-400 hover:text-white hover:bg-gray-800 transition-colors"
                title="Close Guide (Esc)"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Instant Search Bar */}
            <div className="relative">
              <Search className="w-4 h-4 absolute left-3 top-2.5 text-gray-400" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search jargon, formulas, or strategies (e.g. POC, AVWAP, Kelly, VCP)..."
                className="w-full bg-gray-900 border border-gray-700/80 rounded-xl pl-9 pr-8 py-2 text-xs text-gray-200 placeholder-gray-500 focus:outline-none focus:border-cyan-500 transition-all font-mono"
              />
              {searchQuery && (
                <button
                  onClick={() => setSearchQuery('')}
                  className="absolute right-2.5 top-2.5 text-gray-400 hover:text-gray-200"
                >
                  <X className="w-3.5 h-3.5" />
                </button>
              )}
            </div>

            {/* Navigation Tabs */}
            <div className="flex items-center space-x-1 bg-gray-900/90 p-1 rounded-xl border border-gray-800 text-xs">
              <button
                onClick={() => { setSelectedDrawerTab('page'); setSearchQuery(''); }}
                className={`flex-1 py-1.5 rounded-lg font-medium transition-all flex items-center justify-center space-x-1.5 ${
                  selectedDrawerTab === 'page'
                    ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 font-bold'
                    : 'text-gray-400 hover:text-gray-200'
                }`}
              >
                <Layers className="w-3.5 h-3.5" />
                <span>📍 Current Page Guide</span>
              </button>

              <button
                onClick={() => setSelectedDrawerTab('glossary')}
                className={`flex-1 py-1.5 rounded-lg font-medium transition-all flex items-center justify-center space-x-1.5 ${
                  selectedDrawerTab === 'glossary'
                    ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 font-bold'
                    : 'text-gray-400 hover:text-gray-200'
                }`}
              >
                <HelpCircle className="w-3.5 h-3.5" />
                <span>📚 Jargon Dictionary ({Object.keys(UNIVERSAL_GLOSSARY).length})</span>
              </button>

              <button
                onClick={() => setSelectedDrawerTab('strategies')}
                className={`flex-1 py-1.5 rounded-lg font-medium transition-all flex items-center justify-center space-x-1.5 ${
                  selectedDrawerTab === 'strategies'
                    ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 font-bold'
                    : 'text-gray-400 hover:text-gray-200'
                }`}
              >
                <TrendingUp className="w-3.5 h-3.5" />
                <span>🎯 12 Strategies</span>
              </button>
            </div>
          </div>

          {/* Drawer Body Area */}
          <div className="flex-1 overflow-y-auto p-5 space-y-5 custom-scrollbar">

            {/* TAB 1: CURRENT PAGE GUIDE */}
            {selectedDrawerTab === 'page' && !searchQuery && (
              <div className="space-y-5 animate-fadeIn">
                {/* Page Hero Card */}
                <div className="p-4 rounded-xl bg-gradient-to-br from-cyan-950/40 via-blue-950/20 to-gray-900 border border-cyan-500/30 space-y-2">
                  <div className="flex items-center space-x-2 text-cyan-400 text-xs font-bold uppercase tracking-wider font-mono">
                    <Sparkles className="w-3.5 h-3.5" />
                    <span>Operational Blueprint</span>
                  </div>
                  <h3 className="text-base font-bold text-white">{currentGuide.title}</h3>
                  <p className="text-xs text-gray-300 leading-relaxed font-normal">
                    {currentGuide.summary}
                  </p>
                </div>

                {/* Sections breakdown */}
                <div className="space-y-4">
                  {currentGuide.sections.map((sec, idx) => (
                    <div key={idx} className="bg-gray-900/70 border border-gray-800 rounded-xl p-4 space-y-2.5">
                      <h4 className="text-xs font-bold text-cyan-300 tracking-wide flex items-center gap-1.5">
                        <ChevronRight className="w-3.5 h-3.5 text-cyan-400" />
                        {sec.heading}
                      </h4>
                      {sec.description && (
                        <p className="text-xs text-gray-300 leading-relaxed">
                          {sec.description}
                        </p>
                      )}
                      {sec.bullets && (
                        <ul className="space-y-1.5 pl-2 text-xs text-gray-300">
                          {sec.bullets.map((b, bIdx) => (
                            <li key={bIdx} className="flex items-start gap-2">
                              <span className="text-cyan-400 mt-0.5">•</span>
                              <span className="leading-relaxed">{b}</span>
                            </li>
                          ))}
                        </ul>
                      )}
                      {sec.tips && (
                        <div className="p-2.5 rounded-lg bg-cyan-950/30 border border-cyan-800/40 text-[11px] text-cyan-200 flex items-start gap-2">
                          <Lightbulb className="w-3.5 h-3.5 text-cyan-400 flex-shrink-0 mt-0.5" />
                          <span><strong>Pro Tip:</strong> {sec.tips}</span>
                        </div>
                      )}
                    </div>
                  ))}
                </div>

                {/* Real-World Concrete Example */}
                {currentGuide.example && (
                  <div className="p-4 rounded-xl bg-emerald-950/20 border border-emerald-500/30 space-y-2">
                    <div className="flex items-center space-x-1.5 text-emerald-400 text-xs font-bold">
                      <CheckCircle2 className="w-4 h-4" />
                      <span>{currentGuide.example.title}</span>
                    </div>
                    <p className="text-xs text-gray-300 leading-relaxed">
                      {currentGuide.example.text}
                    </p>
                  </div>
                )}
              </div>
            )}

            {/* TAB 2: JARGON DICTIONARY & GLOSSARY */}
            {(selectedDrawerTab === 'glossary' || searchQuery) && (
              <div className="space-y-4 animate-fadeIn">
                {/* Category Chips */}
                {!searchQuery && (
                  <div className="flex items-center gap-1.5 overflow-x-auto pb-1 custom-scrollbar">
                    {categories.map((cat) => (
                      <button
                        key={cat}
                        onClick={() => setSelectedCategory(cat)}
                        className={`px-2.5 py-1 rounded-lg text-[10px] font-mono whitespace-nowrap transition-all ${
                          selectedCategory === cat
                            ? 'bg-cyan-500 text-gray-950 font-bold shadow-sm'
                            : 'bg-gray-900 hover:bg-gray-800 text-gray-400 border border-gray-800'
                        }`}
                      >
                        {cat}
                      </button>
                    ))}
                  </div>
                )}

                {/* Terms List */}
                <div className="space-y-3">
                  {filteredGlossary.map((item) => {
                    const isExpanded = selectedTermKey === item.key;
                    return (
                      <div 
                        key={item.key}
                        className={`bg-gray-900/80 border rounded-xl p-4 transition-all ${
                          isExpanded ? 'border-cyan-500/60 bg-gray-900 shadow-lg' : 'border-gray-800 hover:border-gray-700'
                        }`}
                      >
                        <div 
                          onClick={() => setSelectedTermKey(isExpanded ? null : item.key)}
                          className="flex items-start justify-between cursor-pointer"
                        >
                          <div className="space-y-1">
                            <div className="flex items-center space-x-2">
                              <h4 className="text-xs font-bold text-white group-hover:text-cyan-300 font-mono">
                                {item.term}
                              </h4>
                              {item.acronym && (
                                <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-gray-800 text-cyan-400 border border-gray-700">
                                  {item.acronym}
                                </span>
                              )}
                            </div>
                            <p className="text-xs text-gray-400 leading-relaxed font-normal">
                              {item.short_def}
                            </p>
                          </div>
                          <span className="text-[10px] text-cyan-400 font-mono ml-2 mt-0.5 flex-shrink-0">
                            {isExpanded ? 'Collapse ▲' : 'Details ▼'}
                          </span>
                        </div>

                        {/* Expanded Full Playbook & Math */}
                        {isExpanded && (
                          <div className="mt-3 pt-3 border-t border-gray-800/80 space-y-3 text-xs animate-fadeIn">
                            {/* Formula */}
                            {item.formula && (
                              <div className="bg-gray-950 p-2.5 rounded-lg border border-gray-800 font-mono text-[11px] text-cyan-300">
                                <span className="text-[9px] uppercase font-sans font-bold text-gray-500 block mb-1">
                                  Mathematical Formula / Calculation:
                                </span>
                                <code>{item.formula}</code>
                              </div>
                            )}

                            {/* Institutional Importance */}
                            {item.importance && (
                              <div>
                                <span className="text-gray-400 font-semibold block text-[11px] mb-0.5">Institutional Edge:</span>
                                <p className="text-gray-300 leading-relaxed">{item.importance}</p>
                              </div>
                            )}

                            {/* Actionable Playbook */}
                            {item.playbook && (
                              <div className="p-2.5 rounded-lg bg-cyan-950/30 border border-cyan-800/50 space-y-1 text-cyan-200">
                                <span className="font-bold text-cyan-300 block text-[11px]">How to Trade It:</span>
                                <p className="whitespace-pre-line leading-relaxed text-[11px]">{item.playbook}</p>
                              </div>
                            )}

                            {/* Concrete Example */}
                            {item.example && (
                              <div className="p-2.5 rounded-lg bg-emerald-950/20 border border-emerald-500/30 space-y-1 text-gray-300">
                                <span className="font-bold text-emerald-400 block text-[11px]">Practical Market Example:</span>
                                <p className="leading-relaxed text-[11px]">{item.example}</p>
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    );
                  })}

                  {filteredGlossary.length === 0 && (
                    <div className="text-center py-10 text-gray-500 text-xs">
                      No jargon terms matched "{searchQuery}". Try searching for POC, AVWAP, EV/R, or Kelly.
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* TAB 3: 12 STRATEGIES MASTER PLAYBOOK */}
            {selectedDrawerTab === 'strategies' && !searchQuery && (
              <div className="space-y-4 animate-fadeIn">
                <div className="p-3 bg-gray-950 border border-gray-800 rounded-xl text-xs text-gray-400">
                  Detailed execution checklists, empirical win rates, and holding periods for all 12 quantitative models.
                </div>

                <div className="space-y-3">
                  {filteredStrategies.map((strat) => (
                    <div key={strat.id} className="bg-gray-900/80 border border-gray-800 rounded-xl p-4 space-y-3">
                      <div className="flex items-start justify-between border-b border-gray-800 pb-2">
                        <div>
                          <h4 className="text-sm font-bold text-white">{strat.name}</h4>
                          <span className="text-[10px] text-cyan-400 font-mono uppercase">{strat.category}</span>
                        </div>
                        <div className="text-right">
                          <span className="text-xs font-mono font-bold text-emerald-400 block">{strat.win_rate}</span>
                          <span className="text-[10px] text-gray-500 font-mono">{strat.holding}</span>
                        </div>
                      </div>

                      <p className="text-xs text-gray-300 leading-relaxed font-normal">
                        {strat.summary}
                      </p>

                      <div className="space-y-1.5 text-xs bg-gray-950/80 p-3 rounded-lg border border-gray-800">
                        <div>
                          <strong className="text-emerald-400 text-[11px]">Entry Rule: </strong>
                          <span className="text-gray-300">{strat.entry_rule}</span>
                        </div>
                        <div>
                          <strong className="text-red-400 text-[11px]">Stop Loss: </strong>
                          <span className="text-gray-300">{strat.stop_rule}</span>
                        </div>
                        <div>
                          <strong className="text-cyan-400 text-[11px]">Profit Target: </strong>
                          <span className="text-gray-300">{strat.target_rule}</span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

          </div>

          {/* Bottom Branding Footer */}
          <div className="p-4 border-t border-gray-800/80 bg-gray-950/90 text-center text-xs text-gray-500 font-mono">
            <span>SwingTradeDeskPro Intelligence • </span>
            <a 
              href="https://www.rupeemap.in" 
              target="_blank" 
              rel="noopener noreferrer"
              className="text-cyan-400 hover:underline"
            >
              rupeemap.in labs
            </a>
            <span> by Sandesh Rathi</span>
          </div>

        </div>
      </div>
    </div>
  );
}
