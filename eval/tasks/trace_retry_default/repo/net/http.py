"""Generic HTTP helpers used by the catalog sync (not by payments)."""

MAX_RETRIES = 5


def http_get(session, url):
    last = None
    for _ in range(MAX_RETRIES):
        try:
            return session.get(url)
        except ConnectionError as e:
            last = e
    raise last
