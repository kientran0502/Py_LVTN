# from PyQt5.QtWidgets import (
#     QGroupBox, QVBoxLayout,
#     QGridLayout, QPushButton, QLabel, QLineEdit
# )


# def create_manual_group_box(parent):

#     group = QGroupBox("Manual Laser Control")
#     layout = QVBoxLayout()

#     parent.manual_percent = QLineEdit()
#     parent.manual_percent.setPlaceholderText("Laser % (0-100)")

#     layout.addWidget(QLabel("Power"))
#     layout.addWidget(parent.manual_percent)

#     grid = QGridLayout()

#     for i in range(6):
#         for j in range(6):

#             idx = i * 6 + j + 1

#             btn = QPushButton(str(idx))
#             btn.setFixedSize(38, 38)

#             btn.clicked.connect(
#                 lambda _, x=idx: laser_click(parent, x)
#             )

#             grid.addWidget(btn, i, j)

#     layout.addLayout(grid)
#     group.setLayout(layout)

#     return group


# def laser_click(parent, pos):

#     percent = parent.manual_percent.text() or "0"
#     cmd = f"LASER:{pos}:{percent}"

#     if hasattr(parent, "uart"):
#         parent.uart.send_command(cmd)



from PyQt5.QtWidgets import (
    QGroupBox, QVBoxLayout, QHBoxLayout,
    QGridLayout, QPushButton, QLabel, QLineEdit,
    QFrame, QSizePolicy
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


# ─── Palette (mirror main_window) ────────────────────────────────────────────
BG_SURFACE  = "#111520"
BORDER      = "#1E2840"
ACCENT_CYAN = "#00C8E8"
ACCENT_TEAL = "#00E5B0"
ACCENT_WARN = "#FFB347"
ACCENT_ERR  = "#FF5C5C"
TEXT_PRIM   = "#E8ECF4"
TEXT_SEC    = "#7A8BA8"


def create_manual_group_box(parent):
    group = QGroupBox("LASER CONTROL  —  MANUAL")
    outer = QVBoxLayout()
    outer.setSpacing(10)
    outer.setContentsMargins(10, 10, 10, 10)

    # ── Power input row ───────────────────────────────────────────────────────
    power_row = QHBoxLayout()
    power_lbl = QLabel("Power %")
    power_lbl.setStyleSheet(f"color: {TEXT_SEC}; font-size: 11px;")
    power_lbl.setFixedWidth(58)

    parent.manual_percent = QLineEdit()
    parent.manual_percent.setPlaceholderText("0 – 100")
    parent.manual_percent.setFixedHeight(28)
    parent.manual_percent.setStyleSheet(f"""
        QLineEdit {{
            background: {BG_SURFACE};
            border: 1px solid {BORDER};
            border-radius: 6px;
            color: {ACCENT_CYAN};
            font-size: 12px;
            font-weight: 600;
            padding: 2px 8px;
        }}
        QLineEdit:focus {{ border-color: {ACCENT_CYAN}; }}
    """)

    pct_unit = QLabel("%")
    pct_unit.setStyleSheet(f"color: {TEXT_SEC}; font-size: 11px;")

    power_row.addWidget(power_lbl)
    power_row.addWidget(parent.manual_percent)
    power_row.addWidget(pct_unit)
    outer.addLayout(power_row)

    # ── Divider ───────────────────────────────────────────────────────────────
    div = QFrame()
    div.setFrameShape(QFrame.HLine)
    div.setStyleSheet(f"background: {BORDER}; max-height: 1px; border: none;")
    outer.addWidget(div)

    # ── Grid label ────────────────────────────────────────────────────────────
    grid_lbl = QLabel("Select laser position  (1 – 24)")
    grid_lbl.setStyleSheet(f"color: {TEXT_SEC}; font-size: 10px; letter-spacing: 0.5px;")
    outer.addWidget(grid_lbl)

    # ── 4 × 6 grid  (24 lasers) ───────────────────────────────────────────────
    grid = QGridLayout()
    grid.setSpacing(5)

    parent._laser_buttons = {}

    for pos in range(1, 25):          # 1 … 24
        row = (pos - 1) // 6
        col = (pos - 1) % 6

        btn = _LaserButton(pos)
        btn.clicked.connect(lambda _, x=pos: laser_click(parent, x))

        grid.addWidget(btn, row, col)
        parent._laser_buttons[pos] = btn

    outer.addLayout(grid)

    # ── Quick-fire row ────────────────────────────────────────────────────────
    qf_row = QHBoxLayout()
    qf_row.setSpacing(6)

    fire_all_btn = _ActionButton("ALL ON", ACCENT_WARN)
    fire_all_btn.clicked.connect(lambda: fire_all(parent))

    off_all_btn  = _ActionButton("ALL OFF", ACCENT_ERR)
    off_all_btn.clicked.connect(lambda: off_all(parent))

    qf_row.addWidget(fire_all_btn)
    qf_row.addWidget(off_all_btn)
    outer.addLayout(qf_row)

    group.setLayout(outer)
    return group


# ─── Custom button classes ────────────────────────────────────────────────────

class _LaserButton(QPushButton):
    """Compact numbered laser button with active / inactive states."""

    _STYLE_IDLE = f"""
        QPushButton {{
            background-color: {BG_SURFACE};
            border: 1px solid {BORDER};
            border-radius: 6px;
            color: {TEXT_SEC};
            font-size: 11px;
            font-weight: 600;
        }}
        QPushButton:hover {{
            background-color: #162035;
            border-color: {ACCENT_CYAN};
            color: {ACCENT_CYAN};
        }}
        QPushButton:pressed {{
            background-color: #0C1830;
        }}
    """

    _STYLE_ACTIVE = f"""
        QPushButton {{
            background-color: #0F2A30;
            border: 1.5px solid {ACCENT_CYAN};
            border-radius: 6px;
            color: {ACCENT_CYAN};
            font-size: 11px;
            font-weight: 700;
        }}
        QPushButton:hover {{
            background-color: #133040;
        }}
    """

    def __init__(self, index: int):
        super().__init__(str(index))
        self.setFixedSize(40, 40)
        self._active = False
        self.setStyleSheet(self._STYLE_IDLE)

    def set_active(self, active: bool):
        self._active = active
        self.setStyleSheet(self._STYLE_ACTIVE if active else self._STYLE_IDLE)

    def toggle_active(self):
        self.set_active(not self._active)


class _ActionButton(QPushButton):
    """Wider action button (All On / All Off) with accent colour."""

    def __init__(self, label: str, accent: str):
        super().__init__(label)
        self.setFixedHeight(30)
        self.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Fixed
        )
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {accent}18;
                border: 1px solid {accent}60;
                border-radius: 6px;
                color: {accent};
                font-size: 11px;
                font-weight: 600;
                letter-spacing: 0.5px;
            }}
            QPushButton:hover {{
                background-color: {accent}30;
                border-color: {accent};
            }}
            QPushButton:pressed {{
                background-color: {accent}15;
            }}
        """)


# ─── Handlers ────────────────────────────────────────────────────────────────

def laser_click(parent, pos: int):
    """Toggle a single laser and send the UART command."""
    btn = parent._laser_buttons.get(pos)
    if btn:
        btn.toggle_active()

    percent = parent.manual_percent.text().strip() or "0"
    is_on   = btn._active if btn else True
    state   = "1" if is_on else "0"
    cmd     = f"LASER:{pos}:{percent}:{state}"

    if hasattr(parent, "uart"):
        parent.uart.send_command(cmd)


def fire_all(parent):
    """Turn all 24 lasers ON."""
    percent = parent.manual_percent.text().strip() or "0"
    for pos in range(1, 25):
        btn = parent._laser_buttons.get(pos)
        if btn:
            btn.set_active(True)
    if hasattr(parent, "uart"):
        parent.uart.send_command(f"LASER:ALL:{percent}:1")


def off_all(parent):
    """Turn all 24 lasers OFF."""
    for pos in range(1, 25):
        btn = parent._laser_buttons.get(pos)
        if btn:
            btn.set_active(False)
    if hasattr(parent, "uart"):
        parent.uart.send_command("LASER:ALL:0:0")