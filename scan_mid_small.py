import sys
import time
from tabulate import tabulate
from backend.app.core.index_manager import IndexManager
from backend.app.core.data_engine import data_engine
from backend.app.strategies import STRATEGY_REGISTRY

def run_universe_scan(universe_id: str, label: str):
    print("=" * 95)
    print(f"  🚀 SCANNING: {label.upper()} ({universe_id})")
    print("=" * 95)
    
    start_time = time.time()
    tickers = IndexManager.get_tickers(universe_id)
    print(f"[*] Loaded {len(tickers)} symbols for {universe_id}.")

    batch_df = data_engine.fetch_batch_data(tickers, period="1y", interval="1d", max_workers=25)
    print(f"✓ Data processing complete in {time.time() - start_time:.2f}s ({len(batch_df)} symbols loaded).\n")

    strat_results = {}
    for strat_id, strat in STRATEGY_REGISTRY.items():
        matches = []
        for t in tickers:
            df = batch_df.get(t)
            if df is not None and len(df) >= 60:
                res = strat.evaluate_setup(df, t)
                if res:
                    matches.append(res)
        matches.sort(key=lambda x: x.get("score", 0), reverse=True)
        strat_results[strat.name] = matches

    for strat_name, matches in strat_results.items():
        print(f"  📈 STRATEGY: {strat_name} ({len(matches)} setups)")
        print("-" * 95)
        if matches:
            table_data = []
            for m in matches[:10]: # Top 10 per strategy
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
            headers = ["Symbol", "Score", "CMP", "20 EMA", "RSI", "Stop Loss", "Target 1", "Target 2", "Risk/Share", "Reward 1", "R:R"]
            print(tabulate(table_data, headers=headers, tablefmt="rounded_grid"))
            if len(matches) > 10:
                print(f"  ... and {len(matches) - 10} more setups.")
        else:
            print("  (No setups currently matching criteria)")
        print()

# Run both scans
run_universe_scan("NIFTY_MIDCAP_150", "Nifty Midcap 150 Universe")
run_universe_scan("NIFTY_SMALLCAP_250", "Nifty Smallcap 250 Universe")

