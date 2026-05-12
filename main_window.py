# from PyQt5.QtWidgets import (
#     QWidget, QHBoxLayout, QVBoxLayout,
#     QTextEdit, QGroupBox, QTabWidget,
#     QGridLayout, QFrame, QLabel
# )

# from PyQt5.QtCore import QTimer
# import pyqtgraph as pg

# from uart_ui import create_uart_group_box
# from protocol_parser import parse_uart_line

# from bmp390 import create_bmp390_show_box

# from temp_ctrl import (
#     create_temperature_show_box,
#     create_temperature_graph_box,
#     update_graph
# )

# from exp_manual import create_manual_group_box
# from exp_auto import create_auto_group_box


# class CubeSatMonitor(QWidget):

#     def __init__(self):
#         super().__init__()

#         self.setWindowTitle("EXP Mission Control")
#         self.resize(1600, 900)

#         # =========================
#         # THEME
#         # =========================
#         self.setStyleSheet("""
#         QWidget {
#             background-color: #0F111A;
#             color: #E6E6E6;
#             font-size: 12px;
#         }

#         QGroupBox {
#             background-color: #151C2B;
#             border: 1px solid #1F2A40;
#             border-radius: 8px;
#             padding: 8px;
#         }

#         QGroupBox::title {
#             color: #00D4FF;
#         }

#         QTextEdit {
#             background-color: #0E1420;
#             border: 1px solid #1F2A40;
#         }

#         QPushButton {
#             background-color: #1F2633;
#             border: 1px solid #2A2F3A;
#             padding: 5px;
#         }

#         QPushButton:hover {
#             background-color: #2C3648;
#         }

#         QLineEdit {
#             background-color: #0E1420;
#             border: 1px solid #2A2F3A;
#             padding: 4px;
#         }
#         """)

#         # =========================
#         # ROOT LAYOUT (VERTICAL)
#         # =========================
#         root = QVBoxLayout(self)

#         # =========================
#         # TOP STATUS BAR
#         # =========================
#         self.top_bar = QFrame()
#         self.top_bar.setFixedHeight(60)
#         self.top_bar.setStyleSheet("""
#             QFrame {
#                 background-color: #121A2A;
#                 border-radius: 10px;
#             }
#         """)

#         top_layout = QHBoxLayout(self.top_bar)
#         top_layout.addWidget(QLabel("CPU: 32%"))
#         top_layout.addWidget(QLabel("UART: 127 kbps"))
#         top_layout.addWidget(QLabel("SPI: 820 kbps"))
#         top_layout.addStretch()

#         root.addWidget(self.top_bar)

#         # =========================
#         # GRID DASHBOARD
#         # =========================
#         grid = QGridLayout()
#         root.addLayout(grid)

#         # =========================
#         # LEFT (SENSORS)
#         # =========================
#         self.temp_box = create_temperature_show_box(self)
#         self.bmp390_box = create_bmp390_show_box(self)

#         left_box = QVBoxLayout()
#         left_container = QFrame()
#         left_container.setLayout(left_box)

#         log_group = QGroupBox("Logs")
#         log_layout = QVBoxLayout()

#         self.log_box = QTextEdit()
#         self.log_box.setReadOnly(True)
#         self.log_box.setStyleSheet("font-family: Consolas; font-size: 11px;")

#         log_layout.addWidget(self.log_box)
#         log_group.setLayout(log_layout)

#         left_box.addWidget(self.temp_box)
#         left_box.addWidget(self.bmp390_box)
#         left_box.addWidget(log_group)

#         # =========================
#         # CENTER GRAPH
#         # =========================
#         self.graph_box = create_temperature_graph_box(self)

#         # graph style
#         self.graph.setBackground("#0B0F14")
#         self.graph.showGrid(x=True, y=True, alpha=0.2)
#         self.graph.addLegend()
#         self.graph.setLabel('left', 'Temperature (°C)', color='#00D4FF')
#         self.graph.setLabel('bottom', 'Time', color='#00D4FF')

#         # =========================
#         # RIGHT CONTROL (TAB)
#         # =========================
#         self.manual_box = create_manual_group_box(self)
#         self.auto_box = create_auto_group_box(self)

#         self.tabs = QTabWidget()
#         self.tabs.addTab(self.manual_box, "Manual")
#         self.tabs.addTab(self.auto_box, "Auto")

