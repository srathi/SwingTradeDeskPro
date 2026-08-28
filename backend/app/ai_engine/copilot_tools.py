"""
AlphaChanakya Quantitative Tool Registry & Execution Dispatcher.
Enables native Gemini LLM Function Calling across all SwingTradeDesk Pro engines.

Copyright (c) rupeemap.in labs | by Sandesh Rathi (https://www.rupeemap.in)
"""

from typing import Dict, Any, List, Optional
import math
import pandas as pd
import numpy as np

# Tool Function Declarations for Google Gemini
COPILOT_TOOL_DECLARATIONS = [
    {
        "name": "tool_scan_screener",
        "description": "Scans official equity universes (NIFTY_50, NIFTY_500, NIFTY_MIDCAP_100, BSE_30, US_MEGA) using quantitative swing strategies (e.g. high_52w_breakout, connors_rsi2, trend_pullback, gmma_breakout, volatility_squeeze, pocket_pivot, wyckoff_spring, nr7_expansion, mean_reversion, relative_strength_leader, vcp_breakout, rsi28_divergence).",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "universe": {
                    "type": "STRING",
                    "description": "Universe identifier: 'NIFTY_50', 'NIFTY_500', 'NIFTY_MIDCAP_100', 'NIFTY_SMALLCAP_100', 'BSE_30', or 'US_MEGA'."
                },
                "strategy_id": {
                    "type": "STRING",
                    "description": "Strategy ID: 'high_52w_breakout', 'connors_rsi2', 'trend_pullback', 'gmma_breakout', 'volatility_squeeze', 'pocket_pivot', 'wyckoff_spring', 'nr7_expansion', 'mean_reversion', 'relative_strength_leader', 'vcp_breakout', 'rsi28_divergence'."
                },
                "min_quality": {
                    "type": "INTEGER",
                    "description": "Minimum quality score filter (0-100), default 60."
                }
            },
            "required": ["universe", "strategy_id"]
        }
    },
    {
        "name": "tool_deep_scan_stock",
        "description": "Performs a 360-degree quantitative diagnostic on a specific stock. Returns 4-pillar Alpha Fusion composite score (0-100), Elder Triple Screen matrix (Weekly Tide + Daily Wave), Volume Profile POC/VAH/VAL, and Multi-Pivot AVWAPs.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "ticker": {
                    "type": "STRING",
                    "description": "Stock symbol, e.g. 'TCS.NS', 'RELIANCE.NS', 'TATAMOTORS.NS', 'SBIN.NS'."
                },
                "period": {
                    "type": "STRING",
                    "description": "Lookback period: '6mo', '1y', '2y', default '1y'."
                },
                "strategy_id": {
                    "type": "STRING",
                    "description": "Optional strategy ID to score against."
                }
            },
            "required": ["ticker"]
        }
    },
    {
        "name": "tool_kronos_ai_forecast",
        "description": "Generates autoregressive tokenized candlestick neural path simulations using Kronos AI (AAAI 2026). Returns upside probability P(Up), 90% confidence price corridor [p10, p90], and volatility amplification risk.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "ticker": {
                    "type": "STRING",
                    "description": "Stock symbol, e.g. 'TCS.NS', 'RELIANCE.NS', 'INFY.NS'."
                },
                "pred_len": {
                    "type": "INTEGER",
                    "description": "Number of future trading days to forecast (5 to 30), default 15."
                },
                "n_paths": {
                    "type": "INTEGER",
                    "description": "Number of parallel Monte Carlo paths (10 to 30), default 20."
                }
            },
            "required": ["ticker"]
        }
    },
    {
        "name": "tool_run_backtest",
        "description": "Runs an event-driven walk-forward backtest for a strategy on a specific ticker, incorporating realistic Indian market transaction costs (STT 0.1%, Brokerage ₹20, GST 18%, Slippage 0.08%). Returns Win Rate %, Profit Factor, Max Drawdown %, Sharpe, and trade log.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "strategy_id": {
                    "type": "STRING",
                    "description": "Strategy ID to backtest: e.g. 'connors_rsi2', 'high_52w_breakout', 'trend_pullback', 'gmma_breakout', 'volatility_squeeze'."
                },
                "ticker": {
                    "type": "STRING",
                    "description": "Stock symbol, e.g. 'TCS.NS', 'RELIANCE.NS', 'HDFCBANK.NS'."
                },
                "period": {
                    "type": "STRING",
                    "description": "Historical test window: '1y', '2y', '3y', default '2y'."
                },
                "capital": {
                    "type": "NUMBER",
                    "description": "Initial account capital in INR, default 500000.0."
                },
                "risk_pct": {
                    "type": "NUMBER",
                    "description": "Risk percentage per trade (e.g. 1.0 for 1%), default 1.0."
                }
            },
            "required": ["strategy_id", "ticker"]
        }
    },
    {
        "name": "tool_calculate_position_size",
        "description": "Calculates exact institutional position sizing based on portfolio capital, risk tolerance %, entry price, and stop loss. Audits Half-Kelly sizing and warns if single-position allocation exceeds 25% capital.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "capital": {
                    "type": "NUMBER",
                    "description": "Total portfolio capital in INR (e.g. 500000.0)."
                },
                "risk_pct": {
                    "type": "NUMBER",
                    "description": "Max account risk percentage (e.g. 1.0 or 1.5)."
                },
                "entry_price": {
                    "type": "NUMBER",
                    "description": "Planned buy entry price in INR."
                },
                "stop_loss": {
                    "type": "NUMBER",
                    "description": "Planned stop loss price in INR."
                },
                "target_price": {
                    "type": "NUMBER",
                    "description": "Optional planned target price in INR."
                }
            },
            "required": ["capital", "risk_pct", "entry_price", "stop_loss"]
        }
    },
    {
        "name": "tool_get_sector_pulse",
        "description": "Analyzes all 11 Indian NSE sectors (Auto, IT, Bank, Pharma, FMCG, Metal, Realty, Energy, Infra, PSU Bank, Media) for Mansfield Relative Strength, Hurst Exponent (H), Markov Regime Age & Estimated Runway (Days Remaining), and Exhaustion Hazard.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "market": {
                    "type": "STRING",
                    "description": "Market identifier: 'NSE' or 'US', default 'NSE'."
                }
            }
        }
    },
    {
        "name": "tool_get_sector_constituents",
        "description": "Returns top liquid constituent stocks for a specific sector ranked descending by Technical Merit Score (10-100), including distance to EMAs, RSI, and active setups.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "sector_name": {
                    "type": "STRING",
                    "description": "Sector name or index symbol: e.g. 'AUTO', 'IT', 'BANK', 'PHARMA', 'METAL', 'FMCG', 'REALTY', 'ENERGY', 'INFRA', 'PSU_BANK'."
                }
            },
            "required": ["sector_name"]
        }
    },
    {
        "name": "tool_log_paper_trade",
        "description": "Logs an active swing trade into the local paper trading journal to track real-time P&L, Win Rate %, and R-Multiples.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "ticker": {
                    "type": "STRING",
                    "description": "Stock symbol, e.g. 'TCS.NS'."
                },
                "entry_price": {
                    "type": "NUMBER",
                    "description": "Execution entry price in INR."
                },
                "stop_loss": {
                    "type": "NUMBER",
                    "description": "Stop loss price in INR."
                },
                "target1": {
                    "type": "NUMBER",
                    "description": "Primary profit target price in INR."
                },
                "quantity": {
                    "type": "INTEGER",
                    "description": "Number of shares."
                },
                "strategy_id": {
                    "type": "STRING",
                    "description": "Strategy setup ID."
                }
            },
            "required": ["ticker", "entry_price", "stop_loss", "target1", "quantity", "strategy_id"]
        }
    }
]


