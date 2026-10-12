from datetime import datetime, timezone

from .errors import ValidationError

ACTIVITY_TYPES = {"Walking", "Running", "Workout", "Cycling", "Drum Practice"}


def require_object(data):
    if not isinstance(data, dict): raise ValidationError("Request body must be a JSON object")
    return data


def parse_datetime(value, field="recorded_at"):
    if not isinstance(value, str): raise ValidationError(f"{field} must be an ISO-8601 timestamp")
    try: parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error: raise ValidationError(f"{field} must be a valid ISO-8601 timestamp") from error
    if parsed.tzinfo is None: raise ValidationError(f"{field} must include a timezone")
    return parsed.astimezone(timezone.utc).replace(tzinfo=None)


def number(data, field, minimum=None, maximum=None, required=False, integer=False):
    value = data.get(field)
    if value is None:
        if required: raise ValidationError(f"{field} is required")
        return None
    expected = int if integer else (int, float)
    if isinstance(value, bool) or not isinstance(value, expected): raise ValidationError(f"{field} must be {'an integer' if integer else 'a number'}")
    if (minimum is not None and value < minimum) or (maximum is not None and value > maximum): raise ValidationError(f"{field} is outside the allowed range")
    return value


def text(data, field, maximum=1000):
    value = data.get(field)
    if value is None: return None
    if not isinstance(value, str) or len(value) > maximum: raise ValidationError(f"{field} must be a string of at most {maximum} characters")
    return value.strip() or None


def activity_payload(data):
    data = require_object(data)
    activity_type = data.get("activity_type")
    if activity_type not in ACTIVITY_TYPES: raise ValidationError("activity_type is invalid")
    start_at = parse_datetime(data.get("start_at") or data.get("recorded_at"), "start_at")
    end_at = parse_datetime(data.get("end_at"), "end_at")
    if end_at < start_at: raise ValidationError("end_at must not be before start_at")
    duration = number(data, "duration_minutes", 0.01, required=True)
    distance = number(data, "distance_km", 0)
    steps = number(data, "steps", 0, integer=True)
    speed = number(data, "average_speed_kmh", 0)
    pace = number(data, "average_pace_min_per_km", 0)
    workout_type = text(data, "workout_type", 100)
    practice_type = text(data, "drum_practice_type", 100)
    completed = data.get("completed", True)
    if not isinstance(completed, bool): raise ValidationError("completed must be a boolean")
    if activity_type in {"Walking", "Running", "Cycling"} and distance is None: raise ValidationError("distance_km is required")
    if activity_type == "Workout" and not workout_type: raise ValidationError("workout_type is required")
    if activity_type == "Drum Practice" and not practice_type: raise ValidationError("drum_practice_type is required")
    route = data.get("route", [])
    if not isinstance(route, list): raise ValidationError("route must be an array")
    parsed_route = []
    for point in route:
        require_object(point)
        latitude = number(point, "latitude", -90, 90, True)
        longitude = number(point, "longitude", -180, 180, True)
        timestamp = point.get("recorded_at", point.get("timestamp"))
        if isinstance(timestamp, (int, float)): timestamp = datetime.fromtimestamp(timestamp / 1000, timezone.utc).isoformat()
        parsed_route.append({"latitude": latitude, "longitude": longitude, "recorded_at": parse_datetime(timestamp, "route recorded_at"), "accuracy": number(point, "accuracy", 0)})
    return {"activity_type": activity_type, "start_at": start_at, "end_at": end_at, "duration_minutes": duration, "distance_km": distance, "notes": text(data, "notes"), "steps": steps, "workout_type": workout_type, "completed": completed, "average_speed_kmh": speed, "average_pace_min_per_km": pace, "drum_practice_type": practice_type, "route": parsed_route}


def vital_payload(data):
    data = require_object(data)
    return {"recorded_at": parse_datetime(data.get("recorded_at")), "systolic": number(data, "systolic", 40, 300, True, True), "diastolic": number(data, "diastolic", 20, 200, True, True), "glucose": number(data, "glucose", 1, 1000, True), "pulse": number(data, "pulse", 20, 300, True, True), "spo2": number(data, "spo2", 1, 100, True), "weight": number(data, "weight", 1, 1000, True)}


def date_filters(args):
    start = parse_datetime(args["start_date"], "start_date") if args.get("start_date") else None
    end = parse_datetime(args["end_date"], "end_date") if args.get("end_date") else None
    if start and end and start > end: raise ValidationError("start_date must not be after end_date")
    return start, end
