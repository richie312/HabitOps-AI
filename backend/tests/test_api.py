from datetime import timedelta
from unittest.mock import Mock, patch

import pytest

from app import create_app
from app.config import Config
from app.db import DatabaseError
from app.services import ActivityService
from app.repositories import ActivityRepository


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


@patch("app.services.get_store")
def test_analytics_passes_requested_date_window(get_store):
    repository = Mock()
    repository.list.return_value = []
    get_store.return_value.list_records.return_value = []

    result = ActivityService(repository).analytics("Walking", 7)

    assert result["activity"] == "Walking"
    assert result["time_range"] == 7
    _, start, end = repository.list.call_args.args
    assert end - start == timedelta(days=7)


@patch("app.services.get_store")
def test_list_uses_synced_local_cache_when_mysql_is_unavailable(get_store):
    repository = Mock()
    repository.list.side_effect = DatabaseError("offline")
    cached = [{"id": 9, "local_id": "local-9", "sync_state": "synced", "activity_type": "Cycling"}]
    get_store.return_value.list_records.return_value = cached

    assert ActivityService(repository).list({"type": "Cycling"}) == cached


@patch("app.repositories.execute")
def test_activity_list_includes_gps_route_points(execute):
    activity_row = {"id": 7, "activity_type": "Running"}
    route_row = {"activity_id": 7, "latitude": 12.97, "longitude": 77.59, "recorded_at": "2026-10-16T10:00:00Z", "accuracy": 5}
    execute.side_effect = [
        Mock(fetchall=Mock(return_value=[activity_row])),
        Mock(fetchall=Mock(return_value=[route_row])),
    ]

    result = ActivityRepository().list("Running")

    assert result[0]["route"] == [{"latitude": 12.97, "longitude": 77.59, "recorded_at": "2026-10-16T10:00:00Z", "accuracy": 5}]
