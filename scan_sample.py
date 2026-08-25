import sys
from tabulate import tabulate
from backend.app.core.data_engine import data_engine
from backend.app.strategies import STRATEGY_REGISTRY

# Sample liquid basket of Indian large & mid-cap stocks
TICKERS = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "INFY.NS",
    "BHARTIARTL.NS", "SBIN.NS", "TATAMOTORS.NS", "BAJFINANCE.NS", "LT.NS",
    "TRENT.NS", "BEL.NS", "HAL.NS", "ZOMATO.NS", "VBL.NS", "DLF.NS",
    "CHOLAFIN.NS", "TITAN.NS", "SUNPHARMA.NS", "MARUTI.NS", "AXISBANK.NS",
    "NTPC.NS", "ONGC.NS", "M&M.NS", "TATASTEEL.NS", "COALINDIA.NS",
    "HCLTECH.NS", "KOTAKBANK.NS", "ITC.NS", "HINDUNILVR.NS"
]

print(f"[*] Downloading market data and running quantitative scans on {len(TICKERS)} symbols...\n")

# Fetch batch data (with automatic SQLite disk caching)
batch_df = data_engine.fetch_batch_data(TICKERS, period="1y", interval="1d", max_workers=10)

all_results = []

for strat_id, strat in STRATEGY_REGISTRY.items():
    strat_matches = []
    for ticker in TICKERS:
        df = batch_df.get(ticker)
        if df is not None and len(df) >= 60:
            res = strat.evaluate_setup(df, ticker)
            if res:
                strat_matches.append(res)
    
    strat_matches.sort(key=lambda x: x.get("score", 0), reverse=True)
    all_results.append((strat.name, strat_matches))

# Display formatted tables
found_total = 0
for strat_name, matches in all_results:
    print(f"=========================================================================================")
    print(f"  📊 STRATEGY: {strat_name.upper()} ({len(matches)} setups found)")
    print(f"=========================================================================================")
    if matches:
        found_total += len(matches)
        table_data = []
        for m in matches:
            table_data.append([
                m["ticker"],
                f"Score: {m['score']}/100",
                f"₹{m['close']:.2f}",
                f"₹{m['ema_20']:.2f}",
                f"{m['rsi']}",
                f"₹{m['stop_loss']:.2f}",
                f"₹{m['target_1']:.2f}",
                f"₹{m['target_2']:.2f}",
                f"₹{m['risk_per_share']:.2f} ({m['risk_pct']}%)",
                f"+{m['reward_pct_t1']}%",
                m["rr_ratio"]
            ])
        headers = ["Symbol", "Score", "CMP", "20 EMA", "RSI", "Stop Loss", "Target 1 (2R)", "Target 2 (3R)", "Risk / Share", "Reward 1", "R:R"]
        print(tabulate(table_data, headers=headers, tablefmt="rounded_grid"))
    else:
        print("  (No stocks currently meeting strict entry criteria on latest daily close)")
    print()

print(f"[*] Scan Complete: {found_total} total trade candidates identified across {len(TICKERS)} symbols.")
