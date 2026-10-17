import logging
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS
from werkzeug.exceptions import BadRequest, HTTPException

load_dotenv(Path(__file__).resolve().parents[1] / ".env", override=False)

from .config import Config
from .db import DatabaseError, close_db
from .errors import ApiError
from .offline import OfflineStore
from .routes import api


def create_app(config_object=Config):
    app = Flask(__name__)
    app.config.from_object(config_object)
    app.config["DATABASE_CONFIG"] = config_object.database_config
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    origins = app.config["CORS_ALLOWED_ORIGINS"]
    origins = "*" if origins == "*" else [item.strip() for item in origins.split(",") if item.strip()]
    CORS(app, resources={r"/api/*": {"origins": origins}})
    app.extensions["offline_store"] = OfflineStore(app.config["SQLITE_PATH"])
    app.register_blueprint(api, url_prefix="/api")
    app.teardown_appcontext(close_db)

    @app.before_request
    def log_request(): app.logger.info("request method=%s path=%s", request.method, request.path)

    @app.errorhandler(ApiError)
    def api_error(error): return jsonify(error={"code": error.code, "message": error.message}), error.status

    @app.errorhandler(BadRequest)
    def malformed(_error): return jsonify(error={"code": "BAD_REQUEST", "message": "Malformed request"}), 400

    @app.errorhandler(DatabaseError)
    def database_error(_error): return jsonify(error={"code": "DATABASE_ERROR", "message": "Database operation failed"}), 500

    @app.errorhandler(HTTPException)
    def http_error(error): return jsonify(error={"code": error.name.upper().replace(" ", "_"), "message": error.description}), error.code

    @app.errorhandler(Exception)
    def unexpected(error):
        app.logger.exception("Unexpected error", exc_info=error)
        return jsonify(error={"code": "INTERNAL_ERROR", "message": "Internal server error"}), 500

    app.logger.info("HabitOps API initialized")
    return app
