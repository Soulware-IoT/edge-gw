"""The forwarder: a generic reverse proxy to the cloud backend.

The gateway is a dumb pass-through. It does not know any specific endpoint — it relays
whatever method, path, query string, headers, and body the edge application sends to the
same path on the backend, and hands the backend's response straight back. The edge
device's ``X-Edge-Api-Key`` rides along in the headers like any other header.
"""
import requests

from gateway.config import GatewayConfig

REQUEST_TIMEOUT_SECONDS = 10


class BackendForwarder:
    """Relays an arbitrary request to the backend.

    Args:
        config: the backend URL.
    """

    def __init__(self, config: GatewayConfig):
        self.config = config

    def forward(self, method: str, path: str, params=None, headers=None, data=None) -> requests.Response:
        """Relay a request to ``{backend_url}/{path}`` and return the raw response.

        Args:
            method: the HTTP method to replay.
            path: the request path (without leading slash), forwarded unchanged.
            params: the query-string parameters to forward.
            headers: the request headers to forward (including ``X-Edge-Api-Key``).
            data: the raw request body to forward.

        Returns:
            requests.Response: the backend's response, relayed as-is by the caller.

        Raises:
            requests.RequestException: if the backend is unreachable / times out.
        """
        return requests.request(
            method=method,
            url=f"{self.config.backend_url}/{path}",
            params=params,
            headers=headers,
            data=data,
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
