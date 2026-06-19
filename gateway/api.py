"""The gateway's HTTP surface: a single catch-all that proxies to the backend.

The edge application calls this gateway at the *same path* it wants on the backend
(e.g. ``GET /edge/me``); the gateway forwards it verbatim — method, path, query string,
headers (including ``X-Edge-Api-Key``), and body — and relays the backend's response back.
It knows nothing about specific endpoints; it is simply a pass-through.
"""
import requests
from flask import Blueprint, Response, jsonify, request

from gateway.backend_client import BackendForwarder
from gateway.config import load_config

gateway_api = Blueprint("gateway_api", __name__)

forwarder = BackendForwarder(load_config())

# Headers that must not be forwarded — the outbound request recomputes them.
EXCLUDED_REQUEST_HEADERS = {"host", "content-length"}


@gateway_api.route("/<path:path>", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
def proxy(path: str):
    """Forward any request to the backend at the same path and relay the response."""
    headers = {
        key: value
        for key, value in request.headers
        if key.lower() not in EXCLUDED_REQUEST_HEADERS
    }
    try:
        response = forwarder.forward(
            method=request.method,
            path=path,
            params=request.args,
            headers=headers,
            data=request.get_data(),
        )
    except requests.RequestException as error:
        return jsonify({"error": f"Backend unreachable: {error}"}), 502

    return Response(
        response.content,
        status=response.status_code,
        content_type=response.headers.get("Content-Type"),
    )
