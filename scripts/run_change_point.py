"""Fit the final Bayesian switch-point model and save reproducible artifacts."""

from __future__ import annotations

import json
from pathlib import Path
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.change_point import (  # noqa: E402
    associate_nearest_event,
    build_bayesian_change_point_model,
    posterior_samples_frame,
    prepare_model_window,
    sample_change_point_model,
    save_json,
    summarize_posterior_samples,
)
from src.data_loader import load_brent_prices, load_event_data  # noqa: E402

PRICE_PATH = ROOT / "data" / "raw" / "BrentOilPrices.csv"
EVENT_PATH = ROOT / "data" / "events" / "oil_market_events.csv"
MODEL_DIR = ROOT / "reports" / "model"
FIGURE_DIR = ROOT / "reports" / "figures"
MODEL_START = "2014-09-01"
MODEL_END = "2015-03-31"
MINIMUM_SEGMENT = 15


def main() -> None:
    try:
        import arviz as az
        import pymc as pm
    except ImportError as exc:
        raise SystemExit(
            "PyMC and ArviZ are required. Run: pip install -r requirements.txt"
        ) from exc

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)

    prices = load_brent_prices(PRICE_PATH)
    events = load_event_data(EVENT_PATH)
    window = prepare_model_window(
        prices,
        start_date=MODEL_START,
        end_date=MODEL_END,
        minimum_segment=MINIMUM_SEGMENT,
    )

    model = build_bayesian_change_point_model(window)
    trace = sample_change_point_model(model)

    summary = az.summary(
        trace,
        var_names=["tau", "mu_before", "mu_after", "sigma"],
        hdi_prob=0.94,
        round_to=4,
    )
    summary.index.name = "parameter"
    summary.to_csv(MODEL_DIR / "mcmc_summary.csv")

    samples = posterior_samples_frame(trace, thin=5)
    samples.to_csv(MODEL_DIR / "posterior_samples.csv", index=False)

    insight = summarize_posterior_samples(
        samples,
        model_dates=window.frame["Date"],
        hdi_probability=0.94,
    )
    insight["model_window_start"] = MODEL_START
    insight["model_window_end"] = MODEL_END
    insight["observations"] = int(len(window.frame))
    insight["draws_per_chain"] = 5_000
    insight["tuning_steps_per_chain"] = 2_000
    insight["chains"] = 4
    insight["maximum_r_hat"] = float(summary["r_hat"].max())
    insight["minimum_bulk_ess"] = float(summary["ess_bulk"].min())
    insight["model_description"] = (
        "Single mean-shift Normal model with a DiscreteUniform tau and "
        "pm.math.switch. This is a transparent baseline for one targeted window."
    )
    insight["nearest_event"] = associate_nearest_event(
        insight["change_point_date"], events
    )
    save_json(insight, MODEL_DIR / "change_point_results.json")

    # Price window with inferred break and researched event.
    cp_date = pd.Timestamp(insight["change_point_date"])
    event_date = pd.Timestamp(insight["nearest_event"]["event_date"])
    fig, ax = plt.subplots(figsize=(12, 5.5))
    ax.plot(window.frame["Date"], window.frame["Price"], linewidth=1.8, label="Brent price")
    ax.axvline(cp_date, linestyle="--", linewidth=2, label=f"Posterior median: {cp_date.date()}")
    ax.axvline(event_date, linestyle=":", linewidth=2, label=f"OPEC decision: {event_date.date()}")
    ax.set_title("Brent Price Around the 2014 OPEC Production Decision")
    ax.set_xlabel("Date")
    ax.set_ylabel("USD per barrel")
    ax.legend(frameon=False)
    ax.grid(alpha=0.2)
    fig.tight_layout()
    fig.savefig(FIGURE_DIR / "change_point_window.png", dpi=180, bbox_inches="tight")
    plt.close(fig)

    # Trace diagnostics.
    axes = az.plot_trace(trace, var_names=["tau", "mu_before", "mu_after", "sigma"], compact=True)
    fig = np.asarray(axes).ravel()[0].figure
    fig.suptitle("MCMC Trace and Marginal Distributions", y=1.01)
    fig.tight_layout()
    fig.savefig(FIGURE_DIR / "model_trace.png", dpi=170, bbox_inches="tight")
    plt.close(fig)

    # Tau posterior labeled with dates.
    tau_counts = samples["tau"].round().astype(int).value_counts(normalize=True).sort_index()
    tau_dates = window.frame.loc[tau_counts.index, "Date"]
    fig, ax = plt.subplots(figsize=(10.5, 4.8))
    ax.bar(tau_dates, tau_counts.values, width=1.5)
    ax.axvline(cp_date, linestyle="--", linewidth=1.8, label="Posterior median")
    ax.set_title("Posterior Distribution of the Change Date (tau)")
    ax.set_xlabel("Candidate change date")
    ax.set_ylabel("Posterior probability")
    ax.legend(frameon=False)
    ax.grid(axis="y", alpha=0.2)
    fig.tight_layout()
    fig.savefig(FIGURE_DIR / "tau_posterior.png", dpi=180, bbox_inches="tight")
    plt.close(fig)

    # Before/after parameter posteriors.
    fig, ax = plt.subplots(figsize=(10.5, 4.8))
    ax.hist(samples["mu_before"], bins=40, alpha=0.65, density=True, label="Mean before")
    ax.hist(samples["mu_after"], bins=40, alpha=0.65, density=True, label="Mean after")
    ax.set_title("Posterior Mean Price Before and After the Change Point")
    ax.set_xlabel("USD per barrel")
    ax.set_ylabel("Density")
    ax.legend(frameon=False)
    ax.grid(axis="y", alpha=0.2)
    fig.tight_layout()
    fig.savefig(FIGURE_DIR / "parameter_posteriors.png", dpi=180, bbox_inches="tight")
    plt.close(fig)

    # Posterior predictive check.
    with model:
        predictive = pm.sample_posterior_predictive(
            trace,
            var_names=["observed_price"],
            random_seed=42,
            progressbar=False,
        )
    predicted = predictive.posterior_predictive["observed_price"].stack(
        sample=("chain", "draw")
    )
    pred_mean = predicted.mean("sample").values
    pred_low = predicted.quantile(0.03, dim="sample").values
    pred_high = predicted.quantile(0.97, dim="sample").values
    fig, ax = plt.subplots(figsize=(12, 5.5))
    ax.plot(window.frame["Date"], window.values, linewidth=1.4, label="Observed")
    ax.plot(window.frame["Date"], pred_mean, linewidth=2, label="Posterior predictive mean")
    ax.fill_between(window.frame["Date"], pred_low, pred_high, alpha=0.25, label="94% predictive interval")
    ax.axvline(cp_date, linestyle="--", linewidth=1.6)
    ax.set_title("Posterior Predictive Check")
    ax.set_xlabel("Date")
    ax.set_ylabel("USD per barrel")
    ax.legend(frameon=False)
    ax.grid(alpha=0.2)
    fig.tight_layout()
    fig.savefig(FIGURE_DIR / "posterior_predictive.png", dpi=180, bbox_inches="tight")
    plt.close(fig)

    print(json.dumps(insight, indent=2))


if __name__ == "__main__":
    main()
