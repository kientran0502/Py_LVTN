from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout,
    QTextEdit, QTabWidget,
    QGridLayout, QFrame, QLabel
)
from PyQt5.QtCore import QTimer

import pyqtgraph as pg

# GLOBAL
import global_var

# UART + Parser
from uart_ui import create_uart_group_box
from protocol_parser import parse_uart_line

# Sensors
from bmp390 import create_bmp390_show_box

# TEMP SYSTEM
from temp_ctrl import (
    create_temp_ctrl_tab,
    update_pid_display,
    pipe_to_response
)

from exp_manual import create_manual_group_box
from exp_auto import create_auto_group_box


# ─── COLOR PALETTE ─────────────────────────────────────────────
BG_DEEP     = "#07090F"
BG_PANEL    = "#0D1017"
BG_SURFACE  = "#111520"
BG_CARD     = "#161B28"
BORDER      = "#1E2840"

ACCENT_CYAN = "#00C8E8"

TEXT_PRIM   = "#E8ECF4"


STYLESHEET = f"""
QWidget {{
    background-color: {BG_DEEP};
    color: {TEXT_PRIM};
    font-family: "Segoe UI";
    font-size: 12px;
}}

QFrame {{
    background-color: transparent;
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


# ═══════════════════════════════════════════════════════════════
# MAIN WINDOW
# ═══════════════════════════════════════════════════════════════

class CubeSatMonitor(QWidget):

    def __init__(self):
        super().__init__()

        # IMPORTANT
        global_var.window = self

        self.setWindowTitle("CubeSat Ground Station")
        self.resize(1600, 900)
        self.setStyleSheet(STYLESHEET)

        root = QVBoxLayout(self)

        # ── HEADER ───────────────────────────────────────────
        top = QHBoxLayout()

        title = QLabel("MISSION CONTROL")
        title.setStyleSheet("""
            font-size: 16px;
            color: #00C8E8;
            font-weight: bold;
        """)

        top.addWidget(title)
        top.addStretch()

        root.addLayout(top)

        # ── MAIN GRID ───────────────────────────────────────
        grid = QGridLayout()
        root.addLayout(grid)

        left   = self._build_left()
        center = self._build_center()
        right  = self._build_right()

        grid.addWidget(left,   0, 0)
        grid.addWidget(center, 0, 1)
        grid.addWidget(right,  0, 2)

        grid.setColumnStretch(0, 2)
        grid.setColumnStretch(1, 5)
        grid.setColumnStretch(2, 2)

        # ── TIMER ───────────────────────────────────────────
        self.timer = QTimer()

        self.timer.timeout.connect(
            lambda: self._safe_pid_update()
        )

        self.timer.start(1000)
    
        # ═══════════════════════════════════════════════════════
    # SAFE LOG APPEND
    # ═══════════════════════════════════════════════════════

    def _append_log(self, text):

        try:

            if not hasattr(self, "log_box"):
                return

            self.log_box.append(text)

            # chỉ giữ 200 dòng gần nhất
            doc = self.log_box.document()

            MAX_LINES = 200

            while doc.blockCount() > MAX_LINES:

                cursor = self.log_box.textCursor()

                cursor.movePosition(cursor.Start)
                cursor.select(cursor.LineUnderCursor)
                cursor.removeSelectedText()
                cursor.deleteChar()

        except Exception as e:

            print("log append error:", e)

    # ═══════════════════════════════════════════════════════
    # SAFE PID UPDATE
    # ═══════════════════════════════════════════════════════

    def _safe_pid_update(self):

        try:
            update_pid_display(self)

        except Exception as e:
            print("PID update error:", e)

    # ═══════════════════════════════════════════════════════
    # LEFT
    # ═══════════════════════════════════════════════════════

    def _build_left(self):

        box = QFrame()
        lay = QVBoxLayout(box)

        self.bmp390_box = create_bmp390_show_box(self)
        lay.addWidget(self.bmp390_box)

        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)

        lay.addWidget(self.log_box)

        return box

    # ═══════════════════════════════════════════════════════
    # CENTER
    # ═══════════════════════════════════════════════════════

    def _build_center(self):

        box = QFrame()
        lay = QVBoxLayout(box)

        self.temp_ctrl_tab = create_temp_ctrl_tab(self)

        lay.addWidget(self.temp_ctrl_tab)

        return box

    # ═══════════════════════════════════════════════════════
    # RIGHT
    # ═══════════════════════════════════════════════════════

    def _build_right(self):

        box = QFrame()
        lay = QVBoxLayout(box)

        self.tabs = QTabWidget()

        self.manual_box = create_manual_group_box(self)
        self.auto_box   = create_auto_group_box(self)

        self.tabs.addTab(self.manual_box, "Manual")
        self.tabs.addTab(self.auto_box,   "Auto")

        lay.addWidget(self.tabs)

        self.uart_box = create_uart_group_box(self)

        lay.addWidget(self.uart_box)

        return box

    # ═══════════════════════════════════════════════════════
    # UART RX
    # ═══════════════════════════════════════════════════════

    def process_uart_data(self, line):

        try:

            line = str(line).strip()

            if not line:
                return

            # LOG
            if hasattr(self, "log_box"):
                self._append_log(line)

            # PARSER
            parse_uart_line(line)

            # TEMP CTRL RESPONSE
            pipe_to_response(self, line)

        except Exception as e:

            print("process_uart_data error:", e)

            try:
                self.log_box.append(
                    f"[ERR] process_uart_data: {e}"
                )
            except:
                pass