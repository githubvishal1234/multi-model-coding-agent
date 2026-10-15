from app.config import load_database_url


def connect():
    url = load_database_url()
    return f"connected to {url}"
