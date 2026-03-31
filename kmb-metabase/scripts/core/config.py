"""Centralized runtime configuration for kmb-metabase scripts."""

API_HOST = "https://kmb.qunhequnhe.com"
API_KEY = "mb_h5ddq58TgNTAZsV7e81myvAxMlMcqXWrx1y9TdqArl8="
DEFAULT_TIMEOUT = 30


def build_headers(include_json: bool = False) -> dict:
    headers = {"x-api-key": API_KEY}
    if include_json:
        headers["Content-Type"] = "application/json"
    return headers
