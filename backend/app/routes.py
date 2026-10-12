from flask import Blueprint, jsonify, request

from .db import DatabaseError, get_db
from .offline import get_store, sync_pending
from .services import ActivityService, VitalService

api = Blueprint("api", __name__)


@api.get("/ready")
def ready(): return jsonify(status="ready")


@api.get("/health")
def health():
    database = "unavailable"
    try:
        cursor = get_db().cursor(); cursor.execute("SELECT 1"); cursor.fetchone(); database = "ok"
    except DatabaseError:
        pass
    return jsonify(status="ok", database=database, sync=get_store().status())


@api.post("/sync")
def synchronize(): return jsonify(data=sync_pending())


@api.get("/sync/status")
def sync_status(): return jsonify(data=get_store().status())


@api.route("/activities", methods=["GET", "POST"])
def activities():
    service = ActivityService()
    if request.method == "GET":
        data = service.list(request.args); return jsonify(data=data, count=len(data))
    return jsonify(data=service.create(request.get_json(silent=True), request.headers.get("Idempotency-Key"))), 201


@api.route("/activities/<int:identifier>", methods=["GET", "PUT", "DELETE"])
def activity(identifier):
    service = ActivityService()
    if request.method == "GET": return jsonify(data=service.get(identifier))
    if request.method == "PUT": return jsonify(data=service.update(identifier, request.get_json(silent=True)))
    service.delete(identifier); return "", 204


@api.route("/vitals", methods=["GET", "POST"])
def vitals():
    service = VitalService()
    if request.method == "GET":
        data = service.list(request.args); return jsonify(data=data, count=len(data))
    return jsonify(data=service.create(request.get_json(silent=True), request.headers.get("Idempotency-Key"))), 201


@api.route("/vitals/<int:identifier>", methods=["GET", "PUT", "DELETE"])
def vital(identifier):
    service = VitalService()
    if request.method == "GET": return jsonify(data=service.get(identifier))
    if request.method == "PUT": return jsonify(data=service.update(identifier, request.get_json(silent=True)))
    service.delete(identifier); return "", 204


@api.get("/analytics/activity")
def analytics(): return jsonify(data=ActivityService().analytics(request.args.get("type"), request.args.get("days")))
