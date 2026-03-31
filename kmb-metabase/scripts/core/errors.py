"""Shared error types and formatting for kmb-metabase scripts."""

from __future__ import annotations

import json


class KMBError(Exception):
    """Base error for all runtime failures."""


class KMBHttpError(KMBError):
    def __init__(self, status: int, reason: str, url: str, body: str | None = None):
        self.status = status
        self.reason = reason
        self.url = url
        self.body = body
        super().__init__(f"HTTP {status} - {reason}")


class KMBRequestError(KMBError):
    """Connection or transport level failure."""


def format_error(error: Exception) -> str:
    if isinstance(error, KMBHttpError):
        base = f"HTTP {error.status} - {error.reason}"
        if not error.body:
            return base
        try:
            parsed = json.loads(error.body)
            return f"{base}\nDetails: {parsed}"
        except Exception:
            return f"{base}\nDetails: {error.body}"
    return str(error)
