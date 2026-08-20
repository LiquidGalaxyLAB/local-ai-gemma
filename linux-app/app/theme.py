"""Liquid Galaxy demo-suite — glassmorphic dark theme (QSS).

Frosted-glass look: translucent surfaces, hairline light borders, rounded
corners, cyan accent glow. Base palette is a deep blue gradient feel.
"""

ACCENT = "#00E5FF"
ACCENT_DARK = "#0A84FF"
BG = "#0A0E1A"            # deep navy base
BG2 = "#0E1424"
SURFACE = "#141A2B"       # glass panel body
SURFACE_ALT = "#1B2338"
TEXT = "#E8EAF0"
TEXT_DIM = "#9AA3B2"
OK = "#34C759"
WARN = "#FFC400"
DANGER = "#FF3B30"

# translucent glass helpers
GLASS_BG = "rgba(20, 26, 43, 0.72)"
GLASS_BORDER = "rgba(255, 255, 255, 0.10)"
GLASS_BORDER_HOVER = "rgba(0, 229, 255, 0.55)"


def build_stylesheet() -> str:
    return f"""
* {{
    font-family: "Inter", "Segoe UI", "Ubuntu", "DejaVu Sans", sans-serif;
    font-size: 14px;
    color: {TEXT};
}}
QMainWindow, QDialog {{
    background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 {BG2}, stop:0.5 {BG}, stop:1 #060A14);
}}
QWidget {{
    background-color: transparent;
}}
QLabel {{
    color: {TEXT};
    background: transparent;
}}
QLabel#title {{
    font-size: 20px;
    font-weight: 700;
}}
QLabel#subtitle, QLabel#dim {{
    color: {TEXT_DIM};
}}
QLabel#tagline {{
    color: {TEXT_DIM};
    font-size: 13px;
}}
QLabel#headerTitle {{
    font-size: 16px;
    font-weight: 700;
    letter-spacing: 2px;
    color: {TEXT};
}}
QPushButton {{
    background-color: {GLASS_BG};
    border: 1px solid {GLASS_BORDER};
    border-radius: 10px;
    padding: 8px 16px;
    color: {TEXT};
    font-weight: 600;
}}
QPushButton:hover {{
    border-color: {GLASS_BORDER_HOVER};
    background-color: rgba(0, 229, 255, 0.10);
}}
QPushButton:pressed {{
    background-color: rgba(0, 229, 255, 0.16);
}}
QPushButton:disabled {{
    color: {TEXT_DIM};
    background-color: rgba(20, 26, 43, 0.4);
    border-color: rgba(255, 255, 255, 0.05);
}}
QPushButton#primary {{
    background-color: {ACCENT};
    color: #04121A;
    border: none;
    font-weight: 700;
}}
QPushButton#primary:hover {{
    background-color: #33EAFF;
}}
QPushButton#danger {{
    background-color: {DANGER};
    color: #ffffff;
    border: none;
}}
QPushButton#danger:hover {{
    background-color: #FF5144;
}}
QPushButton#ghost {{
    background-color: rgba(255, 255, 255, 0.04);
    border: 1px solid {GLASS_BORDER};
}}
QPushButton#ghost:hover {{
    border-color: {GLASS_BORDER_HOVER};
}}
QLineEdit, QSpinBox, QComboBox {{
    background-color: {GLASS_BG};
    border: 1px solid {GLASS_BORDER};
    border-radius: 10px;
    padding: 9px;
    color: {TEXT};
    selection-background-color: {ACCENT_DARK};
}}
QLineEdit:focus, QSpinBox:focus, QComboBox:focus {{
    border-color: {GLASS_BORDER_HOVER};
}}
QComboBox QAbstractItemView {{
    background-color: {SURFACE};
    border: 1px solid {GLASS_BORDER};
    border-radius: 10px;
    selection-background-color: {ACCENT_DARK};
}}
QScrollArea {{
    border: none;
    background: transparent;
}}
QScrollArea > QWidget {{
    background: transparent;
}}
QScrollArea > QWidget > QWidget {{
    background: transparent;
}}
QScrollBar:vertical {{
    background: transparent;
    width: 10px;
}}
QScrollBar::handle:vertical {{
    background: rgba(255, 255, 255, 0.16);
    border-radius: 5px;
    min-height: 30px;
}}
QScrollBar::handle:vertical:hover {{
    background: rgba(0, 229, 255, 0.4);
}}
QScrollBar::add-line, QScrollBar::sub-line {{
    height: 0;
}}
QFrame#card {{
    background-color: {GLASS_BG};
    border: 1px solid {GLASS_BORDER};
    border-radius: 16px;
}}
QFrame#card:hover {{
    border-color: {GLASS_BORDER_HOVER};
    background-color: rgba(0, 229, 255, 0.08);
}}
QFrame#header {{
    background-color: rgba(10, 14, 26, 0.55);
    border-bottom: 1px solid {GLASS_BORDER};
}}
QFrame#banner {{
    background-color: rgba(255, 196, 0, 0.10);
    border: 1px solid rgba(255, 196, 0, 0.40);
    border-radius: 12px;
}}
QFrame#okbanner {{
    background-color: rgba(52, 199, 89, 0.10);
    border: 1px solid rgba(52, 199, 89, 0.40);
    border-radius: 12px;
}}
QFrame#errbanner {{
    background-color: rgba(255, 59, 48, 0.10);
    border: 1px solid rgba(255, 59, 48, 0.40);
    border-radius: 12px;
}}
QLabel#dot {{
    border-radius: 6px;
}}
QStatusBar {{
    background-color: rgba(10, 14, 26, 0.55);
    border-top: 1px solid {GLASS_BORDER};
    color: {TEXT_DIM};
}}
QToolTip {{
    background-color: {SURFACE};
    color: {TEXT};
    border: 1px solid {GLASS_BORDER};
    border-radius: 6px;
    padding: 4px;
}}
"""
