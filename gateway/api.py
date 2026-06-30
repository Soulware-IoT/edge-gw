"""The gateway's HTTP surface.

Outbound (edge app → backend): a catch-all that proxies to the backend at the same path.
Inbound (backend → edge app): a specific ``POST /servo`` route that reads the target edge
app IP from the payload and forwards the command directly to that instance.
"""
import requests
from flask import Blueprint, Response, jsonify, request

from gateway.backend_client import BackendForwarder
from gateway.config import load_config
from gateway.edge_app_client import EdgeAppClient

gateway_api = Blueprint("gateway_api", __name__)

_config = load_config()
forwarder = BackendForwarder(_config)
edge_app_client = EdgeAppClient(_config)

# Headers that must not be forwarded — the outbound request recomputes them.
EXCLUDED_REQUEST_HEADERS = {"host", "content-length"}


@gateway_api.route("/servo", methods=["POST"])
def servo():
    """Route a servo command from the backend to the target edge app instance.

    Expected body: ``{"edgeAppIp": "...", "iotDeviceId": "...", "command": "start|stop"}``
    """
    body = request.get_json(silent=True) or {}
    edge_app_ip = body.get("edgeAppIp")
    iot_device_id = body.get("iotDeviceId")
    command = body.get("command")

    if not edge_app_ip or not iot_device_id or not command:
        return jsonify({"error": "Missing required fields: edgeAppIp, iotDeviceId, command"}), 400

    try:
        edge_app_client.send_servo_command(edge_app_ip, iot_device_id, command)
    except requests.RequestException as error:
        return jsonify({"error": f"Edge app unreachable at {edge_app_ip}: {error}"}), 502

    return "", 200


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
