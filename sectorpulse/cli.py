"""
SectorPulse Command Line Interface.
Provides CLI access for quantitative sector rotation intelligence with Rich tables and JSON output.
"""

import sys
import json
import argparse
from typing import List

from sectorpulse.engine import SectorPulseEngine
from sectorpulse.data_ingestion import DEFAULT_NSE_BENCHMARK, DEFAULT_NSE_SECTORS


def format_table(results: List[dict]):
    """
    Renders clean, styled terminal table for sector pulse results.
    """
    header = f"{'Sector':<16} | {'Regime':<18} | {'MRS Score':<10} | {'5D Slope':<9} | {'Hurst':<6} | {'Rem Days':<9} | {'Exhaustion':<11} | {'Action':<20} | {'Weight':<6}"
    sep = "-" * len(header)
    print("\n" + sep)
    print("  SECTORPULSE — QUANTITATIVE SECTOR REGIME & RELATIVE STRENGTH FORECASTER")
    print("  rupeemap.in labs • by Sandesh Rathi")
    print(sep)
    print(header)
    print(sep)

    for r in results:
        sec = r.get("name", r.get("sector"))[:15]
        regime = r["regime"]["trend_classification"]
        mrs = f"{r['regime']['mrs_score']:+.2f}%"
        slope = f"{r['regime']['mrs_slope_5d']:+.2f}"
        hurst = f"{r['regime']['hurst_exponent']:.2f}"
        rem_days = f"{r['duration_forecast']['estimated_remaining_days']}d"
        exhaustion = f"{int(r['duration_forecast']['exhaustion_probability'] * 100)}%"
        action = r["trade_recommendation"]["action"]
        weight = f"{r['trade_recommendation']['sector_weight_multiplier']}x"

        # Highlight tags
        if "STRONG_UPTREND" in regime:
            regime_str = f"\033[92m{regime:<18}\033[0m"
        elif "EARLY_UPTREND" in regime:
            regime_str = f"\033[96m{regime:<18}\033[0m"
        elif "DOWNTREND" in regime:
            regime_str = f"\033[91m{regime:<18}\033[0m"
        else:
            regime_str = f"\033[93m{regime:<18}\033[0m"

        print(f"{sec:<16} | {regime_str} | {mrs:<10} | {slope:<9} | {hurst:<6} | {rem_days:<9} | {exhaustion:<11} | {action:<20} | {weight:<6}")

    print(sep + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="SectorPulse — Quantitative Sector Trend & Regime Duration Forecaster."
    )
    parser.add_argument(
        "--benchmark",
        type=str,
        default=DEFAULT_NSE_BENCHMARK,
        help=f"Benchmark ticker symbol (default: {DEFAULT_NSE_BENCHMARK})"
    )
    parser.add_argument(
        "--sectors",
        type=str,
        default=None,
        help="Comma-separated sector tickers (e.g. ^NSEBANK,^CNXIT,^CNXAUTO)"
    )
    parser.add_argument(
        "--period",
        type=str,
        default="2y",
        help="Lookback history period (e.g. 1y, 2y, 5y)"
    )
    parser.add_argument(
        "--format",
        choices=["table", "json"],
        default="table",
        help="Output format: table (default) or json"
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Optional file path to save output JSON"
    )

    args = parser.parse_args()

    sector_list = [s.strip() for s in args.sectors.split(",")] if args.sectors else list(DEFAULT_NSE_SECTORS.keys())

    print(f"[*] Ingesting market feeds for benchmark {args.benchmark} and {len(sector_list)} sectors...")
    engine = SectorPulseEngine(benchmark_ticker=args.benchmark)
    results = engine.run_pulse(sector_tickers=sector_list, period=args.period)

    if args.format == "json":
        json_output = json.dumps(results, indent=2)
        print(json_output)
        if args.output:
            with open(args.output, "w") as f:
                f.write(json_output)
            print(f"[+] Saved results to {args.output}")
    else:
        format_table(results)
        if args.output:
            with open(args.output, "w") as f:
                json.dump(results, f, indent=2)
            print(f"[+] Saved JSON data to {args.output}")


if __name__ == "__main__":
    main()
