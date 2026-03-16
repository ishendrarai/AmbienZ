"""
main.py — Light Wiz entry point.

Usage:
    python main.py

Build:
    pyinstaller --onefile --noconsole --name LightWiz \
                --add-data "config.json;." \
                --add-data "assets;assets" \
                main.py
"""

import sys
import os

# Ensure repo root is on path (works both dev + PyInstaller)
_BASE = os.path.dirname(os.path.abspath(__file__))
if _BASE not in sys.path:
    sys.path.insert(0, _BASE)

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from ui.main_window import MainWindow
from ui.tray import start_tray


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Light Wiz")
    app.setOrganizationName("LightWiz")

    window = MainWindow()
    window.show()

    # System tray (gracefully no-ops if pystray not installed)
    tray_state = start_tray(
        on_start=window._engine.start,
        on_stop=window._engine.stop,
        on_open=window.show,
        on_quit=app.quit,
        icon_path=os.path.join(_BASE, "assets", "icon.png"),
    )

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
