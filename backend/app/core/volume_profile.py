"""
Volume Profile & Anchored VWAP (AVWAP) Institutional Order Flow Engine.
Academic & Market Profile Foundation: J. Peter Steidlmayer, James Dalton (Mind Over Markets), Brian Shannon (Anchored VWAP).
Calculates Point of Control (POC), Value Area (VAH/VAL 70%), and Multi-Pivot Anchored VWAP series.
"""

from typing import Dict, Any, List, Optional, Tuple
import numpy as np
import pandas as pd


def compute_volume_profile(df: pd.DataFrame, num_bins: int = 50, value_area_pct: float = 0.70) -> Dict[str, Any]:
    """
    Computes Point of Control (POC), Value Area High (VAH), Value Area Low (VAL), and price bin distribution.
    """
    if df is None or len(df) < 10:
        return {
            "poc": 0.0,
            "vah": 0.0,
            "val": 0.0,
            "bins": []
        }

    high_max = float(df['High'].max())
    low_min = float(df['Low'].min())
    if high_max <= low_min:
        return {"poc": high_max, "vah": high_max, "val": low_min, "bins": []}

    bin_edges = np.linspace(low_min, high_max, num_bins + 1)
    bin_volumes = np.zeros(num_bins)

    # Distribute bar volume across the price bins it spans
    for _, row in df.iterrows():
        b_low = float(row['Low'])
        b_high = float(row['High'])
        b_vol = float(row.get('Volume', 0))
        if b_vol <= 0:
            continue

        # Find overlapping bins
        idx_start = max(0, int(np.searchsorted(bin_edges, b_low) - 1))
        idx_end = min(num_bins, int(np.searchsorted(bin_edges, b_high)))
        num_touched = max(1, idx_end - idx_start)
        vol_per_bin = b_vol / num_touched

        for i in range(idx_start, min(num_bins, idx_start + num_touched)):
            bin_volumes[i] += vol_per_bin

    total_volume = float(np.sum(bin_volumes))
    if total_volume <= 0:
        mid = (high_max + low_min) / 2.0
        return {"poc": round(mid, 2), "vah": round(high_max, 2), "val": round(low_min, 2), "bins": []}

    # POC is the bin with maximum volume
    poc_idx = int(np.argmax(bin_volumes))
    poc_price = round(float((bin_edges[poc_idx] + bin_edges[poc_idx + 1]) / 2.0), 2)

    # Calculate Value Area (70% of total volume radiating outward from POC)
    target_vol = total_volume * value_area_pct
    accum_vol = bin_volumes[poc_idx]
    up_idx = poc_idx
    down_idx = poc_idx

    while accum_vol < target_vol and (up_idx < num_bins - 1 or down_idx > 0):
        next_up_vol = bin_volumes[up_idx + 1] if up_idx < num_bins - 1 else 0
        next_down_vol = bin_volumes[down_idx - 1] if down_idx > 0 else 0

        if next_up_vol >= next_down_vol and up_idx < num_bins - 1:
            up_idx += 1
            accum_vol += bin_volumes[up_idx]
        elif down_idx > 0:
            down_idx -= 1
            accum_vol += bin_volumes[down_idx]
        else:
            if up_idx < num_bins - 1:
                up_idx += 1
                accum_vol += bin_volumes[up_idx]
            else:
                break

    vah_price = round(float(bin_edges[up_idx + 1]), 2)
    val_price = round(float(bin_edges[down_idx]), 2)

    # Formatted bins for UI visualization
    bins_data = []
    max_vol = float(np.max(bin_volumes)) if len(bin_volumes) else 1.0
    for i in range(num_bins):
        price_level = round(float((bin_edges[i] + bin_edges[i + 1]) / 2.0), 2)
        vol_pct = round(float((bin_volumes[i] / max_vol) * 100.0), 1) if max_vol > 0 else 0
        bins_data.append({
            "price": price_level,
            "volume": int(bin_volumes[i]),
            "volume_pct": vol_pct,
            "is_poc": i == poc_idx,
            "in_value_area": down_idx <= i <= up_idx
        })

    return {
        "poc": poc_price,
        "vah": vah_price,
        "val": val_price,
        "total_profile_volume": int(total_volume),
        "bins": bins_data
    }


