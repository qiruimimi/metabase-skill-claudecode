"""Centralized runtime configuration for kmb-metabase scripts."""

import os

API_HOST = os.environ.get("KMB_API_HOST", "https://kmb.qunhequnhe.com")
API_KEY = os.environ.get("KMB_API_KEY", "")
DEFAULT_TIMEOUT = int(os.environ.get("KMB_TIMEOUT", "30"))


def build_headers(include_json: bool = False) -> dict:
    """Build request headers with API key."""
    if not API_KEY:
        raise ValueError("KMB_API_KEY environment variable not set")
    headers = {"x-api-key": API_KEY}
    if include_json:
        headers["Content-Type"] = "application/json"
    return headers
