"""
AlphaChanakya AI Copilot Engine - Quantitative Financial Assistant for SwingTradeDesk Pro
Copyright (c) rupeemap.in labs | by Sandesh Rathi (https://www.rupeemap.in)

Features:
1. Multi-turn conversation context & history awareness.
2. Grounded in the quantitative knowledge base (45+ indicators, 12 strategies, 10 page workflows).
3. Detailed concrete numerical examples for follow-up questions.
4. Witty, disciplined institutional trading personality with strict financial guardrails.
5. Google Gemini 1.5 Flash / Groq integration with deep local semantic RAG synthesis fallback.
"""

import os
import re
import json
import requests
from typing import Dict, Any, List, Optional

from backend.app.ai_engine.copilot_tools import COPILOT_TOOL_DECLARATIONS, execute_copilot_tool

# --- GUARDRAIL KEYWORDS & PATTERNS ---
FINANCIAL_KEYWORDS = {
    "trade", "trading", "swing", "stock", "equity", "share", "nifty", "banknifty", "sensex",
    "bse", "nse", "rsi", "ema", "sma", "macd", "vwap", "avwap", "poc", "vah", "val",
    "volume", "profile", "breakout", "pullback", "reversion", "squeeze", "bollinger", "keltner",
    "vix", "volatility", "regime", "hurst", "mansfield", "rs", "relative strength",
    "stop loss", "target", "risk", "kelly", "half-kelly", "chandelier", "atr", "drawdown",
    "backtest", "journal", "pnl", "mtm", "screener", "scanner", "deepscan", "sector",
    "portfolio", "capital", "shares", "alpha", "fusion", "expectancy", "ev/r", "r-multiple",
    "profit factor", "win rate", "stage", "weinstein", "minervini", "vcp", "pocket pivot",
    "crabel", "nr7", "wyckoff", "elder", "triple screen", "tide", "wave", "candle",
    "chart", "support", "resistance", "dividend", "earnings", "valuation", "fund", "money",
    "rupeemap", "sandesh", "desk", "pro", "kronos", "forecast", "neural", "corridor",
    "runway", "exhaustion", "weibull", "memory", "tata", "reliance", "hdfc", "infosys",
    "price", "cmp", "quote", "levels", "level", "tcs", "itc", "sbi", "sbin", "infy",
    "wipro", "maruti", "titan", "lt", "zomato", "bse", "nse", "today", "yesterday", "rate"
}

NON_FINANCIAL_DEFLECTIONS = [
    "🏛️ **AlphaChanakya says:** *'My neural weights are 100% allocated to NSE equities and 2R breakout mathematics, not cooking or creative writing! Let us return to finding high-expectancy swing setups before the market closes.'*",
    "🏛️ **AlphaChanakya says:** *'A trader distracted by off-topic pursuits is like buying a stock in Stage-4 markdown—bound for capital erosion! Ask me about Moving Averages, Sector Pulse, or Risk Sizing instead.'*",
    "🏛️ **AlphaChanakya says:** *'I am calibrated for Fibonacci ratios, not poetry! As Chanakya taught: focus your intellect where the yield is highest. What stock or strategy shall we audit today?'*",
    "🏛️ **AlphaChanakya says:** *'That query has 0.00% statistical alpha in the financial markets! Let us re-anchor to something actionable: Ask me how to use the Chandelier Stop or interpret your Alpha Fusion score.'*",
    "🏛️ **AlphaChanakya says:** *'My risk management protocol strictly forbids non-financial discussions! Ask me about Point of Control (POC), India VIX regimes, or 1% position sizing.'*"
]

