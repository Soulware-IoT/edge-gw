"""Client for forwarding device commands to a specific edge app instance."""
import requests

from gateway.config import GatewayConfig

REQUEST_TIMEOUT_SECONDS = 10


class EdgeAppClient:
    """Sends device commands to an edge app at a given IP.

    The IP is provided per-request (stored in the backend and included in the
    command payload), so one gateway instance can route to any number of edge apps.
    """

    def __init__(self, config: GatewayConfig):
        self.port = config.edge_app_port

    def send_servo_command(self, edge_app_ip: str, iot_device_id: str, command: str) -> None:
        """POST a servo command to the edge app at the given IP.

        Args:
            edge_app_ip: IP address of the target edge app instance.
            iot_device_id: UUID of the IoT device whose servo to control.
            command: ``"start"`` or ``"stop"``.

        Raises:
            requests.RequestException: if the edge app is unreachable or times out.
        """
        url = f"http://{edge_app_ip}:{self.port}/servo"
        requests.post(
            url,
            json={"iotDeviceId": iot_device_id, "command": command},
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
