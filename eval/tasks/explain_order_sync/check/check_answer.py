"""Pass if ANSWER.json matches the real behaviour of sync.py and the code is unchanged."""
import json
import pathlib
import sys

path = pathlib.Path("ANSWER.json")
if not path.exists():
    sys.exit("FAIL: ANSWER.json was not created")
try:
    answer = json.loads(path.read_text(encoding="utf-8"))
except json.JSONDecodeError as e:
    sys.exit(f"FAIL: ANSWER.json is not valid JSON: {e}")
if not isinstance(answer, dict):
    sys.exit("FAIL: ANSWER.json must be a JSON object")

statuses = answer.get("skipped_statuses")
if not isinstance(statuses, list) or {str(s).lower() for s in statuses} != {"cancelled", "test"}:
    sys.exit(f"FAIL: skipped_statuses should be cancelled and test, got {statuses!r}")
if answer.get("attempts_per_page") not in (3, "3"):
    sys.exit(f"FAIL: attempts_per_page should be 3, got {answer.get('attempts_per_page')!r}")
if str(answer.get("on_final_timeout", "")).lower() != "raise":
    sys.exit(f"FAIL: on_final_timeout should be raise, got {answer.get('on_final_timeout')!r}")

sys.path.insert(0, ".")
import sync  # noqa: E402


class Store:
    def __init__(self):
        self.saved = []

    def save(self, order):
        self.saved.append(order["id"])


class FlakyClient:
    def __init__(self):
        self.calls = 0

    def get_orders(self, since, page):
        self.calls += 1
        if page == 1:
            return [{"id": 1, "status": "paid"}, {"id": 2, "status": "cancelled"},
                    {"id": 3, "status": "test"}]
        if page == 2:
            return [{"id": 4, "status": "shipped"}]
        return []


class DeadClient:
    calls = 0

    def get_orders(self, since, page):
        DeadClient.calls += 1
        raise sync.Timeout()


store = Store()
if sync.sync_orders(FlakyClient(), store, "2026-01-01") != 2 or store.saved != [1, 4]:
    sys.exit("FAIL: the code was changed (sync result differs)")
try:
    sync.sync_orders(DeadClient(), Store(), "2026-01-01")
    sys.exit("FAIL: the code was changed (timeout no longer raises)")
except sync.Timeout:
    pass
if DeadClient.calls != 3:
    sys.exit(f"FAIL: the code was changed ({DeadClient.calls} attempts, expected 3)")
print("ok")
