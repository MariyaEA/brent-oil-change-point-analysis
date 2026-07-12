import numpy as np
import pandas as pd
import pytest

from src.features import add_time_series_features, event_window_summary


def test_log_returns_match_definition() -> None:
    prices = pd.DataFrame(
        {
            "Date": pd.date_range("2022-01-01", periods=3),
            "Price": [10.0, 20.0, 10.0],
        }
    )
    result = add_time_series_features(prices, rolling_window=2)

    assert np.isnan(result.loc[0, "log_return"])
    assert result.loc[1, "log_return"] == pytest.approx(np.log(2.0))
    assert result.loc[2, "log_return"] == pytest.approx(np.log(0.5))


def test_event_window_summary_uses_nearest_trading_date() -> None:
    prices = pd.DataFrame(
        {
            "Date": pd.bdate_range("2022-01-03", periods=12),
            "Price": np.arange(10.0, 22.0),
        }
    )
    events = pd.DataFrame(
        {
            "event_date": [pd.Timestamp("2022-01-08")],  # Saturday
            "event_name": ["Weekend event"],
            "category": ["Test"],
        }
    )
    result = event_window_summary(prices, events, 2, 2)

    assert len(result) == 1
    assert result.loc[0, "nearest_trading_date"] == pd.Timestamp("2022-01-10")
