"""Pass if ANSWER.txt's number is the real attempt count and the code still behaves."""
import os
import pathlib
import re
import sys

answer = pathlib.Path("ANSWER.txt")
if not answer.exists():
    sys.exit("FAIL: ANSWER.txt was not created")
numbers = re.findall(r"\d+", answer.read_text(encoding="utf-8", errors="replace"))
if not numbers or numbers[0] != "4":
    sys.exit(f"FAIL: expected 4 as the first number in ANSWER.txt, got {numbers[:3]}")

os.environ.pop("BANK_RETRIES", None)
sys.path.insert(0, ".")
from payments.client import BankError, charge  # noqa: E402


class FailingBank:
    calls = 0

    def charge(self, card, amount):
        FailingBank.calls += 1
        raise BankError("declined")


try:
    charge(FailingBank(), "4111", 10)
except BankError:
    pass
if FailingBank.calls != 4:
    sys.exit(f"FAIL: the code was changed ({FailingBank.calls} bank calls, expected 4)")
print("ok")