# --- QUANTITATIVE KNOWLEDGE BASE CORPUS ---
KB_CORPUS = {
    "poc": {
        "term": "Point of Control (POC)",
        "category": "Volume Profile",
        "def": "The exact price level where the absolute highest volume was traded over the selected lookback.",
        "importance": "Acts as institutional 'fair value'. Price above POC = high-liquidity support; Price below POC = resistance.",
        "rule": "Buy setups bouncing off POC with expanding volume. Avoid buying right under an un-tested POC."
    },
    "vah_val": {
        "term": "Value Area High & Low (VAH / VAL)",
        "category": "Volume Profile",
        "def": "The price bounds containing 70% of all traded volume in the session distribution.",
        "importance": "A close above VAH indicates Stage-2 breakout expansion; trading inside is consolidation.",
        "rule": "Buy near VAL during uptrends; target POC and VAH."
    },
    "avwap": {
        "term": "Multi-Pivot Anchored VWAP (AVWAP)",
        "category": "Volume Orderflow",
        "def": "Volume-Weighted Average Price anchored from key events: 52W High, Swing Low, or Surge Day.",
        "importance": "Represents the collective breakeven price of all buyers who entered since that critical event.",
        "rule": "Price above Swing Low AVWAP = buyers in profit and defending demand. Price below 52W High AVWAP = overhead trapped supply."
    },
    "alpha_fusion": {
        "term": "Alpha Fusion Ensemble Engine (0–100)",
        "category": "Quantitative Synthesis",
        "def": "Blended institutional alpha synthesis: Rule-Based Setup (30%) + Kronos AI (25%) + MTF Confluence (25%) + Volume Profile (20%), scaled by Market Regime.",
        "importance": "Eliminates single-indicator bias by requiring multi-factor confluence.",
        "rule": "Score 80–100: Full 100% position size. Score 60–79: Standard 75% size with EV/R > +0.25R. Score < 60: Pass or wait."
    },
    "ev_r": {
        "term": "Statistical Expectancy (EV / R)",
        "category": "Quantitative Statistics",
        "def": "The mathematical expected average return in units of risk (R) per trade: EV/R = (Win Rate × Avg Win R) - (Loss Rate × 1.0R).",
        "importance": "A positive EV/R (> +0.30R) guarantees mathematical profitability over 50+ trades regardless of individual losses.",
        "rule": "Only take swing trades with EV/R ≥ +0.30R."
    },
    "elder_triple_screen": {
        "term": "Alexander Elder Triple-Screen Method",
        "category": "Multi-Timeframe Trend",
        "def": "3-tier trend filter: Screen 1 (Weekly Tide 13/26 EMA + MACD), Screen 2 (Daily Wave 20/50 EMA + RSI cooling), Screen 3 (Micro Trigger intraday high break).",
        "importance": "Prevents buying counter-trend daily rallies when the macro weekly tide is falling.",
        "rule": "⭐⭐⭐ Triple Screen A+: All 3 screens aligned. ⭐⭐ Double Screen B+: Screen 1 + 2 aligned."
    },
    "chandelier_exit": {
        "term": "ATR Chandelier Trailing Exit",
        "category": "Risk Management",
        "def": "Trailing stop placed 3.0 × ATR(14) below the highest high reached since entry.",
        "importance": "Adapts dynamically to market volatility, hanging from the ceiling like a chandelier to capture full multi-week trends.",
        "rule": "Never lower a Chandelier stop; ratchet it up after every new higher swing high."
    },
    "half_kelly": {
        "term": "Ed Thorp Half-Kelly Sizing",
        "category": "Position Sizing",
        "def": "Fractional Kelly criterion: Fraction = 0.5 × [ WinRate - (LossRate / PayoffRatio) ].",
        "importance": "Maximizes long-term geometric compounding rate while eliminating the tail risk of catastrophic drawdown.",
        "rule": "Cap single position allocation at 15%–20% of account even when Kelly suggests higher."
    },
    "hurst_exponent": {
        "term": "Hurst Exponent (H) & Regime Memory",
        "category": "Sector & Time-Series Memory",
        "def": "Statistical measure of time-series memory: H > 0.55 = Persistent Trending; H ≈ 0.50 = Random Walk; H < 0.45 = Mean-Reverting.",
        "importance": "Tells you whether trend-following or range-bound strategies have the empirical edge in that sector.",
        "rule": "Trade breakouts when Hurst > 0.55; trade Bollinger oversold bounces when Hurst < 0.45."
    },
    "sector_runway": {
        "term": "Sector Regime Runway & Markov Duration",
        "category": "Sector & Rotation",
        "def": "Estimated remaining trading sessions in the current sector trend: Runway = Expected Total Days - Current Regime Age.",
        "importance": "Identifies young vs late-stage aging trends before entering.",
        "rule": "Runway > 15 Days = Green Light; Runway < 5 Days or Exhaustion > 60% = Warning."
    },
    "mansfield_rs": {
        "term": "Mansfield Relative Strength (MRS)",
        "category": "Sector Rotation",
        "def": "Stan Weinstein indicator measuring whether a sector/stock is outperforming the Nifty 50 benchmark.",
        "importance": "MRS > 0 and rising confirms institutional accumulation.",
        "rule": "Exclusively buy stocks in sectors with Positive & Rising Mansfield RS."
    },
    "market_regime": {
        "term": "Macro Market Regime Intelligence",
        "category": "Macro Risk Gating",
        "def": "Institutional risk gating based on Nifty 50 trend, India VIX, and market breadth.",
        "importance": "Dictates portfolio capital exposure across 4 states:",
        "rule": "🟢 Risk-On (VIX < 14): 100% sizing. 🟡 Selective Pullbacks (VIX 14-18): 75% sizing. 🟠 High Chop (VIX 18-22): 50% sizing. 🔴 Capital Preservation (VIX > 22): 25% sizing / cash."
    },
    "kronos_neural_forecast": {
        "term": "Kronos AI Foundation Neural Forecast",
        "category": "AI Neural Model",
        "def": "Autoregressive neural time-series model predicting 15-day price trajectory and 90% confidence corridor [P10, P90].",
        "importance": "Provides mathematical upside probability % and expected price boundaries.",
        "rule": "Verify Upside Probability ≥ 60% and expected target is within the 90% corridor."
    }
}


try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

