"""Flask API serving Brent prices, event context, and model outputs."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
import json
import sys
from typing import Any

import pandas as pd
from flask import Flask, jsonify, request
from flask_cors import CORS

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.data_loader import DataValidationError, load_brent_prices, load_event_data  # noqa: E402


class ApiRequestError(ValueError):
    """Raised for client-supplied query parameters that cannot be processed."""


@lru_cache(maxsize=1)
def _load_prices(path: str) -> pd.DataFrame:
    return load_brent_prices(path)


@lru_cache(maxsize=1)
def _load_events(path: str) -> pd.DataFrame:
    return load_event_data(path)


@lru_cache(maxsize=1)
def _load_json(path: str) -> dict[str, Any]:
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"Required model artifact not found: {file_path}")
    with file_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


@lru_cache(maxsize=1)
def _load_event_windows(path: str) -> pd.DataFrame:
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"Required event-window artifact not found: {file_path}")
    frame = pd.read_csv(file_path)
    for column in ("event_date", "nearest_trading_date"):
        if column in frame.columns:
            frame[column] = pd.to_datetime(frame[column], errors="coerce")
    return frame


def _parse_optional_date(value: str | None, name: str) -> pd.Timestamp | None:
    if value is None or not value.strip():
        return None
    try:
        return pd.Timestamp(value)
    except (ValueError, TypeError) as exc:
        raise ApiRequestError(f"{name} must be a valid date in YYYY-MM-DD format.") from exc


def _filter_dates(
    frame: pd.DataFrame,
    date_column: str,
    start_date: str | None,
    end_date: str | None,
) -> pd.DataFrame:
    start = _parse_optional_date(start_date, "start_date")
    end = _parse_optional_date(end_date, "end_date")
    if start is not None and end is not None and start > end:
        raise ApiRequestError("start_date cannot be later than end_date.")

    filtered = frame
    if start is not None:
        filtered = filtered.loc[filtered[date_column] >= start]
    if end is not None:
        filtered = filtered.loc[filtered[date_column] <= end]
    return filtered.copy()


def _resample_prices(frame: pd.DataFrame, frequency: str) -> pd.DataFrame:
    aliases = {
        "daily": None,
        "weekly": "W-FRI",
        "monthly": "ME",
    }
    if frequency not in aliases:
        raise ApiRequestError("frequency must be one of: daily, weekly, monthly.")
    alias = aliases[frequency]
    if alias is None:
        return frame
    return (
        frame.set_index("Date")["Price"]
        .resample(alias)
        .mean()
        .dropna()
        .rename("Price")
        .reset_index()
    )


def create_app(base_dir: str | Path | None = None) -> Flask:
    """Application factory used by both the CLI server and unit tests."""
    app = Flask(__name__)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    root = Path(base_dir).resolve() if base_dir else ROOT
    price_path = root / "data" / "raw" / "BrentOilPrices.csv"
    event_path = root / "data" / "events" / "oil_market_events.csv"
    model_path = root / "reports" / "model" / "change_point_results.json"
    event_windows_path = root / "reports" / "event_window_summary.csv"

    @app.errorhandler(ApiRequestError)
    def handle_bad_request(error: ApiRequestError):
        return jsonify({"error": str(error), "status": 400}), 400

    @app.errorhandler(FileNotFoundError)
    @app.errorhandler(DataValidationError)
    def handle_data_error(error: Exception):
        return jsonify({"error": str(error), "status": 500}), 500

    @app.errorhandler(Exception)
    def handle_unexpected_error(error: Exception):
        app.logger.exception("Unhandled API error")
        return jsonify({"error": "Unexpected server error.", "status": 500}), 500

    @app.get("/api/health")
    def health():
        return jsonify({"status": "ok", "service": "Birhan Energies Brent API"})

    @app.get("/api/prices")
    def prices_endpoint():
        prices = _load_prices(str(price_path))
        filtered = _filter_dates(
            prices,
            "Date",
            request.args.get("start_date"),
            request.args.get("end_date"),
        )
        frequency = request.args.get("frequency", "weekly").lower()
        filtered = _resample_prices(filtered, frequency)

        records = [
            {"date": row.Date.strftime("%Y-%m-%d"), "price": round(float(row.Price), 3)}
            for row in filtered.itertuples(index=False)
        ]
        return jsonify(
            {
                "frequency": frequency,
                "count": len(records),
                "data": records,
            }
        )

    @app.get("/api/events")
    def events_endpoint():
        events = _load_events(str(event_path))
        filtered = _filter_dates(
            events,
            "event_date",
            request.args.get("start_date"),
            request.args.get("end_date"),
        )
        category = request.args.get("category")
        if category and category.lower() != "all":
            filtered = filtered.loc[
                filtered["category"].str.contains(category, case=False, na=False)
            ]

        records = []
        for row in filtered.itertuples(index=False):
            records.append(
                {
                    "date": row.event_date.strftime("%Y-%m-%d"),
                    "name": row.event_name,
                    "category": row.category,
                    "description": row.description,
                    "pressure": row.hypothesized_short_term_pressure,
                    "source_name": getattr(row, "source_name", ""),
                    "source_url": row.source_url,
                }
            )
        categories = sorted(events["category"].dropna().unique().tolist())
        return jsonify({"count": len(records), "categories": categories, "data": records})

    @app.get("/api/change-points")
    def change_points_endpoint():
        results = _load_json(str(model_path))
        return jsonify({"count": 1, "data": [results]})

    @app.get("/api/event-correlations")
    def event_correlations_endpoint():
        frame = _load_event_windows(str(event_windows_path))
        filtered = _filter_dates(
            frame,
            "event_date",
            request.args.get("start_date"),
            request.args.get("end_date"),
        )
        if "pre_to_post_change_pct" in filtered.columns:
            filtered = filtered.sort_values(
                "pre_to_post_change_pct", key=lambda s: s.abs(), ascending=False
            )

        records = []
        for row in filtered.head(30).to_dict(orient="records"):
            clean: dict[str, Any] = {}
            for key, value in row.items():
                if isinstance(value, pd.Timestamp):
                    clean[key] = value.strftime("%Y-%m-%d")
                elif pd.isna(value):
                    clean[key] = None
                elif isinstance(value, (int, float)):
                    clean[key] = round(float(value), 4)
                else:
                    clean[key] = value
            records.append(clean)
        return jsonify({"count": len(records), "data": records})

    @app.get("/api/summary")
    def summary_endpoint():
        prices = _load_prices(str(price_path))
        model = _load_json(str(model_path))
        return jsonify(
            {
                "coverage_start": prices["Date"].min().strftime("%Y-%m-%d"),
                "coverage_end": prices["Date"].max().strftime("%Y-%m-%d"),
                "observations": int(len(prices)),
                "average_price": round(float(prices["Price"].mean()), 2),
                "maximum_price": round(float(prices["Price"].max()), 2),
                "minimum_price": round(float(prices["Price"].min()), 2),
                "change_point_date": model["change_point_date"],
                "percent_change": round(float(model["percent_change"]), 1),
                "maximum_r_hat": round(float(model["maximum_r_hat"]), 4),
            }
        )

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
