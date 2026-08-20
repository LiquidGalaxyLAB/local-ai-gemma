"""Liquid Galaxy Demo Suite — Ubuntu desktop companion app.

Same use cases + KML assets + SSH protocol as the Android app. Stack:
PySide6 (GUI) + paramiko (SSH), sharing skills.json + assets/kml.

Run:  python3 main.py
"""
import os
import sys

from PySide6.QtWidgets import QApplication

from app.state import AppState
from app.theme import build_stylesheet
from app.ui.main_window import MainWindow

# asset_root = the bundle root (ubuntu_app/), which CONTAINS the assets/ dir.
# skills.json -> assets/skills.json; viz paths -> "assets/kml/...".
ASSET_ROOT = os.path.dirname(os.path.abspath(__file__))


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("DEMO-local-ai-with-gemma-by-google")
    app.setStyleSheet(build_stylesheet())

    state = AppState(ASSET_ROOT)
    state.load_skills()

    win = MainWindow(state)
    win.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
