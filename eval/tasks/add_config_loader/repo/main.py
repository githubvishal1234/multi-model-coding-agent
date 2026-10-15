"""Starts the web app."""

# TODO: read these from the environment with config.load_config()
HOST = "127.0.0.1"
PORT = 8000


def describe():
    return f"serving on {HOST}:{PORT}"
