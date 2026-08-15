"""Home page: skill grid + connection banner + clear-earth action."""
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame, QGridLayout, QHBoxLayout, QLabel, QPushButton, QScrollArea,
    QVBoxLayout, QWidget,
)

from ..theme import ACCENT, ACCENT_DARK, BG, DANGER, OK, TEXT, TEXT_DIM, WARN


# Material icon name -> a simple unicode/emoji stand-in for the desktop app
_ICONS = {
    "wb_sunny": "☀", "flight": "✈", "directions_boat": "⚓", "bolt": "⚡",
    "security": "🛡", "gps_fixed": "◎", "show_chart": "📈", "pets": "🦌",
    "waves": "🌊", "forest": "🌲", "assessment": "📊", "donut_large": "◔",
    "satellite": "🛰", "trending_up": "📈", "newspaper": "📰",
    "public": "🌍", "history_edu": "🏛",
}


class SkillCard(QFrame):
    clicked = Signal(object)   # emits the Skill object

    def __init__(self, skill, parent=None):
        super().__init__(parent)
        self.skill = skill
        self.setObjectName("card")
        self.setCursor(Qt.PointingHandCursor)
        self.setAttribute(Qt.WA_Hover, True)
        self.setFixedSize(190, 150)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(16, 14, 16, 14)
        lay.setSpacing(6)

        icon = QLabel(_ICONS.get(skill.icon, "•"))
        icon.setStyleSheet(f"font-size: 30px; color: {ACCENT};")
        lay.addWidget(icon)

        lay.addStretch(1)

        name = QLabel(skill.name)
        name.setWordWrap(True)
        name.setStyleSheet("font-weight: 700; font-size: 15px;")
        lay.addWidget(name)

        tag = QLabel(skill.tagline)
        tag.setWordWrap(True)
        tag.setMaximumHeight(30)
        tag.setStyleSheet(f"color: {TEXT_DIM}; font-size: 11px;")
        lay.addWidget(tag)

        count = QLabel(f"{len(skill.visualizations)} visualizations")
        count.setStyleSheet(f"color: {ACCENT_DARK}; font-size: 10px;")
        lay.addWidget(count)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.skill)
        super().mousePressEvent(event)


class HomePage(QWidget):
    skill_selected = Signal(object)        # Skill
    open_settings = Signal()
    clear_earth = Signal()
    show_logo = Signal()

    def __init__(self, state, parent=None):
        super().__init__(parent)
        self.state = state
        self._cards = []
        self._build()
        state.skills_changed.connect(self._rebuild_grid)
        state.connected_changed.connect(self._update_banner)
        state.busy_changed.connect(self._update_banner)
        # render cards immediately if skills were already loaded (they are,
        # because AppState.load_skills() runs before MainWindow is created)
        if state.skills_loaded:
            self._rebuild_grid()

    def _build(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # banner
        self.banner = QFrame()
        self.banner.setObjectName("banner")
        self.banner_layout = QHBoxLayout(self.banner)
        self.banner_layout.setContentsMargins(16, 10, 16, 10)
        self.banner.setVisible(False)
        outer.addWidget(self.banner)

        # scrollable grid
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.grid_host = QWidget()
        self.grid_host.setObjectName("gridHost")
        self.grid_host.setStyleSheet(
            f"QWidget#gridHost {{ background-color: {BG}; }}")
        self.grid = QGridLayout(self.grid_host)
        self.grid.setContentsMargins(24, 20, 24, 20)
        self.grid.setSpacing(14)
        self.grid.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.scroll.setWidget(self.grid_host)
        outer.addWidget(self.scroll, 1)

        # bottom action bar
        bar = QHBoxLayout()
        bar.setContentsMargins(16, 10, 16, 14)
        logo_btn = QPushButton("Show logo")
        logo_btn.setObjectName("ghost")
        logo_btn.clicked.connect(self.show_logo.emit)
        clear_btn = QPushButton("Clear Earth")
        clear_btn.setObjectName("danger")
        clear_btn.clicked.connect(self.clear_earth.emit)
        bar.addWidget(logo_btn)
        bar.addStretch(1)
        bar.addWidget(clear_btn)
        outer.addLayout(bar)

        self._update_banner()

    def _update_banner(self, *_):
        if not self.state.has_settings:
            self._set_banner(
                "Not connected yet — configure the rig to start.",
                "Configure", WARN, self.open_settings.emit, object_name="banner")
        elif self.state.connected:
            self._set_banner(
                "Connected to the rig.", None, OK, None, object_name="okbanner")
        else:
            self._set_banner(
                "Not connected — actions will auto-connect using saved settings.",
                None, WARN, None, object_name="banner")

    def _set_banner(self, text, button_text, color, on_click, object_name="banner"):
        while self.banner_layout.count():
            item = self.banner_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()
        self.banner.setObjectName(object_name)
        self.banner.setStyleSheet("")
        self.banner.setVisible(True)

        lbl = QLabel(text)
        lbl.setStyleSheet(f"color: {color}; font-weight: 600;")
        self.banner_layout.addWidget(lbl)
        self.banner_layout.addStretch(1)
        if button_text and on_click:
            btn = QPushButton(button_text)
            btn.setObjectName("primary")
            btn.clicked.connect(on_click)
            self.banner_layout.addWidget(btn)

    def _rebuild_grid(self):
        while self.grid.count():
            item = self.grid.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()
        self._cards.clear()

        cols = 5
        for i, skill in enumerate(self.state.skills):
            card = SkillCard(skill)
            card.clicked.connect(self.skill_selected.emit)
            self.grid.addWidget(card, i // cols, i % cols)
            self._cards.append(card)
