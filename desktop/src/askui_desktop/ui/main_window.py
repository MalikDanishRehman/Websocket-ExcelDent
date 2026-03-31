"""Main window: WebSocket controls and appointment tabs."""

from __future__ import annotations

import logging

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from askui_desktop.config import WORKSPACE_ID as CONFIG_WORKSPACE_ID
from askui_desktop.ui.cancel_appointment_page import CancelAppointmentPage
from askui_desktop.ui.create_appointment_page import CreateAppointmentPage
from askui_desktop.ui.reschedule_appointment_page import RescheduleAppointmentPage
from askui_desktop.ui.websocket_manager import WebSocketManager

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Appointments")
        self.setMinimumSize(520, 420)

        self._ws = WebSocketManager(self)
        self._ws.sig_connected.connect(self._on_ws_connected)
        self._ws.sig_disconnected.connect(self._on_ws_disconnected)
        self._ws.sig_error.connect(self._on_ws_error)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        bar = QHBoxLayout()
        self._btn_connect = QPushButton("Connect WS")
        self._btn_connect.clicked.connect(self._on_connect_ws_clicked)
        self._btn_disconnect = QPushButton("Disconnect")
        self._btn_disconnect.clicked.connect(self._ws.disconnect_from_server)
        bar.addWidget(self._btn_connect)
        bar.addWidget(self._btn_disconnect)
        self._ws_status = QLabel("WS: disconnected")
        self._ws_status.setStyleSheet("color: #c44;")
        bar.addWidget(self._ws_status)
        bar.addWidget(QLabel("Workspace ID:"))
        self._workspace_id = QLineEdit()
        self._workspace_id.setPlaceholderText("required in payload data")
        if CONFIG_WORKSPACE_ID:
            self._workspace_id.setText(CONFIG_WORKSPACE_ID)
        bar.addWidget(self._workspace_id, stretch=1)
        layout.addLayout(bar)

        def workspace_id_provider() -> str:
            return self._workspace_id.text()

        self._tabs = QTabWidget()
        self._tabs.addTab(
            CreateAppointmentPage(self._ws, workspace_id_provider),
            "Create",
        )
        self._tabs.addTab(
            CancelAppointmentPage(self._ws, workspace_id_provider),
            "Cancel",
        )
        self._tabs.addTab(
            RescheduleAppointmentPage(self._ws, workspace_id_provider),
            "Reschedule",
        )
        layout.addWidget(self._tabs)

        # Optional: connect shortly after startup so the UI paints first
        QTimer.singleShot(0, self._on_connect_ws_clicked)

    def _on_connect_ws_clicked(self) -> None:
        self._ws_status.setText("WS: connecting…")
        self._ws_status.setStyleSheet("color: #aa8400;")
        self._ws.connect_to_server(workspace_id=self._workspace_id.text().strip())

    def _on_ws_connected(self) -> None:
        logger.info("UI: WebSocket connected")
        self._ws_status.setText("WS: connected")
        self._ws_status.setStyleSheet("color: #2a4;")
        self.statusBar().showMessage("WebSocket connected", 5000)

    def _on_ws_disconnected(self) -> None:
        logger.info("UI: WebSocket disconnected")
        self._ws_status.setText("WS: disconnected")
        self._ws_status.setStyleSheet("color: #c44;")
        self.statusBar().showMessage("WebSocket disconnected", 5000)

    def _on_ws_error(self, message: str) -> None:
        logger.warning("UI: WebSocket error: %s", message)
        self._ws_status.setText("WS: error (see status bar)")
        self._ws_status.setStyleSheet("color: #c44;")
        self.statusBar().showMessage(f"WebSocket error: {message}", 8000)