#         right_box = QVBoxLayout()
#         right_container = QFrame()
#         right_container.setLayout(right_box)

#         self.uart_box = create_uart_group_box(self)

#         right_box.addWidget(self.tabs)
#         right_box.addWidget(self.uart_box)

#         # =========================
#         # ADD TO GRID (NEW LAYOUT)
#         # =========================
#         grid.addWidget(left_container, 0, 0)
#         grid.addWidget(self.graph_box, 0, 1)
#         grid.addWidget(right_container, 0, 2)

#         # stretch style
#         grid.setColumnStretch(0, 2)
#         grid.setColumnStretch(1, 4)
#         grid.setColumnStretch(2, 2)

#         # =========================
#         # CURVES
#         # =========================
#         self.curves = []

#         for i in range(8):
#             color = pg.intColor(i, 8)
#             curve = self.graph.plot(
#                 pen=pg.mkPen(color=color, width=2),
#                 name=f"NTC{i+1}"
#             )
#             self.curves.append(curve)

#         # =========================
#         # TIMER
#         # =========================
#         self.timer = QTimer()
#         self.timer.timeout.connect(lambda: update_graph(self))
#         self.timer.start(1000)

#     def process_uart_data(self, line):
#         parse_uart_line(line)














# from PyQt5.QtWidgets import (
#     QWidget, QHBoxLayout, QVBoxLayout,
#     QTextEdit, QGroupBox, QTabWidget,
#     QGridLayout, QFrame, QLabel, QSizePolicy
# )
# from PyQt5.QtCore import QTimer, Qt
# from PyQt5.QtGui import QFont, QColor
# import pyqtgraph as pg
# import pyqtgraph.exporters

# from uart_ui import create_uart_group_box
# from protocol_parser import parse_uart_line

# from bmp390 import create_bmp390_show_box

# from temp_ctrl import (
#     create_temperature_show_box,
#     create_temperature_graph_box,
#     update_graph
# )

# from exp_manual import create_manual_group_box
# from exp_auto import create_auto_group_box


# # ─── Color Palette ───────────────────────────────────────────────────────────
# BG_DEEP     = "#07090F"   # root window
# BG_PANEL    = "#0D1017"   # panels / groupboxes
# BG_SURFACE  = "#111520"   # inner surfaces
# BG_CARD     = "#161B28"   # cards / graph bg
# BORDER      = "#1E2840"   # default borders
# BORDER_GLOW = "#00C8E8"   # cyan accent
# ACCENT_CYAN = "#00C8E8"
# ACCENT_TEAL = "#00E5B0"
# ACCENT_WARN = "#FFB347"
# ACCENT_ERR  = "#FF5C5C"
# TEXT_PRIM   = "#E8ECF4"
# TEXT_SEC    = "#7A8BA8"
# TEXT_DIM    = "#3E4D65"

# # NTC curve colours (8 channels)
# NTC_COLORS = [
#     "#00C8E8",  # cyan
#     "#00E5B0",  # teal
#     "#7B61FF",  # violet
#     "#FFB347",  # amber
#     "#FF6B9D",  # pink
#     "#4FC3F7",  # sky
#     "#A8FF78",  # lime
#     "#FF8A65",  # orange
# ]


# STYLESHEET = f"""
# /* ── Root ─────────────────────────────────────────── */
# QWidget {{
#     background-color: {BG_DEEP};
#     color: {TEXT_PRIM};
#     font-family: "Segoe UI", "Inter", sans-serif;
#     font-size: 12px;
# }}

# /* ── GroupBox ──────────────────────────────────────── */
# QGroupBox {{
#     background-color: {BG_PANEL};
#     border: 1px solid {BORDER};
#     border-radius: 10px;
#     margin-top: 22px;
#     padding: 10px 10px 8px 10px;
# }}
# QGroupBox::title {{
#     subcontrol-origin: margin;
#     subcontrol-position: top left;
#     left: 12px;
#     top: 4px;
#     color: {ACCENT_CYAN};
#     font-weight: 600;
#     font-size: 11px;
#     letter-spacing: 1.5px;
#     text-transform: uppercase;
# }}

