from datetime import date, datetime, timezone
from decimal import Decimal


def json_value(value):
    if isinstance(value, datetime):
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.isoformat()
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, Decimal):
        return float(value)
    return value


def rows(cursor):
    columns = [column[0] for column in cursor.description]
    return [
        {column: json_value(value) for column, value in zip(columns, row)}
        for row in cursor.fetchall()
    ]


def one(cursor):
    values = rows(cursor)
    return values[0] if values else None
