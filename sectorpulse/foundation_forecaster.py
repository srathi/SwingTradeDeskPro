"""
Foundation Model & Probabilistic Forecaster for SectorPulse.
Integrates Amazon Chronos (Chronos-Bolt / Chronos-T5) with vectorized Monte Carlo & polynomial inflection fallback.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import logging
import warnings
import numpy as np
import pandas as pd

logger = logging.getLogger("SectorPulse.Forecaster")


@dataclass
class ForecastResult:
    median_peak_horizon_days: int
    exhaustion_probability: float
    forecast_trajectories: List[List[float]]
    is_foundation_model: bool
    model_name: str


class ChronosForecaster:
    """
    Zero-shot probabilistic forecasting on Mansfield Relative Strength time-series.
    Attempts to load Amazon Chronos (Chronos-Bolt / Chronos-T5) via PyTorch if available;
    gracefully falls back to high-order Monte Carlo Drift Diffusion if PyTorch/CUDA is missing.
    """

    def __init__(self, model_name: str = "amazon/chronos-bolt-small", prediction_length: int = 30, num_samples: int = 100):
        self.model_name = model_name
        self.prediction_length = prediction_length
        self.num_samples = num_samples
        self.pipeline = None
        self._initialized = False

    def _init_chronos_if_available(self):
        if self._initialized:
            return
        self._initialized = True
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                import torch
                from chronos import BaseChronosPipeline
                device = "cuda" if torch.cuda.is_available() else "cpu"
                self.pipeline = BaseChronosPipeline.from_pretrained(
                    self.model_name,
                    device_map=device,
                    torch_dtype=torch.bfloat16 if torch.cuda.is_available() else torch.float32,
                )
                logger.info(f"Loaded Amazon Chronos pipeline on {device}: {self.model_name}")
        except Exception as e:
            logger.info(f"Chronos PyTorch pipeline unavailable ({e}). Using Vectorized Monte Carlo Econometric Fallback.")
            self.pipeline = None

    def forecast_relative_strength(self, mrs_series: pd.Series) -> ForecastResult:
        """
        Samples N=100 forecast trajectories for 30–60 periods into the future.
        Derives median peak horizon and exhaustion probability (% trajectories rolling over).
        """
        clean_mrs = mrs_series.dropna().values
        if len(clean_mrs) < 15:
            return ForecastResult(
                median_peak_horizon_days=20,
                exhaustion_probability=0.20,
                forecast_trajectories=[],
                is_foundation_model=False,
                model_name="Priors_Baseline"
            )

        self._init_chronos_if_available()

        # If Chronos is loaded, run foundation model inference
        if self.pipeline is not None:
            try:
                import torch
                context_tensor = torch.tensor(clean_mrs[-120:], dtype=torch.float32).unsqueeze(0)
                forecast = self.pipeline.predict(context_tensor, self.prediction_length, num_samples=self.num_samples)
                # forecast shape: [1, num_samples, prediction_length]
                samples = forecast[0].numpy()
                return self._analyze_forecast_trajectories(samples, model_name=f"Chronos ({self.model_name})", is_foundation=True)
            except Exception as e:
                logger.warning(f"Chronos inference error ({e}), falling back to Monte Carlo...")

        # Analytical Monte Carlo Drift-Diffusion Fallback
        return self._monte_carlo_forecast(clean_mrs)

    def _monte_carlo_forecast(self, history: np.ndarray) -> ForecastResult:
        """
        Vectorized Geometric-Ornstein-Uhlenbeck Drift Diffusion simulation.
        Models momentum persistence with mean-reversion pull towards structural zero.
        """
        recent_window = history[-40:] if len(history) >= 40 else history
        recent_diff = np.diff(recent_window)
        drift = np.mean(recent_diff[-5:]) if len(recent_diff) >= 5 else 0.0
        volatility = np.std(recent_diff) if len(recent_diff) > 1 and np.std(recent_diff) > 0 else 0.5

        current_val = history[-1]
        steps = self.prediction_length
        n_paths = self.num_samples

        # Random shocks: N(0, 1)
        shocks = np.random.normal(0, 1, size=(n_paths, steps))

        # Mean reversion theta towards 0 MRS
        theta = 0.035
        paths = np.zeros((n_paths, steps))

        for t in range(steps):
            prev = current_val if t == 0 else paths[:, t - 1]
            # OU process: dX = (drift * exp(-0.05*t) - theta * prev) + vol * dW
            dx = (drift * np.exp(-0.05 * t) - theta * prev) + volatility * shocks[:, t]
            paths[:, t] = prev + dx

        return self._analyze_forecast_trajectories(paths, model_name="Vectorized_MonteCarlo_OU", is_foundation=False)

    def _analyze_forecast_trajectories(self, paths: np.ndarray, model_name: str, is_foundation: bool) -> ForecastResult:
        """
        Analyzes N=100 forecast paths to compute:
        1. Median Peak Horizon (days until trajectory reaches maximum before flattening).
        2. Exhaustion Probability (% of paths with negative slope over the next 10 bars).
        """
        median_path = np.median(paths, axis=0)
        peak_idx = int(np.argmax(median_path))
        peak_horizon = max(5, peak_idx + 1)

        # Exhaustion probability: % paths whose 10-bar forward slope is negative
        check_bar = min(10, paths.shape[1] - 1)
        diff_10d = paths[:, check_bar] - paths[:, 0]
        exhaustion_prob = float(np.mean(diff_10d < 0))

        # Sub-sample 3 representational quantiles for UI rendering: 10th, 50th, 90th
        q_10 = np.quantile(paths, 0.10, axis=0).round(2).tolist()
        q_50 = median_path.round(2).tolist()
        q_90 = np.quantile(paths, 0.90, axis=0).round(2).tolist()

        return ForecastResult(
            median_peak_horizon_days=peak_horizon,
            exhaustion_probability=round(exhaustion_prob, 2),
            forecast_trajectories=[q_10, q_50, q_90],
            is_foundation_model=is_foundation,
            model_name=model_name
        )