# /* ── Log / TextEdit ────────────────────────────────── */
# QTextEdit {{
#     background-color: {BG_SURFACE};
#     border: 1px solid {BORDER};
#     border-radius: 6px;
#     color: #8FBCD4;
#     font-family: "Cascadia Code", "Consolas", monospace;
#     font-size: 11px;
#     padding: 4px;
# }}

# /* ── Buttons ───────────────────────────────────────── */
# QPushButton {{
#     background-color: {BG_SURFACE};
#     border: 1px solid {BORDER};
#     border-radius: 6px;
#     color: {TEXT_PRIM};
#     padding: 5px 10px;
#     font-size: 11px;
# }}
# QPushButton:hover {{
#     background-color: #1C2540;
#     border-color: {ACCENT_CYAN};
#     color: {ACCENT_CYAN};
# }}
# QPushButton:pressed {{
#     background-color: #0C1830;
# }}

# /* ── Line edit ─────────────────────────────────────── */
# QLineEdit {{
#     background-color: {BG_SURFACE};
#     border: 1px solid {BORDER};
#     border-radius: 6px;
#     color: {TEXT_PRIM};
#     padding: 4px 8px;
#     font-size: 11px;
#     selection-background-color: {ACCENT_CYAN};
# }}
# QLineEdit:focus {{
#     border-color: {ACCENT_CYAN};
# }}

# /* ── Label ─────────────────────────────────────────── */
# QLabel {{
#     background: transparent;
#     color: {TEXT_SEC};
#     font-size: 11px;
# }}

# /* ── TabWidget ─────────────────────────────────────── */
# QTabWidget::pane {{
#     background: {BG_PANEL};
#     border: 1px solid {BORDER};
#     border-radius: 8px;
# }}
# QTabBar::tab {{
#     background: {BG_SURFACE};
#     border: 1px solid {BORDER};
#     border-bottom: none;
#     border-radius: 6px 6px 0 0;
#     color: {TEXT_SEC};
#     padding: 5px 16px;
#     font-size: 11px;
#     min-width: 70px;
# }}
# QTabBar::tab:selected {{
#     background: {BG_CARD};
#     color: {ACCENT_CYAN};
#     border-bottom: 2px solid {ACCENT_CYAN};
# }}
# QTabBar::tab:hover:!selected {{
#     background: #131A2A;
#     color: {TEXT_PRIM};
# }}

# /* ── Scrollbar ─────────────────────────────────────── */
# QScrollBar:vertical {{
#     background: {BG_SURFACE};
#     width: 6px;
#     border-radius: 3px;
# }}
# QScrollBar::handle:vertical {{
#     background: {BORDER};
#     border-radius: 3px;
#     min-height: 20px;
# }}
# QScrollBar::handle:vertical:hover {{
#     background: {ACCENT_CYAN};
# }}
# QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
#     height: 0;
# }}
# """


# class StatusBadge(QLabel):
#     """Small coloured pill label used in the top status bar."""
#     def __init__(self, icon: str, value: str, color: str = ACCENT_CYAN):
#         super().__init__()
#         self._color = color
#         self.update_value(icon, value)
#         self.setFixedHeight(28)

#     def update_value(self, icon: str, value: str):
#         self.setText(f"  {icon}  {value}  ")
#         self.setStyleSheet(f"""
#             QLabel {{
#                 background-color: {BG_SURFACE};
#                 border: 1px solid {self._color}40;
#                 border-radius: 6px;
#                 color: {self._color};
#                 font-size: 11px;
#                 font-weight: 600;
#                 padding: 0 4px;
#             }}
#         """)


# class SectionDivider(QFrame):
#     """Thin 1-px horizontal rule between sections."""
#     def __init__(self):
#         super().__init__()
#         self.setFrameShape(QFrame.HLine)
#         self.setStyleSheet(f"background-color: {BORDER}; max-height: 1px; border: none;")


# class CubeSatMonitor(QWidget):

#     def __init__(self):
#         super().__init__()
#         self.setWindowTitle("EXP Mission Control  ·  CubeSat Ground Station")
#         self.resize(1640, 960)
#         self.setStyleSheet(STYLESHEET)

#         root = QVBoxLayout(self)
#         root.setSpacing(8)
#         root.setContentsMargins(10, 10, 10, 10)

#         # ── TOP BAR ──────────────────────────────────────────────────────────
#         root.addWidget(self._build_top_bar())

