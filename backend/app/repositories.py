from datetime import datetime, timedelta

from .db import DatabaseError, execute, execute_write, get_db
from .serializers import json_value

ACTIVITY_COLUMNS = "id, client_id, activity_type, start_at, end_at, duration_minutes, distance_km, notes, steps, workout_type, completed, average_speed_kmh, average_pace_min_per_km, drum_practice_type, created_at, updated_at"
VITAL_COLUMNS = "id, client_id, recorded_at, systolic, diastolic, glucose, pulse, spo2, weight, created_at, updated_at"


def row(cursor):
    value = cursor.fetchone()
    return {key: json_value(item) for key, item in value.items()} if value else None


def rows(cursor):
    return [{key: json_value(item) for key, item in value.items()} for value in cursor.fetchall()]


class ActivityRepository:
    def list(self, activity_type=None, start=None, end=None):
        clauses, parameters = [], []
        if activity_type: clauses.append("activity_type = %s"); parameters.append(activity_type)
        if start: clauses.append("start_at >= %s"); parameters.append(start)
        if end: clauses.append("start_at <= %s"); parameters.append(end)
        where = " WHERE " + " AND ".join(clauses) if clauses else ""
        return rows(execute(f"SELECT {ACTIVITY_COLUMNS} FROM activities{where} ORDER BY start_at DESC", tuple(parameters)))

    def get(self, identifier):
        activity = row(execute(f"SELECT {ACTIVITY_COLUMNS} FROM activities WHERE id = %s", (identifier,)))
        if activity:
            activity["route"] = rows(execute("SELECT latitude,longitude,recorded_at,accuracy FROM activity_route_points WHERE activity_id=%s ORDER BY sequence_number", (identifier,)))
        return activity

    def create(self, values, client_id=None):
        values = dict(values); route = values.pop("route", [])
        connection = get_db()
        try:
            cursor = connection.cursor(dictionary=True)
            if client_id:
                cursor.execute(f"SELECT {ACTIVITY_COLUMNS} FROM activities WHERE client_id=%s", (client_id,))
                existing = cursor.fetchone()
                if existing:
                    connection.rollback(); return self.get(existing["id"])
            cursor.execute("INSERT INTO activities (client_id,activity_type,start_at,end_at,duration_minutes,distance_km,notes,steps,workout_type,completed,average_speed_kmh,average_pace_min_per_km,drum_practice_type) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", (client_id, *values.values()))
            identifier = cursor.lastrowid
            for sequence, point in enumerate(route):
                cursor.execute("INSERT INTO activity_route_points (activity_id,sequence_number,latitude,longitude,recorded_at,accuracy) VALUES (%s,%s,%s,%s,%s,%s)", (identifier, sequence, point["latitude"], point["longitude"], point["recorded_at"], point.get("accuracy")))
            connection.commit()
        except Exception as error:
            connection.rollback()
            if isinstance(error, DatabaseError): raise
            from mysql.connector import Error
            if isinstance(error, Error): raise DatabaseError("Database operation failed") from error
            raise
        return self.get(identifier)

    def update(self, identifier, values):
        if not self.get(identifier): return None
        values = dict(values); route = values.pop("route", []); connection = get_db()
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("UPDATE activities SET activity_type=%s,start_at=%s,end_at=%s,duration_minutes=%s,distance_km=%s,notes=%s,steps=%s,workout_type=%s,completed=%s,average_speed_kmh=%s,average_pace_min_per_km=%s,drum_practice_type=%s,updated_at=UTC_TIMESTAMP(6) WHERE id=%s", (*values.values(), identifier))
            cursor.execute("DELETE FROM activity_route_points WHERE activity_id=%s", (identifier,))
            for sequence, point in enumerate(route): cursor.execute("INSERT INTO activity_route_points (activity_id,sequence_number,latitude,longitude,recorded_at,accuracy) VALUES (%s,%s,%s,%s,%s,%s)", (identifier, sequence, point["latitude"], point["longitude"], point["recorded_at"], point.get("accuracy")))
            connection.commit()
        except Exception:
            connection.rollback(); raise
        return self.get(identifier)

    def delete(self, identifier): return execute_write("DELETE FROM activities WHERE id=%s", (identifier,)).rowcount > 0
    def analytics(self, activity_type, days): return self.list(activity_type, datetime.utcnow() - timedelta(days=days), None)


class VitalRepository:
    def list(self, start=None, end=None):
        clauses, parameters = [], []
        if start: clauses.append("recorded_at >= %s"); parameters.append(start)
        if end: clauses.append("recorded_at <= %s"); parameters.append(end)
        where = " WHERE " + " AND ".join(clauses) if clauses else ""
        return rows(execute(f"SELECT {VITAL_COLUMNS} FROM vitals{where} ORDER BY recorded_at DESC", tuple(parameters)))
    def get(self, identifier): return row(execute(f"SELECT {VITAL_COLUMNS} FROM vitals WHERE id=%s", (identifier,)))
    def create(self, values, client_id=None):
        if client_id:
            existing = row(execute(f"SELECT {VITAL_COLUMNS} FROM vitals WHERE client_id=%s", (client_id,)))
            if existing: return existing
        cursor = execute_write("INSERT INTO vitals (client_id,recorded_at,systolic,diastolic,glucose,pulse,spo2,weight) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)", (client_id, *values.values()))
        return self.get(cursor.lastrowid)
    def update(self, identifier, values):
        cursor = execute_write("UPDATE vitals SET recorded_at=%s,systolic=%s,diastolic=%s,glucose=%s,pulse=%s,spo2=%s,weight=%s,updated_at=UTC_TIMESTAMP(6) WHERE id=%s", (*values.values(), identifier)); return self.get(identifier) if cursor.rowcount else None
    def delete(self, identifier): return execute_write("DELETE FROM vitals WHERE id=%s", (identifier,)).rowcount > 0
