"""Settings dialog: connection fields + test + advanced actions."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox, QDialog, QFormLayout, QHBoxLayout, QLabel, QLineEdit,
    QMessageBox, QPushButton, QVBoxLayout,
)

from ..theme import DANGER, OK, TEXT_DIM


class SettingsDialog(QDialog):
    def __init__(self, state, parent=None):
        super().__init__(parent)
        self.state = state
        self.setWindowTitle("Settings")
        self.setMinimumWidth(480)
        self._build()
        self._load()
        state.busy_changed.connect(self._update_busy)
        state.status_message.connect(self._on_status)
        state.connected_changed.connect(self._on_connected)

    def _build(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(24, 24, 24, 24)
        outer.setSpacing(14)

        title = QLabel("Liquid Galaxy Connection")
        title.setObjectName("title")
        outer.addWidget(title)

        sub = QLabel("Enter the rig's master node details to control it.")
        sub.setObjectName("dim")
        outer.addWidget(sub)

        form = QFormLayout()
        form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignRight)

        self.host = QLineEdit()
        self.host.setPlaceholderText("e.g. 192.168.1.12")
        form.addRow("Master IP address", self.host)

        self.username = QLineEdit()
        form.addRow("SSH username", self.username)

        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)
        form.addRow("SSH password", self.password)

        self.port = QLineEdit()
        self.port.setPlaceholderText("22")
        form.addRow("SSH port", self.port)

        self.screens = QComboBox()
        for n in range(2, 10):
            self.screens.addItem(str(n), n)
        form.addRow("Number of screens", self.screens)
        outer.addLayout(form)

        # status line
        self.status = QLabel("")
        self.status.setWordWrap(True)
        self.status.setStyleSheet(f"color: {TEXT_DIM};")
        outer.addWidget(self.status)

        # actions
        row = QHBoxLayout()
        test_btn = QPushButton("Test connection")
        test_btn.setObjectName("primary")
        test_btn.clicked.connect(self._test)
        row.addWidget(test_btn)
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self._save)
        row.addWidget(save_btn)
        row.addStretch(1)
        close_btn = QPushButton("Close")
        close_btn.setObjectName("ghost")
        close_btn.clicked.connect(self.accept)
        row.addWidget(close_btn)
        outer.addLayout(row)

        # advanced
        adv_label = QLabel("Advanced")
        adv_label.setStyleSheet(f"color: {TEXT_DIM}; font-weight: 600;")
        outer.addWidget(adv_label)

        adv = QHBoxLayout()
        logo_btn = QPushButton("Show logo")
        logo_btn.setObjectName("ghost")
        logo_btn.clicked.connect(lambda: self.state.show_logo())
        relaunch_btn = QPushButton("Relaunch Earth")
        relaunch_btn.setObjectName("ghost")
        relaunch_btn.clicked.connect(self._confirm_relaunch)
        reboot_btn = QPushButton("Reboot rig")
        reboot_btn.setObjectName("danger")
        reboot_btn.clicked.connect(self._confirm_reboot)
        adv.addWidget(logo_btn)
        adv.addWidget(relaunch_btn)
        adv.addWidget(reboot_btn)
        adv.addStretch(1)
        outer.addLayout(adv)

        self._adv_buttons = [logo_btn, relaunch_btn, reboot_btn]

    def _load(self):
        self.host.setText(self.state.host)
        self.username.setText(self.state.username)
        self.password.setText(self.state.password)
        self.port.setText(self.state.port)
        idx = self.screens.findData(self.state.screen_count)
        if idx >= 0:
            self.screens.setCurrentIndex(idx)

    def _read_form(self):
        """Copy form field values into state (BEFORE validating/saving)."""
        self.state.host = self.host.text().strip()
        self.state.username = self.username.text().strip()
        self.state.password = self.password.text()
        self.state.port = self.port.text().strip()
        self.state.screens = str(self.screens.currentData() or 3)

    def _validate(self) -> bool:
        if not self.state.host:
            QMessageBox.warning(self, "Settings",
                                "Please enter the master IP address.")
            return False
        try:
            p = int(self.state.port)
            if not (1 <= p <= 65535):
                raise ValueError
        except ValueError:
            QMessageBox.warning(self, "Settings",
                                "SSH port must be a number between 1 and 65535.")
            return False
        return True

    def _save(self):
        self._read_form()          # read the form FIRST
        if not self._validate():
            return
        self.state.save_settings()
        self._set_status("Settings saved", OK)

    def _test(self):
        self._read_form()          # read the form FIRST
        if not self._validate():
            return
        self.state.save_settings()
        self._set_status("Connecting…", TEXT_DIM)
        self.state.test_connection()

    def _confirm_relaunch(self):
        if self._confirm("Relaunch Earth?", "This restarts Earth on all screens."):
            self.state.relaunch_rig()

    def _confirm_reboot(self):
        if self._confirm("Reboot the rig?",
                         "All screens will reboot. Cannot be undone remotely."):
            self.state.reboot_rig()

    def _confirm(self, title, body):
        r = QMessageBox.question(
            self, title, body,
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        return r == QMessageBox.Yes

    def _set_status(self, text, color=TEXT_DIM):
        self.status.setText(text)
        self.status.setStyleSheet(f"color: {color};")

    def _on_status(self, message, is_error):
        self._set_status(message, DANGER if is_error else OK)

    def _on_connected(self, connected):
        if connected:
            self._set_status("Connected to the rig ✓", OK)

    def _update_busy(self, busy):
        for b in self._adv_buttons:
            b.setEnabled(not busy)
