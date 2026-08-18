"""Skill detail page: the 2-3 fixed visualizations as tappable tiles."""
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QPushButton, QScrollArea, QVBoxLayout,
    QWidget,
)

from ..theme import ACCENT, ACCENT_DARK, OK, TEXT, TEXT_DIM


class VizTile(QFrame):
    deploy = Signal(object)    # Visualization
    orbit = Signal()
    stop_orbit = Signal()

    def __init__(self, viz, parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        self.setCursor(Qt.PointingHandCursor)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(16, 12, 16, 12)
        lay.setSpacing(8)
        top = QHBoxLayout()

        marker = QLabel("▶" if viz.tour else "▲")
        marker.setStyleSheet(
            f"font-size: 22px; color: {OK if viz.tour else ACCENT};")
        top.addWidget(marker)

        text_col = QVBoxLayout()
        title = QLabel(viz.label)
        title.setStyleSheet("font-weight: 700; font-size: 15px;")
        text_col.addWidget(title)
        desc = QLabel(viz.desc)
        desc.setWordWrap(True)
        desc.setStyleSheet(f"color: {TEXT_DIM}; font-size: 12px;")
        text_col.addWidget(desc)
        top.addLayout(text_col, 1)

        play = QPushButton("Fly to location")
        play.setObjectName("primary")
        play.clicked.connect(lambda: self.deploy.emit(viz))
        top.addWidget(play)
        lay.addLayout(top)

        self.orbit_hint = QLabel("This view becomes orbit-ready after it is live.")
        self.orbit_hint.setStyleSheet(f"color: {TEXT_DIM}; font-size: 12px;")
        self.orbit_hint.hide()
        lay.addWidget(self.orbit_hint)
        self.orbit_btn = QPushButton("Orbit this region")
        self.orbit_btn.setObjectName("ghost")
        self.orbit_btn.hide()
        self.orbit_btn.clicked.connect(self.orbit.emit)
        lay.addWidget(self.orbit_btn)

    def set_active(self, active, orbiting=False):
        self.orbit_hint.setVisible(active)
        self.orbit_btn.setVisible(active)
        self.orbit_btn.setText("Stop orbit" if orbiting else "Orbit this region")
        try:
            self.orbit_btn.clicked.disconnect()
        except RuntimeError:
            pass
        self.orbit_btn.clicked.connect(self.stop_orbit.emit if orbiting else self.orbit.emit)


class SkillDetailPage(QWidget):
    back = Signal()
    deploy_viz = Signal(object)   # Visualization

    def __init__(self, skill, parent=None):
        super().__init__(parent)
        self.skill = skill
        self._build()

    def _build(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(20, 16, 20, 16)
        outer.setSpacing(12)

        # header
        header = QHBoxLayout()
        back_btn = QPushButton("← Back")
        back_btn.clicked.connect(self.back.emit)
        header.addWidget(back_btn)
        title = QLabel(self.skill.name)
        title.setObjectName("title")
        header.addWidget(title, 1)
        outer.addLayout(header)

        tagline = QLabel(self.skill.tagline)
        tagline.setObjectName("tagline")
        outer.addWidget(tagline)

        # viz list
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        host = QWidget()
        col = QVBoxLayout(host)
        col.setContentsMargins(0, 8, 0, 0)
        col.setSpacing(10)
        self.tiles = []
        for viz in self.skill.visualizations:
            tile = VizTile(viz)
            tile.deploy.connect(self.deploy_viz.emit)
            self.tiles.append((viz, tile))
            col.addWidget(tile)
        col.addStretch(1)
        scroll.setWidget(host)
        outer.addWidget(scroll, 1)

    def set_active_visualization(self, viz, orbiting=False):
        for tile_viz, tile in self.tiles:
            tile.set_active(tile_viz is viz, orbiting and tile_viz is viz)
