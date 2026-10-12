import json
import sqlite3
import threading
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

from flask import current_app

from .db import DatabaseError
from .repositories import ActivityRepository, VitalRepository

_SCHEMA = """
CREATE TABLE IF NOT EXISTS local_records (
 id TEXT PRIMARY KEY, record_type TEXT NOT NULL, operation TEXT NOT NULL,
 payload TEXT NOT NULL, remote_id INTEGER, sync_state TEXT NOT NULL,
 attempts INTEGER NOT NULL DEFAULT 0, next_attempt_at REAL NOT NULL DEFAULT 0,
 last_error TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_local_records_sync ON local_records(sync_state,next_attempt_at,created_at);
CREATE TABLE IF NOT EXISTS sync_metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL);
"""


def _json_default(value):
    if isinstance(value, datetime):
        return value.replace(tzinfo=timezone.utc).isoformat()
    raise TypeError(f"Cannot serialize {type(value).__name__}")


class OfflineStore:
    def __init__(self, path):
        self.path = str(path)
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        with self.connect() as connection:
            connection.executescript(_SCHEMA)

    def connect(self):
        connection = sqlite3.connect(self.path, timeout=2)
        connection.row_factory = sqlite3.Row
        return connection

    def save(self, record_type, payload, record_id=None, remote_id=None, state="pending"):
        identifier = record_id or str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        with self._lock, self.connect() as connection:
            connection.execute(
                "INSERT INTO local_records(id,record_type,operation,payload,remote_id,sync_state,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET payload=excluded.payload,remote_id=excluded.remote_id,sync_state=excluded.sync_state,updated_at=excluded.updated_at",
                (identifier, record_type, "upsert", json.dumps(payload, default=_json_default), remote_id, state, now, now),
            )
        return identifier

    def pending(self):
        with self.connect() as connection:
            rows = connection.execute("SELECT * FROM local_records WHERE sync_state='pending' AND next_attempt_at<=? ORDER BY CASE record_type WHEN 'activity' THEN 0 ELSE 1 END,created_at,id", (time.time(),)).fetchall()
        return [dict(item) for item in rows]

    def list_records(self, record_type):
        with self.connect() as connection:
            rows = connection.execute("SELECT * FROM local_records WHERE record_type=? ORDER BY created_at DESC", (record_type,)).fetchall()
        return [{**json.loads(item["payload"]), "local_id": item["id"], "sync_state": item["sync_state"], "id": item["remote_id"] or item["id"]} for item in rows]

    def mark_synced(self, identifier, remote_id):
        with self._lock, self.connect() as connection:
            connection.execute("UPDATE local_records SET remote_id=?,sync_state='synced',last_error=NULL,updated_at=? WHERE id=?", (remote_id, datetime.now(timezone.utc).isoformat(), identifier))

    def mark_failed(self, identifier, attempts, message):
        delay = min(300, 2 ** min(attempts, 8))
        with self._lock, self.connect() as connection:
            connection.execute("UPDATE local_records SET attempts=?,next_attempt_at=?,last_error=?,updated_at=? WHERE id=?", (attempts, time.time() + delay, message[:500], datetime.now(timezone.utc).isoformat(), identifier))

    def status(self):
        with self.connect() as connection:
            pending = connection.execute("SELECT COUNT(*) FROM local_records WHERE sync_state='pending'").fetchone()[0]
            failed = connection.execute("SELECT COUNT(*) FROM local_records WHERE last_error IS NOT NULL").fetchone()[0]
        return {"pending": pending, "with_errors": failed}


def get_store():
    store = current_app.extensions.get("offline_store")
    if store is None:
        store = OfflineStore(current_app.config["SQLITE_PATH"])
        current_app.extensions["offline_store"] = store
    return store


def _idempotency_id(record_type, key):
    namespace = uuid.UUID("916d4548-e6f3-4e4b-bcad-e97d971fc03d")
    return str(uuid.uuid5(namespace, f"{record_type}:{key}"))


class DurableService:
    def __init__(self, record_type, remote_repository):
        self.record_type = record_type
        self.remote = remote_repository

    def create(self, payload, idempotency_key=None):
        local_id = _idempotency_id(self.record_type, idempotency_key) if idempotency_key else None
        try:
            result = self.remote.create(dict(payload), client_id=local_id)
            get_store().save(self.record_type, payload, local_id, result["id"], "synced")
            return {**result, "local_id": local_id, "sync_state": "synced"}
        except DatabaseError:
            local_id = get_store().save(self.record_type, payload, local_id)
            return {**payload, "id": local_id, "local_id": local_id, "sync_state": "pending"}


def sync_pending():
    store = get_store()
    repositories = {"activity": ActivityRepository(), "vital": VitalRepository()}
    for record in store.pending():
        try:
            payload = json.loads(record["payload"])
            result = repositories[record["record_type"]].create(payload, client_id=record["id"])
            store.mark_synced(record["id"], result["id"])
        except DatabaseError as error:
            store.mark_failed(record["id"], record["attempts"] + 1, str(error))
            break
    return store.status()
