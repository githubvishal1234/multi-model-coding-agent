"""Old settings loader, kept for the one-off migration script. Not used by the app."""

import os


def get_db():
    return os.environ.get("DATABASE_URL", "postgres://localhost/legacy")
