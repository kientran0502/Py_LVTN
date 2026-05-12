# from PyQt5.QtWidgets import (
#     QGroupBox,
#     QVBoxLayout,
#     QLabel
# )

# import pyqtgraph as pg
# import global_var
# import numpy as np

# from bmp390 import update_bmp390_ui


# def create_temperature_show_box(parent):

#     group = QGroupBox("Temperature Monitor")

#     layout = QVBoxLayout()

#     parent.temp_labels = []

#     for i in range(8):

#         lbl = QLabel(f"NTC{i+1}: 0.0 C")

#         layout.addWidget(lbl)

#         parent.temp_labels.append(lbl)

#     group.setLayout(layout)

#     return group


# def create_temperature_graph_box(parent):

#     group = QGroupBox("Temperature Graph")

#     layout = QVBoxLayout()

#     parent.graph = pg.PlotWidget()

#     parent.graph.showGrid(x=True, y=True)

#     layout.addWidget(parent.graph)

#     group.setLayout(layout)

#     return group


# def update_graph(parent):

#     update_bmp390_ui(
#         parent,
#         global_var.bmp390_temp / 10.0,
#         global_var.bmp390_press / 10.0
#     )

#     if not hasattr(parent, "x_data"):

#         parent.x_data = []
#         parent.index = 0

#         parent.history = {
#             f"NTC{i}": [] for i in range(8)
#         }

#     parent.index += 1

#     parent.x_data.append(parent.index)

#     for i in range(8):

#         key = f"NTC{i}"

#         val = global_var.ntc_temp[key] / 10.0

#         parent.history[key].append(val)

#         parent.history[key] = parent.history[key][-100:]

#         y = np.array(parent.history[key])

#         x = np.array(parent.x_data[-len(y):])

#         parent.curves[i].setData(x, y)

#         parent.temp_labels[i].setText(
#             f"NTC{i+1}: {val:.1f} C"
#         )




# temp_ctrl_ui.py
# ─────────────────────────────────────────────────────────────────────────────
# Tab điều khiển nhiệt độ — bao gồm panel PID realtime + mini graph
# ─────────────────────────────────────────────────────────────────────────────

