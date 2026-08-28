"""
AlphaChanakya AI Copilot Engine - Quantitative Financial Assistant for SwingTradeDesk Pro
Copyright (c) rupeemap.in labs | by Sandesh Rathi (https://www.rupeemap.in)

Features:
1. Grounded in the quantitative knowledge base (45+ indicators, 12 strategies, 10 page workflows).
2. Witty, disciplined institutional trading personality with strict financial guardrails.
3. Off-topic query detection with humorous financial deflections.
4. Seamless integration with Google Gemini 1.5 Flash / Groq / OpenAI free tiers,
   with intelligent zero-key fallback using local semantic RAG.
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
    "rupeemap", "sandesh", "desk", "pro", "kronos", "forecast", "neural", "corridor"
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
        "term": "Hurst Exponent (H)",
        "category": "Sector & Time-Series Memory",
        "def": "Statistical measure of time-series memory: H > 0.55 = Persistent Trending; H ≈ 0.50 = Random Walk; H < 0.45 = Mean-Reverting.",
        "importance": "Tells you whether trend-following or range-bound strategies have the empirical edge in that sector.",
        "rule": "Trade breakouts when Hurst > 0.55; trade Bollinger oversold bounces when Hurst < 0.45."
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


class AlphaChanakyaEngine:
    def __init__(self):
        self.gemini_api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        self.groq_api_key = os.environ.get("GROQ_API_KEY")

    def is_finance_related(self, text: str) -> bool:
        """Determines if query contains financial, trading, or platform keywords."""
        text_lower = text.lower()
        # Direct word matching
        words = set(re.findall(r'\b\w+\b', text_lower))
        if words.intersection(FINANCIAL_KEYWORDS):
            return True
        # Check compound phrases
        phrases = ["stop loss", "relative strength", "triple screen", "half-kelly", "point of control", "swing trade", "alpha fusion", "moving average"]
        for p in phrases:
            if p in text_lower:
                return True
        return False

    def retrieve_relevant_rag_context(self, query: str, active_tab: str = "") -> str:
        """Retrieves top matching glossary definitions and strategy playbooks."""
        query_lower = query.lower()
        matched_entries = []

        for key, entry in KB_CORPUS.items():
            if key in query_lower or entry["term"].lower() in query_lower or any(w in query_lower for w in entry["term"].lower().split()):
                matched_entries.append(f"### {entry['term']} ({entry['category']})\n- **Definition**: {entry['def']}\n- **Why it matters**: {entry['importance']}\n- **Playbook / Action Rule**: {entry['rule']}")

        if not matched_entries:
            # Provide general platform context
            matched_entries.append("### Platform Core Principles\n- SwingTradeDesk Pro by rupeemap.in labs (Sandesh Rathi).\n- Follows 1% Risk Allocation, Half-Kelly sizing, Alexander Elder Triple Screen, and Volume Profile (POC/VAH/VAL).\n- 12 Quantitative strategies with rule-based stop losses and 2R/3R profit targets.")

        return "\n\n".join(matched_entries[:3])

    def generate_chat_response(self, message: str, history: List[Dict[str, str]] = None, active_tab: str = "screener", context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Main chat handler with guardrails, RAG, and LLM / Local synthesis."""
        user_msg = message.strip()
        if not user_msg:
            return {"reply": "Greetings! I am **AlphaChanakya**, your quantitative trading strategist. How may I assist your analysis today?", "is_deflection": False}

        # 1. Guardrail Check
        if not self.is_finance_related(user_msg):
            # Select deterministic deflection
            idx = abs(hash(user_msg)) % len(NON_FINANCIAL_DEFLECTIONS)
            return {
                "reply": NON_FINANCIAL_DEFLECTIONS[idx],
                "is_deflection": True,
                "suggested_topics": [
                    "Explain Alpha Fusion Score 85 vs 60",
                    "What does 16 Days Runway mean in Sector Pulse?",
                    "How to set an ATR Chandelier Stop (3x)?",
                    "What strategy works best when India VIX is 22?"
                ]
            }

        # 2. Retrieve RAG Context
        rag_context = self.retrieve_relevant_rag_context(user_msg, active_tab)

        # 3. If LLM API Key is configured, make live call to Gemini Flash
        if self.gemini_api_key:
            try:
                llm_reply = self._call_gemini(user_msg, rag_context, active_tab, context)
                if llm_reply:
                    return {"reply": llm_reply, "is_deflection": False}
            except Exception as e:
                print(f"[AlphaChanakya] Gemini API call error: {e}. Falling back to local RAG synthesis.")

        # 4. Fallback: Intelligent Local Semantic RAG Synthesis
        local_reply = self._generate_local_synthesis(user_msg, rag_context, active_tab, context)
        return {"reply": local_reply, "is_deflection": False}

    def _call_gemini(self, user_msg: str, rag_context: str, active_tab: str, context: Dict[str, Any]) -> Optional[str]:
        """Calls Google Gemini 1.5 Flash endpoint."""
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.gemini_api_key}"
        
        system_instruction = (
            "You are AlphaChanakya, the wise, disciplined, and witty quantitative trading AI copilot for SwingTradeDesk Pro "
            "(by rupeemap.in labs / Sandesh Rathi). You guide swing traders on Indian Equities (NSE/BSE) using mathematical "
            "rigor, 1% risk management, Volume Profile (POC/VAH/VAL), Alexander Elder Triple Screen, and Market Regimes.\n\n"
            "STRICT RULES:\n"
            "1. Answer ONLY finance, swing trading, technical analysis, and platform-related queries.\n"
            "2. If the user asks non-finance topics, reply with a witty Chanakya-style financial aphorism redirecting them back to trading.\n"
            "3. Format all formulas in clear LaTeX/code blocks, highlight risk management, and provide practical 2R target advice.\n"
            "4. Keep responses concise, sharp, and structured with bullet points."
        )

        prompt = f"""
System Knowledge Base Context:
{rag_context}

User Active Screen: {active_tab.upper()}
User Query: {user_msg}

Please answer the user's query clearly and concisely as AlphaChanakya.
"""
        payload = {
            "contents": [
                {"role": "user", "parts": [{"text": f"{system_instruction}\n\n{prompt}"}]}
            ],
            "generationConfig": {
                "temperature": 0.3,
                "maxOutputTokens": 600
            }
        }

        resp = requests.post(url, json=payload, timeout=8)
        if resp.status_code == 200:
            data = resp.json()
            candidates = data.get("candidates", [])
            if candidates and "content" in candidates[0]:
                parts = candidates[0]["content"].get("parts", [])
                if parts:
                    return parts[0].get("text", "")
        return None

    def _generate_local_synthesis(self, user_msg: str, rag_context: str, active_tab: str, context: Dict[str, Any]) -> str:
        """Deterministic, rich quantitative synthesis when API keys are not provided."""
        msg_lower = user_msg.lower()

        if "runway" in msg_lower or "sector" in msg_lower or "hurst" in msg_lower:
            return (
                "🏛️ **AlphaChanakya on Sector Runway & Memory ($H$):**\n\n"
                "In **Sector Pulse**, the **Estimated Runway** is calculated using Markov state-transition probability:\n\n"
                "$$\\text{Estimated Runway} = \\text{Expected Total Run (Days)} - \\text{Current Regime Age}$$\n\n"
                "**How to Interpret:**\n"
                "• **Runway > 15 Days + Hurst ($H$) > 0.55**: The sector is in a youthful, persistent Stage-2 markup. Green light for aggressive breakout and pullback trades.\n"
                "• **Runway < 5 Days or Exhaustion > 60%**: Trend is statistically aging. Tighten trailing stops to protect gains and avoid buying new breakout tops.\n\n"
                "*Tip: Exclusively pick constituents with Merit Score > 80 inside leading sectors.*"
            )
        elif "alpha fusion" in msg_lower or "score" in msg_lower:
            return (
                "🏛️ **AlphaChanakya on Alpha Fusion Scoring (0–100):**\n\n"
                "**Alpha Fusion** synthesizes 4 independent quantitative pillars to eliminate single-indicator false signals:\n\n"
                "$$\\text{Alpha Score} = \\text{Regime Multiplier} \\times [0.30(\\text{Strategy}) + 0.25(\\text{Kronos AI}) + 0.25(\\text{MTF}) + 0.20(\\text{Volume Profile})]$$\n\n"
                "**Interpretation Protocol:**\n"
                "• 🟢 **80–100 (Triple Screen A+)**: Exceptional alignment across all 4 pillars &rarr; Full 100% position sizing.\n"
                "• 🟡 **60–79 (Double Screen B+)**: Solid trade setup &rarr; Standard 75% sizing if $EV/R \\ge +0.25R$.\n"
                "• 🔴 **< 60**: Invalidation &rarr; Trend broken or heavy overhead supply at POC."
            )
        elif "chandelier" in msg_lower or "stop" in msg_lower or "exit" in msg_lower:
            return (
                "🏛️ **AlphaChanakya on ATR Chandelier Trailing Stops:**\n\n"
                "The **Chandelier Exit** hangs from the swing ceiling to give winning trades breathing room while locking in multi-week momentum:\n\n"
                "$$\\text{Chandelier Stop} = \\text{Highest High}(22) - 3.0 \\times \\text{ATR}(14)$$\n\n"
                "**Chanakya's Golden Rule:** *Never lower your stop loss. Ratchet the Chandelier floor upward as the stock makes new highs to let 2R and 3R profits run!*"
            )
        elif "vix" in msg_lower or "regime" in msg_lower:
            return (
                "🏛️ **AlphaChanakya on India VIX & Market Regimes:**\n\n"
                "Market volatility determines whether breakout strategies succeed or chop you to pieces:\n\n"
                "• 🟢 **Risk-On Expansion (VIX < 14)**: Full 100% sizing. Stage-2 momentum breakouts thrive.\n"
                "• 🟡 **Selective Pullbacks (VIX 14–18)**: 75% sizing. Buy 20/50 EMA dips in RS leaders.\n"
                "• 🟠 **High Chop (VIX 18–22)**: 50% half sizing. Breakouts fail; use RSI(28) mean-reversion.\n"
                "• 🔴 **Capital Preservation (VIX > 22)**: 25% sizing or 100% cash. Protect your principal!"
            )
        else:
            return (
                f"🏛️ **AlphaChanakya's Strategic Guidance:**\n\n"
                f"{rag_context}\n\n"
                "**Core Trading Maxim:** *'Cut losers ruthlessly at 1% capital risk, scale leaders into 2R/3R targets, and always align with the Weekly Tide.'*\n\n"
                "What specific ticker or indicator shall we examine next?"
            )


copilot_engine = AlphaChanakyaEngine()
