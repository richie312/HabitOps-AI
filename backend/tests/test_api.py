from unittest.mock import patch

import pytest

from app import create_app
from app.config import Config


class TestConfig(Config):
    TESTING = True
    CORS_ALLOWED_ORIGINS = "*"
    SQLITE_PATH = ":memory:"
    @classmethod
    def database_config(cls): return {}


@pytest.fixture
def client(tmp_path):
    TestConfig.SQLITE_PATH = str(tmp_path / "test.db")
    return create_app(TestConfig).test_client()


def activity():
    return {"id": 1, "activity_type": "Walking", "start_at": "2025-01-01T00:00:00+00:00", "end_at": "2025-01-01T00:20:00+00:00", "distance_km": 2, "duration_minutes": 20, "steps": 2500, "route": []}


def vital():
    return {"id": 1, "recorded_at": "2025-01-01T00:00:00+00:00", "systolic": 120, "diastolic": 80, "glucose": 90, "pulse": 70, "spo2": 98, "weight": 75}


def test_startup_and_ready(client):
    assert client.get("/api/ready").status_code == 200


@patch("app.routes.get_db")
def test_health(database, client):
    database.return_value.cursor.return_value.fetchone.return_value = (1,)
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json["status"] == "ok" and response.json["database"] == "ok"


@patch("app.routes.ActivityService")
def test_activity_create_retrieve_filter_and_not_found(service, client):
    service.return_value.create.return_value = activity(); service.return_value.get.return_value = activity(); service.return_value.list.return_value = [activity()]
    assert client.post("/api/activities", json=activity(), headers={"Idempotency-Key": "key"}).status_code == 201
    assert client.get("/api/activities/1").status_code == 200
    assert client.get("/api/activities?type=Walking").json["count"] == 1


def test_activity_validation(client):
    assert client.post("/api/activities", json={"activity_type": "Unknown"}).status_code == 400


@patch("app.routes.VitalService")
def test_vital_create_retrieve_and_filter(service, client):
    service.return_value.create.return_value = vital(); service.return_value.get.return_value = vital(); service.return_value.list.return_value = [vital()]
    assert client.post("/api/vitals", json=vital()).status_code == 201
    assert client.get("/api/vitals/1").status_code == 200
    assert client.get("/api/vitals").json["count"] == 1


def test_vital_validation(client): assert client.post("/api/vitals", json={}).status_code == 400


@patch("app.routes.ActivityService")
def test_analytics(service, client):
    service.return_value.analytics.return_value = {"activity": "Walking", "time_range": 30, "metric": "distance_km", "unit": "km", "records": []}
    assert client.get("/api/analytics/activity?type=Walking&days=30").status_code == 200


def test_sync_status(client):
    assert client.get("/api/sync/status").json["data"]["pending"] == 0
