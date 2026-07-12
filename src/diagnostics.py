"""Statistical diagnostics used during exploratory time-series analysis."""

from __future__ import annotations

import warnings

import pandas as pd
from statsmodels.tsa.stattools import adfuller, kpss
from statsmodels.tools.sm_exceptions import InterpolationWarning


def stationarity_report(series: pd.Series, series_name: str) -> pd.DataFrame:
    """Return Augmented Dickey-Fuller and KPSS results for a numeric series.

    ADF null hypothesis: unit root / non-stationary.
    KPSS null hypothesis: level-stationary.
    Using both tests provides a more balanced diagnostic than either test alone.
    """
    values = pd.Series(series).dropna().astype(float)
    if len(values) < 30:
        raise ValueError("At least 30 non-missing observations are required.")

    adf_stat, adf_p, adf_lags, adf_nobs, *_ = adfuller(values, autolag="AIC")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", InterpolationWarning)
        kpss_stat, kpss_p, kpss_lags, _ = kpss(values, regression="c", nlags="auto")

    return pd.DataFrame(
        [
            {
                "series": series_name,
                "test": "ADF",
                "statistic": adf_stat,
                "p_value": adf_p,
                "lags": adf_lags,
                "observations": adf_nobs,
                "null_hypothesis": "Unit root / non-stationary",
                "decision_at_5pct": "Reject null" if adf_p < 0.05 else "Fail to reject null",
            },
            {
                "series": series_name,
                "test": "KPSS",
                "statistic": kpss_stat,
                "p_value": kpss_p,
                "lags": kpss_lags,
                "observations": len(values),
                "null_hypothesis": "Level-stationary",
                "decision_at_5pct": "Reject null" if kpss_p < 0.05 else "Fail to reject null",
            },
        ]
    )