def compute_anchored_vwap(df: pd.DataFrame, anchor_idx: int) -> pd.Series:
    """
    Computes Anchored VWAP from a specific integer bar index to the end of the dataframe.
    """
    n = len(df)
    avwap_series = pd.Series(index=df.index, dtype=float)
    if anchor_idx < 0 or anchor_idx >= n:
        return avwap_series

    typical_price = (df['High'] + df['Low'] + df['Close']) / 3.0
    volume = df['Volume']

    cum_pv = 0.0
    cum_vol = 0.0

    for i in range(anchor_idx, n):
        pv = typical_price.iloc[i] * volume.iloc[i]
        v = volume.iloc[i]
        cum_pv += pv
        cum_vol += v
        if cum_vol > 0:
            avwap_series.iloc[i] = cum_pv / cum_vol
        else:
            avwap_series.iloc[i] = typical_price.iloc[i]

    return avwap_series


def compute_institutional_avwaps(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Computes key institutional Anchored VWAPs:
    1. 52-Week High Pivot AVWAP (Resistance into blue-sky breakout)
    2. Major Swing Low Anchor (Institutional Base Floor)
    3. Maximum Volume Spike Day Anchor (Institutional Accumulation Pivot)
    """
    if df is None or len(df) < 15:
        return {}

    n = len(df)
    lookback = min(252, n)
    recent_df = df.iloc[-lookback:]

    # 1. 52-Week High Pivot Index
    high_idx_recent = int(np.argmax(recent_df['High'].values))
    high_idx_global = n - lookback + high_idx_recent
    high_date = str(df.index[high_idx_global])[:10]
    high_price = float(df['High'].iloc[high_idx_global])
    avwap_52w_high = compute_anchored_vwap(df, high_idx_global)

    # 2. Major Swing Low Anchor (Lowest low of last 60 sessions)
    low_lookback = min(60, n)
    low_df = df.iloc[-low_lookback:]
    low_idx_recent = int(np.argmin(low_df['Low'].values))
    low_idx_global = n - low_lookback + low_idx_recent
    low_date = str(df.index[low_idx_global])[:10]
    low_price = float(df['Low'].iloc[low_idx_global])
    avwap_swing_low = compute_anchored_vwap(df, low_idx_global)

    # 3. Maximum Volume Day Anchor (Last 90 sessions)
    vol_lookback = min(90, n)
    vol_df = df.iloc[-vol_lookback:]
    max_vol_recent = int(np.argmax(vol_df['Volume'].values))
    max_vol_global = n - vol_lookback + max_vol_recent
    max_vol_date = str(df.index[max_vol_global])[:10]
    max_vol_val = int(df['Volume'].iloc[max_vol_global])
    avwap_max_vol = compute_anchored_vwap(df, max_vol_global)

    latest_close = float(df['Close'].iloc[-1])
    val_high = float(avwap_52w_high.iloc[-1]) if not np.isnan(avwap_52w_high.iloc[-1]) else latest_close
    val_low = float(avwap_swing_low.iloc[-1]) if not np.isnan(avwap_swing_low.iloc[-1]) else latest_close
    val_maxvol = float(avwap_max_vol.iloc[-1]) if not np.isnan(avwap_max_vol.iloc[-1]) else latest_close

    return {
        "avwap_52w_high": {
            "current_val": round(val_high, 2),
            "anchor_date": high_date,
            "anchor_price": round(high_price, 2),
            "price_vs_avwap_pct": round(((latest_close - val_high) / val_high) * 100.0, 2),
            "is_above": latest_close >= val_high
        },
        "avwap_swing_low": {
            "current_val": round(val_low, 2),
            "anchor_date": low_date,
            "anchor_price": round(low_price, 2),
            "price_vs_avwap_pct": round(((latest_close - val_low) / val_low) * 100.0, 2),
            "is_above": latest_close >= val_low
        },
        "avwap_max_volume": {
            "current_val": round(val_maxvol, 2),
            "anchor_date": max_vol_date,
            "anchor_volume": max_vol_val,
            "price_vs_avwap_pct": round(((latest_close - val_maxvol) / val_maxvol) * 100.0, 2),
            "is_above": latest_close >= val_maxvol
        }
    }
