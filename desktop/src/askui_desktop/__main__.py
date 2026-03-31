"""Run the desktop app: python -m askui_desktop"""

from __future__ import annotations

import logging
import sys

from PySide6.QtWidgets import QApplication

from askui_desktop.ui.main_window import MainWindow

logging.basicConfig(level=logging.INFO)


def main() -> None:
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    raise SystemExit(app.exec())


if __name__ == "__main__":
    main()
