"""Data loading and validation utilities.

The provided Brent dataset contains two date formats. This module parses both
explicitly so results do not depend on locale-specific date inference.
"""

from __future__ import annotations

from pathlib import Path
import warnings

import pandas as pd


class DataValidationError(ValueError):
    """Raised when an input file exists but does not satisfy the expected schema."""


def _validate_file(path: str | Path) -> Path:
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(
            f"Input file not found: {file_path}. Check the path or copy the challenge data into data/raw/."
        )
    if not file_path.is_file():
        raise DataValidationError(f"Expected a file but received: {file_path}")
    return file_path


def parse_brent_dates(values: pd.Series) -> pd.Series:
    """Parse the two date formats present in the challenge dataset.

    Supported formats:
    - ``20-May-87``
    - ``Nov 14, 2022``

    A final generic parser is used only for otherwise unmatched values.
    """
    text = values.astype("string").str.strip()
    parsed = pd.Series(pd.NaT, index=text.index, dtype="datetime64[ns]")

    short_mask = text.str.match(r"^\d{2}-[A-Za-z]{3}-\d{2}$", na=False)
    long_mask = text.str.match(r"^[A-Za-z]{3} \d{2}, \d{4}$", na=False)

    parsed.loc[short_mask] = pd.to_datetime(
        text.loc[short_mask], format="%d-%b-%y", errors="coerce"
    )
    parsed.loc[long_mask] = pd.to_datetime(
        text.loc[long_mask], format="%b %d, %Y", errors="coerce"
    )

    remaining = ~(short_mask | long_mask)
    if remaining.any():
        parsed.loc[remaining] = pd.to_datetime(text.loc[remaining], errors="coerce")

    return parsed


def load_brent_prices(path: str | Path) -> pd.DataFrame:
    """Load, validate, and sort the Brent oil price dataset."""
    file_path = _validate_file(path)

    try:
        frame = pd.read_csv(file_path)
    except (pd.errors.ParserError, UnicodeDecodeError) as exc:
        raise DataValidationError(f"Could not parse CSV file: {file_path}") from exc

    required = {"Date", "Price"}
    missing = required.difference(frame.columns)
    if missing:
        raise DataValidationError(
            f"Missing required column(s): {sorted(missing)}. Expected Date and Price."
        )

    clean = frame.loc[:, ["Date", "Price"]].copy()
    clean["Date"] = parse_brent_dates(clean["Date"])
    clean["Price"] = pd.to_numeric(clean["Price"], errors="coerce")

    invalid_dates = int(clean["Date"].isna().sum())
    invalid_prices = int(clean["Price"].isna().sum())
    if invalid_dates or invalid_prices:
        raise DataValidationError(
            f"Invalid values detected: {invalid_dates} date(s), {invalid_prices} price(s)."
        )

    if (clean["Price"] <= 0).any():
        raise DataValidationError("Brent prices must be strictly positive for log-return analysis.")

    duplicate_count = int(clean["Date"].duplicated().sum())
    if duplicate_count:
        warnings.warn(
            f"Found {duplicate_count} duplicate date(s); keeping the last observation for each date.",
            stacklevel=2,
        )
        clean = clean.drop_duplicates(subset="Date", keep="last")

    return clean.sort_values("Date").reset_index(drop=True)


def load_event_data(path: str | Path) -> pd.DataFrame:
    """Load and validate the researched event catalogue."""
    file_path = _validate_file(path)
    try:
        events = pd.read_csv(file_path)
    except (pd.errors.ParserError, UnicodeDecodeError) as exc:
        raise DataValidationError(f"Could not parse event CSV: {file_path}") from exc

    required = {
        "event_date",
        "event_name",
        "category",
        "description",
        "hypothesized_short_term_pressure",
        "source_url",
    }
    missing = required.difference(events.columns)
    if missing:
        raise DataValidationError(f"Event file is missing columns: {sorted(missing)}")

    events = events.copy()
    events["event_date"] = pd.to_datetime(events["event_date"], errors="coerce")
    if events["event_date"].isna().any():
        raise DataValidationError("One or more event dates could not be parsed.")
    if events["event_name"].astype(str).str.strip().eq("").any():
        raise DataValidationError("Event names cannot be blank.")

    return events.sort_values("event_date").reset_index(drop=True)