#         # ── MAIN GRID ────────────────────────────────────────────────────────
#         grid = QGridLayout()
#         grid.setSpacing(8)
#         root.addLayout(grid)

#         # Left column  – sensor readouts + log
#         left = self._build_left_column()
#         # Center column – temperature graph (wide)
#         center = self._build_center_column()
#         # Right column  – controls
#         right = self._build_right_column()

#         grid.addWidget(left,   0, 0)
#         grid.addWidget(center, 0, 1)
#         grid.addWidget(right,  0, 2)

#         # column proportions  2 : 5 : 2
#         grid.setColumnStretch(0, 2)
#         grid.setColumnStretch(1, 5)
#         grid.setColumnStretch(2, 2)

#         # ── CURVES ───────────────────────────────────────────────────────────
#         self.curves = []
#         for i in range(8):
#             pen = pg.mkPen(color=NTC_COLORS[i], width=2)
#             curve = self.graph.plot(pen=pen, name=f"NTC {i+1}")
#             self.curves.append(curve)

#         # ── TIMER ────────────────────────────────────────────────────────────
#         self.timer = QTimer()
#         self.timer.timeout.connect(lambda: update_graph(self))
#         self.timer.start(1000)

#     # ─────────────────────────────────────────────────────────────────────────
#     # Builder helpers
#     # ─────────────────────────────────────────────────────────────────────────

#     def _build_top_bar(self) -> QFrame:
#         bar = QFrame()
#         bar.setFixedHeight(48)
#         bar.setStyleSheet(f"""
#             QFrame {{
#                 background-color: {BG_PANEL};
#                 border: 1px solid {BORDER};
#                 border-radius: 8px;
#             }}
#         """)
#         lay = QHBoxLayout(bar)
#         lay.setContentsMargins(14, 0, 14, 0)
#         lay.setSpacing(10)

#         # Mission title
#         title = QLabel("EXP  MISSION  CONTROL")
#         title.setStyleSheet(f"""
#             font-family: "Segoe UI", monospace;
#             font-size: 14px;
#             font-weight: 700;
#             letter-spacing: 3px;
#             color: {ACCENT_CYAN};
#         """)
#         lay.addWidget(title)

#         lay.addSpacing(20)
#         lay.addWidget(SectionDivider() if False else self._vline())

#         self.badge_cpu  = StatusBadge("⬡", "CPU  32%",       ACCENT_CYAN)
#         self.badge_uart = StatusBadge("⇄", "UART  127 kbps", ACCENT_TEAL)
#         self.badge_spi  = StatusBadge("⇅", "SPI  820 kbps",  "#7B61FF")
#         self.badge_conn = StatusBadge("●", "CONNECTED",       ACCENT_TEAL)

#         for b in (self.badge_cpu, self.badge_uart, self.badge_spi, self.badge_conn):
#             lay.addWidget(b)

#         lay.addStretch()

#         ts = QLabel("T+00:00:00")
#         ts.setStyleSheet(f"""
#             font-family: "Cascadia Code", monospace;
#             font-size: 13px;
#             font-weight: 600;
#             color: {ACCENT_WARN};
#             letter-spacing: 1px;
#         """)
#         lay.addWidget(ts)
#         self.mission_clock = ts
#         return bar

#     def _vline(self) -> QFrame:
#         f = QFrame()
#         f.setFrameShape(QFrame.VLine)
#         f.setFixedWidth(1)
#         f.setStyleSheet(f"background: {BORDER}; border: none;")
#         return f

#     def _build_left_column(self) -> QFrame:
#         container = QFrame()
#         lay = QVBoxLayout(container)
#         lay.setSpacing(8)
#         lay.setContentsMargins(0, 0, 0, 0)

#         # Sensor readouts
#         self.temp_box   = create_temperature_show_box(self)
#         self.bmp390_box = create_bmp390_show_box(self)
#         lay.addWidget(self.temp_box)
#         lay.addWidget(self.bmp390_box)

#         # Log
#         log_group = QGroupBox("SERIAL LOG")
#         log_lay = QVBoxLayout()
#         log_lay.setContentsMargins(6, 6, 6, 6)
#         self.log_box = QTextEdit()
#         self.log_box.setReadOnly(True)
#         log_lay.addWidget(self.log_box)
#         log_group.setLayout(log_lay)
#         lay.addWidget(log_group, stretch=1)

