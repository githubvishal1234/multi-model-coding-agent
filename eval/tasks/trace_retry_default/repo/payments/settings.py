import os

from core import defaults

BANK_RETRIES = int(os.environ.get("BANK_RETRIES", defaults.BANK_RETRY_LIMIT))
TIMEOUT_SECONDS = 30
