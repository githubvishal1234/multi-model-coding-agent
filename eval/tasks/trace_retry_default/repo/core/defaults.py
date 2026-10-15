"""Derived defaults. Override these through environment variables in settings modules."""

from core.constants import CACHE_TTL_SECONDS, RETRY_BASE

# The bank allows one extra attempt on top of the shared retry budget.
BANK_RETRY_LIMIT = RETRY_BASE + 1
HTTP_RETRY_LIMIT = RETRY_BASE
SESSION_TTL_SECONDS = CACHE_TTL_SECONDS * 2
