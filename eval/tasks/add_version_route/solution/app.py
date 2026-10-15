"""Tiny request router used by the service."""

from version import __version__

ROUTES = {}


def route(path):
    def register(handler):
        ROUTES[path] = handler
        return handler
    return register


def handle(path):
    handler = ROUTES.get(path)
    if handler is None:
        return 404, {"error": "not found"}
    return 200, handler()


@route("/health")
def health():
    return {"status": "ok"}


@route("/version")
def version():
    return {"version": __version__}
