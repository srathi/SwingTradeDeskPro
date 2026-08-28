// JargonTooltip.jsx - Interactive Micro-Tooltips & Info Cards for SwingTradeDeskPro
// Copyright (c) rupeemap.in labs | by Sandesh Rathi (https://www.rupeemap.in)

import React, { useState, useRef, useEffect } from 'react';
import { HelpCircle, ExternalLink, Sparkles, BookOpen } from 'lucide-react';
import { UNIVERSAL_GLOSSARY } from '../data/knowledgeBase';

export default function JargonTooltip({ 
  termKey, 
  title, 
  definition, 
  formula, 
  children, 
  position = 'top',
  onOpenGuide
}) {
  const [isOpen, setIsOpen] = useState(false);
  const triggerRef = useRef(null);
  const popoverRef = useRef(null);

  const termData = termKey ? UNIVERSAL_GLOSSARY[termKey] : null;
  const displayTitle = title || (termData ? termData.term : 'Quantitative Metric');
  const displayDef = definition || (termData ? termData.short_def : '');
  const displayFormula = formula || (termData ? termData.formula : '');
  const displayPlaybook = termData ? termData.playbook : null;

  // Handle outside click to close
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (
        popoverRef.current && !popoverRef.current.contains(e.target) &&
        triggerRef.current && !triggerRef.current.contains(e.target)
      ) {
        setIsOpen(false);
      }
    };
    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [isOpen]);

  const handleOpenFull = (e) => {
    e.stopPropagation();
    setIsOpen(false);
    if (onOpenGuide) {
      onOpenGuide(termKey);
    } else {
      window.dispatchEvent(new CustomEvent('open-help-drawer', { detail: { term: termKey } }));
    }
  };

  const getPositionClasses = () => {
    switch (position) {
      case 'bottom':
        return 'top-full mt-2 left-1/2 -translate-x-1/2';
      case 'left':
        return 'right-full mr-2 top-1/2 -translate-y-1/2';
      case 'right':
        return 'left-full ml-2 top-1/2 -translate-y-1/2';
      case 'top':
      default:
        return 'bottom-full mb-2 left-1/2 -translate-x-1/2';
    }
  };

  return (
    <span className="relative inline-flex items-center" ref={triggerRef}>
      {children ? (
        <span 
          onClick={() => setIsOpen(!isOpen)}
          onMouseEnter={() => setIsOpen(true)}
          onMouseLeave={() => setIsOpen(false)}
          className="cursor-help border-b border-dotted border-gray-500 hover:border-cyan-400 transition-colors inline-flex items-center gap-1"
        >
          {children}
        </span>
      ) : (
        <button
          type="button"
          onClick={() => setIsOpen(!isOpen)}
          onMouseEnter={() => setIsOpen(true)}
          onMouseLeave={() => setIsOpen(false)}
          className="p-0.5 text-gray-500 hover:text-cyan-400 transition-colors focus:outline-none"
          title={`Learn about ${displayTitle}`}
        >
          <HelpCircle className="w-3.5 h-3.5" />
        </button>
      )}

      {/* Floating Micro-Card Popover */}
      {isOpen && (
        <div 
          ref={popoverRef}
          onMouseEnter={() => setIsOpen(true)}
          onMouseLeave={() => setIsOpen(false)}
          className={`absolute ${getPositionClasses()} z-50 w-72 sm:w-80 p-3.5 bg-gray-950/95 border border-cyan-500/40 rounded-xl shadow-2xl backdrop-blur-md text-left text-xs text-gray-200 transition-all pointer-events-auto select-text`}
          style={{ filter: 'drop-shadow(0 10px 20px rgba(0,0,0,0.7))' }}
        >
          {/* Header */}
          <div className="flex items-center justify-between border-b border-gray-800 pb-1.5 mb-2">
            <div className="flex items-center space-x-1.5">
              <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
              <span className="font-bold text-white tracking-wide">{displayTitle}</span>
            </div>
            {termData?.category && (
              <span className="text-[9px] uppercase font-mono px-1.5 py-0.5 rounded bg-cyan-950 text-cyan-300 border border-cyan-800/80">
                {termData.category}
              </span>
            )}
          </div>

          {/* Definition */}
          {displayDef && (
            <p className="text-gray-300 text-[11px] leading-relaxed mb-2 font-normal">
              {displayDef}
            </p>
          )}

          {/* Math Formula if present */}
          {displayFormula && (
            <div className="bg-gray-900/90 border border-gray-800 rounded-lg p-2 mb-2 font-mono text-[10px] text-cyan-300 overflow-x-auto">
              <span className="text-gray-500 block text-[9px] uppercase tracking-wider mb-0.5 font-sans font-bold">Calculation Formula:</span>
              <code>{displayFormula}</code>
            </div>
          )}

          {/* Footer Action */}
          <div className="pt-1.5 border-t border-gray-800/80 flex items-center justify-between text-[10px]">
            <span className="text-gray-500">Instant Jargon Tooltip</span>
            <button
              onClick={handleOpenFull}
              className="text-cyan-400 hover:text-cyan-300 font-semibold flex items-center space-x-1 transition-colors group"
            >
              <span>Read Full Playbook</span>
              <ExternalLink className="w-3 h-3 group-hover:translate-x-0.5 transition-transform" />
            </button>
          </div>
        </div>
      )}
    </span>
  );
}
