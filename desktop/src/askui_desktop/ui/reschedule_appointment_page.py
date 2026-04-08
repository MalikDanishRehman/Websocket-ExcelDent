"""Reschedule appointment form — submits via WebSocket."""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

from PySide6.QtCore import QDate, QTime
from PySide6.QtWidgets import (
    QDateEdit,
    QFormLayout,
    QGroupBox,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTimeEdit,
    QVBoxLayout,
    QWidget,
)

if TYPE_CHECKING:
    from askui_desktop.ui.websocket_manager import WebSocketManager


class RescheduleAppointmentPage(QWidget):
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
        self._new_date = QDateEdit()
        self._new_date.setCalendarPopup(True)
        self._new_date.setDate(QDate.currentDate())
        self._new_start_time = QTimeEdit()
        self._new_start_time.setDisplayFormat("HH:mm")
        self._new_start_time.setTime(QTime(10, 0))
        self._new_end_time = QTimeEdit()
        self._new_end_time.setDisplayFormat("HH:mm")
        self._new_end_time.setTime(QTime(10, 30))
        self._notes = QLineEdit()

        form = QFormLayout()
        form.addRow("Patient", self._patient)
        form.addRow("Date", self._new_date)
        form.addRow("New Start Time", self._new_start_time)
        form.addRow("New End Time", self._new_end_time)
        form.addRow("Notes", self._notes)

        box = QGroupBox("Reschedule appointment")
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
            QMessageBox.warning(self, "Reschedule appointment", "Workspace ID is required.")
            return

        new_start = self._new_start_time.time().toString("HH:mm")
        new_end = self._new_end_time.time().toString("HH:mm")
        data = {
            "patient_name": self._patient.text().strip(),
            "file_number": None,
            "new_date": self._new_date.date().toString("yyyy-MM-dd"),
            "new_start_time": new_start,
            "new_end_time": new_end,
            "notes": self._notes.text().strip(),
        }
        payload = {
            "action": "reschedule_appointment",
            "workspace_id": workspace_id,
            "data": data,
        }
        if not self._ws.send_json(payload):
            QMessageBox.warning(
                self,
                "Reschedule appointment",
                "WebSocket not connected. Click Connect WS first.",
            )
