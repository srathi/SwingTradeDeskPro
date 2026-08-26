"""
Persistence & Econometric Regime Modeling Engine for SectorPulse.
Implements Hurst Exponent (Rescaled Range R/S analysis) and Discrete Markov State Transition Matrix modeling.
"""

from typing import Dict, Any, Tuple, Optional
import math
import numpy as np
import pandas as pd


def calculate_hurst_exponent(series: pd.Series, max_lag: int = 64) -> float:
    """
    Computes the Hurst Exponent (H) via classical Rescaled Range (R/S) analysis on log returns:
        E[R(tau) / S(tau)] ~ c * tau^H
        => log(R/S) = H * log(tau) + c
    Interpretation:
        H > 0.55 : Persistent / Trending (Momentum Memory)
        0.45 <= H <= 0.55 : Geometric Brownian Motion (Random Walk)
        H < 0.45 : Anti-persistent / Mean-Reverting
    """
    prices = np.asarray(series.dropna().values, dtype=float)
    if len(prices) < 30:
        return 0.50

    # Log returns
    rets = np.diff(np.log(np.maximum(prices, 1e-8)))
    n = len(rets)
    
    potential_lags = [4, 8, 16, 32, 64, 128]
    lags = [l for l in potential_lags if l <= min(max_lag, n // 2)]
    if len(lags) < 3:
        lags = [4, 8, max(12, n // 3)]

    rs_list = []
    valid_lags = []

    for l in lags:
        if l >= n:
            continue
        num_chunks = n // l
        if num_chunks < 1:
            continue

        sub_rets = rets[:num_chunks * l].reshape(-1, l)
        mean_adj = sub_rets - sub_rets.mean(axis=1, keepdims=True)
        cum_dev = np.cumsum(mean_adj, axis=1)
        r = np.max(cum_dev, axis=1) - np.min(cum_dev, axis=1)
        s = np.std(sub_rets, axis=1, ddof=1)
        s = np.where(s > 1e-9, s, 1e-9)
        rs_list.append(float(np.mean(r / s)))
        valid_lags.append(l)

    if len(valid_lags) < 3:
        return 0.50

    poly = np.polyfit(np.log(valid_lags), np.log(rs_list), 1)
    hurst = float(poly[0])

    # Bound hurst within domain [0.05, 0.95]
    return float(np.clip(hurst, 0.05, 0.95))


def compute_markov_regime_duration(
    mrs_series: pd.Series,
    ma_hierarchy_series: pd.Series
) -> Dict[str, Any]:
    """
    Constructs a Discrete 2-State Markov Chain (State 0: Uptrend, State 1: Downtrend/Neutral)
    from historical Relative Strength and Moving Average hierarchies.
    Computes:
        P_00: Probability of staying in Uptrend
        P_11: Probability of staying in Downtrend
        Expected Total Duration E[D] = 1 / (1 - P_00)
        Current Regime Age & Estimated Remaining Days
    """
    # Define boolean uptrend state: (MRS > 0) & (MA Hierarchy >= 2)
    state_series = ((mrs_series > 0) & (ma_hierarchy_series >= 2)).astype(int)
    states = state_series.values

    if len(states) < 15:
        return {
            "current_state": "UPTREND" if (states[-1] if len(states) > 0 else 1) == 1 else "DOWNTREND",
            "current_regime_age_days": 5,
            "expected_total_duration_days": 30,
            "estimated_remaining_days": 25,
            "p_stay_uptrend": 0.85
        }

    # Transition counts
    s_curr = states[:-1]
    s_next = states[1:]

    n00 = np.sum((s_curr == 1) & (s_next == 1))
    n01 = np.sum((s_curr == 1) & (s_next == 0))
    n10 = np.sum((s_curr == 0) & (s_next == 1))
    n11 = np.sum((s_curr == 0) & (s_next == 0))

    # Transition probabilities with Laplace smoothing
    p00 = (n00 + 1.0) / (n00 + n01 + 2.0)
    p11 = (n11 + 1.0) / (n10 + n11 + 2.0)

    # Expected regime duration: E[D] = 1 / (1 - P_00)
    p00 = min(p00, 0.975)  # Cap to prevent division by zero or infinite duration
    expected_uptrend_duration = int(round(1.0 / (1.0 - p00)))
    expected_downtrend_duration = int(round(1.0 / (1.0 - min(p11, 0.975))))

    # Calculate current regime age (consecutive days in current state)
    current_state_val = states[-1]
    age = 0
    for s in reversed(states):
        if s == current_state_val:
            age += 1
        else:
            break

    is_uptrend = (current_state_val == 1)
    expected_total = expected_uptrend_duration if is_uptrend else expected_downtrend_duration
    remaining = max(1, expected_total - age)

    return {
        "current_state": "UPTREND" if is_uptrend else "DOWNTREND",
        "current_regime_age_days": int(age),
        "expected_total_duration_days": int(expected_total),
        "estimated_remaining_days": int(remaining),
        "p_stay_uptrend": round(float(p00), 3)
    }
