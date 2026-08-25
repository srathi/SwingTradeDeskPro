import sys
import time
from tabulate import tabulate
from backend.app.core.index_manager import IndexManager
from backend.app.core.data_engine import data_engine
from backend.app.strategies import STRATEGY_REGISTRY

print("=========================================================================================")
print("  🚀 FULL NIFTY 500 QUANTITATIVE SWING SCANNER")
print("=========================================================================================")

# 1. Ingest Nifty 500 constituents
start_time = time.time()
tickers = IndexManager.get_tickers("NIFTY_500")
print(f"[*] Loaded {len(tickers)} Nifty 500 symbols from exchange universe feed.")

# 2. Parallel data fetching with SQLite disk caching
print(f"[*] Downloading / loading 1-year daily candles across {len(tickers)} tickers (30 parallel workers)...")
batch_df = data_engine.fetch_batch_data(tickers, period="1y", interval="1d", max_workers=30)
fetch_time = time.time() - start_time
print(f"✓ Data processing completed in {fetch_time:.2f}s ({len(batch_df)} symbols successfully loaded).\n")

# 3. Evaluate each strategy
results_by_strat = {}

for strat_id, strat in STRATEGY_REGISTRY.items():
    matches = []
    for t in tickers:
        df = batch_df.get(t)
        if df is not None and len(df) >= 60:
            res = strat.evaluate_setup(df, t)
            if res:
                matches.append(res)
    
    matches.sort(key=lambda x: x.get("score", 0), reverse=True)
    results_by_strat[strat.name] = matches

# 4. Print results
total_matches = 0
for strat_name, matches in results_by_strat.items():
    print(f"=========================================================================================")
    print(f"  📈 STRATEGY: {strat_name.upper()} ({len(matches)} setups found)")
    print(f"=========================================================================================")
    if matches:
        total_matches += len(matches)
        table_data = []
        # Show top 15 highest scoring setups per strategy if large
        display_matches = matches[:15]
        for m in display_matches:
            table_data.append([
                m["ticker"].replace(".NS", ""),
                f"{m['score']}/100",
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
        headers = ["Symbol", "Score", "CMP", "20 EMA", "RSI", "Stop Loss", "Target 1 (2R)", "Target 2 (3R)", "Risk/Share", "Reward 1", "R:R"]
        print(tabulate(table_data, headers=headers, tablefmt="rounded_grid"))
        if len(matches) > 15:
            print(f"  ... and {len(matches) - 15} more setups available in UI / CSV export.")
    else:
        print("  (No stocks currently meeting strict entry criteria on latest daily close)")
    print()

print(f"[*] Full Nifty 500 Scan Complete: {total_matches} total setups identified in {time.time() - start_time:.2f} seconds.")
