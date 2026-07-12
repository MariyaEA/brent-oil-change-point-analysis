"""Reproduce the interim EDA outputs from the command line."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.data_loader import load_brent_prices, load_event_data
from src.diagnostics import stationarity_report
from src.features import add_time_series_features, event_window_summary
from src.plotting import (
    plot_log_returns,
    plot_price_with_events,
    plot_raw_price,
    plot_rolling_volatility,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--prices",
        type=Path,
        default=PROJECT_ROOT / "data/raw/BrentOilPrices.csv",
        help="Path to the Brent price CSV.",
    )
    parser.add_argument(
        "--events",
        type=Path,
        default=PROJECT_ROOT / "data/events/oil_market_events.csv",
        help="Path to the researched event CSV.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=PROJECT_ROOT / "reports",
        help="Directory for generated outputs.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    figure_dir = args.output_dir / "figures"
    figure_dir.mkdir(parents=True, exist_ok=True)

    prices = load_brent_prices(args.prices)
    events = load_event_data(args.events)
    analysis = add_time_series_features(prices, rolling_window=30)

    diagnostics = pd.concat(
        [
            stationarity_report(analysis["Price"], "Price"),
            stationarity_report(analysis["log_return"], "Log return"),
        ],
        ignore_index=True,
    )
    diagnostics.to_csv(args.output_dir / "stationarity_results.csv", index=False)

    event_summary = event_window_summary(analysis, events, 5, 5)
    event_summary.to_csv(args.output_dir / "event_window_summary.csv", index=False)

    figures = [
        plot_raw_price(analysis, figure_dir / "raw_brent_price.png"),
        plot_log_returns(analysis, figure_dir / "brent_log_returns.png"),
        plot_rolling_volatility(analysis, 30, figure_dir / "rolling_volatility.png"),
        plot_price_with_events(analysis, events, "2008-01-01", figure_dir / "price_with_events.png"),
    ]
    for fig in figures:
        plt.close(fig)

    max_price_row = analysis.loc[analysis["Price"].idxmax()]
    min_price_row = analysis.loc[analysis["Price"].idxmin()]
    vol_col = "annualized_volatility_30"
    max_vol_row = analysis.loc[analysis[vol_col].idxmax()]
    summary = {
        "observations": int(len(analysis)),
        "start_date": analysis["Date"].min().date().isoformat(),
        "end_date": analysis["Date"].max().date().isoformat(),
        "mean_price": round(float(analysis["Price"].mean()), 4),
        "median_price": round(float(analysis["Price"].median()), 4),
        "max_price": round(float(max_price_row["Price"]), 4),
        "max_price_date": max_price_row["Date"].date().isoformat(),
        "min_price": round(float(min_price_row["Price"]), 4),
        "min_price_date": min_price_row["Date"].date().isoformat(),
        "highest_rolling_volatility_date": max_vol_row["Date"].date().isoformat(),
        "highest_rolling_volatility": round(float(max_vol_row[vol_col]), 4),
    }
    (args.output_dir / "eda_summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
