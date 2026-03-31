"""Backend base URL (HTTPS) and derived API / WebSocket URLs."""

from __future__ import annotations

import os
from pathlib import Path
from urllib.parse import urlencode, urlparse, urlunparse

from dotenv import load_dotenv

# desktop/ is parents[2] from src/askui_desktop/config.py
_DESKTOP_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(_DESKTOP_ROOT / ".env")
load_dotenv()

_DEFAULT_BACKEND_BASE_URL = "https://03c9-96-21-151-117.ngrok-free.app"
BACKEND_BASE_URL = os.environ.get("BACKEND_BASE_URL", _DEFAULT_BACKEND_BASE_URL).strip()
if not BACKEND_BASE_URL:
    BACKEND_BASE_URL = _DEFAULT_BACKEND_BASE_URL
APPOINTMENTS_WS_PATH = "/v1/appointments/ws/appointments"

WORKSPACE_ID = os.environ.get("WORKSPACE_ID", "").strip()

NGROK_HTTP_HEADERS: dict[str, str] = {"ngrok-skip-browser-warning": "true"}


def appointments_websocket_url(workspace_id: str) -> str:
    """WSS URL with workspace_id query for backend auth."""
    u = urlparse(BACKEND_BASE_URL.rstrip("/"))
    path = (
        APPOINTMENTS_WS_PATH
        if APPOINTMENTS_WS_PATH.startswith("/")
        else f"/{APPOINTMENTS_WS_PATH}"
    )
    query = urlencode({"workspace_id": workspace_id.strip()})
    return urlunparse(("wss", u.netloc, path, "", query, ""))


def api_url(relative_path: str) -> str:
    """Join BACKEND_BASE_URL with a path for HTTP requests (e.g. ``/v1/foo``)."""
    base = BACKEND_BASE_URL.rstrip("/")
    p = relative_path.strip()
    if not p.startswith("/"):
        p = f"/{p}"
    return f"{base}{p}"