#         return container

#     def _build_center_column(self) -> QFrame:
#         container = QFrame()
#         lay = QVBoxLayout(container)
#         lay.setSpacing(0)
#         lay.setContentsMargins(0, 0, 0, 0)

#         # Outer card
#         card = QGroupBox("TEMPERATURE GRAPH  —  NTC 1–8")
#         card_lay = QVBoxLayout()
#         card_lay.setContentsMargins(8, 8, 8, 8)

#         # ── pyqtgraph widget ─────────────────────────────────────
#         self.graph_box = create_temperature_graph_box(self)

#         pg.setConfigOptions(antialias=True)
#         self.graph.setBackground(BG_CARD)

#         # Grid lines (subtle)
#         self.graph.showGrid(x=True, y=True, alpha=0.12)

#         # Axis styling
#         axis_pen  = pg.mkPen(color=BORDER, width=1)
#         tick_font = QFont("Segoe UI", 9)

#         left_ax  = self.graph.getAxis("left")
#         bot_ax   = self.graph.getAxis("bottom")

#         for ax in (left_ax, bot_ax):
#             ax.setPen(axis_pen)
#             ax.setTickFont(tick_font)
#             ax.setTextPen(pg.mkPen(color=TEXT_SEC))

#         self.graph.setLabel("left",   "Temperature (°C)",
#                             color=TEXT_SEC, size="10pt")
#         self.graph.setLabel("bottom", "Time (s)",
#                             color=TEXT_SEC, size="10pt")

#         # Legend inside graph
#         legend = self.graph.addLegend(
#             offset=(10, 10),
#             labelTextColor=TEXT_SEC,
#             pen=pg.mkPen(color=BORDER),
#             brush=pg.mkBrush(BG_SURFACE + "CC"),
#         )

#         # Top legend for legend item text colour
#         # (pyqtgraph does not directly expose it, so we patch after add)
#         self.graph.setSizePolicy(
#             QSizePolicy.Expanding, QSizePolicy.Expanding
#         )

#         card_lay.addWidget(self.graph_box)
#         card.setLayout(card_lay)
#         lay.addWidget(card, stretch=1)

#         return container

#     def _build_right_column(self) -> QFrame:
#         container = QFrame()
#         lay = QVBoxLayout(container)
#         lay.setSpacing(8)
#         lay.setContentsMargins(0, 0, 0, 0)

#         # Tabs: Manual / Auto
#         self.manual_box = create_manual_group_box(self)
#         self.auto_box   = create_auto_group_box(self)

#         self.tabs = QTabWidget()
#         self.tabs.setDocumentMode(True)
#         self.tabs.addTab(self.manual_box, "Manual")
#         self.tabs.addTab(self.auto_box,   "Auto")
#         lay.addWidget(self.tabs)

#         # UART
#         self.uart_box = create_uart_group_box(self)
#         lay.addWidget(self.uart_box)

#         return container

#     # ─────────────────────────────────────────────────────────────────────────
#     # UART entry point (keep original interface)
#     # ─────────────────────────────────────────────────────────────────────────
#     def process_uart_data(self, line):
#         parse_uart_line(line)








from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout,
    QTextEdit, QGroupBox, QTabWidget,
    QGridLayout, QFrame, QLabel, QSizePolicy
)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QFont

import pyqtgraph as pg

# UART + Parser
from uart_ui import create_uart_group_box
from protocol_parser import parse_uart_line

# Sensors
from bmp390 import create_bmp390_show_box

# NEW TEMP SYSTEM (IMPORTANT)
from temp_ctrl import (
    create_temp_ctrl_tab,
    update_pid_display,
    pipe_to_response
)

from exp_manual import create_manual_group_box
from exp_auto import create_auto_group_box


# ─── COLOR PALETTE ───────────────────────────────────────────────────────────
BG_DEEP     = "#07090F"
BG_PANEL    = "#0D1017"
BG_SURFACE  = "#111520"
BG_CARD     = "#161B28"
BORDER      = "#1E2840"

ACCENT_CYAN = "#00C8E8"
ACCENT_TEAL = "#00E5B0"
ACCENT_WARN = "#FFB347"
ACCENT_ERR  = "#FF5C5C"

