from __future__ import annotations

from pathlib import Path

from dashboard.backend.app import create_app

ROOT = Path(__file__).resolve().parents[1]


def client():
    app = create_app(ROOT)
    app.config.update(TESTING=True)
    return app.test_client()


def test_health_endpoint() -> None:
    response = client().get("/api/health")
    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"


def test_prices_endpoint_filters_and_resamples() -> None:
    response = client().get(
        "/api/prices?start_date=2014-11-01&end_date=2014-12-31&frequency=weekly"
    )
    payload = response.get_json()
    assert response.status_code == 200
    assert payload["count"] > 0
    assert payload["frequency"] == "weekly"


def test_invalid_date_range_returns_400() -> None:
    response = client().get(
        "/api/prices?start_date=2022-01-01&end_date=2020-01-01"
    )
    assert response.status_code == 400
    assert "start_date" in response.get_json()["error"]


def test_change_point_endpoint_returns_model_result() -> None:
    response = client().get("/api/change-points")
    payload = response.get_json()
    assert response.status_code == 200
    assert payload["count"] == 1
    assert payload["data"][0]["change_point_date"] == "2014-12-01"
