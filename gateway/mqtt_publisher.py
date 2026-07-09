"""MQTT publisher: relays servo commands to the target edge app via the broker."""
import json

import paho.mqtt.publish as publish

from gateway.config import GatewayConfig

SERVO_TOPIC_TEMPLATE = "cocina360/edge/{edge_code}/servo"


class ServoCommandPublisher:
    """Publishes servo commands to an edge app's MQTT topic.

    Each edge app subscribes to its own topic (keyed by its edge device code) on
    connection, so publishing here reaches it regardless of its network location —
    unlike a direct HTTP call, this works behind NAT/CGNAT since the edge app holds
    the outbound connection to the broker.
    """

    def __init__(self, config: GatewayConfig):
        self.host = config.mqtt_host
        self.port = config.mqtt_port
        self.username = config.mqtt_username
        self.password = config.mqtt_password

    def send_servo_command(self, edge_code: str, iot_device_id: str, command: str) -> None:
        """Publish a servo command to the given edge device's topic.

        Args:
            edge_code: The target edge device's code (e.g. ``EDGE-FA9ABE9C``).
            iot_device_id: UUID of the IoT device whose servo to control.
            command: ``"start"`` or ``"stop"``.

        Raises:
            Exception: if the broker connection or publish fails.
        """
        topic = SERVO_TOPIC_TEMPLATE.format(edge_code=edge_code)
        payload = json.dumps({"iotDeviceId": iot_device_id, "command": command})
        publish.single(
            topic,
            payload=payload,
            hostname=self.host,
            port=self.port,
            auth={"username": self.username, "password": self.password},
            tls={},
        )