from PyQt5.QtWidgets import (
    QWidget, QGroupBox, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QLineEdit, QFrame,
    QTextEdit, QDoubleSpinBox, QSpinBox, QSizePolicy, QScrollArea
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QColor
import pyqtgraph as pg

# ─── Palette ──────────────────────────────────────────────────────────────────
BG_SURFACE  = "#111520"
BG_CARD     = "#161B28"
BORDER      = "#1E2840"
ACCENT_CYAN = "#00C8E8"
ACCENT_TEAL = "#00E5B0"
ACCENT_WARN = "#FFB347"
ACCENT_ERR  = "#FF5C5C"
ACCENT_PRP  = "#7B61FF"
ACCENT_LIME = "#A8FF78"
TEXT_PRIM   = "#E8ECF4"
TEXT_SEC    = "#7A8BA8"
TEXT_DIM    = "#3E4D65"

# Màu STEP badge
STEP_COLORS = {
    "NONE": ("#3E4D65", "#7A8BA8"),    # (bg, fg)
    "HEAT": ("#2A1500", "#FFB347"),
    "COOL": ("#001525", "#00C8E8"),
    "SOAK": ("#001A0F", "#00E5B0"),
}


# ═══════════════════════════════════════════════════════════════════════════════
# PUBLIC BUILDER
# ═══════════════════════════════════════════════════════════════════════════════

def create_temp_ctrl_tab(parent) -> QWidget:
    """
    Trả về QWidget dùng làm tab trong QTabWidget của main_window.

    Thêm vào main_window.py:
        from temp_ctrl_ui import create_temp_ctrl_tab
        self.temp_ctrl_widget = create_temp_ctrl_tab(self)
        self.tabs.addTab(self.temp_ctrl_widget, "Temp Ctrl")
    """
    root = QScrollArea()
    root.setWidgetResizable(True)
    root.setStyleSheet("QScrollArea { border: none; background: transparent; }")

    inner = QWidget()
    lay   = QVBoxLayout(inner)
    lay.setSpacing(8)
    lay.setContentsMargins(4, 4, 4, 4)

    # ── A. PID Realtime monitor (đặt trên cùng, quan trọng nhất) ─────────────
    lay.addWidget(_build_pid_monitor(parent))

    # ── B. Mini graph PV vs SP ────────────────────────────────────────────────
    lay.addWidget(_build_pid_graph(parent))

    # ── C. Profile section ────────────────────────────────────────────────────
    lay.addWidget(_build_profile_section(parent))

    # ── D. PID config ─────────────────────────────────────────────────────────
    lay.addWidget(_build_pid_section(parent))

    # ── E. Run control ────────────────────────────────────────────────────────
    lay.addWidget(_build_run_section(parent))

    # ── F. Response log ───────────────────────────────────────────────────────
    lay.addWidget(_build_response_box(parent), stretch=1)

    root.setWidget(inner)
    return root


# ═══════════════════════════════════════════════════════════════════════════════
# PID REALTIME MONITOR
# ═══════════════════════════════════════════════════════════════════════════════

def _build_pid_monitor(parent) -> QGroupBox:
    """4 card: STEP / SP / PV / ERR  — cập nhật realtime từ update_pid_display()."""

    grp = QGroupBox("PID  MONITOR  —  REALTIME")
    lay = QVBoxLayout()
    lay.setContentsMargins(8, 8, 8, 8)
    lay.setSpacing(8)

    # ── Top row: STEP badge (full width) ──────────────────────────────────────
    parent.pid_step_badge = _StepBadge()
    lay.addWidget(parent.pid_step_badge)

    # ── Bottom row: SP / PV / ERR / OUT cards ─────────────────────────────────
    cards_row = QHBoxLayout()
    cards_row.setSpacing(6)

    parent.pid_card_sp  = _MetricCard("SP",  "°C", ACCENT_CYAN)
    parent.pid_card_pv  = _MetricCard("PV",  "°C", ACCENT_TEAL)
    parent.pid_card_err = _MetricCard("ERR", "°C", ACCENT_WARN)
    parent.pid_card_out = _MetricCard("OUT", "%",  ACCENT_PRP)

    for card in (parent.pid_card_sp, parent.pid_card_pv,
                 parent.pid_card_err, parent.pid_card_out):
        cards_row.addWidget(card)

    lay.addLayout(cards_row)
    grp.setLayout(lay)
    return grp


def _build_pid_graph(parent) -> QGroupBox:
    """Mini pyqtgraph: PV (teal) và SP (cyan dashed)."""

    grp = QGroupBox("PV  vs  SP  HISTORY")
    lay = QVBoxLayout()
    lay.setContentsMargins(6, 6, 6, 6)

    pg.setConfigOptions(antialias=True)
    parent.pid_graph = pg.PlotWidget()
    parent.pid_graph.setBackground(BG_CARD)
    parent.pid_graph.setFixedHeight(160)
    parent.pid_graph.showGrid(x=True, y=True, alpha=0.12)
    parent.pid_graph.setLabel("left",   "°C",    color=TEXT_SEC, size="9pt")
    parent.pid_graph.setLabel("bottom", "sample", color=TEXT_SEC, size="9pt")

    axis_pen = pg.mkPen(color=BORDER, width=1)
    for ax_name in ("left", "bottom"):
        ax = parent.pid_graph.getAxis(ax_name)
        ax.setPen(axis_pen)
        ax.setTextPen(pg.mkPen(color=TEXT_SEC))

    legend = parent.pid_graph.addLegend(
        offset=(8, 8),
        labelTextColor=TEXT_SEC,
        pen=pg.mkPen(color=BORDER),
        brush=pg.mkBrush(BG_SURFACE + "CC"),
    )

    parent.pid_curve_pv = parent.pid_graph.plot(
        pen=pg.mkPen(color=ACCENT_TEAL, width=2),
        name="PV"
    )
    parent.pid_curve_sp = parent.pid_graph.plot(
        pen=pg.mkPen(color=ACCENT_CYAN, width=1.5,
                     style=Qt.DashLine),
        name="SP"
    )
    parent.pid_curve_err = parent.pid_graph.plot(
        pen=pg.mkPen(color=ACCENT_WARN, width=1,
                     style=Qt.DotLine),
        name="ERR"
    )

    lay.addWidget(parent.pid_graph)

    # Nút clear history
    clear_btn = QPushButton("Clear history")
    clear_btn.setFixedHeight(22)
    clear_btn.setStyleSheet(f"""
        QPushButton {{
            background: transparent; border: none;
            color: {TEXT_DIM}; font-size: 10px;
        }}
        QPushButton:hover {{ color: {ACCENT_ERR}; }}
    """)
    clear_btn.clicked.connect(lambda: _clear_pid_history(parent))
    lay.addWidget(clear_btn, alignment=Qt.AlignRight)

    grp.setLayout(lay)
    return grp


# ═══════════════════════════════════════════════════════════════════════════════
# PROFILE SECTION
# ═══════════════════════════════════════════════════════════════════════════════

def _build_profile_section(parent) -> QGroupBox:

    grp = QGroupBox("PROFILE")
    lay = QVBoxLayout()
    lay.setSpacing(6)
    lay.setContentsMargins(8, 8, 8, 8)

    # Profile ID
    id_row = QHBoxLayout()
    id_lbl = _lbl("Profile ID")
    id_lbl.setFixedWidth(68)

    parent.tc_profile_id = QSpinBox()
    parent.tc_profile_id.setRange(0, 7)
    parent.tc_profile_id.setValue(0)
    parent.tc_profile_id.setFixedHeight(28)
    parent.tc_profile_id.setStyleSheet(_spinbox_style())

    id_row.addWidget(id_lbl)
    id_row.addWidget(parent.tc_profile_id)
    id_row.addStretch()
    lay.addLayout(id_row)

    # Buttons
    btn_row = QHBoxLayout()
    btn_row.setSpacing(6)

    display_btn  = _btn("Display",  ACCENT_CYAN)
    validate_btn = _btn("Validate", ACCENT_WARN)
    set_btn      = _btn("Set",      ACCENT_TEAL)

    display_btn.setToolTip("temp_profile_diplay <id>")
    validate_btn.setToolTip("temp_profile_val")
    set_btn.setToolTip("temp_profile_set <id>  →  wizard Y/N")

    display_btn.clicked.connect(lambda: _cmd_profile_display(parent))
    validate_btn.clicked.connect(lambda: _cmd_profile_validate(parent))
    set_btn.clicked.connect(lambda: _cmd_profile_set(parent))

    btn_row.addWidget(display_btn)
    btn_row.addWidget(validate_btn)
    btn_row.addWidget(set_btn)
    lay.addLayout(btn_row)

    # Wizard input
    lay.addWidget(_hline())
    wiz_lbl = _lbl("Wizard input  (Y / N / params)")
    wiz_lbl.setStyleSheet(
        f"color: {TEXT_SEC}; font-size: 10px; letter-spacing: 0.4px;"
    )
    lay.addWidget(wiz_lbl)

    wiz_row = QHBoxLayout()
    wiz_row.setSpacing(6)

    parent.tc_wizard_input = QLineEdit()
    parent.tc_wizard_input.setPlaceholderText("e.g.  Y   or   2500 2700 60 1")
    parent.tc_wizard_input.setFixedHeight(28)
    parent.tc_wizard_input.setStyleSheet(_input_style())
    parent.tc_wizard_input.returnPressed.connect(lambda: _cmd_wizard_send(parent))

    send_wiz_btn = _icon_btn("↵", ACCENT_CYAN)
    send_wiz_btn.setToolTip("Gửi dòng wizard (hoặc nhấn Enter)")
    send_wiz_btn.clicked.connect(lambda: _cmd_wizard_send(parent))

    wiz_row.addWidget(parent.tc_wizard_input)
    wiz_row.addWidget(send_wiz_btn)
    lay.addLayout(wiz_row)

    grp.setLayout(lay)
    return grp


# ═══════════════════════════════════════════════════════════════════════════════
# PID CONFIG SECTION
# ═══════════════════════════════════════════════════════════════════════════════

def _build_pid_section(parent) -> QGroupBox:

    grp = QGroupBox("PID  CONSTANTS")
    lay = QVBoxLayout()
    lay.setSpacing(6)
    lay.setContentsMargins(8, 8, 8, 8)

    # State ID
    sid_row = QHBoxLayout()
    sid_lbl = _lbl("State ID")
    sid_lbl.setFixedWidth(68)

    parent.tc_pid_state = QSpinBox()
    parent.tc_pid_state.setRange(1, 8)
    parent.tc_pid_state.setValue(1)
    parent.tc_pid_state.setFixedHeight(28)
    parent.tc_pid_state.setStyleSheet(_spinbox_style())

    sid_row.addWidget(sid_lbl)
    sid_row.addWidget(parent.tc_pid_state)
    sid_row.addStretch()
    lay.addLayout(sid_row)

    # Kp Ki Kd
    pid_grid = QGridLayout()
    pid_grid.setSpacing(6)

    for col, (lbl_txt, attr) in enumerate(
        [("Kp", "tc_kp"), ("Ki", "tc_ki"), ("Kd", "tc_kd")]
    ):
        col_lbl = _lbl(lbl_txt)
        col_lbl.setAlignment(Qt.AlignCenter)
        pid_grid.addWidget(col_lbl, 0, col)

        spin = QDoubleSpinBox()
        spin.setRange(0.0, 100.0)
        spin.setSingleStep(0.1)
        spin.setDecimals(2)
        spin.setValue(1.0)
        spin.setFixedHeight(28)
        spin.setStyleSheet(_spinbox_style())
        setattr(parent, attr, spin)
        pid_grid.addWidget(spin, 1, col)

    lay.addLayout(pid_grid)

    # GET / SET
    pid_btn_row = QHBoxLayout()
    pid_btn_row.setSpacing(6)

    get_btn = _btn("GET", ACCENT_CYAN)
    set_btn = _btn("SET", ACCENT_TEAL)

    get_btn.setToolTip("temp_auto_pid_get <state_id>")
    set_btn.setToolTip("temp_auto_pid_set <state_id> <kp> <ki> <kd>")

    get_btn.clicked.connect(lambda: _cmd_pid_get(parent))
    set_btn.clicked.connect(lambda: _cmd_pid_set(parent))

    pid_btn_row.addWidget(get_btn)
    pid_btn_row.addWidget(set_btn)
    lay.addLayout(pid_btn_row)

    grp.setLayout(lay)
    return grp


# ═══════════════════════════════════════════════════════════════════════════════
# RUN SECTION
# ═══════════════════════════════════════════════════════════════════════════════

def _build_run_section(parent) -> QGroupBox:

    grp = QGroupBox("RUN  CONTROL")
    lay = QVBoxLayout()
    lay.setSpacing(6)
    lay.setContentsMargins(8, 8, 8, 8)

    # Profile ID (sync với section Profile)
    run_id_row = QHBoxLayout()
    run_id_lbl = _lbl("Profile ID")
    run_id_lbl.setFixedWidth(68)

    parent.tc_run_profile_id = QSpinBox()
    parent.tc_run_profile_id.setRange(0, 7)
    parent.tc_run_profile_id.setValue(0)
    parent.tc_run_profile_id.setFixedHeight(28)
    parent.tc_run_profile_id.setStyleSheet(_spinbox_style())

    parent.tc_profile_id.valueChanged.connect(
        lambda v: parent.tc_run_profile_id.setValue(v)
    )
    parent.tc_run_profile_id.valueChanged.connect(
        lambda v: parent.tc_profile_id.setValue(v)
    )

    run_id_row.addWidget(run_id_lbl)
    run_id_row.addWidget(parent.tc_run_profile_id)
    run_id_row.addStretch()
    lay.addLayout(run_id_row)

    # Auto ENA / Start
    auto_row = QHBoxLayout()
    auto_row.setSpacing(6)

    auto_ena_btn   = _btn("▶  AUTO ENA",    ACCENT_TEAL)
    auto_start_btn = _btn("▶▶  AUTO START", ACCENT_CYAN)

    auto_ena_btn.setToolTip("temp_auto_ena <id> — bật auto, preheat đến setpoint")
    auto_start_btn.setToolTip("temp_auto_start <id> — bắt đầu chạy sequence")

    auto_ena_btn.clicked.connect(lambda: _cmd_auto_ena(parent))
    auto_start_btn.clicked.connect(lambda: _cmd_auto_start(parent))

    auto_row.addWidget(auto_ena_btn)
    auto_row.addWidget(auto_start_btn)
    lay.addLayout(auto_row)

    # Manual / Toggle log
    misc_row = QHBoxLayout()
    misc_row.setSpacing(6)

    manu_btn       = _btn("⚙  MANUAL",     ACCENT_WARN)
    log_toggle_btn = _btn("◉  TOGGLE LOG", ACCENT_PRP)

    manu_btn.setToolTip("temp_manu <id>")
    log_toggle_btn.setToolTip("c — toggle NTC console log")

    manu_btn.clicked.connect(lambda: _cmd_manu(parent))
    log_toggle_btn.clicked.connect(lambda: _cmd_toggle_log(parent))

    misc_row.addWidget(manu_btn)
    misc_row.addWidget(log_toggle_btn)
    lay.addLayout(misc_row)

    grp.setLayout(lay)
    return grp


# ═══════════════════════════════════════════════════════════════════════════════
# RESPONSE LOG
# ═══════════════════════════════════════════════════════════════════════════════

def _build_response_box(parent) -> QGroupBox:

    grp = QGroupBox("FIRMWARE  RESPONSE")
    lay = QVBoxLayout()
    lay.setContentsMargins(6, 6, 6, 6)

    parent.tc_response_box = QTextEdit()
    parent.tc_response_box.setReadOnly(True)
    parent.tc_response_box.setFixedHeight(120)
    parent.tc_response_box.setStyleSheet(f"""
        QTextEdit {{
            background-color: {BG_SURFACE};
            border: 1px solid {BORDER};
            border-radius: 6px;
            color: #8FBCD4;
            font-family: "Cascadia Code", "Consolas", monospace;
            font-size: 10px;
            padding: 4px;
        }}
    """)

    header = QHBoxLayout()
    header.addStretch()
    clear_btn = QPushButton("Clear")
    clear_btn.setFixedHeight(22)
    clear_btn.setStyleSheet(f"""
        QPushButton {{ background: transparent; border: none;
                       color: {TEXT_DIM}; font-size: 10px; }}
        QPushButton:hover {{ color: {ACCENT_ERR}; }}
    """)
    clear_btn.clicked.connect(lambda: parent.tc_response_box.clear())
    header.addWidget(clear_btn)

    lay.addLayout(header)
    lay.addWidget(parent.tc_response_box)
    grp.setLayout(lay)
    return grp


# ═══════════════════════════════════════════════════════════════════════════════
# REALTIME UPDATE  —  gọi từ protocol_parser.py mỗi khi có dòng PID mới
# ═══════════════════════════════════════════════════════════════════════════════

def update_pid_display(parent):
    """
    Được gọi tự động từ protocol_parser.py sau khi parse xong 1 dòng PID.
    Cập nhật badge STEP, 4 card số, và graph.
    Không cần gọi thủ công.
    """
    import global_var

    try:
        # STEP badge
        if hasattr(parent, "pid_step_badge"):
            parent.pid_step_badge.set_step(global_var.pid_step)

        # Metric cards
        if hasattr(parent, "pid_card_sp"):
            parent.pid_card_sp.set_value(global_var.pid_sp)
        if hasattr(parent, "pid_card_pv"):
            parent.pid_card_pv.set_value(global_var.pid_pv)
        if hasattr(parent, "pid_card_err"):
            # Tô đỏ nếu |ERR| > 5°C
            err = global_var.pid_err
            accent = ACCENT_ERR if abs(err) > 5.0 else ACCENT_WARN
            parent.pid_card_err.set_value(err, accent_override=accent)
        if hasattr(parent, "pid_card_out"):
            parent.pid_card_out.set_value(global_var.pid_out)

        # Graph curves
        if hasattr(parent, "pid_curve_pv"):
            hist_pv  = global_var.pid_pv_history
            hist_sp  = global_var.pid_sp_history
            hist_err = global_var.pid_err_history
            xs = list(range(len(hist_pv)))

            parent.pid_curve_pv.setData(xs, hist_pv)
            parent.pid_curve_sp.setData(xs, hist_sp)
            parent.pid_curve_err.setData(xs, hist_err)

    except Exception as e:
        print("PID display update error:", e)


def _clear_pid_history(parent):
    import global_var
    global_var.pid_pv_history.clear()
    global_var.pid_sp_history.clear()
    global_var.pid_err_history.clear()
    if hasattr(parent, "pid_curve_pv"):
        parent.pid_curve_pv.setData([], [])
        parent.pid_curve_sp.setData([], [])
        parent.pid_curve_err.setData([], [])


# ═══════════════════════════════════════════════════════════════════════════════
# CUSTOM WIDGETS
# ═══════════════════════════════════════════════════════════════════════════════

class _StepBadge(QLabel):
    """
    Hiển thị STEP hiện tại dạng DOS badge full-width.
    Màu thay đổi theo loại step: HEAT=cam, COOL=cyan, SOAK=teal, NONE=xám.
    """

    def __init__(self):
        super().__init__()
        self.setAlignment(Qt.AlignCenter)
        self.setFixedHeight(32)
        self.set_step("NONE")

    def set_step(self, step: str):
        step_upper = step.upper()
        # Tìm màu khớp, fallback về NONE
        bg, fg = STEP_COLORS.get(step_upper, STEP_COLORS["NONE"])

        # Label dạng DOS: "  ■  HEAT  ■  "
        symbols = {"HEAT": "▲", "COOL": "▼", "SOAK": "◆", "NONE": "·"}
        sym = symbols.get(step_upper, "■")
        self.setText(f"  {sym}  STEP : {step_upper}  {sym}  ")

        self.setStyleSheet(f"""
            QLabel {{
                background-color: {bg};
                border: 1px solid {fg}55;
                border-radius: 6px;
                color: {fg};
                font-family: "Cascadia Code", "Consolas", monospace;
                font-size: 12px;
                font-weight: 700;
                letter-spacing: 3px;
            }}
        """)


class _MetricCard(QFrame):
    """
    Card hiển thị 1 metric: label nhỏ trên + số lớn dưới.
    Tương tự metric card của dashboard.
    """

    def __init__(self, label: str, unit: str, accent: str):
        super().__init__()
        self._accent = accent
        self._unit   = unit

        self.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_SURFACE};
                border: 1px solid {BORDER};
                border-radius: 8px;
                padding: 4px;
            }}
        """)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setFixedHeight(64)

        lay = QVBoxLayout(self)
        lay.setSpacing(2)
        lay.setContentsMargins(8, 6, 8, 6)

        self._label_w = QLabel(label)
        self._label_w.setAlignment(Qt.AlignCenter)
        self._label_w.setStyleSheet(
            f"color: {TEXT_SEC}; font-size: 10px; letter-spacing: 1px;"
            f" background: transparent; border: none;"
        )

        self._value_w = QLabel("—")
        self._value_w.setAlignment(Qt.AlignCenter)
        self._value_w.setStyleSheet(
            f"color: {accent}; font-size: 16px; font-weight: 700;"
            f" background: transparent; border: none;"
        )

        lay.addWidget(self._label_w)
        lay.addWidget(self._value_w)

    def set_value(self, value: float, accent_override: str = None):
        accent = accent_override or self._accent
        self._value_w.setText(f"{value:+.2f} {self._unit}")
        self._value_w.setStyleSheet(
            f"color: {accent}; font-size: 16px; font-weight: 700;"
            f" background: transparent; border: none;"
        )


# ═══════════════════════════════════════════════════════════════════════════════
# COMMAND HANDLERS  —  đổi lệnh gửi đi tại đây
# ═══════════════════════════════════════════════════════════════════════════════

def _cmd_profile_display(parent):
    _send(parent, f"temp_profile_diplay {parent.tc_profile_id.value()}")

def _cmd_profile_validate(parent):
    _send(parent, "temp_profile_val")

def _cmd_profile_set(parent):
    pid = parent.tc_profile_id.value()
    _send(parent, f"temp_profile_set {pid}")
    _log_resp(parent, f"[UI] Wizard started for profile {pid}  →  dùng ô Wizard input")

def _cmd_wizard_send(parent):
    text = parent.tc_wizard_input.text().strip()
    if not text:
        return
    _send(parent, text)
    parent.tc_wizard_input.clear()

def _cmd_pid_get(parent):
    _send(parent, f"temp_auto_pid_get {parent.tc_pid_state.value()}")

def _cmd_pid_set(parent):
    sid = parent.tc_pid_state.value()
    kp  = parent.tc_kp.value()
    ki  = parent.tc_ki.value()
    kd  = parent.tc_kd.value()
    _send(parent, f"temp_auto_pid_set {sid} {kp:.2f} {ki:.2f} {kd:.2f}")

def _cmd_auto_ena(parent):
    pid = parent.tc_run_profile_id.value()
    _send(parent, f"temp_auto_ena {pid}")
    _log_resp(parent, f"[UI] Auto ENA → profile {pid}  preheat starting...")

def _cmd_auto_start(parent):
    pid = parent.tc_run_profile_id.value()
    _send(parent, f"temp_auto_start {pid}")
    _log_resp(parent, f"[UI] Auto START → profile {pid}")

def _cmd_manu(parent):
    pid = parent.tc_run_profile_id.value()
    _send(parent, f"temp_manu {pid}")
    _log_resp(parent, f"[UI] Manual mode → profile {pid}")

def _cmd_toggle_log(parent):
    _send(parent, "c")
    _log_resp(parent, "[UI] Toggled NTC console log")


# ═══════════════════════════════════════════════════════════════════════════════
# UART HELPER
# ═══════════════════════════════════════════════════════════════════════════════

def _send(parent, cmd: str):
    _log_resp(parent, f"→ {cmd}")
    if hasattr(parent, "uart") and parent.uart:
        parent.uart.send_command(cmd)
    else:
        _log_resp(parent, "  [ERR] Not connected")

def _log_resp(parent, msg: str):
    if hasattr(parent, "tc_response_box"):
        parent.tc_response_box.append(msg)

def pipe_to_response(parent, line: str):
    """Pipe mọi dòng UART vào response box — gọi từ protocol_parser.py."""
    if hasattr(parent, "tc_response_box"):
        parent.tc_response_box.append(f"  {line}")


# ═══════════════════════════════════════════════════════════════════════════════
# STYLE HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def _btn(label: str, accent: str) -> QPushButton:
    b = QPushButton(label)
    b.setFixedHeight(30)
    b.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
    b.setStyleSheet(f"""
        QPushButton {{
            background-color: {accent}18;
            border: 1px solid {accent}55;
            border-radius: 6px;
            color: {accent};
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 0.8px;
        }}
        QPushButton:hover {{
            background-color: {accent}30;
            border-color: {accent};
        }}
        QPushButton:pressed {{ background-color: {accent}10; }}
    """)
    return b

def _icon_btn(icon: str, accent: str) -> QPushButton:
    b = QPushButton(icon)
    b.setFixedSize(28, 28)
    b.setStyleSheet(f"""
        QPushButton {{
            background-color: {BG_SURFACE};
            border: 1px solid {BORDER};
            border-radius: 6px;
            color: {accent};
            font-size: 14px;
            font-weight: 700;
        }}
        QPushButton:hover {{
            background-color: #1C2540;
            border-color: {accent};
        }}
    """)
    return b

def _lbl(text: str) -> QLabel:
    l = QLabel(text)
    l.setStyleSheet(f"color: {TEXT_SEC}; font-size: 11px;")
    return l

def _hline() -> QFrame:
    f = QFrame()
    f.setFrameShape(QFrame.HLine)
    f.setStyleSheet(f"background: {BORDER}; max-height: 1px; border: none;")
    return f

def _spinbox_style() -> str:
    return f"""
        QSpinBox, QDoubleSpinBox {{
            background: {BG_SURFACE};
            border: 1px solid {BORDER};
            border-radius: 6px;
            color: {ACCENT_CYAN};
            font-size: 12px;
            font-weight: 600;
            padding: 2px 6px;
        }}
        QSpinBox:focus, QDoubleSpinBox:focus {{ border-color: {ACCENT_CYAN}; }}
        QSpinBox::up-button, QDoubleSpinBox::up-button,
        QSpinBox::down-button, QDoubleSpinBox::down-button {{
            width: 16px; border: none; background: transparent;
        }}
    """

def _input_style() -> str:
    return f"""
        QLineEdit {{
            background: {BG_SURFACE};
            border: 1px solid {BORDER};
            border-radius: 6px;
            color: {TEXT_PRIM};
            font-family: "Cascadia Code", "Consolas", monospace;
            font-size: 11px;
            padding: 2px 8px;
        }}
        QLineEdit:focus {{ border-color: {ACCENT_CYAN}; }}
    """