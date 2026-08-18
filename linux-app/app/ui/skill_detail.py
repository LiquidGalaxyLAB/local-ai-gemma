"""Skill detail page: the 2-3 fixed visualizations as tappable tiles."""
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QPushButton, QScrollArea, QVBoxLayout,
    QWidget,
)

from ..theme import ACCENT, ACCENT_DARK, OK, TEXT, TEXT_DIM


class VizTile(QFrame):
    deploy = Signal(object)    # Visualization

    def __init__(self, viz, parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        self.setCursor(Qt.PointingHandCursor)

        lay = QHBoxLayout(self)
        lay.setContentsMargins(16, 12, 16, 12)
        lay.setSpacing(12)

        marker = QLabel("▶" if viz.tour else "▲")
        marker.setStyleSheet(
            f"font-size: 22px; color: {OK if viz.tour else ACCENT};")
        lay.addWidget(marker)

        text_col = QVBoxLayout()
        title = QLabel(viz.label)
        title.setStyleSheet("font-weight: 700; font-size: 15px;")
        text_col.addWidget(title)
        desc = QLabel(viz.desc)
        desc.setWordWrap(True)
        desc.setStyleSheet(f"color: {TEXT_DIM}; font-size: 12px;")
        text_col.addWidget(desc)
        lay.addLayout(text_col, 1)

        play = QPushButton("Fly to location")
        play.setObjectName("primary")
        play.clicked.connect(lambda: self.deploy.emit(viz))
        lay.addWidget(play)

    def mouseDoubleClickEvent(self, event):
        # no-op: use the Fly to location button (explicit)
        super().mouseDoubleClickEvent(event)


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
        for viz in self.skill.visualizations:
            tile = VizTile(viz)
            tile.deploy.connect(self.deploy_viz.emit)
            col.addWidget(tile)
        col.addStretch(1)
        scroll.setWidget(host)
        outer.addWidget(scroll, 1)
