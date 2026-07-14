"""Bayesian change-point utilities for Brent oil prices.

PyMC and ArviZ are imported lazily inside modeling functions so the repository's
lightweight data/API tests can run without compiling the probabilistic stack.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class ModelWindow:
    """Validated data and metadata for one targeted change-point model."""

    frame: pd.DataFrame
    values: np.ndarray
    index: np.ndarray
    start_date: pd.Timestamp
    end_date: pd.Timestamp
    minimum_segment: int


def prepare_model_window(
    prices: pd.DataFrame,
    start_date: str | pd.Timestamp,
    end_date: str | pd.Timestamp,
    minimum_segment: int = 15,
) -> ModelWindow:
    """Filter and validate a modeling window.

    A targeted window is used because one switch-point model cannot represent all
    regimes in the 1987–2022 series. The final report interprets the chosen window
    as a focused case study rather than a complete causal model of the oil market.
    """
    required = {"Date", "Price"}
    missing = required.difference(prices.columns)
    if missing:
        raise ValueError(f"prices is missing required column(s): {sorted(missing)}")
    if minimum_segment < 5:
        raise ValueError("minimum_segment must be at least 5 observations.")

    start = pd.Timestamp(start_date)
    end = pd.Timestamp(end_date)
    if start >= end:
        raise ValueError("start_date must be earlier than end_date.")

    frame = prices.loc[
        prices["Date"].between(start, end, inclusive="both"), ["Date", "Price"]
    ].copy()
    frame = frame.dropna().sort_values("Date").reset_index(drop=True)

    if len(frame) < (2 * minimum_segment + 1):
        raise ValueError(
            "Model window is too short. It must contain observations on both sides "
            "of every allowed switch point."
        )
    if (frame["Price"] <= 0).any():
        raise ValueError("Price values must be positive.")

    values = frame["Price"].to_numpy(dtype=float)
    return ModelWindow(
        frame=frame,
        values=values,
        index=np.arange(len(frame), dtype=int),
        start_date=start,
        end_date=end,
        minimum_segment=minimum_segment,
    )


def build_bayesian_change_point_model(window: ModelWindow) -> Any:
    """Build the required PyMC switch-point model for a change in mean price.

    Model specification:
    - tau: discrete uniform switch point
    - mu_before / mu_after: mean prices before and after tau
    - sigma: common residual standard deviation
    - pm.math.switch: selects the active mean for each observation
    - Normal likelihood: connects the switched mean to observed prices
    """
    try:
        import pymc as pm
    except ImportError as exc:  # pragma: no cover - depends on optional runtime
        raise RuntimeError(
            "PyMC is required for Task 2. Install the full requirements.txt file."
        ) from exc

    y = window.values
    prior_center = float(y.mean())
    prior_scale = max(float(y.std(ddof=1) * 2), 1.0)
    sigma_scale = max(float(y.std(ddof=1)), 1.0)

    with pm.Model() as model:
        tau = pm.DiscreteUniform(
            "tau",
            lower=window.minimum_segment,
            upper=len(y) - window.minimum_segment - 1,
        )
        mu_before = pm.Normal(
            "mu_before", mu=prior_center, sigma=prior_scale
        )
        mu_after = pm.Normal(
            "mu_after", mu=prior_center, sigma=prior_scale
        )
        sigma = pm.HalfNormal("sigma", sigma=sigma_scale)

        switched_mean = pm.math.switch(
            window.index < tau,
            mu_before,
            mu_after,
        )
        pm.Normal("observed_price", mu=switched_mean, sigma=sigma, observed=y)

    return model


def sample_change_point_model(
    model: Any,
    draws: int = 5_000,
    tune: int = 2_000,
    chains: int = 4,
    random_seed: int = 42,
) -> Any:
    """Run MCMC with settings chosen to diagnose the discrete tau reliably."""
    if draws < 500 or tune < 500:
        raise ValueError("Use at least 500 draws and 500 tuning iterations.")
    if chains < 2:
        raise ValueError("Use at least two chains for convergence diagnostics.")

    try:
        import pymc as pm
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("PyMC is not installed.") from exc

    with model:
        trace = pm.sample(
            draws=draws,
            tune=tune,
            chains=chains,
            cores=1,
            random_seed=random_seed,
            target_accept=0.90,
            progressbar=False,
            return_inferencedata=True,
        )
    return trace


def posterior_samples_frame(trace: Any, thin: int = 5) -> pd.DataFrame:
    """Convert posterior draws into a tidy frame suitable for saved artifacts."""
    if thin < 1:
        raise ValueError("thin must be at least 1.")
    variables = ["tau", "mu_before", "mu_after", "sigma"]
    missing = [name for name in variables if name not in trace.posterior]
    if missing:
        raise ValueError(f"Posterior is missing variable(s): {missing}")

    stacked = trace.posterior[variables].stack(sample=("chain", "draw"))
    frame = stacked.to_dataframe().reset_index()
    frame = frame.loc[::thin, ["chain", "draw", *variables]].reset_index(drop=True)
    return frame


def summarize_posterior_samples(
    samples: pd.DataFrame,
    model_dates: pd.Series,
    hdi_probability: float = 0.94,
) -> dict[str, Any]:
    """Create stakeholder-ready estimates from posterior samples.

    This helper intentionally operates on a DataFrame, making the calculation
    testable without importing PyMC or ArviZ.
    """
    required = {"tau", "mu_before", "mu_after", "sigma"}
    missing = required.difference(samples.columns)
    if missing:
        raise ValueError(f"samples is missing required column(s): {sorted(missing)}")
    if not 0.5 < hdi_probability < 1:
        raise ValueError("hdi_probability must be between 0.5 and 1.")

    dates = pd.Series(model_dates).reset_index(drop=True)
    if dates.empty:
        raise ValueError("model_dates cannot be empty.")

    alpha = (1.0 - hdi_probability) / 2.0
    tau_values = samples["tau"].round().astype(int).clip(0, len(dates) - 1)
    tau_median = int(tau_values.median())
    tau_low = int(tau_values.quantile(alpha, interpolation="nearest"))
    tau_high = int(tau_values.quantile(1 - alpha, interpolation="nearest"))

    before_mean = float(samples["mu_before"].mean())
    after_mean = float(samples["mu_after"].mean())
    absolute_change = after_mean - before_mean
    percent_change = (absolute_change / before_mean) * 100.0

    return {
        "tau_index_median": tau_median,
        "change_point_date": pd.Timestamp(dates.iloc[tau_median]).strftime("%Y-%m-%d"),
        "change_point_date_hdi_low": pd.Timestamp(dates.iloc[tau_low]).strftime("%Y-%m-%d"),
        "change_point_date_hdi_high": pd.Timestamp(dates.iloc[tau_high]).strftime("%Y-%m-%d"),
        "mu_before_mean": before_mean,
        "mu_after_mean": after_mean,
        "absolute_change_usd": absolute_change,
        "percent_change": percent_change,
        "probability_after_lower": float(
            (samples["mu_after"] < samples["mu_before"]).mean()
        ),
        "sigma_mean": float(samples["sigma"].mean()),
        "posterior_draws_saved": int(len(samples)),
        "hdi_probability": hdi_probability,
    }


def associate_nearest_event(
    change_date: str | pd.Timestamp,
    events: pd.DataFrame,
) -> dict[str, Any]:
    """Find the event nearest a posterior change date without asserting causality."""
    if not {"event_date", "event_name", "category"}.issubset(events.columns):
        raise ValueError("events must contain event_date, event_name, and category.")
    if events.empty:
        raise ValueError("events cannot be empty.")

    date = pd.Timestamp(change_date)
    work = events.copy()
    work["event_date"] = pd.to_datetime(work["event_date"], errors="raise")
    work["distance_days"] = (work["event_date"] - date).dt.days
    nearest = work.iloc[work["distance_days"].abs().argmin()]

    return {
        "event_date": nearest["event_date"].strftime("%Y-%m-%d"),
        "event_name": str(nearest["event_name"]),
        "event_category": str(nearest["category"]),
        "distance_days": int(nearest["distance_days"]),
        "interpretation_guardrail": (
            "Temporal proximity supports an event-association hypothesis; it does "
            "not establish that the event caused the structural break."
        ),
    }


def save_json(payload: dict[str, Any], path: str | Path) -> None:
    """Write a JSON artifact with parent-directory creation."""
    import json

    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)
