"""
Stock Search and Natural Company Name Lookup Routes.
"""

from typing import List, Optional
from fastapi import APIRouter, Query
from backend.app.core.search_engine import SearchEngine

router = APIRouter(prefix="/api/search", tags=["Search"])


@router.get("")
def search_stocks(
    q: str = Query(..., description="Stock symbol or natural company name", min_length=1),
    limit: Optional[int] = Query(8, ge=1, le=20)
):
    """
    Returns fuzzy suggestions matching symbol or company name.
    """
    results = SearchEngine.search(q, limit=limit)
    return {
        "query": q,
        "count": len(results),
        "results": results
    }
