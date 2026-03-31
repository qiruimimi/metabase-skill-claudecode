"""Shared HTTP helpers for kmb-metabase scripts."""

from __future__ import annotations

import json
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from core.config import API_HOST, DEFAULT_TIMEOUT, build_headers
from core.errors import KMBHttpError, KMBRequestError


def _build_url(path: str, params: dict | None = None) -> str:
    base = path if path.startswith("http") else f"{API_HOST}{path}"
    if not params:
        return base
    query = urlencode(params)
    return f"{base}?{query}"


def request_json(method: str, path: str, payload: dict | None = None, params: dict | None = None) -> dict:
    url = _build_url(path, params)
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    headers = build_headers(include_json=payload is not None)

    req = Request(url, data=data, headers=headers, method=method.upper())

    try:
        with urlopen(req, timeout=DEFAULT_TIMEOUT) as response:
            body = response.read().decode("utf-8")
            if not body:
                return {}
            return json.loads(body)
    except HTTPError as e:
        body = e.read().decode("utf-8", errors="replace") if e.fp else ""
        raise KMBHttpError(e.code, e.reason, url, body) from e
    except URLError as e:
        raise KMBRequestError(f"Connection failed: {e.reason}") from e


def get_json(path: str, params: dict | None = None) -> dict:
    return request_json("GET", path, params=params)


def post_json(path: str, payload: dict | None = None) -> dict:
    return request_json("POST", path, payload=payload)
