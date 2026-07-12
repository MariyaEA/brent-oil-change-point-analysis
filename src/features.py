"""Feature engineering for oil-price time series analysis."""

from __future__ import annotations

import numpy as np
import pandas as pd


def add_time_series_features(
    prices: pd.DataFrame,
    rolling_window: int = 30,
    trading_days_per_year: int = 252,
) -> pd.DataFrame:
    """Add log prices, log returns, rolling trend, and annualized volatility."""
    if rolling_window < 2:
        raise ValueError("rolling_window must be at least 2.")
    if trading_days_per_year <= 0:
        raise ValueError("trading_days_per_year must be positive.")
    if not {"Date", "Price"}.issubset(prices.columns):
        raise ValueError("prices must contain Date and Price columns.")
    if (prices["Price"] <= 0).any():
        raise ValueError("Prices must be positive before taking logarithms.")

    frame = prices.copy()
    frame["log_price"] = np.log(frame["Price"])
    frame["log_return"] = frame["log_price"].diff()
    frame[f"rolling_mean_{rolling_window}"] = frame["Price"].rolling(
        rolling_window, min_periods=max(2, rolling_window // 3)
    ).mean()
    frame[f"rolling_std_{rolling_window}"] = frame["log_return"].rolling(
        rolling_window, min_periods=max(2, rolling_window // 3)
    ).std()
    frame[f"annualized_volatility_{rolling_window}"] = (
        frame[f"rolling_std_{rolling_window}"] * np.sqrt(trading_days_per_year)
    )
    return frame


def event_window_summary(
    prices: pd.DataFrame,
    events: pd.DataFrame,
    observations_before: int = 5,
    observations_after: int = 5,
) -> pd.DataFrame:
    """Calculate descriptive price changes around researched events.

    The window is measured in observed trading days, not calendar days. Results are
    exploratory associations and must not be interpreted as causal effects.
    """
    if observations_before < 1 or observations_after < 1:
        raise ValueError("Event windows must include at least one observation on each side.")

    price_frame = prices.sort_values("Date").reset_index(drop=True)
    event_frame = events.sort_values("event_date").reset_index(drop=True)
    dates = price_frame["Date"].to_numpy(dtype="datetime64[ns]")

    rows: list[dict[str, object]] = []
    for event in event_frame.itertuples(index=False):
        event_date = np.datetime64(event.event_date)
        event_idx = int(np.searchsorted(dates, event_date, side="left"))
        if event_idx >= len(price_frame):
            continue
        before_idx = event_idx - observations_before
        after_idx = event_idx + observations_after
        if before_idx < 0 or after_idx >= len(price_frame):
            continue

        before_price = float(price_frame.loc[before_idx, "Price"])
        event_price = float(price_frame.loc[event_idx, "Price"])
        after_price = float(price_frame.loc[after_idx, "Price"])
        rows.append(
            {
                "event_date": pd.Timestamp(event.event_date),
                "nearest_trading_date": price_frame.loc[event_idx, "Date"],
                "event_name": event.event_name,
                "category": event.category,
                "price_before": before_price,
                "price_on_or_after_event": event_price,
                "price_after": after_price,
                "pre_to_post_change_pct": ((after_price / before_price) - 1.0) * 100.0,
                "event_to_post_change_pct": ((after_price / event_price) - 1.0) * 100.0,
                "window_observations_before": observations_before,
                "window_observations_after": observations_after,
            }
        )

    return pd.DataFrame(rows)