def execute_copilot_tool(tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Executes a declared quantitative tool and returns structured data for LLM synthesis.
    """
    args = args or {}

    try:
        # 1. Screener Scan
        if tool_name == "tool_scan_screener":
            from backend.app.core.index_manager import IndexManager
            from backend.app.core.data_engine import data_engine
            from backend.app.strategies import get_strategy

            universe = args.get("universe", "NIFTY_50")
            strategy_id = args.get("strategy_id", "high_52w_breakout")
            min_quality = int(args.get("min_quality", 60))

            tickers = IndexManager.get_tickers(universe)
            strat = get_strategy(strategy_id)
            batch_df = data_engine.fetch_batch_data(tickers, period="1y", interval="1d", max_workers=10)

            matches = []
            for ticker, df in batch_df.items():
                res = strat.evaluate_setup(df, ticker)
                if res and res.get("score", 0) >= min_quality:
                    matches.append({
                        "symbol": res.get("symbol", ticker),
                        "name": res.get("name", ticker),
                        "cmp": res.get("cmp", res.get("entry")),
                        "entry": res.get("entry"),
                        "stop_loss": res.get("stop_loss"),
                        "target_1": res.get("target_1"),
                        "target_2": res.get("target_2"),
                        "score": res.get("score", 0),
                        "risk_reward": res.get("risk_reward", "1:2"),
                        "setup": res.get("setup_description", "")
                    })

            matches.sort(key=lambda x: x.get("score", 0), reverse=True)
            return {
                "success": True,
                "tool": tool_name,
                "universe": universe,
                "strategy_id": strategy_id,
                "scanned_count": len(tickers),
                "total_matches": len(matches),
                "top_setups": matches[:8]
            }

        # 2. Deep Scan & Alpha Fusion
        elif tool_name == "tool_deep_scan_stock":
            from backend.app.core.alpha_fusion import AlphaFusionEngine
            ticker = args.get("ticker", "RELIANCE.NS").strip().upper()
            if not ticker.endswith(".NS") and not ticker.endswith(".BO") and not ticker.startswith("^"):
                ticker += ".NS"
            period = args.get("period", "1y")
            strategy_id = args.get("strategy_id")

            result = AlphaFusionEngine.evaluate_alpha_fusion(ticker, period=period, strategy_id=strategy_id)
            return {
                "success": True,
                "tool": tool_name,
                "ticker": ticker,
                "composite_alpha_score": result.get("composite_alpha_score"),
                "conviction_tier": result.get("conviction_tier"),
                "pillars": result.get("pillars"),
                "trade_blueprint": result.get("trade_blueprint"),
                "elder_matrix": result.get("elder_matrix"),
                "volume_profile": result.get("volume_profile")
            }

        # 3. Kronos AI Forecast
        elif tool_name == "tool_kronos_ai_forecast":
            from backend.app.ai_engine.kronos_forecaster import kronos_forecaster
            ticker = args.get("ticker", "TCS.NS").strip().upper()
            if not ticker.endswith(".NS") and not ticker.endswith(".BO") and not ticker.startswith("^"):
                ticker += ".NS"
            pred_len = int(args.get("pred_len", 15))
            n_paths = int(args.get("n_paths", 20))

            res = kronos_forecaster.forecast(ticker=ticker, pred_len=pred_len, n_paths=n_paths)
            return {
                "success": True,
                "tool": tool_name,
                "ticker": ticker,
                "cmp": res.get("current_price"),
                "upside_probability_pct": res.get("p_up"),
                "expected_return_pct": res.get("expected_return_pct"),
                "corridor_90_pct": res.get("corridor_90"),
                "volatility_amplification": res.get("vol_amplification"),
                "model_status": res.get("model_status")
            }

        # 4. Walk-Forward Backtest
        elif tool_name == "tool_run_backtest":
            from backend.app.backtester.engine import BacktestEngine
            from backend.app.backtester.analytics import compute_performance_metrics
            from backend.app.core.data_engine import data_engine

            strategy_id = args.get("strategy_id", "connors_rsi2")
            ticker = args.get("ticker", "TCS.NS").strip().upper()
            if not ticker.endswith(".NS") and not ticker.endswith(".BO") and not ticker.startswith("^"):
                ticker += ".NS"
            period = args.get("period", "2y")
            capital = float(args.get("capital", 500000.0))
            risk_pct = float(args.get("risk_pct", 1.0))

            engine = BacktestEngine(
                initial_capital=capital,
                risk_per_trade_pct=risk_pct,
                slippage_pct=0.08,
                enable_indian_taxes=True
            )
            clean_ticker, df = data_engine.fetch_ticker_data_with_resolved_sym(ticker, period=period, interval="1d")
            if df is None or len(df) < 40:
                clean_ticker, df = data_engine.fetch_ticker_data_with_resolved_sym(ticker, period="1y", interval="1d")

            sim_res = engine.run_single(clean_ticker, df, strategy_id=strategy_id)
            metrics = compute_performance_metrics(sim_res["trades"], sim_res["equity_curve"], capital)

            return {
                "success": True,
                "tool": tool_name,
                "ticker": clean_ticker,
                "strategy_id": strategy_id,
                "total_trades": metrics.get("total_trades"),
                "win_rate_pct": metrics.get("win_rate_pct"),
                "net_profit_pct": metrics.get("net_profit_pct"),
                "profit_factor": metrics.get("profit_factor"),
                "max_drawdown_pct": metrics.get("max_drawdown_pct"),
                "sharpe_ratio": metrics.get("sharpe_ratio"),
                "cagr_pct": metrics.get("cagr_pct"),
                "payoff_ratio": metrics.get("payoff_ratio")
            }

        # 5. Position & Risk Sizing
        elif tool_name == "tool_calculate_position_size":
            from backend.app.core.risk_calculator import calculate_position_sizing
            capital = float(args.get("capital", 500000.0))
            risk_pct = float(args.get("risk_pct", 1.0))
            entry = float(args.get("entry_price", 100.0))
            stop = float(args.get("stop_loss", 95.0))
            target = float(args.get("target_price")) if args.get("target_price") else None

            res = calculate_position_sizing(
                capital=capital,
                risk_pct=risk_pct,
                entry_price=entry,
                stop_loss=stop,
                target_price=target
            )
            return {
                "success": True,
                "tool": tool_name,
                "shares_quantity": res.get("shares"),
                "entry_price": res.get("entry_price"),
                "stop_loss": res.get("stop_loss"),
                "capital_required": res.get("capital_required"),
                "total_risk_amount": res.get("total_risk_amount"),
                "total_risk_pct": res.get("total_risk_pct"),
                "portfolio_allocation_pct": res.get("portfolio_allocation_pct"),
                "target_1_2R": res.get("target_1_2R"),
                "target_2_3R": res.get("target_2_3R"),
                "potential_profit_target_1": res.get("potential_profit_target_1"),
                "risk_reward_ratio": res.get("risk_reward_ratio"),
                "is_over_allocation": res.get("is_over_allocation"),
                "warnings": res.get("warnings", [])
            }

        # 6. Sector Pulse
        elif tool_name == "tool_get_sector_pulse":
            from sectorpulse.engine import SectorPulseEngine
            from sectorpulse.data_ingestion import DEFAULT_NSE_BENCHMARK, DEFAULT_US_BENCHMARK

            market = (args.get("market") or "NSE").upper()
            bench = DEFAULT_US_BENCHMARK if market == "US" else DEFAULT_NSE_BENCHMARK
            engine = SectorPulseEngine(benchmark_ticker=bench)
            pipeline_res = engine.run_multi_sector_pipeline(period="2y")
            
            sectors_summary = []
            for s in pipeline_res.get("sectors", [])[:8]:
                sectors_summary.append({
                    "name": s.get("name"),
                    "sector": s.get("sector"),
                    "mrs": s.get("regime", {}).get("mrs_score"),
                    "trend": s.get("regime", {}).get("trend_classification"),
                    "hurst": s.get("regime", {}).get("hurst_exponent"),
                    "remaining_days": s.get("duration_forecast", {}).get("estimated_remaining_days"),
                    "exhaustion_prob": s.get("duration_forecast", {}).get("exhaustion_probability")
                })

            return {
                "success": True,
                "tool": tool_name,
                "market": market,
                "leading_sectors": sectors_summary
            }

        # 7. Sector Constituents
        elif tool_name == "tool_get_sector_constituents":
            from sectorpulse.constituents import get_sector_top_constituents
            sector_name = (args.get("sector_name") or "AUTO").upper()
            
            SECTOR_SYMBOL_MAP = {
                "AUTO": "^CNXAUTO",
                "IT": "^CNXIT",
                "BANK": "^NSEBANK",
                "PHARMA": "^CNXPHARMA",
                "FMCG": "^CNXFMCG",
                "METAL": "^CNXMETAL",
                "REALTY": "^CNXREALTY",
                "ENERGY": "^CNXENERGY",
                "INFRA": "^CNXINFRA",
                "PSU_BANK": "^CNXPSUBANK"
            }
            sector_key = SECTOR_SYMBOL_MAP.get(sector_name, sector_name)
            ranked = get_sector_top_constituents(sector_key, limit=6)
            
            return {
                "success": True,
                "tool": tool_name,
                "sector": sector_name,
                "constituents_count": len(ranked),
                "top_ranked_leaders": ranked
            }

        # 8. Log Paper Trade
        elif tool_name == "tool_log_paper_trade":
            from backend.app.core.trade_journal import TradeJournalEngine
            logged = TradeJournalEngine.add_trade(
                ticker=args.get("ticker", "").strip().upper(),
                strategy=args.get("strategy_id", "manual"),
                entry_price=float(args.get("entry_price", 0.0)),
                shares=int(args.get("quantity", 1)),
                stop_loss=float(args.get("stop_loss", 0.0)),
                target_1=float(args.get("target1", 0.0)),
                target_2=float(args.get("target2", 0.0)) if args.get("target2") else None,
                notes=args.get("notes", "Logged via AlphaChanakya Copilot")
            )
            return {
                "success": True,
                "tool": tool_name,
                "logged_trade": logged
            }

        else:
            return {"success": False, "error": f"Unknown tool '{tool_name}'"}

    except Exception as e:
        return {"success": False, "tool": tool_name, "error": str(e)}
