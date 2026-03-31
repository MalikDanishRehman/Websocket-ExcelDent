"""Create appointment form — submits via WebSocket."""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

from PySide6.QtCore import QDate, QTime
from PySide6.QtWidgets import (
    QComboBox,
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


def _configure_time_24h(widget: QTimeEdit) -> None:
    """Force 24-hour display (HH:mm), no AM/PM."""
    widget.setDisplayFormat("HH:mm")


class CreateAppointmentPage(QWidget):
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
        self._phone = QLineEdit()
        self._language = QComboBox()
        self._language.addItems(["English", "French"])
        self._gender = QComboBox()
        self._gender.addItems(["Male", "Female"])
        self._doctor = QLineEdit()
        self._date = QDateEdit()
        self._date.setCalendarPopup(True)
        self._date.setDate(QDate.currentDate())
        self._start_time = QTimeEdit()
        self._start_time.setTime(QTime(9, 0))
        _configure_time_24h(self._start_time)
        self._end_time = QTimeEdit()
        self._end_time.setTime(QTime(9, 30))
        _configure_time_24h(self._end_time)
        self._notes = QLineEdit()

        form = QFormLayout()
        form.addRow("Patient", self._patient)
        form.addRow("Phone Number", self._phone)
        form.addRow("Language", self._language)
        form.addRow("Gender", self._gender)
        form.addRow("Doctor", self._doctor)
        form.addRow("Date", self._date)
        form.addRow("Start Time", self._start_time)
        form.addRow("End Time", self._end_time)
        form.addRow("Notes", self._notes)

        box = QGroupBox("Create appointment")
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
            QMessageBox.warning(self, "Create appointment", "Workspace ID is required.")
            return

        start_time = self._start_time.time().toString("HH:mm")
        end_time = self._end_time.time().toString("HH:mm")
        data = {
            "date": self._date.date().toString("yyyy-MM-dd"),
            "start_time": start_time,
            "end_time": end_time,
            "patient": {
                "name": self._patient.text().strip(),
                "file_number": None,
                "phone_number": self._phone.text().strip(),
                "language": self._language.currentText(),
                "gender": self._gender.currentText(),
            },
            "notes": self._notes.text().strip(),
            "optional": {
                "professional": self._doctor.text().strip(),
                "treatment": None,
            },
        }
        payload = {
            "action": "create_appointment",
            "workspace_id": workspace_id,
            "data": data,
        }
        if not self._ws.send_json(payload):
            QMessageBox.warning(
                self,
                "Create appointment",
                "WebSocket not connected. Click Connect WS first.",
            )
