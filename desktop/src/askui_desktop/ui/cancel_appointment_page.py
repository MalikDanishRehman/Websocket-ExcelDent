"""Cancel appointment form — submits via WebSocket."""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

from PySide6.QtWidgets import (
    QFormLayout,
    QGroupBox,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

if TYPE_CHECKING:
    from askui_desktop.ui.websocket_manager import WebSocketManager


class CancelAppointmentPage(QWidget):
    def __init__(
        self,
        ws_manager: WebSocketManager,
        workspace_id_provider: Callable[[], str],
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._ws = ws_manager
        self._workspace_id_provider = workspace_id_provider

        self._patient = QLineEdit()
        self._notes = QLineEdit()

        form = QFormLayout()
        form.addRow("Patient", self._patient)
        form.addRow("Notes", self._notes)

        box = QGroupBox("Cancel appointment")
        box.setLayout(form)

        self._submit = QPushButton("Submit")
        self._submit.clicked.connect(self._on_submit)

        root = QVBoxLayout(self)
        root.addWidget(box)
        root.addWidget(self._submit)
        root.addStretch()

    def _on_submit(self) -> None:
        workspace_id = self._workspace_id_provider().strip()
        if not workspace_id:
            QMessageBox.warning(self, "Cancel appointment", "Workspace ID is required.")
            return

        data = {
            "patient_name": self._patient.text().strip(),
            "file_number": None,
            "notes": self._notes.text().strip(),
        }
        payload = {
            "action": "cancel_appointment",
            "workspace_id": workspace_id,
            "data": data,
        }
        if not self._ws.send_json(payload):
            QMessageBox.warning(
                self,
                "Cancel appointment",
                "WebSocket not connected. Click Connect WS first.",
            )