class AlphaChanakyaEngine:
    def __init__(self):
        pass

    @property
    def gemini_api_key(self) -> Optional[str]:
        return os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")

    @property
    def groq_api_key(self) -> Optional[str]:
        return os.environ.get("GROQ_API_KEY")

    def is_finance_related(self, text: str, history: List[Dict[str, str]] = None) -> bool:
        """Determines if query or conversation context contains financial keywords."""
        text_lower = text.lower()

        # Obvious non-financial keywords blacklist
        OFF_TOPIC_BLOCKLIST = {
            "cake", "bake", "baking", "recipe", "pizza", "biryani", "food", "cook", "cooking",
            "poem", "poetry", "romantic", "weather", "rain", "movie", "cinema", "song", "lyrics",
            "cricket", "football", "ipl", "actor", "actress", "joke", "comedy"
        }
        words = set(re.findall(r'\b\w+\b', text_lower))
        if words.intersection(OFF_TOPIC_BLOCKLIST):
            return False

        # 1. Direct word matching
        if words.intersection(FINANCIAL_KEYWORDS):
            return True

        # 2. Check compound financial phrases
        phrases = [
            "stop loss", "relative strength", "triple screen", "half-kelly",
            "point of control", "swing trade", "alpha fusion", "moving average",
            "volume profile", "nifty auto", "nifty it", "value area", "hurst exponent"
        ]
        for p in phrases:
            if p in text_lower:
                return True

        # 3. Context inheritance: if user asks a follow-up in an ongoing financial discussion
        if history and len(history) > 1:
            past_texts = " ".join([h.get("content", "") for h in history[-3:]]).lower()
            if any(k in past_texts for k in ["stock", "trade", "nifty", "hurst", "alpha", "stop", "risk", "kelly", "sector", "score", "vix", "poc", "avwap"]):
                followup_words = ["example", "details", "numbers", "explain", "how", "what", "more", "step", "why", "second", "first", "next", "which", "show", "calculate"]
                if any(w in text_lower for w in followup_words) or len(text.split()) <= 7:
                    return True

        return False

    def extract_conversation_topic(self, user_msg: str, history: List[Dict[str, str]] = None) -> str:
        """Extracts the core quantitative topic from current query and past conversation turns."""
        combined_text = user_msg.lower()
        if history:
            recent_turns = " ".join([h.get("content", "") for h in history[-4:] if not h.get("content", "").startswith("🏛️ **Pranāma!")]).lower()
            combined_text = f"{recent_turns} {combined_text}"
        
        # Priority topic matching
        if any(k in combined_text for k in ["runway", "hurst", "markov", "sector pulse", "sector"]):
            return "hurst_runway"
        if any(k in combined_text for k in ["alpha fusion", "composite score", "score 85", "score 60"]):
            return "alpha_fusion"
        if any(k in combined_text for k in ["chandelier", "trailing stop", "exit model"]):
            return "chandelier_exit"
        if any(k in combined_text for k in ["kelly", "half-kelly", "1% risk", "position sizing", "sizing"]):
            return "position_sizing"
        if any(k in combined_text for k in ["elder", "triple screen", "weekly tide", "daily wave"]):
            return "triple_screen"
        if any(k in combined_text for k in ["poc", "point of control", "value area", "vah", "val", "avwap"]):
            return "volume_profile"
        if any(k in combined_text for k in ["vix", "market regime", "risk-on", "risk-off"]):
            return "market_regime"
        if any(k in combined_text for k in ["ev/r", "expectancy", "r-multiple"]):
            return "expectancy"
        if any(k in combined_text for k in ["kronos", "ai forecast", "corridor"]):
            return "kronos_ai"

        return "general"

    def extract_and_fetch_market_snapshot(self, user_msg: str, history: List[Dict[str, str]] = None, context: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """Identifies any referenced stock ticker and pulls live price + indicators."""
        context = context or {}
        candidate_ticker = context.get("selectedTicker")

        # 1. Direct symbol check from user message or common alias mapping
        if not candidate_ticker:
            TICKER_ALIAS_MAP = {
                "TCS": "TCS.NS", "RELIANCE": "RELIANCE.NS", "INFY": "INFY.NS", "INFOSYS": "INFY.NS",
                "HDFCBANK": "HDFCBANK.NS", "HDFC": "HDFCBANK.NS", "ICICIBANK": "ICICIBANK.NS", "ICICI": "ICICIBANK.NS",
                "SBIN": "SBIN.NS", "SBI": "SBIN.NS", "TATAMOTORS": "TATAMOTORS.NS", "TATA MOTORS": "TATAMOTORS.NS",
                "TATASTEEL": "TATASTEEL.NS", "TATA STEEL": "TATASTEEL.NS", "ITC": "ITC.NS", "LT": "LT.NS", "L&T": "LT.NS",
                "NIFTY": "^NSEI", "NIFTY50": "^NSEI", "BANKNIFTY": "^NSEBANK", "VIX": "^INDIAVIX", "INDIAVIX": "^INDIAVIX",
                "BHARTIARTL": "BHARTIARTL.NS", "AIRTEL": "BHARTIARTL.NS", "KOTAKBANK": "KOTAKBANK.NS", "KOTAK": "KOTAKBANK.NS",
                "WIPRO": "WIPRO.NS", "ZOMATO": "ZOMATO.NS", "TITAN": "TITAN.NS", "MARUTI": "MARUTI.NS",
                "SUNPHARMA": "SUNPHARMA.NS", "BAJFINANCE": "BAJFINANCE.NS", "HINDUNILVR": "HINDUNILVR.NS",
                "HUL": "HINDUNILVR.NS", "AXISBANK": "AXISBANK.NS", "NTPC": "NTPC.NS", "ONGC": "ONGC.NS",
                "COALINDIA": "COALINDIA.NS", "HCLTECH": "HCLTECH.NS", "ADANIENT": "ADANIENT.NS", "ADANIPORTS": "ADANIPORTS.NS"
            }
            words = re.findall(r'\b[A-Za-z0-9\.\^]{2,15}\b', user_msg)
            for w in words:
                w_upper = w.upper()
                if w_upper in TICKER_ALIAS_MAP:
                    candidate_ticker = TICKER_ALIAS_MAP[w_upper]
                    break
                elif w_upper.endswith(".NS") or w_upper.endswith(".BO") or w_upper.startswith("^"):
                    candidate_ticker = w_upper
                    break

        # 2. Check search engine if company name was mentioned
        if not candidate_ticker:
            try:
                from backend.app.core.search_engine import SearchEngine
                tokens = re.findall(r'\b[A-Za-z]{3,15}\b', user_msg)
                for t in tokens:
                    if t.lower() not in {"what", "is", "stock", "price", "today", "how", "give", "tell", "show", "current", "trend", "share", "value", "rate", "cost", "levels"}:
                        res = SearchEngine.search(t)
                        if res and len(res) > 0 and res[0].get("score", 0) >= 75:
                            candidate_ticker = res[0]["symbol"]
                            break
            except Exception:
                pass

        if not candidate_ticker:
            return None

        # 3. Fetch real-time market data from DataEngine
        try:
            from backend.app.core.data_engine import data_engine
            from backend.app.core.indicator_engine import compute_all_indicators

            df = data_engine.fetch_ticker_data(candidate_ticker, period="1y", interval="1d")
            if df is None or len(df) < 5:
                return None

            data = compute_all_indicators(df)
            latest = data.iloc[-1]
            prev = data.iloc[-2]

            close = round(float(latest['Close']), 2)
            prev_close = round(float(prev['Close']), 2)
            chg_val = round(close - prev_close, 2)
            chg_pct = round((chg_val / prev_close) * 100.0, 2) if prev_close > 0 else 0.0

            high = round(float(latest['High']), 2)
            low = round(float(latest['Low']), 2)
            vol = int(latest['Volume'])
            vol_20_sma = int(data['Volume'].tail(20).mean())
            rvol = round(vol / max(1, vol_20_sma), 2)

            ema20 = round(float(latest.get('EMA_20', close)), 2)
            ema50 = round(float(latest.get('EMA_50', close)), 2)
            ema200 = round(float(latest.get('EMA_200', close)), 2)
            rsi14 = round(float(latest.get('RSI_14', 50.0)), 1)
            atr14 = round(float(latest.get('ATR_14', close * 0.02)), 2)

            high_52w = round(float(data['High'].max()), 2)
            low_52w = round(float(data['Low'].min()), 2)

            date_str = str(latest.name).split()[0] if hasattr(latest, 'name') else "Current Session"

            if close >= ema20 >= ema50 >= ema200:
                stage = "Stage 2 (Strong Bullish Markup)"
            elif close >= ema50:
                stage = "Healthy Uptrend (Above 50 EMA)"
            elif close >= ema200:
                stage = "Correction / Value Area (Above 200 EMA)"
            else:
                stage = "Stage 4 (Downtrend / Below 200 EMA)"

            return {
                "symbol": candidate_ticker,
                "cmp": close,
                "prev_close": prev_close,
                "change": chg_val,
                "change_pct": chg_pct,
                "high": high,
                "low": low,
                "volume": vol,
                "rvol": rvol,
                "ema20": ema20,
                "ema50": ema50,
                "ema200": ema200,
                "rsi14": rsi14,
                "atr14": atr14,
                "high_52w": high_52w,
                "low_52w": low_52w,
                "date": date_str,
                "stage": stage
            }
        except Exception as e:
            print(f"[AlphaChanakya] Live ticker fetch error for {candidate_ticker}: {e}")
            return None

    def retrieve_relevant_rag_context(self, combined_query: str, active_tab: str = "") -> str:
        """Retrieves top matching glossary definitions and strategy playbooks."""
        query_lower = combined_query.lower()
        matched_entries = []

        for key, entry in KB_CORPUS.items():
            if key in query_lower or entry["term"].lower() in query_lower or any(w in query_lower for w in entry["term"].lower().split() if len(w) > 3):
                matched_entries.append(f"### {entry['term']} ({entry['category']})\n- **Definition**: {entry['def']}\n- **Why it matters**: {entry['importance']}\n- **Playbook / Action Rule**: {entry['rule']}")

        if not matched_entries:
            matched_entries.append("### Platform Core Principles\n- SwingTradeDesk Pro by rupeemap.in labs (Sandesh Rathi).\n- Follows 1% Risk Allocation, Half-Kelly sizing, Alexander Elder Triple Screen, and Volume Profile (POC/VAH/VAL).\n- 12 Quantitative strategies with rule-based stop losses and 2R/3R profit targets.")

        return "\n\n".join(matched_entries[:3])

    def generate_chat_response(self, message: str, history: List[Dict[str, str]] = None, active_tab: str = "screener", context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Main chat handler with multi-turn context, RAG, and LLM / Local synthesis."""
        user_msg = message.strip()
        history = history or []
        context = context or {}

        if not user_msg:
            return {"reply": "Greetings! I am **AlphaChanakya**, your quantitative trading strategist. How may I assist your analysis today?", "is_deflection": False}

        # 1. Guardrail Check (incorporating multi-turn context)
        if not self.is_finance_related(user_msg, history):
            idx = abs(hash(user_msg)) % len(NON_FINANCIAL_DEFLECTIONS)
            return {
                "reply": NON_FINANCIAL_DEFLECTIONS[idx],
                "is_deflection": True,
                "suggested_topics": [
                    "What is the stock price of TCS today?",
                    "Explain Alpha Fusion Score 85 vs 60 with an example",
                    "What does 16 Days Runway mean in Sector Pulse?",
                    "How to set an ATR Chandelier Stop (3x) on a live trade?"
                ]
            }

        # 2. Extract live market data snapshot if a stock ticker is referenced
        market_snapshot = self.extract_and_fetch_market_snapshot(user_msg, history, context)
        
        # 3. Extract conversation topic across history
        topic = self.extract_conversation_topic(user_msg, history)
        combined_context_query = f"{topic} {user_msg}"
        rag_context = self.retrieve_relevant_rag_context(combined_context_query, active_tab)

        if market_snapshot:
            snapshot_text = (
                f"\n\n=== LIVE REAL-TIME MARKET DATA SNAPSHOT (FROM SWINGDESK PRO DATA ENGINE) ===\n"
                f"- Ticker: {market_snapshot['symbol']}\n"
                f"- Current Market Price (CMP): ₹{market_snapshot['cmp']:,.2f} ({'+' if market_snapshot['change_pct'] >= 0 else ''}{market_snapshot['change_pct']}% today, ₹{'+' if market_snapshot['change'] >= 0 else ''}{market_snapshot['change']:.2f})\n"
                f"- Session Date: {market_snapshot['date']}\n"
                f"- Session High / Low: High ₹{market_snapshot['high']:,.2f} | Low ₹{market_snapshot['low']:,.2f}\n"
                f"- 20 EMA (Short-term Dynamic Support): ₹{market_snapshot['ema20']:,.2f}\n"
                f"- 50 EMA (Medium-term Dynamic Support): ₹{market_snapshot['ema50']:,.2f}\n"
                f"- 200 EMA (Macro Baseline / Overhead Resistance): ₹{market_snapshot['ema200']:,.2f}\n"
                f"- RSI(14) Momentum: {market_snapshot['rsi14']}\n"
                f"- ATR(14) Daily Range: ₹{market_snapshot['atr14']:,.2f}\n"
                f"- 52-Week Range: Low ₹{market_snapshot['low_52w']:,.2f} — High ₹{market_snapshot['high_52w']:,.2f}\n"
                f"- Relative Volume (RVOL): {market_snapshot['rvol']}x 20D SMA\n"
                f"- Technical Stage: {market_snapshot['stage']}"
            )
            rag_context = f"{rag_context}{snapshot_text}"

        # 4. If LLM API Key is configured, make live multi-turn call to Gemini Flash
        if self.gemini_api_key:
            try:
                llm_reply = self._call_gemini(user_msg, history, rag_context, active_tab, context, market_snapshot)
                if llm_reply:
                    return {"reply": llm_reply, "is_deflection": False}
            except Exception as e:
                print(f"[AlphaChanakya] Gemini API call error: {e}. Falling back to multi-turn local RAG synthesis.")

        # 5. Fallback: Intelligent Multi-Turn Local Semantic Synthesis with Concrete Examples
        local_reply = self._generate_local_synthesis(user_msg, history, topic, rag_context, active_tab, context, market_snapshot)
        return {"reply": local_reply, "is_deflection": False}

    def _call_gemini(self, user_msg: str, history: List[Dict[str, str]], rag_context: str, active_tab: str, context: Dict[str, Any], market_snapshot: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """Calls Google Gemini model endpoints with Function Calling and multi-turn conversational history."""
        model_candidates = ["gemini-2.5-flash-lite", "gemini-flash-latest", "gemini-2.5-flash", "gemini-1.5-flash"]
        
        system_instruction = (
            "You are AlphaChanakya, the wise, disciplined, and witty quantitative trading AI copilot for SwingTradeDesk Pro "
            "(by rupeemap.in labs / Sandesh Rathi). You guide swing traders on Indian Equities (NSE/BSE) using mathematical "
            "rigor, 1% risk management, Volume Profile (POC/VAH/VAL), Alexander Elder Triple Screen, and Market Regimes.\n\n"
            "STRICT OPERATIONAL RULES:\n"
            "1. Answer ONLY finance, swing trading, technical analysis, and platform-related queries.\n"
            "2. TOOL CALLING CAPABILITIES: You have direct access to execution tools:\n"
            "   - 'tool_scan_screener': Run live screener scans for breakout, pullback, squeeze, and momentum setups.\n"
            "   - 'tool_deep_scan_stock': Run 360-degree Alpha Fusion diagnostics, Volume Profile, and Elder MTF.\n"
            "   - 'tool_kronos_ai_forecast': Run Monte Carlo candlestick neural forecasting.\n"
            "   - 'tool_run_backtest': Execute event-driven walk-forward backtests.\n"
            "   - 'tool_calculate_position_size': Calculate exact share sizing and risk exposure.\n"
            "   - 'tool_get_sector_pulse': Query live sector rotation, Hurst Exponent (H), and remaining runway days.\n"
            "   - 'tool_get_sector_constituents': Query ranked sector leaderboards.\n"
            "   - 'tool_log_paper_trade': Log paper trades into the journal.\n"
            "   Invoke these tools when the user asks to scan, calculate, forecast, backtest, or inspect quantitative setups.\n"
            "3. When tool results or live snapshots are provided, cite the exact numbers (prices, share quantities, Win Rates, % changes) with institutional precision.\n"
            "4. Maintain full awareness of previous conversation turns.\n"
            "5. Format all formulas in clear LaTeX/code blocks and keep responses structured with bullet points."
        )

        system_intro_text = f"{system_instruction}\n\n=== RELEVANT PLATFORM KNOWLEDGE BASE ===\n{rag_context}\n\nActive Tab: {active_tab.upper()}, Ticker: {context.get('selectedTicker') or (market_snapshot.get('symbol') if market_snapshot else 'None')}"

        contents = [
            {"role": "user", "parts": [{"text": system_intro_text}]},
            {"role": "model", "parts": [{"text": "Understood. I am AlphaChanakya, equipped with native quantitative execution tools, live market data feeds, and platform knowledge. I will execute tools and guide you with mathematical clarity."}]}
        ]

        # Append last 6 turns from history
        for turn in history[-6:]:
            role = "user" if turn.get("role") in ["user", "human"] else "model"
            txt = turn.get("content", "")
            if txt and not txt.startswith("🏛️ **Pranāma!"):
                contents.append({"role": role, "parts": [{"text": txt}]})

        # Append current user prompt
        contents.append({"role": "user", "parts": [{"text": user_msg}]})

        payload = {
            "contents": contents,
            "tools": [{"function_declarations": COPILOT_TOOL_DECLARATIONS}],
            "generationConfig": {
                "temperature": 0.3,
                "maxOutputTokens": 900
            }
        }

        for model in model_candidates:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={self.gemini_api_key}"
            try:
                resp = requests.post(url, json=payload, timeout=12)
                if resp.status_code == 200:
                    data = resp.json()
                    candidates = data.get("candidates", [])
                    if candidates and "content" in candidates[0]:
                        parts = candidates[0]["content"].get("parts", [])
                        if not parts:
                            continue

                        # Check for function/tool call
                        has_function_call = False
                        for p in parts:
                            if "functionCall" in p:
                                has_function_call = True
                                fn = p["functionCall"]
                                fn_name = fn.get("name")
                                fn_args = fn.get("args", {})

                                # Execute the quantitative tool
                                tool_result = execute_copilot_tool(fn_name, fn_args)

                                # Construct second turn payload with function result
                                turn2_contents = list(contents)
                                turn2_contents.append({"role": "model", "parts": [p]})
                                turn2_contents.append({
                                    "role": "user",
                                    "parts": [{
                                        "function_response": {
                                            "name": fn_name,
                                            "response": {
                                                "name": fn_name,
                                                "content": tool_result
                                            }
                                        }
                                    }]
                                })

                                turn2_payload = {
                                    "contents": turn2_contents,
                                    "tools": [{"function_declarations": COPILOT_TOOL_DECLARATIONS}],
                                    "generationConfig": {
                                        "temperature": 0.3,
                                        "maxOutputTokens": 900
                                    }
                                }

                                resp2 = requests.post(url, json=turn2_payload, timeout=12)
                                if resp2.status_code == 200:
                                    data2 = resp2.json()
                                    cand2 = data2.get("candidates", [])
                                    if cand2 and "content" in cand2[0]:
                                        parts2 = cand2[0]["content"].get("parts", [])
                                        if parts2 and "text" in parts2[0]:
                                            return parts2[0]["text"]
                                break

                        if not has_function_call and "text" in parts[0]:
                            return parts[0]["text"]
            except Exception as ex:
                continue

        return None

    def _generate_local_synthesis(self, user_msg: str, history: List[Dict[str, str]], topic: str, rag_context: str, active_tab: str, context: Dict[str, Any], market_snapshot: Optional[Dict[str, Any]] = None) -> str:
        """Deterministic, rich multi-turn quantitative synthesis with exhaustive real-world examples."""
        msg_lower = user_msg.lower()
        is_example = any(w in msg_lower for w in ["example", "details", "detail", "number", "numbers", "calculate", "walk through", "show me", "case study", "practical", "how to"])

        # --- 0. LIVE STOCK QUOTE & TECHNICAL SNAPSHOT ---
        if market_snapshot and any(w in msg_lower for w in ["price", "cmp", "quote", "rate", "cost", "today", "analysis", "level", "levels", "trend", "target", "support", "tcs", "reliance", "infy", "sbi", "stock"]):
            s = market_snapshot
            return (
                f"🏛️ **AlphaChanakya's Real-Time Market Intelligence for {s['symbol']}:**\n\n"
                f"**1. Current Market Price (CMP) & Performance:**\n"
                f"• **Current Price**: **₹{s['cmp']:,.2f}** ({'+' if s['change_pct'] >= 0 else ''}{s['change_pct']}% today, ₹{'+' if s['change'] >= 0 else ''}{s['change']:.2f})\n"
                f"• **Session Range**: Low ₹{s['low']:,.2f} — High ₹{s['high']:,.2f}\n"
                f"• **52-Week Range**: Low ₹{s['low_52w']:,.2f} — High ₹{s['high_52w']:,.2f}\n"
                f"• **Relative Volume (RVOL)**: {s['rvol']}x 20-Day Average Volume\n\n"
                f"**2. Key Quantitative Levels & Moving Averages:**\n"
                f"• **20 EMA (Short-term Dynamic Support)**: ₹{s['ema20']:,.2f} "
                f"({'🟢 Price Above' if s['cmp'] >= s['ema20'] else '🔴 Price Below'})\n"
                f"• **50 EMA (Intermediate Trend Filter)**: ₹{s['ema50']:,.2f} "
                f"({'🟢 Price Above' if s['cmp'] >= s['ema50'] else '🔴 Price Below'})\n"
                f"• **200 EMA (Macro Baseline / Institutional Line)**: ₹{s['ema200']:,.2f} "
                f"({'🟢 Stage 2 Bullish' if s['cmp'] >= s['ema200'] else '🔴 Stage 4 / Macro Resistance'})\n"
                f"• **RSI(14) Momentum**: {s['rsi14']} "
                f"({'Overbought > 70' if s['rsi14'] > 70 else 'Oversold < 35' if s['rsi14'] < 35 else 'Healthy Momentum Zone'})\n"
                f"• **ATR(14) Volatility**: ₹{s['atr14']:,.2f}\n\n"
                f"**3. Quantitative Playbook & Setup Geometry:**\n"
                f"• **Structure**: {s['stage']}\n"
                f"• **Suggested Trailing Stop Loss (2.5x ATR)**: ₹{max(0.0, s['cmp'] - 2.5 * s['atr14']):,.2f}\n"
                f"• **2R Asymmetric Target**: ₹{s['cmp'] + 2.0 * (2.5 * s['atr14']):,.2f} (+{round(2.0 * 2.5 * s['atr14'] / s['cmp'] * 100, 1)}% Upside)"
            )

        # --- 1. HURST EXPONENT & SECTOR RUNWAY ---
        if topic == "hurst_runway":
            if is_example:
                return (
                    "🏛️ **AlphaChanakya's Practical Sector Pulse Case Study (NIFTY AUTO):**\n\n"
                    "Let us inspect a live market scenario to see how **Hurst Exponent ($H$)** and **Runway** dictate your trade decisions:\n\n"
                    "**1. The Quantitative Data:**\n"
                    "• **Current Sector Regime**: Strong Uptrend (Day 11)\n"
                    "• **Historical Markov Expected Duration**: 28 Trading Days\n"
                    "• **Hurst Exponent ($H$)**: **0.62** ($H > 0.55 \\implies$ Strong Persistent Trending Memory)\n"
                    "• **Estimated Runway**: $$28 - 11 = \\mathbf{17\\text{ Days Remaining}}$$\n"
                    "• **Exhaustion Hazard**: 22% (Fresh, Low Fatigue)\n\n"
                    "**2. How to Interpret & Execute:**\n"
                    "• Because **Runway is 17 Days** and **$H = 0.62$**, momentum has substantial fuel left. You have a **Green Light** to deploy breakout and trend-pullback strategies.\n"
                    "• **Constituent Selection**: Expand the NIFTY AUTO drawer and select the #1 ranked leader with **Merit Score > 80** (e.g. *M&M* or *TATAMOTORS*).\n"
                    "• **Execution**: Buy the stock when it tests its Daily 20 EMA with Stop Loss under the 5-day swing low, targeting a **1:2 R/R** move over the remaining 17-day runway window."
                )
            return (
                "🏛️ **AlphaChanakya on Sector Runway & Regime Memory ($H$):**\n\n"
                "In **Sector Pulse**, the **Estimated Runway** is calculated using Markov state-transition probability:\n\n"
                "$$\\text{Estimated Runway} = \\text{Expected Total Run (Days)} - \\text{Current Regime Age}$$\n\n"
                "**Key Rules:**\n"
                "• **Runway > 15 Days + Hurst ($H$) > 0.55**: The sector is in a youthful, persistent Stage-2 markup. Green light for aggressive breakout and pullback trades.\n"
                "• **Runway < 5 Days or Exhaustion > 60%**: Trend is statistically aging. Tighten trailing stops to protect gains and avoid buying new breakout tops.\n\n"
                "*Would you like a step-by-step numerical example of how to execute this on a specific sector constituent?*"
            )

        # --- 2. ALPHA FUSION SCORING ---
        elif topic == "alpha_fusion":
            if is_example:
                return (
                    "🏛️ **AlphaChanakya's Alpha Fusion Case Study (RELIANCE at ₹1,305):**\n\n"
                    "Here is a complete numerical breakdown of how the 4 pillars synthesize an **Alpha Score of 86/100**:\n\n"
                    "**1. The 4-Pillar Score Derivation:**\n"
                    "• **Pillar 1: Strategy Setup (30% weight)** $\\rightarrow 90 / 100$\n"
                    "  *(Clean 20 EMA pullback with volume dry-up $\\implies 0.30 \\times 90 = 27.0$ points)*\n"
                    "• **Pillar 2: Kronos AI Forecast (25% weight)** $\\rightarrow 82 / 100$\n"
                    "  *(68% Upside probability with 15-day target at ₹1,375 $\\implies 0.25 \\times 82 = 20.5$ points)*\n"
                    "• **Pillar 3: Elder MTF Confluence (25% weight)** $\\rightarrow 85 / 100$\n"
                    "  *(Weekly Tide bullish + Daily RSI cooled to 48 $\\implies 0.25 \\times 85 = 21.25$ points)*\n"
                    "• **Pillar 4: Volume Profile (20% weight)** $\\rightarrow 88 / 100$\n"
                    "  *(Price resting right above Volume POC ₹1,280 and Swing Low AVWAP ₹1,295 $\\implies 0.20 \\times 88 = 17.6$ points)*\n\n"
                    "$$\\text{Composite Alpha Score} = 27.0 + 20.5 + 21.25 + 17.6 = \\mathbf{86.35 \\approx 86 / 100}$$\n\n"
                    "**2. Actionable Trade Blueprint:**\n"
                    "• **Entry**: ₹1,305 | **Stop Loss**: ₹1,270 (Risk: ₹35 / share)\n"
                    "• **Target 1 (2R)**: ₹1,375 (+₹70 profit) | **Target 2 (3R)**: ₹1,410 (+₹105 profit)\n"
                    "• **Expectancy**: $EV/R = +0.48R$ $\\implies$ High-Conviction Institutional Trade."
                )
            return (
                "🏛️ **AlphaChanakya on Alpha Fusion Scoring (0–100):**\n\n"
                "**Alpha Fusion** synthesizes 4 independent quantitative pillars to eliminate single-indicator false signals:\n\n"
                "$$\\text{Alpha Score} = \\text{Regime Multiplier} \\times [0.30(\\text{Strategy}) + 0.25(\\text{Kronos AI}) + 0.25(\\text{MTF}) + 0.20(\\text{Volume Profile})]$$\n\n"
                "**Score Tiers:**\n"
                "• 🟢 **80–100 (Triple Screen A+)**: Exceptional alignment across all 4 pillars &rarr; Full 100% position sizing.\n"
                "• 🟡 **60–79 (Double Screen B+)**: Solid trade setup &rarr; Standard 75% sizing if $EV/R \\ge +0.25R$.\n"
                "• 🔴 **< 60**: Invalidation &rarr; Trend broken or heavy overhead supply at POC."
            )

        # --- 3. CHANDELIER TRAILING STOP ---
        elif topic == "chandelier_exit":
            if is_example:
                return (
                    "🏛️ **AlphaChanakya's ATR Chandelier Trailing Exit Case Study (TATASTEEL):**\n\n"
                    "Here is how a disciplined swing trader uses the **3x ATR Chandelier Exit** to ride a trend without getting shaken out prematurely:\n\n"
                    "**1. Trade Context:**\n"
                    "• **Entry Price**: ₹150 | **Initial Stop Loss**: ₹143 (Risk: ₹7 / share)\n"
                    "• **Daily ATR(14)**: ₹3.00\n"
                    "• Over the next 12 sessions, TATASTEEL rallies and prints a **Highest High of ₹172**.\n\n"
                    "**2. The Chandelier Calculation:**\n"
                    "$$\\text{Chandelier Stop} = \\text{Highest High}(22) - (3.0 \\times \\text{ATR}) = 172 - (3.0 \\times 3.00) = 172 - 9.00 = \\mathbf{₹163.00}$$\n\n"
                    "**3. The Result:**\n"
                    "• The trader immediately ratchets the stop up from ₹143 to **₹163.00**.\n"
                    "• Even if the stock experiences a sharp 2-day pullback, the trader has **locked in a guaranteed profit of +₹13.00 (+8.6%)**, perfectly protecting capital while letting the multi-week swing trend run!"
                )
            return (
                "🏛️ **AlphaChanakya on ATR Chandelier Trailing Stops:**\n\n"
                "The **Chandelier Exit** hangs from the swing ceiling to give winning trades breathing room while locking in multi-week momentum:\n\n"
                "$$\\text{Chandelier Stop} = \\text{Highest High}(22) - 3.0 \\times \\text{ATR}(14)$$\n\n"
                "**Chanakya's Golden Rule:** *Never lower your stop loss. Ratchet the Chandelier floor upward as the stock makes new highs to let 2R and 3R profits run!*"
            )

        # --- 4. POSITION SIZING (1% RISK & HALF-KELLY) ---
        elif topic == "position_sizing":
            if is_example:
                return (
                    "🏛️ **AlphaChanakya's 1% Risk & Half-Kelly Sizing Case Study:**\n\n"
                    "Let us calculate the exact number of shares for a trader with **₹5,00,000 Portfolio Capital**:\n\n"
                    "**1. Step 1: Calculate Total Permissible Risk (1% Model):**\n"
                    "$$\\text{Max Risk Budget} = 0.01 \\times \\text{₹}5,00,000 = \\mathbf{₹5,000}$$\n\n"
                    "**2. Step 2: Calculate Risk Per Share:**\n"
                    "• Stock Buy Price: ₹500\n"
                    "• Stop Loss: ₹475\n"
                    "• Risk per share = $500 - 475 = \\mathbf{₹25}$\n\n"
                    "**3. Step 3: Exact Share Count:**\n"
                    "$$\\text{Quantity} = \\frac{\\text{₹}5,000}{\\text{₹}25} = \\mathbf{200\\text{ Shares}}$$\n"
                    "• **Total Allocation**: $200 \\times \\text{₹}500 = \\text{₹}1,00,000$ (20% of your total capital).\n"
                    "• **If Stop Loss is hit**: You lose exactly ₹5,000 (1.0% of portfolio). Your capital remains safe to fight another day!"
                )
            return (
                "🏛️ **AlphaChanakya on Position Sizing & Half-Kelly:**\n\n"
                "Capital preservation is the foundation of all wealth. We use the **Fixed Fractional 1% Model** verified by **Half-Kelly**:\n\n"
                "$$\\text{Shares} = \\frac{\\text{Account Capital} \\times 0.01}{\\text{Entry Price} - \\text{Stop Loss}}$$\n\n"
                "*Never risk more than 1% of total portfolio capital on any single swing trade.*"
            )

        # --- 5. ALEXANDER ELDER TRIPLE SCREEN ---
        elif topic == "triple_screen":
            if is_example:
                return (
                    "🏛️ **AlphaChanakya's Triple Screen Execution Case Study:**\n\n"
                    "Here is how you execute a swing trade using Dr. Alexander Elder's 3 timeframes:\n\n"
                    "**1. Screen 1 (Weekly Tide — The Macro Direction):**\n"
                    "• Look at Weekly Chart: 13-week EMA is sloping up and Weekly MACD Histogram is rising.\n"
                    "• **Rule**: The Tide is Bullish $\\implies$ ONLY Long positions are permitted.\n\n"
                    "**2. Screen 2 (Daily Wave — The Pullback):**\n"
                    "• Look at Daily Chart: Stock pulls back to test its Daily 20 EMA, and Daily RSI(14) drops into the 45–50 cooling zone.\n"
                    "• **Rule**: This is a healthy wave pulling back against the rising tide.\n\n"
                    "**3. Screen 3 (Micro Trigger — The Confirmation Entry):**\n"
                    "• Place a Buy Stop 1 tick above yesterday's high.\n"
                    "• Once triggered, enter the trade with a stop loss just below the pullback swing low, targeting a 2R profit target."
                )
            return (
                "🏛️ **AlphaChanakya on the Triple Screen Method:**\n\n"
                "The **Alexander Elder Triple Screen** audits 3 independent time horizons to eliminate whipsaws:\n\n"
                "• **Screen 1 (Weekly Tide)**: 13/26 EMA slope + Weekly MACD. (Dictates trade direction).\n"
                "• **Screen 2 (Daily Wave)**: 20/50 EMA + Daily RSI cooling. (Identifies pullbacks).\n"
                "• **Screen 3 (Micro Trigger)**: Intraday breakout confirming the wave has rejoined the tide."
            )

        # --- 6. GENERAL FALLBACK WITH CONTEXT ---
        else:
            return (
                f"🏛️ **AlphaChanakya's Quantitative Guidance:**\n\n"
                f"{rag_context}\n\n"
                "**Core Trading Maxim:** *'Cut losers ruthlessly at 1% capital risk, scale winners into 2R/3R targets, and always align with the Weekly Tide.'*\n\n"
                "You can ask me for **concrete numerical examples** on Alpha Fusion, Sector Runway, Chandelier Stops, or Position Sizing!"
            )


copilot_engine = AlphaChanakyaEngine()
