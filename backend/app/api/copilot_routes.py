"""
AlphaChanakya AI Copilot API Routes
Copyright (c) rupeemap.in labs | by Sandesh Rathi (https://www.rupeemap.in)
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

from backend.app.ai_engine.copilot_engine import copilot_engine

router = APIRouter(prefix="/api/ai/copilot", tags=["AlphaChanakya Copilot"])


class ChatRequest(BaseModel):
    message: str = Field(..., description="User question or query for AlphaChanakya")
    history: Optional[List[Dict[str, str]]] = Field(default=[], description="Chat conversation history")
    active_tab: Optional[str] = Field(default="screener", description="Current active tab on the client")
    context: Optional[Dict[str, Any]] = Field(default={}, description="Optional contextual payload (e.g. selected stock, regime)")


class ChatResponse(BaseModel):
    reply: str
    is_deflection: bool = False
    suggested_topics: Optional[List[str]] = None


@router.post("/chat", response_model=ChatResponse)
async def chat_with_copilot(req: ChatRequest):
    """
    Primary endpoint for AlphaChanakya AI Copilot.
    Processes user query with RAG context, strict financial guardrails, and Gemini/Local synthesis.
    """
    try:
        res = copilot_engine.generate_chat_response(
            message=req.message,
            history=req.history,
            active_tab=req.active_tab or "screener",
            context=req.context or {}
        )
        return ChatResponse(
            reply=res.get("reply", ""),
            is_deflection=res.get("is_deflection", False),
            suggested_topics=res.get("suggested_topics")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AlphaChanakya Engine error: {str(e)}")


@router.get("/status")
async def get_copilot_status():
    """Returns the operational status and active LLM configuration of AlphaChanakya."""
    has_gemini = bool(copilot_engine.gemini_api_key)
    has_groq = bool(copilot_engine.groq_api_key)
    return {
        "status": "ONLINE",
        "bot_name": "AlphaChanakya",
        "provider": "Google Gemini 1.5 Flash" if has_gemini else "Groq Llama-3" if has_groq else "Local Semantic RAG Engine",
        "has_external_api": has_gemini or has_groq,
        "supported_topics": ["Indian Equities (NSE/BSE)", "12 Quantitative Strategies", "Volume Profile (POC/VAH/VAL)", "Alexander Elder Triple Screen", "Risk Management (Half-Kelly, 1% Model)"]
    }
