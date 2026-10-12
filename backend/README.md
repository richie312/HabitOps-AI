# HabitOps Flask Backend

Flask uses the existing Raspberry Pi MySQL 8 service first and app-private SQLite as a durable connectivity fallback. It never creates/removes the MySQL container or volume.

Copy `.env.example` to an untracked `.env`, apply the additive `schema.sql`, and run `python run.py` for desktop tests. On Android, Chaquopy packages this directory and starts Flask automatically on loopback port 8765. MySQL remains at `MYSQL_HOST` (not localhost).

API: `/api/ready`, `/api/health`, `/api/activities`, `/api/vitals`, `/api/analytics/activity`, `/api/sync`, `/api/sync/status`. POST accepts `Idempotency-Key`. Failed connectivity writes return a persisted resource with `sync_state: pending`; startup/active periodic sync retries with bounded exponential backoff. Passwords are never logged.

```bash
python -m pip install -r requirements.txt
pytest
```

SQLite differs physically from MySQL by storing each validated payload (including route children) as JSON plus UUID, remote ID, timestamps and sync metadata. MySQL remains authoritative and uses unique nullable `client_id` columns for retry deduplication.
