"""
Kronos Financial Foundation Model Service for SwingTradeDeskPro.
Provides probabilistic K-line forecasting, parallel Monte Carlo path simulation,
confidence dispersion funnels, and quantitative strategy confluence analysis.
"""

import os
import time
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta

import numpy as np
import pandas as pd

logger = logging.getLogger("kronos_engine")

PRICE_COLS = ["open", "high", "low", "close"]
VOL_COL = "volume"
AMT_COL = "amount"
ALL_COLS = PRICE_COLS + [VOL_COL, AMT_COL]


class KronosEngine:
    def __init__(self):
        self._tokenizer = None
        self._model = None
        self._predictor = None
        self._device = self._detect_device()
        self._model_name = "mini"  # Default lightweight for Render & CPU compatibility
        self._cache: Dict[str, Tuple[float, Dict[str, Any]]] = {}
        self._cache_ttl_seconds = 3600  # 1 hour TTL
        self._is_loaded = False
        self._load_error = None

    def _detect_device(self) -> str:
        try:
            import torch
            if getattr(torch.backends, "mps", None) is not None and torch.backends.mps.is_available():
                return "mps"
            if torch.cuda.is_available():
                return "cuda:0"
        except Exception:
            pass
        return "cpu"

    def get_status(self) -> Dict[str, Any]:
        return {
            "is_loaded": self._is_loaded,
            "device": self._device,
            "model_name": self._model_name,
            "cached_entries": len(self._cache),
            "load_error": self._load_error
        }

    def _lazy_load_model(self, model_type: str = "mini"):
        if self._is_loaded and self._model_name == model_type:
            return

        try:
            import torch
            from .model.kronos import KronosTokenizer, Kronos, KronosPredictor

            logger.info(f"Loading Kronos Foundation Model ({model_type}) on device: {self._device}...")
            
            if model_type == "mini":
                tokenizer_id = "NeoQuasar/Kronos-Tokenizer-2k"
                model_id = "NeoQuasar/Kronos-mini"
                max_context = 2048
            elif model_type == "small":
                tokenizer_id = "NeoQuasar/Kronos-Tokenizer-base"
                model_id = "NeoQuasar/Kronos-small"
                max_context = 512
            else:
                tokenizer_id = "NeoQuasar/Kronos-Tokenizer-base"
                model_id = "NeoQuasar/Kronos-base"
                max_context = 512

            self._tokenizer = KronosTokenizer.from_pretrained(tokenizer_id)
            self._model = Kronos.from_pretrained(model_id)
            self._model.to(self._device)
            self._model.eval()

            self._predictor = KronosPredictor(
                model=self._model,
                tokenizer=self._tokenizer,
                device=self._device,
                max_context=max_context
            )
            self._model_name = model_type
            self._is_loaded = True
            self._load_error = None
            logger.info(f"✅ Kronos {model_type} loaded successfully.")
        except Exception as e:
            self._load_error = str(e)
            logger.warning(f"Could not load PyTorch Kronos weights ({e}). Falling back to statistical Monte Carlo simulation.")

    def _preprocess_df(self, df: pd.DataFrame) -> pd.DataFrame:
        """Ensure standard OHLCV and amount columns with lowercase headers."""
        data = df.copy()
        col_map = {
            "Open": "open", "High": "high", "Low": "low",
            "Close": "close", "Volume": "volume", "Amount": "amount"
        }
        data = data.rename(columns=col_map)
        
        for col in PRICE_COLS:
            if col not in data.columns:
                raise ValueError(f"Missing required price column: {col}")

        if VOL_COL not in data.columns:
            data[VOL_COL] = 100000.0
        if AMT_COL not in data.columns:
            data[AMT_COL] = data[VOL_COL] * data[PRICE_COLS].mean(axis=1)

        # Drop NaNs and sort ascending
        data = data.dropna(subset=PRICE_COLS).sort_index()
        return data

    def _generate_future_timestamps(self, last_date: pd.Timestamp, pred_len: int, interval: str = "1d") -> List[str]:
        """Generate future trading timestamps excluding weekends."""
        future_dates = []
        curr = pd.to_datetime(last_date)
        step = 0
        while len(future_dates) < pred_len:
            curr += timedelta(days=1)
            # Skip Saturday (5) and Sunday (6) for daily interval
            if interval == "1d" and curr.weekday() >= 5:
                continue
            future_dates.append(curr.strftime("%Y-%m-%d"))
        return future_dates

    def _apply_circuit_limits(self, paths: np.ndarray, last_close: float, max_daily_chg: float = 0.10) -> np.ndarray:
        """Cap single-day moves to reflect NSE/BSE circuit bands (±10%)."""
        capped = paths.copy()
        n_paths, pred_len, _ = capped.shape
        
        for p in range(n_paths):
            prev_c = last_close
            for t in range(pred_len):
                o, h, l, c = capped[p, t, 0], capped[p, t, 1], capped[p, t, 2], capped[p, t, 3]
                max_hi = prev_c * (1.0 + max_daily_chg)
                min_lo = prev_c * (1.0 - max_daily_chg)

                c = np.clip(c, min_lo, max_hi)
                o = np.clip(o, min_lo, max_hi)
                h = max(o, c, np.clip(h, min_lo, max_hi * 1.02))
                l = min(o, c, np.clip(l, min_lo * 0.98, max_hi))

                capped[p, t, 0] = o
                capped[p, t, 1] = h
                capped[p, t, 2] = l
                capped[p, t, 3] = c
                prev_c = c
        return capped

    def _statistical_monte_carlo(self, df: pd.DataFrame, pred_len: int, n_paths: int) -> np.ndarray:
        """High-fidelity Geometric Brownian Motion fallback if model weights are unavailable."""
        closes = df["close"].values
        returns = np.diff(np.log(np.maximum(closes, 1e-5)))
        mu = np.mean(returns[-30:]) if len(returns) >= 30 else 0.0005
        sigma = np.std(returns[-30:]) if len(returns) >= 30 else 0.015
        sigma = max(sigma, 0.005)

        last_close = float(closes[-1])
        paths = np.zeros((n_paths, pred_len, 6))

        for p in range(n_paths):
            cur_price = last_close
            for t in range(pred_len):
                drift = (mu - 0.5 * sigma**2)
                shock = sigma * np.random.normal()
                next_price = cur_price * np.exp(drift + shock)
                
                high_p = max(cur_price, next_price) * (1.0 + abs(np.random.normal(0, sigma * 0.4)))
                low_p = min(cur_price, next_price) * (1.0 - abs(np.random.normal(0, sigma * 0.4)))
                
                paths[p, t, 0] = cur_price
                paths[p, t, 1] = high_p
                paths[p, t, 2] = low_p
                paths[p, t, 3] = next_price
                paths[p, t, 4] = float(df["volume"].iloc[-1])
                paths[p, t, 5] = next_price * paths[p, t, 4]
                cur_price = next_price

        return self._apply_circuit_limits(paths, last_close)

    def forecast(
        self,
        df: pd.DataFrame,
        ticker: str,
        pred_len: int = 15,
        n_paths: int = 20,
        temperature: float = 1.0,
        top_p: float = 0.9,
        model_type: str = "mini"
    ) -> Dict[str, Any]:
        """
        Run full Monte Carlo forecasting and return JSON-serializable trajectory metrics.
        """
        cache_key = f"{ticker}_{pred_len}_{n_paths}_{model_type}"
        now = time.time()
        if cache_key in self._cache:
            ts, res = self._cache[cache_key]
            if now - ts < self._cache_ttl_seconds:
                return res

        clean_df = self._preprocess_df(df)
        last_date = clean_df.index[-1]
        last_close = float(clean_df["close"].iloc[-1])
        future_dates = self._generate_future_timestamps(last_date, pred_len)

        # Attempt Kronos PyTorch Inference
        paths = None
        self._lazy_load_model(model_type)

        if self._is_loaded and self._predictor is not None:
            try:
                import torch
                from .model.kronos import auto_regressive_inference, calc_time_stamps

                lookback = min(len(clean_df), self._predictor.max_context - pred_len)
                x_df = clean_df.iloc[-lookback:][ALL_COLS]
                
                x_timestamps = pd.Series(pd.to_datetime(clean_df.index[-lookback:])).reset_index(drop=True)
                y_timestamps = pd.Series(pd.to_datetime(future_dates)).reset_index(drop=True)

                x_time_df = calc_time_stamps(x_timestamps)
                y_time_df = calc_time_stamps(y_timestamps)

                x = x_df.values.astype(np.float32)
                x_mean, x_std = np.mean(x, axis=0), np.std(x, axis=0) + 1e-5
                x_norm = np.clip((x - x_mean) / x_std, -self._predictor.clip, self._predictor.clip)

                x_stamp = x_time_df.values.astype(np.float32)
                y_stamp = y_time_df.values.astype(np.float32)

                x_batch = np.repeat(x_norm[np.newaxis], n_paths, axis=0)
                x_stamp_batch = np.repeat(x_stamp[np.newaxis], n_paths, axis=0)
                y_stamp_batch = np.repeat(y_stamp[np.newaxis], n_paths, axis=0)

                with torch.no_grad():
                    preds = auto_regressive_inference(
                        self._predictor.tokenizer,
                        self._predictor.model,
                        torch.from_numpy(np.ascontiguousarray(x_batch)).to(self._device),
                        torch.from_numpy(np.ascontiguousarray(x_stamp_batch)).to(self._device),
                        torch.from_numpy(np.ascontiguousarray(y_stamp_batch)).to(self._device),
                        self._predictor.max_context,
                        pred_len,
                        self._predictor.clip,
                        temperature,
                        0,
                        top_p,
                        1,
                        False
                    )
                if hasattr(preds, 'cpu'):
                    preds = preds.cpu().numpy()
                preds = preds[:, -pred_len:, :]
                raw_paths = preds * x_std + x_mean
                paths = self._apply_circuit_limits(raw_paths[..., :6], last_close)
            except Exception as e:
                logger.error(f"Inference error with Kronos weights: {e}. Using statistical simulation fallback.")
                paths = None

        if paths is None:
            paths = self._statistical_monte_carlo(clean_df, pred_len, n_paths)

        # -------------------------------------------------------------
        # Calculate Path Statistics & Metrics
        # -------------------------------------------------------------
        mean_path = np.mean(paths, axis=0)
        median_path = np.median(paths, axis=0)
        p10_path = np.percentile(paths, 10, axis=0)
        p90_path = np.percentile(paths, 90, axis=0)

        final_closes = paths[:, -1, 3]
        upside_count = np.sum(final_closes > last_close)
        upside_prob = float(np.mean(final_closes > last_close))
        
        expected_close = float(mean_path[-1, 3])
        expected_chg_pct = float(((expected_close - last_close) / last_close) * 100.0)
        
        p10_close = float(p10_path[-1, 3])
        p90_close = float(p90_path[-1, 3])
        p10_chg_pct = float(((p10_close - last_close) / last_close) * 100.0)
        p90_chg_pct = float(((p90_close - last_close) / last_close) * 100.0)
        dispersion_spread = float(p90_close - p10_close)
        corridor_bandwidth_pct = float((dispersion_spread / last_close) * 100.0)

        overall_low = float(np.min(p10_path[:, 2]))
        overall_high = float(np.max(p90_path[:, 1]))

        hist_ret = np.diff(np.log(np.maximum(clean_df["close"].values[-30:], 1e-5)))
        hist_vol = float(np.std(hist_ret)) if len(hist_ret) > 1 else 0.015
        path_vols = np.std(np.diff(np.log(np.maximum(paths[:, :, 3], 1e-5)), axis=1), axis=1)
        vol_amp = float(np.mean(path_vols) / (hist_vol + 1e-5))

        # Build predicted candlestick list
        forecast_candles = []
        for i in range(pred_len):
            forecast_candles.append({
                "date": future_dates[i],
                "open": round(float(mean_path[i, 0]), 2),
                "high": round(float(mean_path[i, 1]), 2),
                "low": round(float(mean_path[i, 2]), 2),
                "close": round(float(mean_path[i, 3]), 2),
                "volume": int(mean_path[i, 4]),
                "band_low": round(float(p10_path[i, 3]), 2),
                "band_high": round(float(p90_path[i, 3]), 2)
            })

        # Sample 5 ghost paths for visual scenario fan chart
        sample_paths = []
        for p in range(min(5, n_paths)):
            sample_paths.append([
                {"date": future_dates[i], "close": round(float(paths[p, i, 3]), 2)}
                for i in range(pred_len)
            ])

        # Qualitative Confluence Note
        if upside_prob >= 0.70:
            regime = "Bullish Acceleration"
            confluence_badge = "Strong Long Confluence"
        elif upside_prob >= 0.55:
            regime = "Moderate Upward Drift"
            confluence_badge = "Favorable Long Bias"
        elif upside_prob <= 0.35:
            regime = "Bearish Breakdown Pressure"
            confluence_badge = "Caution: Downside Drag"
        else:
            regime = "Neutral Rangebound"
            confluence_badge = "Neutral / Low Edge"

        result = {
            "ticker": ticker,
            "last_close": round(last_close, 2),
            "pred_len": pred_len,
            "n_paths": n_paths,
            "upside_prob": round(upside_prob * 100.0, 1),
            "upside_prob_raw": round(upside_prob, 2),
            "expected_close": round(expected_close, 2),
            "expected_change_pct": round(expected_chg_pct, 2),
            "p10_close": round(p10_close, 2),
            "p90_close": round(p90_close, 2),
            "p10_change_pct": round(p10_chg_pct, 2),
            "p90_change_pct": round(p90_chg_pct, 2),
            "dispersion_spread": round(dispersion_spread, 2),
            "corridor_bandwidth_pct": round(corridor_bandwidth_pct, 2),
            "overall_projected_low": round(overall_low, 2),
            "overall_projected_high": round(overall_high, 2),
            "volatility_amplification": round(vol_amp, 2),
            "regime": regime,
            "confluence_badge": confluence_badge,
            "forecast_candles": forecast_candles,
            "sample_paths": sample_paths,
            "engine_mode": "Kronos Foundation Model" if self._is_loaded else "Monte Carlo Regime Forecaster"
        }

        self._cache[cache_key] = (now, result)
        return result


# Global singleton instance
kronos_engine = KronosEngine()
