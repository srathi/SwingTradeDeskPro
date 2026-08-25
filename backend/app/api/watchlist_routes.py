"""
Watchlist Management API Routes.
"""

import os
import sqlite3
import json
from typing import List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data_cache", "watchlists.db")

router = APIRouter(prefix="/api/watchlists", tags=["Watchlists"])


def _init_watchlist_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS watchlists (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE,
                tickers_json TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # Insert default watchlist if empty
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM watchlists")
        if cursor.fetchone()[0] == 0:
            default_tickers = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "INFY.NS", "TATAMOTORS.NS", "BHARTIARTL.NS"]
            conn.execute(
                "INSERT INTO watchlists (name, tickers_json) VALUES (?, ?)",
                ("Primary Swing Watchlist", json.dumps(default_tickers))
            )
        conn.commit()


_init_watchlist_db()


class WatchlistCreate(BaseModel):
    name: str
    tickers: List[str]


class WatchlistUpdate(BaseModel):
    name: Optional[str] = None
    tickers: List[str]


@router.get("")
def get_watchlists():
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM watchlists ORDER BY id ASC")
        rows = cursor.fetchall()
        return [
            {
                "id": r["id"],
                "name": r["name"],
                "tickers": json.loads(r["tickers_json"]),
                "count": len(json.loads(r["tickers_json"])),
                "created_at": r["created_at"]
            }
            for r in rows
        ]


@router.post("")
def create_watchlist(wl: WatchlistCreate):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO watchlists (name, tickers_json) VALUES (?, ?)",
                (wl.name, json.dumps([t.strip().upper() for t in wl.tickers]))
            )
            conn.commit()
            return {"id": cursor.lastrowid, "name": wl.name, "tickers": wl.tickers}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail=f"Watchlist '{wl.name}' already exists.")


@router.put("/{watchlist_id}")
def update_watchlist(watchlist_id: int, wl: WatchlistUpdate):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        if wl.name:
            cursor.execute(
                "UPDATE watchlists SET name=?, tickers_json=? WHERE id=?",
                (wl.name, json.dumps([t.strip().upper() for t in wl.tickers]), watchlist_id)
            )
        else:
            cursor.execute(
                "UPDATE watchlists SET tickers_json=? WHERE id=?",
                (json.dumps([t.strip().upper() for t in wl.tickers]), watchlist_id)
            )
        conn.commit()
        return {"id": watchlist_id, "tickers": wl.tickers}


@router.delete("/{watchlist_id}")
def delete_watchlist(watchlist_id: int):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("DELETE FROM watchlists WHERE id=?", (watchlist_id,))
        conn.commit()
        return {"status": "deleted", "id": watchlist_id}
