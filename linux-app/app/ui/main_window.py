"""Main window: header (title + connection dot + settings gear), stacked
Home / SkillDetail, and a status bar."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QMainWindow, QPushButton, QStackedWidget,
    QStatusBar, QVBoxLayout, QWidget,
)

from ..theme import ACCENT, DANGER, OK, TEXT, TEXT_DIM, WARN
from .home import HomePage
from .settings import SettingsDialog
from .skill_detail import SkillDetailPage


class MainWindow(QMainWindow):
    def __init__(self, state):
        super().__init__()
        self.state = state
        self.setWindowTitle("DEMO-local-ai-with-gemma-by-google")
        self.resize(1080, 720)

        central = QWidget()
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ---- header bar ----
        header = QFrame()
        header.setObjectName("header")
        header.setFixedHeight(56)
        hl = QHBoxLayout(header)
        hl.setContentsMargins(20, 0, 16, 0)

        title = QLabel("demo app by Nara (Hermes Agent)")
        title.setObjectName("headerTitle")
        hl.addWidget(title)

        hl.addStretch(1)

        self.dot = QLabel()
        self.dot.setObjectName("dot")
        self.dot.setFixedSize(12, 12)
        hl.addWidget(self.dot)

        self.conn_label = QLabel("Not connected")
        self.conn_label.setObjectName("dim")
        hl.addWidget(self.conn_label)

        self.settings_btn = QPushButton("⚙ Settings")
        self.settings_btn.setObjectName("ghost")
        self.settings_btn.setCursor(Qt.PointingHandCursor)
        self.settings_btn.clicked.connect(self._open_settings)
        hl.addWidget(self.settings_btn)

        root.addWidget(header)

        # ---- content stack ----
        self.stack = QStackedWidget()
        self.home = HomePage(state)
        self.stack.addWidget(self.home)
        root.addWidget(self.stack, 1)

        self.setCentralWidget(central)

        # ---- status bar ----
        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self._status_label = QLabel("Ready")
        self._status_label.setStyleSheet(f"color: {TEXT_DIM}; padding: 0 8px;")
        self.status.addWidget(self._status_label)

        # ---- signals ----
        self.home.skill_selected.connect(self._open_skill)
        self.home.open_settings.connect(self._open_settings)
        self.home.clear_earth.connect(self._clear_earth)
        self.home.show_logo.connect(lambda: self.state.show_logo())

        state.status_message.connect(self._on_status)
        state.busy_changed.connect(self._on_busy)
        state.connected_changed.connect(self._on_connected)

        self._on_connected(state.connected)

    # ------------------------------------------------------------- nav
    def _open_skill(self, skill):
        page = SkillDetailPage(skill)
        page.back.connect(self._go_home)
        page.deploy_viz.connect(self._deploy)
        self.stack.addWidget(page)
        self.stack.setCurrentWidget(page)

    def _go_home(self):
        while self.stack.count() > 1:
            w = self.stack.widget(self.stack.count() - 1)
            self.stack.removeWidget(w)
            w.deleteLater()
        self.stack.setCurrentWidget(self.home)

    def _open_settings(self):
        dlg = SettingsDialog(self.state, self)
        dlg.exec()

    # ------------------------------------------------------------- actions
    def _deploy(self, viz):
        self.state.send_visualization(viz)

    def _clear_earth(self):
        self.state.clear_earth()

    # ------------------------------------------------------------- status
    def _on_status(self, message, is_error):
        color = DANGER if is_error else TEXT_DIM
        self._status_label.setText(message)
        self._status_label.setStyleSheet(f"color: {color}; padding: 0 8px;")
        self.status.showMessage(message, 6000)

    def _on_busy(self, busy):
        if busy:
            self._status_label.setText("Working…")
            self._status_label.setStyleSheet(f"color: {TEXT_DIM}; padding: 0 8px;")

    def _on_connected(self, connected):
        if connected:
            self.dot.setStyleSheet(f"background-color: {OK};")
            self.conn_label.setText("Connected")
        else:
            self.dot.setStyleSheet(f"background-color: {WARN};")
            self.conn_label.setText("Not connected")
