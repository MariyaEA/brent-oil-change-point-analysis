"""Plotting functions for the interim EDA."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def _finish(fig: plt.Figure, output_path: str | Path | None) -> plt.Figure:
    fig.tight_layout()
    if output_path is not None:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(path, dpi=160, bbox_inches="tight")
    return fig


def plot_raw_price(frame: pd.DataFrame, output_path: str | Path | None = None) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(frame["Date"], frame["Price"], linewidth=1)
    ax.set_title("Daily Brent Crude Oil Price")
    ax.set_xlabel("Date")
    ax.set_ylabel("USD per barrel")
    ax.grid(alpha=0.25)
    return _finish(fig, output_path)


def plot_log_returns(frame: pd.DataFrame, output_path: str | Path | None = None) -> plt.Figure:
    fig, ax = plt.subplots(figsize=(12, 4.5))
    ax.plot(frame["Date"], frame["log_return"], linewidth=0.7)
    ax.axhline(0, linewidth=0.8)
    ax.set_title("Daily Brent Log Returns")
    ax.set_xlabel("Date")
    ax.set_ylabel("Log return")
    ax.grid(alpha=0.25)
    return _finish(fig, output_path)


def plot_rolling_volatility(
    frame: pd.DataFrame,
    window: int = 30,
    output_path: str | Path | None = None,
) -> plt.Figure:
    column = f"annualized_volatility_{window}"
    if column not in frame.columns:
        raise ValueError(f"Missing feature column: {column}")
    fig, ax = plt.subplots(figsize=(12, 4.5))
    ax.plot(frame["Date"], frame[column], linewidth=0.9)
    ax.set_title(f"Rolling {window}-Observation Annualized Volatility")
    ax.set_xlabel("Date")
    ax.set_ylabel("Annualized volatility")
    ax.grid(alpha=0.25)
    return _finish(fig, output_path)


def plot_price_with_events(
    frame: pd.DataFrame,
    events: pd.DataFrame,
    start_date: str = "2008-01-01",
    output_path: str | Path | None = None,
) -> plt.Figure:
    subset = frame.loc[frame["Date"] >= pd.Timestamp(start_date)].copy()
    event_subset = events.loc[events["event_date"] >= pd.Timestamp(start_date)].copy()

    fig, ax = plt.subplots(figsize=(13, 6))
    ax.plot(subset["Date"], subset["Price"], linewidth=1)
    for idx, event in enumerate(event_subset.itertuples(index=False)):
        ax.axvline(event.event_date, alpha=0.25, linewidth=0.8)
        if idx % 2 == 0:
            y_pos = ax.get_ylim()[1] * 0.92
            ax.text(
                event.event_date,
                y_pos,
                str(event.event_name),
                rotation=90,
                va="top",
                ha="right",
                fontsize=7,
            )
    ax.set_title("Brent Price with Researched Events (2008 onward)")
    ax.set_xlabel("Date")
    ax.set_ylabel("USD per barrel")
    ax.grid(alpha=0.2)
    return _finish(fig, output_path)
