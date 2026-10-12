from .errors import NotFoundError, ValidationError
from .offline import DurableService, get_store
from .repositories import ActivityRepository, VitalRepository
from .validators import ACTIVITY_TYPES, activity_payload, date_filters, vital_payload


class ActivityService:
    def __init__(self, repository=None): self.repository = repository or ActivityRepository()
    def list(self, args):
        activity_type = args.get("type")
        if activity_type and activity_type not in ACTIVITY_TYPES: raise ValidationError("type is invalid")
        start, end = date_filters(args)
        try: remote = self.repository.list(activity_type, start, end)
        except Exception: remote = []
        local = get_store().list_records("activity")
        if activity_type: local = [item for item in local if item.get("activity_type") == activity_type]
        remote_ids = {str(item.get("client_id")) for item in remote if item.get("client_id")}
        return remote + [item for item in local if item.get("local_id") not in remote_ids and item.get("sync_state") == "pending"]
    def get(self, identifier):
        item = self.repository.get(identifier)
        if not item: raise NotFoundError("Activity not found")
        return item
    def create(self, data, idempotency_key=None): return DurableService("activity", self.repository).create(activity_payload(data), idempotency_key)
    def update(self, identifier, data):
        item = self.repository.update(identifier, activity_payload(data))
        if not item: raise NotFoundError("Activity not found")
        return item
    def delete(self, identifier):
        if not self.repository.delete(identifier): raise NotFoundError("Activity not found")
    def analytics(self, activity_type, days):
        if activity_type not in ACTIVITY_TYPES: raise ValidationError("type is invalid")
        try: days = int(days)
        except (TypeError, ValueError): raise ValidationError("days is invalid")
        if days not in {7, 14, 30, 90, 180, 365}: raise ValidationError("days is invalid")
        metric, unit = ("distance_km", "km") if activity_type in {"Walking", "Running", "Cycling"} else ("duration_minutes", "minutes")
        records = [{"id": item["id"], "recorded_at": item["start_at"], "value": item.get(metric)} for item in self.list({"type": activity_type})]
        return {"activity": activity_type, "time_range": days, "metric": metric, "unit": unit, "records": records}


class VitalService:
    def __init__(self, repository=None): self.repository = repository or VitalRepository()
    def list(self, args):
        start, end = date_filters(args)
        try: remote = self.repository.list(start, end)
        except Exception: remote = []
        remote_ids = {str(item.get("client_id")) for item in remote if item.get("client_id")}
        return remote + [item for item in get_store().list_records("vital") if item.get("local_id") not in remote_ids and item.get("sync_state") == "pending"]
    def get(self, identifier):
        item = self.repository.get(identifier)
        if not item: raise NotFoundError("Vital record not found")
        return item
    def create(self, data, idempotency_key=None): return DurableService("vital", self.repository).create(vital_payload(data), idempotency_key)
    def update(self, identifier, data):
        item = self.repository.update(identifier, vital_payload(data))
        if not item: raise NotFoundError("Vital record not found")
        return item
    def delete(self, identifier):
        if not self.repository.delete(identifier): raise NotFoundError("Vital record not found")
