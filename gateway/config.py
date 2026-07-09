"""Edge gateway configuration loaded from the environment.

The gateway is a dumb forwarder: it owns no identity of its own. It only needs to know
where the backend is and how to reach the MQTT broker used to relay servo commands to
edge apps (which may sit behind NAT/CGNAT and are unreachable by direct HTTP). The edge
*device* (the edge application) holds the API key and sends it; the gateway passes that
header through unchanged.

    BACKEND_URL=http://localhost:8080 \
    MQTT_HOST=xxxx.s1.eu.hivemq.cloud \
    MQTT_PORT=8883 \
    MQTT_USERNAME=cocina360Publisher \
    MQTT_PASSWORD=... \
    PORT=5001 \
    python app.py
"""
import os
from dataclasses import dataclass


@dataclass(frozen=True)
class GatewayConfig:
    """Connection details the gateway uses to reach the backend and the MQTT broker.

    Attributes:
        backend_url: Base URL of the cloud backend (e.g. ``http://localhost:8080``).
        mqtt_host: Hostname of the MQTT broker (HiveMQ Cloud cluster URL).
        mqtt_port: TLS port of the MQTT broker (HiveMQ Cloud: 8883).
        mqtt_username: Broker username for the gateway's publisher credentials.
        mqtt_password: Broker password for the gateway's publisher credentials.
    """

    backend_url: str
    mqtt_host: str
    mqtt_port: int
    mqtt_username: str
    mqtt_password: str


def load_config() -> GatewayConfig:
    """Build the :class:`GatewayConfig` from environment variables.

    Raises:
        RuntimeError: if a required environment variable is missing or blank.
    """
    backend_url = os.environ.get("BACKEND_URL", "").strip()
    if not backend_url:
        raise RuntimeError(
            "Missing required environment variable: BACKEND_URL. "
            "The edge gateway cannot start without the backend URL."
        )
    mqtt_host = os.environ.get("MQTT_HOST", "").strip()
    if not mqtt_host:
        raise RuntimeError("Missing required environment variable: MQTT_HOST.")
    mqtt_username = os.environ.get("MQTT_USERNAME", "").strip()
    mqtt_password = os.environ.get("MQTT_PASSWORD", "").strip()
    if not mqtt_username or not mqtt_password:
        raise RuntimeError("Missing required environment variables: MQTT_USERNAME / MQTT_PASSWORD.")
    mqtt_port = int(os.environ.get("MQTT_PORT", "8883"))
    return GatewayConfig(
        backend_url=backend_url.rstrip("/"),
        mqtt_host=mqtt_host,
        mqtt_port=mqtt_port,
        mqtt_username=mqtt_username,
        mqtt_password=mqtt_password,
    )
