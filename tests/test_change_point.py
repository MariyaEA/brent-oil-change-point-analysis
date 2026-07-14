from __future__ import annotations

import pandas as pd
import pytest

from src.change_point import (
    associate_nearest_event,
    prepare_model_window,
    summarize_posterior_samples,
)


def sample_prices() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Date": pd.date_range("2020-01-01", periods=50, freq="D"),
            "Price": [50.0] * 25 + [35.0] * 25,
        }
    )


def test_prepare_model_window_filters_and_indexes() -> None:
    result = prepare_model_window(
        sample_prices(), "2020-01-05", "2020-02-10", minimum_segment=5
    )
    assert result.frame.iloc[0]["Date"] == pd.Timestamp("2020-01-05")
    assert len(result.index) == len(result.frame)
    assert result.values.dtype.kind == "f"


def test_prepare_model_window_rejects_short_window() -> None:
    with pytest.raises(ValueError, match="too short"):
        prepare_model_window(
            sample_prices(), "2020-01-01", "2020-01-08", minimum_segment=5
        )


def test_summarize_posterior_samples() -> None:
    samples = pd.DataFrame(
        {
            "tau": [23, 24, 25, 25, 26, 25],
            "mu_before": [50, 51, 49, 50, 50, 50],
            "mu_after": [35, 34, 36, 35, 35, 35],
            "sigma": [2, 2.2, 1.9, 2.1, 2.0, 2.0],
        }
    )
    result = summarize_posterior_samples(samples, sample_prices()["Date"])
    assert result["change_point_date"] == "2020-01-26"
    assert result["percent_change"] < 0
    assert result["probability_after_lower"] == 1.0


def test_associate_nearest_event() -> None:
    events = pd.DataFrame(
        {
            "event_date": ["2020-01-20", "2020-02-15"],
            "event_name": ["Event A", "Event B"],
            "category": ["Economic", "OPEC"],
        }
    )
    result = associate_nearest_event("2020-01-25", events)
    assert result["event_name"] == "Event A"
    assert result["distance_days"] == -5
