from datetime import datetime

from app.offline import DurableService, OfflineStore
from app.db import DatabaseError


class OfflineRepository:
    def create(self, payload, client_id=None):
        raise DatabaseError("offline")


class SuccessfulRepository:
    def __init__(self): self.ids = {}
    def create(self, payload, client_id=None):
        self.ids.setdefault(client_id, len(self.ids) + 1)
        return {**payload, "id": self.ids[client_id]}


def test_offline_write_is_durable_and_idempotent(tmp_path, monkeypatch):
    store = OfflineStore(tmp_path / "offline.db")
    from app import offline
    monkeypatch.setattr(offline, "get_store", lambda: store)
    payload = {"recorded_at": datetime(2025, 1, 1), "pulse": 70}
    first = DurableService("vital", OfflineRepository()).create(payload, "same-key")
    second = DurableService("vital", OfflineRepository()).create(payload, "same-key")
    assert first["id"] == second["id"]
    assert store.status()["pending"] == 1
    reopened = OfflineStore(tmp_path / "offline.db")
    assert reopened.status()["pending"] == 1


def test_synced_write_is_recorded(tmp_path, monkeypatch):
    store = OfflineStore(tmp_path / "offline.db")
    from app import offline
    monkeypatch.setattr(offline, "get_store", lambda: store)
    result = DurableService("activity", SuccessfulRepository()).create({"activity_type": "Workout"}, "key")
    assert result["sync_state"] == "synced"
    assert store.status()["pending"] == 0
