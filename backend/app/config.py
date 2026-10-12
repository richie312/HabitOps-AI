import os


class Config:
    FLASK_ENV = os.getenv("FLASK_ENV", "production")
    MYSQL_HOST = os.getenv("MYSQL_HOST", "")
    MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
    MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "")
    MYSQL_USERNAME = os.getenv("MYSQL_USERNAME", "")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
    MYSQL_CONNECT_TIMEOUT = int(os.getenv("MYSQL_CONNECT_TIMEOUT", "3"))
    SQLITE_PATH = os.getenv("HABITOPS_SQLITE_PATH", "habitops-local.db")
    CORS_ALLOWED_ORIGINS = os.getenv("CORS_ALLOWED_ORIGINS", "http://127.0.0.1:8765,http://localhost:8765")
    JSON_SORT_KEYS = False

    @classmethod
    def database_config(cls):
        required = {
            "MYSQL_HOST": cls.MYSQL_HOST,
            "MYSQL_DATABASE": cls.MYSQL_DATABASE,
            "MYSQL_USERNAME": cls.MYSQL_USERNAME,
            "MYSQL_PASSWORD": cls.MYSQL_PASSWORD,
        }
        missing = [name for name, value in required.items() if not value]
        if missing:
            raise RuntimeError(f"Missing database configuration: {', '.join(missing)}")
        return {
            "host": cls.MYSQL_HOST,
            "port": cls.MYSQL_PORT,
            "database": cls.MYSQL_DATABASE,
            "user": cls.MYSQL_USERNAME,
            "password": cls.MYSQL_PASSWORD,
            "connection_timeout": cls.MYSQL_CONNECT_TIMEOUT,
            "autocommit": False,
        }
