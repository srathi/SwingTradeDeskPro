"""
Quantitative Technical Indicators & Relative Strength Engine for SectorPulse.
Implements vectorized Mansfield Relative Strength (MRS), Moving Average Hierarchies, ADX(14), and ATR(14).
"""

from typing import Dict, Any, Tuple
import numpy as np
import pandas as pd


def calculate_mansfield_rs(
    sector_close: pd.Series,
    benchmark_close: pd.Series,
    lookback_period: int = 50
) -> pd.Series:
    """
    Computes Stan Weinstein / Mansfield Relative Strength (MRS):
        RS(t) = Sector_Close(t) / Benchmark_Close(t)
        MRS(t) = ((RS(t) / SMA_n(RS(t))) - 1) * 100
    """
    if len(sector_close) == 0 or len(benchmark_close) == 0:
        return pd.Series(dtype=float)

    # Avoid zero division
    bench_clean = benchmark_close.replace(0, np.nan).ffill().bfill()
    raw_rs = sector_close / bench_clean
    sma_rs = raw_rs.rolling(window=lookback_period, min_periods=max(5, lookback_period // 2)).mean()
    
    # Mansfield Normalized RS Formula
    mrs = ((raw_rs / sma_rs) - 1.0) * 100.0
    return mrs.fillna(0.0)


def compute_adx(
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
    length: int = 14
) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """
    Computes Wilder's Directional Movement Index: +DI, -DI, and ADX.
    """
    up_move = high.diff()
    down_move = -low.diff()

    plus_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0.0)
    minus_dm = np.where((down_move > up_move) & (down_move > 0), down_move, 0.0)

    tr1 = high - low
    tr2 = (high - close.shift(1)).abs()
    tr3 = (low - close.shift(1)).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

    # Wilder's smoothing (alpha = 1 / length)
    atr = tr.ewm(alpha=1.0 / length, min_periods=length, adjust=False).mean()
    plus_di = 100.0 * (pd.Series(plus_dm, index=high.index).ewm(alpha=1.0 / length, min_periods=length, adjust=False).mean() / atr)
    minus_di = 100.0 * (pd.Series(minus_dm, index=high.index).ewm(alpha=1.0 / length, min_periods=length, adjust=False).mean() / atr)

    dx_denom = (plus_di + minus_di).replace(0, np.nan)
    dx = (100.0 * (plus_di - minus_di).abs() / dx_denom).fillna(0.0)
    adx = dx.ewm(alpha=1.0 / length, min_periods=length, adjust=False).mean().fillna(0.0)

    return plus_di.fillna(0.0), minus_di.fillna(0.0), adx.fillna(0.0)


def compute_atr(
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
    length: int = 14
) -> pd.Series:
    """
    Computes Average True Range (ATR).
    """
    tr1 = high - low
    tr2 = (high - close.shift(1)).abs()
    tr3 = (low - close.shift(1)).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    return tr.ewm(alpha=1.0 / length, min_periods=length, adjust=False).mean().fillna(tr.rolling(length).mean()).bfill()


def compute_sector_indicators(
    sector_df: pd.DataFrame,
    benchmark_df: pd.DataFrame,
    mrs_lookback: int = 50
) -> pd.DataFrame:
    """
    Calculates comprehensive indicator suite for a given sector relative to the benchmark:
    - Mansfield RS & 5-day slope
    - EMA 20, 50, 200 and hierarchy score
    - ADX(14), +DI, -DI
    - ATR(14)
    """
    df = sector_df.copy()
    
    # 1. Mansfield Relative Strength
    df["MRS"] = calculate_mansfield_rs(df["Close"], benchmark_df["Close"], lookback_period=mrs_lookback)
    df["MRS_Slope_5d"] = df["MRS"].diff(5).fillna(0.0)

    # 2. Moving Averages
    df["EMA_20"] = df["Close"].ewm(span=20, adjust=False).mean()
    df["EMA_50"] = df["Close"].ewm(span=50, adjust=False).mean()
    df["EMA_200"] = df["Close"].ewm(span=200, adjust=False).mean()

    # Hierarchy Score (0 to 3: Stage 2 Markup alignment)
    is_above_20 = (df["Close"] > df["EMA_20"]).astype(int)
    is_20_above_50 = (df["EMA_20"] > df["EMA_50"]).astype(int)
    is_50_above_200 = (df["EMA_50"] > df["EMA_200"]).astype(int)
    df["MA_Hierarchy_Score"] = is_above_20 + is_20_above_50 + is_50_above_200

    # 3. Directional Movement (ADX)
    plus_di, minus_di, adx = compute_adx(df["High"], df["Low"], df["Close"], length=14)
    df["Plus_DI"] = plus_di
    df["Minus_DI"] = minus_di
    df["ADX_14"] = adx

    # 4. Volatility (ATR)
    df["ATR_14"] = compute_atr(df["High"], df["Low"], df["Close"], length=14)

    return df
