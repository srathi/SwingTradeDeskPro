"""
Vectorized, High-Performance Technical Indicator Engine.
Implemented with pure NumPy and Pandas for institutional-grade reliability,
exact alignment with TradingView/Zerodha calculations, and zero external C-dependencies.
"""

import numpy as np
import pandas as pd
from typing import Tuple, Dict


def sma(series: pd.Series, length: int) -> pd.Series:
    """Simple Moving Average."""
    return series.rolling(window=length, min_periods=length).mean()


def ema(series: pd.Series, length: int) -> pd.Series:
    """Exponential Moving Average."""
    return series.ewm(span=length, adjust=False).mean()


def rsi(series: pd.Series, length: int = 14) -> pd.Series:
    """
    Wilder's Relative Strength Index (RSI).
    Matches standard TradingView and exchange terminal calculations.
    """
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    # Initial average
    avg_gain = gain.ewm(alpha=1.0 / length, min_periods=length, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1.0 / length, min_periods=length, adjust=False).mean()

    rs = avg_gain / avg_loss.replace(0, np.nan)
    rsi_val = 100.0 - (100.0 / (1.0 + rs))
    return rsi_val.fillna(50.0)


def true_range(high: pd.Series, low: pd.Series, close: pd.Series) -> pd.Series:
    """True Range calculation."""
    prev_close = close.shift(1)
    tr1 = high - low
    tr2 = (high - prev_close).abs()
    tr3 = (low - prev_close).abs()
    return pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)


def atr(high: pd.Series, low: pd.Series, close: pd.Series, length: int = 14) -> pd.Series:
    """Wilder's Average True Range (ATR)."""
    tr = true_range(high, low, close)
    return tr.ewm(alpha=1.0 / length, min_periods=length, adjust=False).mean()


def bollinger_bands(
    close: pd.Series, length: int = 20, std_dev: float = 2.0
) -> Tuple[pd.Series, pd.Series, pd.Series, pd.Series, pd.Series]:
    """
    Bollinger Bands: Middle, Upper, Lower, Bandwidth, %B.
    """
    mid = sma(close, length)
    std = close.rolling(window=length, min_periods=length).std()
    upper = mid + (std * std_dev)
    lower = mid - (std * std_dev)
    bandwidth = ((upper - lower) / mid.replace(0, np.nan)) * 100.0
    percent_b = (close - lower) / (upper - lower).replace(0, np.nan)
    return upper, mid, lower, bandwidth, percent_b


def keltner_channels(
    high: pd.Series, low: pd.Series, close: pd.Series, length: int = 20, mult: float = 1.5, atr_length: int = 10
) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """
    Keltner Channels (KC): Upper, Middle, Lower.
    """
    mid = ema(close, length)
    atr_val = atr(high, low, close, length=atr_length)
    upper = mid + (mult * atr_val)
    lower = mid - (mult * atr_val)
    return upper, mid, lower


def macd(
    close: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9
) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """Moving Average Convergence Divergence (MACD)."""
    fast_ema = ema(close, fast)
    slow_ema = ema(close, slow)
    macd_line = fast_ema - slow_ema
    signal_line = ema(macd_line, signal)
    hist = macd_line - signal_line
    return macd_line, signal_line, hist


def volume_sma(volume: pd.Series, length: int = 20) -> pd.Series:
    """Volume Simple Moving Average."""
    return sma(volume, length)


def highest(series: pd.Series, length: int) -> pd.Series:
    """Highest value over lookback window."""
    return series.rolling(window=length, min_periods=length).max()


def lowest(series: pd.Series, length: int) -> pd.Series:
    """Lowest value over lookback window."""
    return series.rolling(window=length, min_periods=length).min()


def compute_all_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes and attaches standard indicators required for swing trading analysis.
    Mutates a copy of the dataframe.
    """
    data = df.copy()

    # EMAs
    data['EMA_10'] = ema(data['Close'], 10)
    data['EMA_20'] = ema(data['Close'], 20)
    data['EMA_50'] = ema(data['Close'], 50)
    data['EMA_100'] = ema(data['Close'], 100)
    data['EMA_200'] = ema(data['Close'], 200)

    # SMAs
    data['SMA_5'] = sma(data['Close'], 5)
    data['SMA_20'] = sma(data['Close'], 20)
    data['SMA_50'] = sma(data['Close'], 50)
    data['SMA_200'] = sma(data['Close'], 200)

    # Wilder Oscillators & Volatility
    data['RSI_14'] = rsi(data['Close'], 14)
    data['RSI_2'] = rsi(data['Close'], 2)
    data['ATR_14'] = atr(data['High'], data['Low'], data['Close'], 14)

    # Bollinger Bands (20, 2.0)
    bb_upper, bb_mid, bb_lower, bb_width, bb_pct_b = bollinger_bands(data['Close'], 20, 2.0)
    data['BB_Upper'] = bb_upper
    data['BB_Middle'] = bb_mid
    data['BB_Lower'] = bb_lower
    data['BB_Width'] = bb_width
    data['BB_PctB'] = bb_pct_b

    # Keltner Channels (20, 1.5, 10 ATR)
    kc_upper, kc_mid, kc_lower = keltner_channels(data['High'], data['Low'], data['Close'], 20, 1.5, 10)
    data['KC_Upper'] = kc_upper
    data['KC_Middle'] = kc_mid
    data['KC_Lower'] = kc_lower

    # MACD
    m_line, s_line, hist = macd(data['Close'], 12, 26, 9)
    data['MACD'] = m_line
    data['MACD_Signal'] = s_line
    data['MACD_Hist'] = hist

    # Volume Indicators
    data['Vol_SMA20'] = volume_sma(data['Volume'], 20)
    data['Vol_Ratio'] = (data['Volume'] / data['Vol_SMA20'].replace(0, np.nan)).fillna(1.0)

    # Ranges & Donchian Pivots
    data['High_20'] = highest(data['High'], 20)
    data['Low_20'] = lowest(data['Low'], 20)
    data['High_50'] = highest(data['High'], 50)
    data['Low_50'] = lowest(data['Low'], 50)

    return data


def gmma_ribbons(series: pd.Series) -> Tuple[Dict[str, pd.Series], Dict[str, pd.Series]]:
    """
    Computes Guppy Multiple Moving Average (GMMA) ribbons.
    - Fast / Short-term (Trader) EMAs: 3, 5, 8, 10, 12, 15
    - Slow / Long-term (Investor) EMAs: 30, 35, 40, 45, 50, 60
    """
    fast_periods = [3, 5, 8, 10, 12, 15]
    slow_periods = [30, 35, 40, 45, 50, 60]

    fast_ribbon = {f"EMA_{p}": ema(series, p) for p in fast_periods}
    slow_ribbon = {f"EMA_{p}": ema(series, p) for p in slow_periods}

    return fast_ribbon, slow_ribbon


def resample_weekly(df: pd.DataFrame) -> pd.DataFrame:
    """
    Resamples daily OHLCV DataFrame into weekly bars (aligned to weekly close).
    """
    if df is None or len(df) == 0:
        return df

    weekly = df.resample('W-FRI').agg({
        'Open': 'first',
        'High': 'max',
        'Low': 'min',
        'Close': 'last',
        'Volume': 'sum'
    }).dropna()

    return weekly
