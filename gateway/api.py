"""The gateway's HTTP surface.

Outbound (edge app → backend): a catch-all that proxies to the backend at the same path.
Inbound (backend → edge app): a specific ``POST /servo`` route that publishes the command
to the target edge app's MQTT topic — the edge app holds the subscription, so this works
even when the edge app is behind NAT/CGNAT and unreachable by direct HTTP.
"""
import requests
from flask import Blueprint, Response, jsonify, request

from gateway.backend_client import BackendForwarder
from gateway.config import load_config
from gateway.mqtt_publisher import ServoCommandPublisher

gateway_api = Blueprint("gateway_api", __name__)

_config = load_config()
forwarder = BackendForwarder(_config)
servo_publisher = ServoCommandPublisher(_config)

# Headers that must not be forwarded — the outbound request recomputes them.
EXCLUDED_REQUEST_HEADERS = {"host", "content-length", "accept-encoding"}


@gateway_api.route("/servo", methods=["POST"])
def servo():
    """Route a servo command from the backend to the target edge app instance via MQTT.

    Expected body: ``{"edgeCode": "...", "iotDeviceId": "...", "command": "start|stop"}``
    """
    body = request.get_json(silent=True) or {}
    edge_code = body.get("edgeCode")
    iot_device_id = body.get("iotDeviceId")
    command = body.get("command")

    if not edge_code or not iot_device_id or not command:
        return jsonify({"error": "Missing required fields: edgeCode, iotDeviceId, command"}), 400

    try:
        servo_publisher.send_servo_command(edge_code, iot_device_id, command)
    except Exception as error:
        return jsonify({"error": f"Failed to publish servo command via MQTT: {error}"}), 502

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
