#!/bin/bash

echo "=========================================================="
echo "    🚀 Starting SwingDesk Pro Trading Platform"
echo "=========================================================="

# Check Python version
python3 -c "import fastapi, uvicorn, yfinance, pandas" 2>/dev/null
if [ $? -ne 0 ]; then
  echo "[*] Installing Python backend requirements..."
  pip3 install -r backend/requirements.txt
fi

# Build frontend if dist doesn't exist
if [ ! -d "frontend/dist" ]; then
  echo "[*] Building frontend assets..."
  npm install --prefix frontend
  npm run build --prefix frontend
fi

echo ""
echo "----------------------------------------------------------"
echo "  🌐 Backend & Web Dashboard: http://localhost:8888"
echo "  📊 API Documentation:       http://localhost:8888/docs"
echo "----------------------------------------------------------"
echo "Press Ctrl+C to terminate."
echo ""

# Start FastAPI server on port 8888
python3 -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8888 --reload
