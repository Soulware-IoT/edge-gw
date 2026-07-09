"""Flask entry point for the Cocina360 Edge Gateway.

A standalone, stateless artifact that sits between the edge application and the
cloud backend. It forwards the edge app's calls to the backend, attaching the edge
API key issued at registration. It owns no database — the edge application persists
anything pulled (e.g. the device registry).

Typical usage::

    BACKEND_URL=http://localhost:8080 \
    EDGE_API_KEY=<key issued by the backend> \
    PORT=5001 \
    python app.py
"""
import os

from dotenv import load_dotenv

# Load .env before importing the blueprint: config is resolved at import time.
load_dotenv()

from flask import Flask

from gateway.api import gateway_api

app = Flask(__name__)


@app.get("/healthz")
def healthz():
    """Liveness probe for the platform — answered locally, never proxied to the backend."""
    return {"status": "ok"}, 200


app.register_blueprint(gateway_api)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5001")), debug=True)
