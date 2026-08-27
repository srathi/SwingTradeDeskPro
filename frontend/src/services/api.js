// Dynamic API Base URL supporting both direct port 8888 and Vite dev port 5173
const getApiBase = () => {
  if (typeof window !== 'undefined') {
    const host = window.location.port === '5173' ? 'localhost:8888' : window.location.host;
    const protocol = window.location.protocol;
    return `${protocol}//${host}/api`;
  }
  return 'http://localhost:8888/api';
};

const API_BASE = getApiBase();

export async function searchStocks(query) {
  if (!query || query.trim().length === 0) return [];
  try {
    const res = await fetch(`${API_BASE}/search?q=${encodeURIComponent(query.trim())}&limit=8`);
    if (!res.ok) return [];
    const data = await res.json();
    return data.results || [];
  } catch (e) {
    return [];
  }
}

export async function fetchUniverses() {
  const res = await fetch(`${API_BASE}/screener/universes`);
  if (!res.ok) throw new Error("Failed to load universes");
  return res.json();
}

export async function fetchStrategies() {
  const res = await fetch(`${API_BASE}/screener/strategies`);
  if (!res.ok) throw new Error("Failed to load strategies");
  return res.json();
}

export async function runScanSync(payload) {
  const res = await fetch(`${API_BASE}/screener/scan`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  if (!res.ok) throw new Error("Scan request failed");
  return res.json();
}

export async function fetchChartData(ticker, period = "1y", strategyId = "trend_pullback") {
  const res = await fetch(`${API_BASE}/chart/${encodeURIComponent(ticker)}?period=${period}&strategy_id=${strategyId}`);
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Failed to load chart data");
  }
  return res.json();
}

export async function runBacktest(payload) {
  const res = await fetch(`${API_BASE}/backtest/run`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Failed to run backtest");
  }
  return res.json();
}

export async function calculateRisk(payload) {
  const res = await fetch(`${API_BASE}/risk/calculate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  if (!res.ok) throw new Error("Risk calculation failed");
  return res.json();
}

export async function fetchWatchlists() {
  const res = await fetch(`${API_BASE}/watchlists`);
  if (!res.ok) throw new Error("Failed to load watchlists");
  return res.json();
}

export async function createWatchlist(name, tickers) {
  const res = await fetch(`${API_BASE}/watchlists`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, tickers })
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Failed to create watchlist");
  }
  return res.json();
}

export async function updateWatchlist(id, tickers, name = null) {
  const res = await fetch(`${API_BASE}/watchlists/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, tickers })
  });
  if (!res.ok) throw new Error("Failed to update watchlist");
  return res.json();
}

export async function deleteWatchlist(id) {
  const res = await fetch(`${API_BASE}/watchlists/${id}`, { method: "DELETE" });
  if (!res.ok) throw new Error("Failed to delete watchlist");
  return res.json();
}

export async function fetchDeepScan(ticker, period = "2y", capital = 500000, riskPct = 1.0) {
  const res = await fetch(`${API_BASE}/deep-scan/${encodeURIComponent(ticker)}?period=${period}&capital=${capital}&risk_pct=${riskPct}`);
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Failed to run deep scan on '${ticker}'`);
  }
  return res.json();
}

export async function fetchSectorPulse(market = "NSE", period = "2y") {
  const res = await fetch(`${API_BASE}/sectors/pulse?market=${encodeURIComponent(market)}&period=${encodeURIComponent(period)}`);
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Failed to load sector pulse data");
  }
  return res.json();
}

export async function fetchSectorConstituents(sectorTicker) {
  const res = await fetch(`${API_BASE}/sectors/constituents?sector=${encodeURIComponent(sectorTicker)}`);
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Failed to load constituents for ${sectorTicker}`);
  }
  return res.json();
}
