"""WebSocket client for appointment remote-control actions (Qt event loop, non-blocking)."""

from __future__ import annotations

import json
import logging
import os

from PySide6.QtCore import QObject, QUrl, Signal
from PySide6.QtNetwork import QAbstractSocket
from PySide6.QtWebSockets import QWebSocket

from askui_desktop.config import appointments_websocket_url

logger = logging.getLogger(__name__)


def resolve_ws_url(
    explicit: str | None = None,
    workspace_id: str | None = None,
) -> str:
    """URL order: explicit arg, env ASKUI_WS_URL, then appointments URL + workspace_id query."""
    if explicit:
        return explicit
    env_url = os.environ.get("ASKUI_WS_URL", "").strip()
    if env_url:
        return env_url
    wid = (workspace_id or "").strip()
    if not wid:
        return ""
    return appointments_websocket_url(wid)


class WebSocketManager(QObject):
    """Owns a QWebSocket; connect/disconnect and send JSON without blocking the UI."""

    sig_connected = Signal()
    sig_disconnected = Signal()
    sig_error = Signal(str)
    sig_message_received = Signal(str)

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._socket = QWebSocket()
        self._socket.connected.connect(self._on_socket_connected)
        self._socket.disconnected.connect(self._on_socket_disconnected)
        self._socket.textMessageReceived.connect(self._on_text_message)
        self._socket.errorOccurred.connect(self._on_error)

    def _on_socket_connected(self) -> None:
        logger.info("WebSocket connected to %s", self._socket.requestUrl().toString())
        self.sig_connected.emit()

    def _on_socket_disconnected(self) -> None:
        logger.info("WebSocket disconnected")
        self.sig_disconnected.emit()

    def _on_text_message(self, message: str) -> None:
        logger.info("WS recv: %s", message)
        print(f"[WS] {message}")
        self.sig_message_received.emit(message)

    def _on_error(self, error) -> None:
        err = self._socket.errorString()
        logger.warning("WebSocket error: %s (%s)", err, error)
        self.sig_error.emit(err)

    def connect_to_server(
        self,
        url: str | None = None,
        workspace_id: str | None = None,
    ) -> None:
        resolved = resolve_ws_url(url, workspace_id)
        if not resolved:
            msg = (
                "WebSocket URL missing: set WORKSPACE_ID (e.g. in .env), fill Workspace ID, "
                "or set ASKUI_WS_URL."
            )
            logger.error(msg)
            self.sig_error.emit(msg)
            return
        logger.info("WebSocket connect to %s", resolved)
        self._socket.open(QUrl(resolved))

    def disconnect_from_server(self) -> None:
        self._socket.close()

    def is_connected(self) -> bool:
        return self._socket.state() == QAbstractSocket.SocketState.ConnectedState

    def send_json(self, obj: dict) -> bool:
        if not self.is_connected():
            logger.warning("send_json skipped: not connected")
            return False
        try:
            text = json.dumps(obj)
        except (TypeError, ValueError) as e:
            logger.exception("send_json: invalid payload: %s", e)
            return False
        self._socket.sendTextMessage(text)
        logger.info("WS send: %s", text)
        return True
