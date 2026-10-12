import mysql.connector
from flask import current_app, g


class DatabaseError(Exception):
    pass


def get_db():
    if "db" not in g:
        try:
            g.db = mysql.connector.connect(**current_app.config["DATABASE_CONFIG"]())
        except (mysql.connector.Error, RuntimeError) as error:
            current_app.logger.error("Database connection failed")
            raise DatabaseError("Database operation failed") from error
    return g.db


def close_db(_error=None):
    connection = g.pop("db", None)
    if connection is not None and connection.is_connected():
        connection.close()


def execute(sql, parameters=()):
    try:
        cursor = get_db().cursor(dictionary=True)
        cursor.execute(sql, parameters)
        return cursor
    except mysql.connector.Error as error:
        current_app.logger.error("Database query failed")
        raise DatabaseError("Database operation failed") from error


def execute_write(sql, parameters=()):
    connection = get_db()
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(sql, parameters)
        connection.commit()
        return cursor
    except mysql.connector.Error as error:
        connection.rollback()
        current_app.logger.error("Database write failed")
        raise DatabaseError("Database operation failed") from error
