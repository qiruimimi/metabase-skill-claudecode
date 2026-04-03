"""Shared HTTP helpers for kmb-metabase scripts."""

from __future__ import annotations

import json
import subprocess
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from kmb.config import API_HOST, DEFAULT_TIMEOUT, build_headers
from kmb.errors import KMBHttpError, KMBRequestError


def _build_url(path: str, params: dict | None = None) -> str:
    """Build full URL from path and query params."""
    base = path if path.startswith("http") else f"{API_HOST}{path}"
    if not params:
        return base
    query = urlencode(params)
    return f"{base}?{query}"


def _request_json_with_curl(
    method: str,
    url: str,
    payload: dict | None = None,
    headers: dict | None = None,
) -> dict:
    cmd = [
        "curl",
        "-sS",
        "--http1.1",
        "-X",
        method.upper(),
        url,
        "-w",
        "\n%{http_code}",
    ]

    for key, value in (headers or {}).items():
        cmd.extend(["-H", f"{key}: {value}"])

    if payload is not None:
        cmd.extend(["--data", json.dumps(payload)])

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=DEFAULT_TIMEOUT,
            check=False,
        )
    except Exception as e:
        raise KMBRequestError(f"curl fallback failed: {e}") from e

    if result.returncode != 0:
        raise KMBRequestError(result.stderr.strip() or "curl fallback failed")

    body, _, status_text = result.stdout.rpartition("\n")
    try:
        status_code = int(status_text.strip())
    except ValueError as e:
        raise KMBRequestError("curl fallback returned an invalid HTTP status") from e

    if status_code >= 400:
        raise KMBHttpError(status_code, "curl fallback HTTP error", url, body)

    if not body.strip():
        return {}
    return json.loads(body)


def request_json(
    method: str,
    path: str,
    payload: dict | None = None,
    params: dict | None = None
) -> dict:
    """Make HTTP request and return JSON response."""
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
        reason = str(e.reason)
        if "SSL:" in reason or "EOF occurred in violation of protocol" in reason:
            return _request_json_with_curl(method, url, payload=payload, headers=headers)
        raise KMBRequestError(f"Connection failed: {e.reason}") from e


def get_json(path: str, params: dict | None = None) -> dict:
    """Make GET request and return JSON."""
    return request_json("GET", path, params=params)


def post_json(path: str, payload: dict | None = None) -> dict:
    """Make POST request and return JSON."""
    return request_json("POST", path, payload=payload)


def put_json(path: str, payload: dict | None = None) -> dict:
    """Make PUT request and return JSON."""
    return request_json("PUT", path, payload=payload)


def delete_json(path: str, params: dict | None = None) -> dict:
    """Make DELETE request and return JSON."""
    return request_json("DELETE", path, params=params)