TEXT_PRIM   = "#E8ECF4"
TEXT_SEC    = "#7A8BA8"


STYLESHEET = f"""
QWidget {{
    background-color: {BG_DEEP};
    color: {TEXT_PRIM};
    font-family: "Segoe UI";
    font-size: 12px;
}}

QGroupBox {{
    background-color: {BG_PANEL};
    border: 1px solid {BORDER};
    border-radius: 8px;
    margin-top: 18px;
}}

QGroupBox::title {{
    color: {ACCENT_CYAN};
    subcontrol-origin: margin;
    left: 10px;
    top: 2px;
}}

QTextEdit {{
    background-color: {BG_SURFACE};
    border: 1px solid {BORDER};
    border-radius: 6px;
    color: #8FBCD4;
    font-family: Consolas;
}}

QTabWidget::pane {{
    border: 1px solid {BORDER};
    background: {BG_PANEL};
}}

QTabBar::tab {{
    background: {BG_SURFACE};
    padding: 6px;
    border: 1px solid {BORDER};
}}

QTabBar::tab:selected {{
    background: {BG_CARD};
    color: {ACCENT_CYAN};
}}
"""


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN WINDOW
# ═══════════════════════════════════════════════════════════════════════════════

class CubeSatMonitor(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("CubeSat Ground Station")
        self.resize(1600, 900)
        self.setStyleSheet(STYLESHEET)

        root = QVBoxLayout(self)

        # ── TOP LAYOUT (optional placeholder) ────────────────────────────────
        top = QHBoxLayout()
        title = QLabel("MISSION CONTROL")
        title.setStyleSheet("font-size: 16px; color: #00C8E8; font-weight: bold;")
        top.addWidget(title)
        top.addStretch()
        root.addLayout(top)

        # ── MAIN GRID ────────────────────────────────────────────────────────
        grid = QGridLayout()
        root.addLayout(grid)

        # LEFT
        left = self._build_left()
        # CENTER
        center = self._build_center()
        # RIGHT
        right = self._build_right()

        grid.addWidget(left,   0, 0)
        grid.addWidget(center, 0, 1)
        grid.addWidget(right,  0, 2)

        grid.setColumnStretch(0, 2)
        grid.setColumnStretch(1, 5)
        grid.setColumnStretch(2, 2)

        # ── TIMER (PID update ONLY) ─────────────────────────────────────────
        self.timer = QTimer()
        self.timer.timeout.connect(lambda: update_pid_display(self))
        self.timer.start(1000)

    # ═══════════════════════════════════════════════════════════════════════
    # LEFT COLUMN
    # ═══════════════════════════════════════════════════════════════════════
    def _build_left(self):
        box = QFrame()
        lay = QVBoxLayout(box)

        self.bmp390_box = create_bmp390_show_box(self)
        lay.addWidget(self.bmp390_box)

        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        lay.addWidget(self.log_box)

        return box

    # ═══════════════════════════════════════════════════════════════════════
    # CENTER COLUMN
    # ═══════════════════════════════════════════════════════════════════════
    def _build_center(self):
        box = QFrame()
        lay = QVBoxLayout(box)

        # TEMP CTRL TAB (NEW SYSTEM)
        self.temp_ctrl_tab = create_temp_ctrl_tab(self)
        lay.addWidget(self.temp_ctrl_tab)

        return box

    # ═══════════════════════════════════════════════════════════════════════
    # RIGHT COLUMN
    # ═══════════════════════════════════════════════════════════════════════
    def _build_right(self):
        box = QFrame()
        lay = QVBoxLayout(box)

        self.tabs = QTabWidget()

        self.manual_box = create_manual_group_box(self)
        self.auto_box   = create_auto_group_box(self)

        self.tabs.addTab(self.manual_box, "Manual")
        self.tabs.addTab(self.auto_box, "Auto")

        lay.addWidget(self.tabs)

        self.uart_box = create_uart_group_box(self)
        lay.addWidget(self.uart_box)

        return box

    # ═══════════════════════════════════════════════════════════════════════
    # UART ENTRY
    # ═══════════════════════════════════════════════════════════════════════
    def process_uart_data(self, line):
        parse_uart_line(line)
        pipe_to_response(self, line)