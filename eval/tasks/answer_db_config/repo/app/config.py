import os

DEFAULT_DATABASE_URL = "sqlite:///data/app.db"


def load_database_url():
    """Return the database URL the app connects to."""
    return os.environ.get("APP_DATABASE_URL", DEFAULT_DATABASE_URL)


def load_log_level():
    return os.environ.get("APP_LOG_LEVEL", "INFO")
