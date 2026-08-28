import React, { useState, useEffect, useRef } from 'react';
import { 
  Bot, 
  Send, 
  X, 
  Trash2, 
  Sparkles, 
  ShieldCheck, 
  MessageSquare, 
  HelpCircle, 
  Check, 
  Copy, 
  ChevronDown, 
  RefreshCw,
  ExternalLink,
  Flame,
  Zap,
  Layers,
  AlertTriangle
} from 'lucide-react';
import { sendCopilotMessage, fetchCopilotStatus } from '../services/api';

export default function AlphaChanakyaDrawer({ activeTab = 'screener', selectedTicker = null }) {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([
    {
      id: 'welcome',
      sender: 'bot',
      text: "🏛️ **Pranāma! I am AlphaChanakya**, your AI quantitative trading strategist for SwingTradeDesk Pro.\n\nAsk me anything about **technical setups, 12 strategies, Volume Profile (POC/VAH/VAL), Sector Pulse runway, or 1% risk management**.\n\n*(Note: I am strictly calibrated for financial markets and swing trading. Distractions will be met with sharp Chanakyan wit!)*",
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }
  ]);
  const [inputVal, setInputVal] = useState('');
  const [loading, setLoading] = useState(false);
  const [statusInfo, setStatusInfo] = useState(null);
  const [copiedId, setCopiedId] = useState(null);

  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Suggested quick prompt chips
  const STARTER_CHIPS = [
    { label: "⚡ Alpha Fusion 85 vs 60", query: "Explain the difference between Alpha Fusion Score 85 and Score 60." },
    { label: "🧭 Sector Pulse Runway", query: "What does Estimated Runway and Hurst Exponent mean in Sector Pulse?" },
    { label: "🛡️ Half-Kelly & 1% Risk", query: "How do I calculate position sizing using the 1% risk model and Half-Kelly?" },
    { label: "🌊 Elder Triple Screen", query: "How do I trade with Alexander Elder Triple Screen methodology?" },
    { label: "🍕 Test Guardrail (Pizza)", query: "Can you give me a recipe for homemade pizza?" }
  ];

  useEffect(() => {
    fetchCopilotStatus()
      .then(data => setStatusInfo(data))
      .catch(() => setStatusInfo({ status: 'ONLINE', provider: 'Quant RAG Engine' }));
  }, []);

  useEffect(() => {
    if (isOpen) {
      setTimeout(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
        inputRef.current?.focus();
      }, 100);
    }
  }, [isOpen, messages]);

  const handleSendMessage = async (textToSend) => {
    const query = (textToSend || inputVal).trim();
    if (!query || loading) return;

    const userMsg = {
      id: `user-${Date.now()}`,
      sender: 'user',
      text: query,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    setMessages(prev => [...prev, userMsg]);
    setInputVal('');
    setLoading(true);

    try {
      const historyPayload = messages.map(m => ({ role: m.sender === 'bot' ? 'assistant' : 'user', content: m.text }));
      const contextPayload = { selectedTicker, activeTab };
      
      const res = await sendCopilotMessage(query, historyPayload, activeTab, contextPayload);
      
      const botMsg = {
        id: `bot-${Date.now()}`,
        sender: 'bot',
        text: res.reply || "Strategy without execution is void. Please restate your query.",
        isDeflection: res.is_deflection || false,
        suggestedTopics: res.suggested_topics || [],
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };

      setMessages(prev => [...prev, botMsg]);
    } catch (err) {
      const errMsg = {
        id: `bot-err-${Date.now()}`,
        sender: 'bot',
        text: `⚠️ **AlphaChanakya encountered an error:** ${err.message || 'Unable to connect to reasoning engine. Please try again.'}`,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      setMessages(prev => [...prev, errMsg]);
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = (id, text) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const clearChat = () => {
    setMessages([
      {
        id: 'welcome-reset',
        sender: 'bot',
        text: "🏛️ **Chat reset.** What stock setup, risk equation, or sector dynamic shall we analyze now?",
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      }
    ]);
  };

  // Helper to format bot markdown text cleanly
  const renderFormattedContent = (text) => {
    // Split into lines for basic markdown rendering
    const lines = text.split('\n');
    return (
      <div className="space-y-1.5 text-xs sm:text-[13px] leading-relaxed">
        {lines.map((line, idx) => {
          if (!line.trim()) return <div key={idx} className="h-1" />;
          
          // Headings
          if (line.startsWith('### ')) {
            return <div key={idx} className="font-bold text-cyan-300 mt-2 text-sm">{line.replace('### ', '')}</div>;
          }
          if (line.startsWith('## ')) {
            return <div key={idx} className="font-bold text-white mt-2 text-sm">{line.replace('## ', '')}</div>;
          }
          
          // Math block
          if (line.startsWith('$$') && line.endsWith('$$')) {
            return (
              <div key={idx} className="my-1.5 p-2 bg-gray-950/90 rounded-lg border border-cyan-500/30 text-cyan-200 font-mono text-[11px] overflow-x-auto shadow-inner text-center">
                {line.replaceAll('$$', '')}
              </div>
            );
          }

          // Bullet points
          if (line.trim().startsWith('• ') || line.trim().startsWith('- ')) {
            const clean = line.trim().replace(/^[•-]\s+/, '');
            return (
              <div key={idx} className="flex items-start gap-1.5 pl-1.5">
                <span className="text-cyan-400 mt-0.5">•</span>
                <span className="text-gray-200">{formatInlineFormatting(clean)}</span>
              </div>
            );
          }

          return <div key={idx} className="text-gray-200">{formatInlineFormatting(line)}</div>;
        })}
      </div>
    );
  };

  const formatInlineFormatting = (str) => {
    // Basic bold and italics parser
    const parts = str.split(/(\*\*.*?\*\*|\*.*?\*|`.*?`)/g);
    return parts.map((part, i) => {
      if (part.startsWith('**') && part.endsWith('**')) {
        return <strong key={i} className="text-cyan-300 font-semibold">{part.slice(2, -2)}</strong>;
      }
      if (part.startsWith('*') && part.endsWith('*')) {
        return <em key={i} className="text-amber-200 italic">{part.slice(1, -1)}</em>;
      }
      if (part.startsWith('`') && part.endsWith('`')) {
        return <code key={i} className="px-1 py-0.5 rounded bg-gray-950 border border-gray-800 text-cyan-400 font-mono text-[11px]">{part.slice(1, -1)}</code>;
      }
      return part;
    });
  };

  return (
    <>
      {/* Floating Trigger Button (Bottom Right) */}
      {!isOpen && (
        <div className="fixed bottom-5 right-5 z-40">
          <button
            onClick={() => setIsOpen(true)}
            className="group relative flex items-center gap-2.5 px-4 py-2.5 rounded-2xl bg-gradient-to-r from-cyan-600 via-blue-600 to-indigo-700 hover:from-cyan-500 hover:to-indigo-600 text-white shadow-2xl shadow-cyan-600/30 border border-cyan-400/40 transition-all duration-200 hover:scale-105 active:scale-95"
            title="Ask AlphaChanakya AI Quantitative Copilot"
          >
            {/* Animated Pulse Ring */}
            <span className="absolute -top-1 -right-1 flex h-3 w-3">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-3 w-3 bg-cyan-400"></span>
            </span>

            <div className="w-6 h-6 rounded-lg bg-black/30 flex items-center justify-center text-amber-300 shadow-inner">
              <Sparkles className="w-3.5 h-3.5" />
            </div>

            <div className="text-left">
              <div className="text-xs font-bold font-sans tracking-tight flex items-center gap-1.5">
                <span>AlphaChanakya</span>
                <span className="text-[10px] px-1 py-0.2 rounded bg-amber-500/20 text-amber-300 border border-amber-500/40 font-mono">
                  AI
                </span>
              </div>
              <div className="text-[10px] text-cyan-200/80 font-mono">
                Quantitative Copilot
              </div>
            </div>
          </button>
        </div>
      )}

      {/* Slide-over / Modal Chat Window */}
      {isOpen && (
        <div className="fixed bottom-4 right-4 z-50 w-[95vw] sm:w-[480px] h-[600px] max-h-[90vh] bg-[#080d1a]/95 backdrop-blur-2xl border border-cyan-500/40 rounded-2xl shadow-2xl flex flex-col overflow-hidden animate-in slide-in-from-bottom-5">
          
          {/* Header Bar */}
          <div className="bg-gradient-to-r from-[#0c1427] via-[#091122] to-[#080d1a] border-b border-gray-800/80 p-3.5 flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-cyan-600/40 to-amber-500/30 border border-cyan-400/50 flex items-center justify-center text-amber-300 shadow-lg shadow-cyan-500/10">
                <Bot className="w-5 h-5" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h3 className="text-sm font-bold text-white">AlphaChanakya AI</h3>
                  <span className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 font-mono font-semibold flex items-center gap-1">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
                    Online
                  </span>
                </div>
                <p className="text-[11px] text-gray-400 font-mono flex items-center gap-1 mt-0.5">
                  <span>{statusInfo?.provider || 'Gemini 1.5 Flash • Quant RAG'}</span>
                  <span>•</span>
                  <span className="text-cyan-400 font-semibold uppercase">{activeTab}</span>
                </p>
              </div>
            </div>

            <div className="flex items-center gap-1.5">
              <button
                onClick={clearChat}
                className="p-1.5 rounded-lg text-gray-400 hover:text-rose-300 hover:bg-rose-500/10 border border-transparent hover:border-rose-500/30 transition-colors"
                title="Clear Chat History"
              >
                <Trash2 className="w-4 h-4" />
              </button>
              <button
                onClick={() => setIsOpen(false)}
                className="p-1.5 rounded-lg text-gray-400 hover:text-white hover:bg-gray-800 transition-colors"
                title="Minimize Copilot"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
          </div>

          {/* Active Context Banner */}
          <div className="bg-gray-950/80 px-3.5 py-1.5 border-b border-gray-900 flex items-center justify-between text-[11px] font-mono text-gray-400">
            <span className="flex items-center gap-1">
              <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
              Grounded in 12 Strategies & Knowledge Base
            </span>
            <span className="text-gray-500">
              by <a href="https://www.rupeemap.in" target="_blank" rel="noopener noreferrer" className="text-cyan-400 hover:underline">rupeemap.in</a>
            </span>
          </div>

          {/* Messages Stream Container */}
          <div className="flex-1 overflow-y-auto p-4 space-y-3.5 scrollbar-thin scrollbar-thumb-gray-800">
            {messages.map((m) => (
              <div
                key={m.id}
                className={`flex flex-col ${m.sender === 'user' ? 'items-end' : 'items-start'}`}
              >
                <div
                  className={`max-w-[90%] rounded-2xl p-3.5 shadow-md relative group transition-all ${
                    m.sender === 'user'
                      ? 'bg-gradient-to-r from-cyan-600 to-blue-600 text-white rounded-br-none border border-cyan-400/30'
                      : m.isDeflection
                      ? 'bg-amber-950/40 border border-amber-500/40 text-amber-100 rounded-bl-none'
                      : 'bg-gray-900/90 border border-gray-800 hover:border-cyan-500/30 text-gray-200 rounded-bl-none'
                  }`}
                >
                  {/* Sender Header */}
                  <div className="flex items-center justify-between mb-1 pb-1 border-b border-white/10 text-[10px] font-mono text-gray-400">
                    <span className="font-semibold text-gray-300">
                      {m.sender === 'user' ? 'You' : '🏛️ AlphaChanakya'}
                    </span>
                    <div className="flex items-center gap-1.5">
                      <span>{m.timestamp}</span>
                      {m.sender === 'bot' && (
                        <button
                          onClick={() => handleCopy(m.id, m.text)}
                          className="opacity-0 group-hover:opacity-100 p-0.5 rounded hover:bg-gray-800 text-gray-400 hover:text-cyan-300 transition-all"
                          title="Copy Answer"
                        >
                          {copiedId === m.id ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
                        </button>
                      )}
                    </div>
                  </div>

                  {/* Message Content */}
                  {m.sender === 'user' ? (
                    <div className="text-xs sm:text-[13px] font-sans leading-relaxed">{m.text}</div>
                  ) : (
                    renderFormattedContent(m.text)
                  )}

                  {/* Suggested Topics if deflected */}
                  {m.suggestedTopics && m.suggestedTopics.length > 0 && (
                    <div className="mt-3 pt-2 border-t border-amber-500/20 space-y-1.5">
                      <div className="text-[10px] text-amber-300 font-mono font-semibold">
                        Suggested Financial Topics:
                      </div>
                      <div className="flex flex-wrap gap-1.5">
                        {m.suggestedTopics.map((topic, tidx) => (
                          <button
                            key={tidx}
                            onClick={() => handleSendMessage(topic)}
                            className="text-[10px] px-2 py-1 rounded bg-amber-500/10 hover:bg-amber-500/20 text-amber-200 border border-amber-500/30 font-mono transition-colors text-left"
                          >
                            ⚡ {topic}
                          </button>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            ))}

            {loading && (
              <div className="flex items-center space-x-2 p-3 bg-gray-900/80 rounded-2xl border border-cyan-500/30 max-w-[80%]">
                <RefreshCw className="w-4 h-4 text-cyan-400 animate-spin" />
                <span className="text-xs font-mono text-cyan-300">AlphaChanakya is calculating quantitative edge...</span>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Quick Starter Chips */}
          <div className="px-3.5 py-2 bg-gray-950/90 border-t border-gray-900 overflow-x-auto flex items-center gap-1.5 scrollbar-none">
            {STARTER_CHIPS.map((chip, idx) => (
              <button
                key={idx}
                onClick={() => handleSendMessage(chip.query)}
                className="whitespace-nowrap text-[10px] px-2.5 py-1 rounded-full bg-gray-900 hover:bg-cyan-500/20 border border-gray-800 hover:border-cyan-500/40 text-gray-300 hover:text-cyan-300 font-mono transition-all flex-shrink-0"
              >
                {chip.label}
              </button>
            ))}
          </div>

          {/* Input Area */}
          <div className="p-3 bg-[#0a0f1d] border-t border-gray-800/80">
            <form
              onSubmit={(e) => {
                e.preventDefault();
                handleSendMessage();
              }}
              className="flex items-center gap-2"
            >
              <input
                ref={inputRef}
                type="text"
                value={inputVal}
                onChange={(e) => setInputVal(e.target.value)}
                placeholder="Ask about setups, POC, Runway, or risk sizing..."
                className="flex-1 bg-gray-950 border border-gray-800 focus:border-cyan-400 rounded-xl px-3.5 py-2 text-xs sm:text-sm text-white placeholder-gray-500 focus:outline-none focus:ring-1 focus:ring-cyan-500 transition-all font-sans"
              />
              <button
                type="submit"
                disabled={!inputVal.trim() || loading}
                className="p-2.5 rounded-xl bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 disabled:opacity-40 text-white font-medium shadow-lg shadow-cyan-600/20 transition-all active:scale-95 flex-shrink-0"
                title="Send query"
              >
                <Send className="w-4 h-4" />
              </button>
            </form>
            <div className="text-[9px] text-gray-500 text-center mt-1.5 font-mono">
              Strictly for educational swing trading & risk management. Not financial advice.
            </div>
          </div>

        </div>
      )}
    </>
  );
}
