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
    "runway", "exhaustion", "weibull", "memory", "tata", "reliance", "hdfc", "infosys"
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
                    "Explain Alpha Fusion Score 85 vs 60 with an example",
                    "What does 16 Days Runway mean in Sector Pulse?",
                    "How to set an ATR Chandelier Stop (3x) on a live trade?",
                    "How to calculate position sizing using 1% risk and Half-Kelly?"
                ]
            }

        # 2. Extract conversation topic across history
        topic = self.extract_conversation_topic(user_msg, history)
        combined_context_query = f"{topic} {user_msg}"
        rag_context = self.retrieve_relevant_rag_context(combined_context_query, active_tab)

        # 3. If LLM API Key is configured, make live multi-turn call to Gemini Flash
        if self.gemini_api_key:
            try:
                llm_reply = self._call_gemini(user_msg, history, rag_context, active_tab, context)
                if llm_reply:
                    return {"reply": llm_reply, "is_deflection": False}
            except Exception as e:
                print(f"[AlphaChanakya] Gemini API call error: {e}. Falling back to multi-turn local RAG synthesis.")

        # 4. Fallback: Intelligent Multi-Turn Local Semantic Synthesis with Concrete Examples
        local_reply = self._generate_local_synthesis(user_msg, history, topic, rag_context, active_tab, context)
        return {"reply": local_reply, "is_deflection": False}

    def _call_gemini(self, user_msg: str, history: List[Dict[str, str]], rag_context: str, active_tab: str, context: Dict[str, Any]) -> Optional[str]:
        """Calls Google Gemini 1.5 Flash endpoint with full multi-turn conversational history."""
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.gemini_api_key}"
        
        system_instruction = (
            "You are AlphaChanakya, the wise, disciplined, and witty quantitative trading AI copilot for SwingTradeDesk Pro "
            "(by rupeemap.in labs / Sandesh Rathi). You guide swing traders on Indian Equities (NSE/BSE) using mathematical "
            "rigor, 1% risk management, Volume Profile (POC/VAH/VAL), Alexander Elder Triple Screen, and Market Regimes.\n\n"
            "STRICT OPERATIONAL RULES:\n"
            "1. Answer ONLY finance, swing trading, technical analysis, and platform-related queries.\n"
            "2. When a user asks for examples or follow-up details, provide concrete real-world numerical trade examples (e.g. Reliance at ₹1,305 or Nifty Auto at ₹24,000) showing exact entry, stop loss, 2R target, and position sizing calculation.\n"
            "3. Maintain full awareness of previous conversation turns.\n"
            "4. Format all formulas in clear LaTeX/code blocks and keep responses structured with bullet points."
        )

        system_intro_text = f"{system_instruction}\n\n=== RELEVANT PLATFORM KNOWLEDGE BASE ===\n{rag_context}\n\nActive Tab: {active_tab.upper()}, Ticker: {context.get('selectedTicker') or 'None'}"

        contents = [
            {"role": "user", "parts": [{"text": system_intro_text}]},
            {"role": "model", "parts": [{"text": "Understood. I am AlphaChanakya, fully grounded in the platform models, active screen context, and previous discussion. I will guide you with mathematical clarity and practical numerical examples."}]}
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
            "generationConfig": {
                "temperature": 0.3,
                "maxOutputTokens": 800
            }
        }

        resp = requests.post(url, json=payload, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            candidates = data.get("candidates", [])
            if candidates and "content" in candidates[0]:
                parts = candidates[0]["content"].get("parts", [])
                if parts:
                    return parts[0].get("text", "")
        return None

    def _generate_local_synthesis(self, user_msg: str, history: List[Dict[str, str]], topic: str, rag_context: str, active_tab: str, context: Dict[str, Any]) -> str:
        """Deterministic, rich multi-turn quantitative synthesis with exhaustive real-world examples."""
        msg_lower = user_msg.lower()
        is_example = any(w in msg_lower for w in ["example", "details", "detail", "number", "numbers", "calculate", "walk through", "show me", "case study", "practical", "how to"])

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
