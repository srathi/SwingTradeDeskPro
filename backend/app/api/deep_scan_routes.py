"""
Single Stock Deep Scan and Quantitative Profiler API Route.
Provides an exhaustive technical, multi-strategy setup, backtest snapshot, and candlestick analysis for a single ticker.
"""

from typing import Optional
import math
import numpy as np
import pandas as pd
from fastapi import APIRouter, HTTPException, Query

from backend.app.core.data_engine import data_engine
from backend.app.core.search_engine import LOCAL_STOCK_MASTER, SearchEngine
from backend.app.core.indicator_engine import compute_all_indicators, macd
from backend.app.strategies import STRATEGY_REGISTRY
from backend.app.backtester.engine import BacktestEngine
from backend.app.backtester.analytics import compute_performance_metrics

router = APIRouter(prefix="/api/deep-scan", tags=["DeepScan"])


@router.get("/{ticker:path}")
def run_single_stock_deep_scan(
    ticker: str,
    period: str = "2y",
    capital: float = 500000.0,
    risk_pct: float = 1.0
):
    """
    Runs a full quantitative deep-scan on a single stock symbol or natural name.
    """
    resolved_sym, df = data_engine.fetch_ticker_data_with_resolved_sym(ticker, period=period, interval="1d")
    
    if df is None or len(df) < 15:
        # Check suggestions for error rebound
        suggestions = SearchEngine.search(ticker, limit=4)
        raise HTTPException(
            status_code=404,
            detail={
                "message": f"No price data available for '{ticker}'",
                "suggestions": suggestions
            }
        )

    clean_ticker = resolved_sym or ticker.strip().upper()
    company_name = SearchEngine.get_company_name(clean_ticker)

    df = df[~df.index.duplicated(keep='first')].sort_index()
    data = compute_all_indicators(df)
    macd_line, sig_line, hist = macd(data['Close'])
    data['MACD'] = macd_line
    data['MACD_Signal'] = sig_line
    data['MACD_Hist'] = hist

    latest = data.iloc[-1]
    prev = data.iloc[-2] if len(data) >= 2 else latest

    cmp = float(latest['Close'])
    open_p = float(latest['Open'])
    high_p = float(latest['High'])
    low_p = float(latest['Low'])
    vol = float(latest['Volume'])
    prev_close = float(prev['Close'])
    change_pct = round(((cmp - prev_close) / prev_close) * 100.0, 2) if prev_close != 0 else 0.0

    # Moving averages
    ema20 = float(latest.get('EMA_20', np.nan))
    ema50 = float(latest.get('EMA_50', np.nan))
    ema100 = float(latest.get('EMA_100', np.nan))
    ema200 = float(latest.get('EMA_200', np.nan))
    sma20 = float(latest.get('SMA_20', np.nan))
    sma50 = float(latest.get('SMA_50', np.nan))
    sma200 = float(latest.get('SMA_200', np.nan))

    # Oscillators & Volatility
    rsi_val = float(latest.get('RSI_14', 50.0))
    atr_val = float(latest.get('ATR_14', cmp * 0.02))
    vol_sma = float(latest.get('Vol_SMA20', vol))
    vol_ratio = float(latest.get('Vol_Ratio', 1.0))
    bb_upper = float(latest.get('BB_Upper', cmp * 1.05))
    bb_mid = float(latest.get('BB_Middle', cmp))
    bb_lower = float(latest.get('BB_Lower', cmp * 0.95))
    bb_width = float(latest.get('BB_Width', 10.0))

    macd_val = float(latest.get('MACD', 0.0))
    macd_sig = float(latest.get('MACD_Signal', 0.0))
    macd_h = float(latest.get('MACD_Hist', 0.0))

    # Ranges
    lookback_52w = min(252, len(data))
    high_52w = float(data['High'].iloc[-lookback_52w:].max())
    low_52w = float(data['Low'].iloc[-lookback_52w:].min())

    lookback_20d = min(20, len(data))
    high_20d = float(data['High'].iloc[-lookback_20d:].max())
    low_20d = float(data['Low'].iloc[-lookback_20d:].min())

    def calc_dist(ma_val):
        if math.isnan(ma_val) or ma_val == 0:
            return None
        return round(((cmp - ma_val) / ma_val) * 100.0, 2)

    ma_matrix = {
        "ema_20": {"value": round(ema20, 2) if not math.isnan(ema20) else None, "dist_pct": calc_dist(ema20)},
        "ema_50": {"value": round(ema50, 2) if not math.isnan(ema50) else None, "dist_pct": calc_dist(ema50)},
        "ema_100": {"value": round(ema100, 2) if not math.isnan(ema100) else None, "dist_pct": calc_dist(ema100)},
        "ema_200": {"value": round(ema200, 2) if not math.isnan(ema200) else None, "dist_pct": calc_dist(ema200)},
        "sma_20": {"value": round(sma20, 2) if not math.isnan(sma20) else None, "dist_pct": calc_dist(sma20)},
        "sma_50": {"value": round(sma50, 2) if not math.isnan(sma50) else None, "dist_pct": calc_dist(sma50)},
        "sma_200": {"value": round(sma200, 2) if not math.isnan(sma200) else None, "dist_pct": calc_dist(sma200)}
    }

    # Strategy evaluations
    strategy_evaluations = []
    primary_setup = None

    for strat_id, strat in STRATEGY_REGISTRY.items():
        res = strat.evaluate_setup(df, clean_ticker)
        is_active = res is not None
        if is_active and not primary_setup:
            primary_setup = res

        strategy_evaluations.append({
            "strategy_id": strat_id,
            "name": strat.name,
            "description": strat.description,
            "is_active": is_active,
            "setup": res
        })

    # Run quick 2-year backtest
    target_strat_id = primary_setup["strategy_id"] if primary_setup else "trend_pullback"
    engine = BacktestEngine(initial_capital=capital, risk_per_trade_pct=risk_pct)
    sim = engine.run_single(clean_ticker, df, strategy_id=target_strat_id)
    backtest_kpis = compute_performance_metrics(sim["trades"], sim["equity_curve"], capital)

    # Position sizing
    risk_per_share = primary_setup["risk_per_share"] if primary_setup else round(atr_val * 1.5, 2)
    stop_loss_price = primary_setup["stop_loss"] if primary_setup else round(cmp - risk_per_share, 2)
    target_1_price = primary_setup["target_1"] if primary_setup else round(cmp + (risk_per_share * 2.0), 2)
    target_2_price = primary_setup["target_2"] if primary_setup else round(cmp + (risk_per_share * 3.0), 2)

    risk_budget = capital * (risk_pct / 100.0)
    shares = int(risk_budget // risk_per_share) if risk_per_share > 0 else 0
    capital_req = round(shares * cmp, 2)
    allocation_pct = round((capital_req / capital) * 100.0, 2) if capital > 0 else 0.0

    # Recent 10 candles
    recent_candles = []
    tail_len = min(10, len(data))
    for i in range(len(data) - tail_len, len(data)):
        bar = data.iloc[i]
        d_str = data.index[i].strftime("%Y-%m-%d") if hasattr(data.index[i], "strftime") else str(data.index[i])[:10]
        recent_candles.append({
            "date": d_str,
            "open": round(float(bar['Open']), 2),
            "high": round(float(bar['High']), 2),
            "low": round(float(bar['Low']), 2),
            "close": round(float(bar['Close']), 2),
            "volume": int(bar['Volume']),
            "ema_20": round(float(bar['EMA_20']), 2) if not pd.isna(bar.get('EMA_20')) else None,
            "rsi_14": round(float(bar['RSI_14']), 1) if not pd.isna(bar.get('RSI_14')) else None
        })

    # Verdict
    verdict_title = "Neutral / Watching"
    verdict_type = "NEUTRAL"
    verdict_text = f"{clean_ticker} is currently consolidating with RSI at {rsi_val:.1f}. No active breakout or pullback triggered on the latest close."

    if primary_setup:
        verdict_title = f"Bullish Setup: {primary_setup['strategy']}"
        verdict_type = "BULLISH"
        verdict_text = f"Triggered high-probability {primary_setup['strategy']} with a Setup Quality Score of {primary_setup['score']}/100. Risk-to-Reward is {primary_setup['rr_ratio']} with target at ₹{primary_setup['target_1']}."
    elif cmp > ema200 and ema20 > ema50:
        verdict_title = "Macro Uptrend (Waiting for Pullback)"
        verdict_type = "UPTREND"
        verdict_text = f"Trading $+{calc_dist(ema200)}% above 200 EMA in confirmed macro bull structure. Watch for a pullback to the 20 EMA (₹{ema20:.2f}) for optimal entry."
    elif cmp < ema200:
        verdict_title = "Bearish / Below 200 EMA"
        verdict_type = "BEARISH"
        verdict_text = f"Trading {calc_dist(ema200)}% below 200 EMA (₹{ema200:.2f}). Swing trend strategies are currently filtered out."

    return {
        "ticker": clean_ticker,
        "company_name": company_name,
        "cmp": round(cmp, 2),
        "open": round(open_p, 2),
        "high": round(high_p, 2),
        "low": round(low_p, 2),
        "change_pct": change_pct,
        "prev_close": round(prev_close, 2),
        "range_52w": {"low": round(low_52w, 2), "high": round(high_52w, 2)},
        "range_20d": {"low": round(low_20d, 2), "high": round(high_20d, 2)},
        "atr_14": round(atr_val, 2),
        "atr_pct": round((atr_val / cmp) * 100.0, 2),
        "moving_averages": ma_matrix,
        "oscillators": {
            "rsi_14": round(rsi_val, 1),
            "rsi_status": "Oversold" if rsi_val <= 35 else ("Overbought" if rsi_val >= 70 else "Bullish Momentum" if rsi_val >= 50 else "Consolidating"),
            "macd": round(macd_val, 2),
            "macd_signal": round(macd_sig, 2),
            "macd_hist": round(macd_h, 2),
            "bollinger": {
                "upper": round(bb_upper, 2),
                "mid": round(bb_mid, 2),
                "lower": round(bb_lower, 2),
                "width_pct": round(bb_width, 1)
            },
            "volume_today": int(vol),
            "vol_sma20": int(vol_sma),
            "vol_ratio": round(vol_ratio, 2)
        },
        "strategy_evaluations": strategy_evaluations,
        "active_setup": primary_setup,
        "position_sizing": {
            "shares": shares,
            "entry_price": round(cmp, 2),
            "stop_loss": stop_loss_price,
            "target_1": target_1_price,
            "target_2": target_2_price,
            "risk_per_share": round(risk_per_share, 2),
            "total_risk_amount": round(risk_budget, 2),
            "capital_required": capital_req,
            "portfolio_allocation_pct": allocation_pct,
            "potential_profit_target_1": round(shares * (target_1_price - cmp), 2),
            "potential_profit_target_2": round(shares * (target_2_price - cmp), 2)
        },
        "backtest_snapshot": {
            "strategy_id": target_strat_id,
            "win_rate": backtest_kpis["win_rate"],
            "total_trades": backtest_kpis["total_trades"],
            "winning_trades": backtest_kpis["winning_trades"],
            "losing_trades": backtest_kpis["losing_trades"],
            "profit_factor": backtest_kpis["profit_factor"],
            "net_profit": backtest_kpis["net_profit"],
            "net_profit_pct": backtest_kpis["net_profit_pct"],
            "max_drawdown_pct": backtest_kpis["max_drawdown_pct"]
        },
        "recent_candles": recent_candles,
        "verdict": {
            "title": verdict_title,
            "type": verdict_type,
            "text": verdict_text
        }
    }
