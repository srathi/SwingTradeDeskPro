# Workspace Rules for SwingTrades

1. **Python Program Execution**: Always allow and proactively run Python programs, scripts, tests, and servers for this project without asking for extra confirmation.
2. **Architecture**: Maintain the modular separation between `backend/` (FastAPI, quantitative strategies, backtester, caching) and `frontend/` (React, TradingView charts).
3. **Data Ingestion**: Use `yfinance` via `backend/app/core/data_engine.py` with SQLite disk caching to prevent exchange rate limits.
4. **State Tracking**: Keep `STATE.md` updated with any major architectural additions or configuration changes.
