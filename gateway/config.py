"""Edge gateway configuration loaded from the environment.

The gateway is a dumb forwarder: it owns no identity of its own. It only needs to know
where the backend is. The edge *device* (the edge application) holds the API key and
sends it; the gateway passes that header through unchanged.

    BACKEND_URL=http://localhost:8080 \
    PORT=5001 \
    python app.py
"""
import os
from dataclasses import dataclass


@dataclass(frozen=True)
class GatewayConfig:
    """Connection details the gateway uses to reach the backend.

    Attributes:
        backend_url: Base URL of the cloud backend (e.g. ``http://localhost:8080``).
    """

    backend_url: str


def load_config() -> GatewayConfig:
    """Build the :class:`GatewayConfig` from the required environment variable.

    Raises:
        RuntimeError: if ``BACKEND_URL`` is missing or blank.
    """
    backend_url = os.environ.get("BACKEND_URL", "").strip()
    if not backend_url:
        raise RuntimeError(
            "Missing required environment variable: BACKEND_URL. "
            "The edge gateway cannot start without the backend URL."
        )
    return GatewayConfig(backend_url=backend_url.rstrip("/"))
