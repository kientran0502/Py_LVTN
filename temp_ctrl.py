# temp_ctrl_ui.py  —  v3
# PID realtime monitor + graph (fixed) + Profile Wizard tự động gửi tuần tự

from PyQt5.QtWidgets import (
    QWidget, QGroupBox, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QLineEdit, QFrame, QSpinBox, QDoubleSpinBox,
    QTextEdit, QSizePolicy, QScrollArea, QComboBox, QCheckBox
)
from PyQt5.QtCore import Qt, QTimer
import pyqtgraph as pg
import numpy as np

# ─── Palette ──────────────────────────────────────────────────────────────────
BG_SURFACE  = "#111520"
BG_CARD     = "#161B28"
BORDER      = "#1E2840"
ACCENT_CYAN = "#00C8E8"
ACCENT_TEAL = "#00E5B0"
ACCENT_WARN = "#FFB347"
ACCENT_ERR  = "#FF5C5C"
ACCENT_PRP  = "#7B61FF"
TEXT_PRIM   = "#E8ECF4"
TEXT_SEC    = "#7A8BA8"
TEXT_DIM    = "#3E4D65"

STEP_COLORS = {
    "NONE": ("#1A1D2E", "#7A8BA8"),
    "HEAT": ("#2A1500", "#FFB347"),
    "COOL": ("#001525", "#00C8E8"),
    "SOAK": ("#001A0F", "#00E5B0"),
}

STEP_MODE_OPTIONS = ["SOAK", "HEAT", "COOL"]   # index 0/1/2 = firmware value


# ═══════════════════════════════════════════════════════════════════════════════
# PUBLIC BUILDER
# ═══════════════════════════════════════════════════════════════════════════════

def create_temp_ctrl_tab(parent) -> QWidget:
    root = QScrollArea()
    root.setWidgetResizable(True)
    root.setStyleSheet("QScrollArea { border: none; background: transparent; }")

    inner = QWidget()
    lay   = QVBoxLayout(inner)
    lay.setSpacing(8)
    lay.setContentsMargins(4, 4, 4, 4)

    lay.addWidget(_build_pid_monitor(parent))   # A. STEP + cards
    lay.addWidget(_build_pid_graph(parent))     # B. PV/SP graph
    lay.addWidget(_build_profile_wizard(parent))# C. Profile wizard (NEW)
    lay.addWidget(_build_pid_section(parent))   # D. PID constants
    lay.addWidget(_build_run_section(parent))   # E. Run control
    lay.addWidget(_build_response_box(parent), stretch=1)  # F. Log

    root.setWidget(inner)
    return root


# ═══════════════════════════════════════════════════════════════════════════════
# A.  PID MONITOR
# ═══════════════════════════════════════════════════════════════════════════════

def _build_pid_monitor(parent) -> QGroupBox:
    grp = QGroupBox("PID  MONITOR  —  REALTIME")
    lay = QVBoxLayout()
    lay.setContentsMargins(8, 8, 8, 8)
    lay.setSpacing(8)

    parent.pid_step_badge = _StepBadge()
    lay.addWidget(parent.pid_step_badge)

    row = QHBoxLayout()
    row.setSpacing(6)
    parent.pid_card_sp  = _MetricCard("SP",  "°C", ACCENT_CYAN)
    parent.pid_card_pv  = _MetricCard("PV",  "°C", ACCENT_TEAL)
    parent.pid_card_err = _MetricCard("ERR", "°C", ACCENT_WARN)
    parent.pid_card_out = _MetricCard("OUT", "%",  ACCENT_PRP)
    for c in (parent.pid_card_sp, parent.pid_card_pv,
              parent.pid_card_err, parent.pid_card_out):
        row.addWidget(c)

    lay.addLayout(row)
    grp.setLayout(lay)
    return grp


# ═══════════════════════════════════════════════════════════════════════════════
# B.  PID GRAPH  (fixed: dùng numpy array, ViewBox autoRange)
# ═══════════════════════════════════════════════════════════════════════════════

def _build_pid_graph(parent) -> QGroupBox:
    grp = QGroupBox("PV  vs  SP  HISTORY")
    lay = QVBoxLayout()
    lay.setContentsMargins(6, 6, 6, 6)

    pg.setConfigOptions(antialias=True)

    pw = pg.PlotWidget()
    pw.setBackground(BG_CARD)
    pw.setFixedHeight(170)
    pw.showGrid(x=True, y=True, alpha=0.15)
    pw.setLabel("left",   "°C",     color=TEXT_SEC, size="9pt")
    pw.setLabel("bottom", "sample", color=TEXT_SEC, size="9pt")
    pw.getViewBox().setMouseEnabled(x=True, y=True)   # allow pan/zoom

    axis_pen = pg.mkPen(color=BORDER, width=1)
    for name in ("left", "bottom"):
        ax = pw.getAxis(name)
        ax.setPen(axis_pen)
        ax.setTextPen(pg.mkPen(color=TEXT_SEC))

    pw.addLegend(
        offset=(8, 8),
        labelTextColor=TEXT_SEC,
        pen=pg.mkPen(color=BORDER),
        brush=pg.mkBrush(BG_SURFACE + "CC"),
    )

    # ── curves stored on parent ───────────────────────────────────────────────
    parent.pid_curve_pv  = pw.plot(
        np.array([], dtype=float), np.array([], dtype=float),
        pen=pg.mkPen(color=ACCENT_TEAL, width=2), name="PV"
    )
    parent.pid_curve_sp  = pw.plot(
        np.array([], dtype=float), np.array([], dtype=float),
        pen=pg.mkPen(color=ACCENT_CYAN, width=1.5, style=Qt.DashLine), name="SP"
    )
    parent.pid_curve_err = pw.plot(
        np.array([], dtype=float), np.array([], dtype=float),
        pen=pg.mkPen(color=ACCENT_WARN, width=1,   style=Qt.DotLine),  name="ERR"
    )

    # keep reference to PlotWidget so we can call autoRange
    parent._pid_plot_widget = pw

    lay.addWidget(pw)

    btn_row = QHBoxLayout()
    auto_range_btn = QPushButton("Auto range")
    auto_range_btn.setFixedHeight(22)
    auto_range_btn.setStyleSheet(
        f"QPushButton {{ background:transparent; border:none; "
        f"color:{TEXT_SEC}; font-size:10px; }}"
        f"QPushButton:hover {{ color:{ACCENT_CYAN}; }}"
    )
    auto_range_btn.clicked.connect(
        lambda: parent._pid_plot_widget.getViewBox().autoRange()
    )

    clear_btn = QPushButton("Clear")
    clear_btn.setFixedHeight(22)
    clear_btn.setStyleSheet(
        f"QPushButton {{ background:transparent; border:none; "
        f"color:{TEXT_DIM}; font-size:10px; }}"
        f"QPushButton:hover {{ color:{ACCENT_ERR}; }}"
    )
    clear_btn.clicked.connect(lambda: _clear_pid_history(parent))

    btn_row.addWidget(auto_range_btn)
    btn_row.addStretch()
    btn_row.addWidget(clear_btn)
    lay.addLayout(btn_row)

    grp.setLayout(lay)
    return grp


# ═══════════════════════════════════════════════════════════════════════════════
# C.  PROFILE WIZARD  (nhập form → tự gửi tuần tự)
# ═══════════════════════════════════════════════════════════════════════════════
# Flow firmware (từ log thực tế):
#   1. temp_profile_set <id>
#   2. firmware: "Do you want to continue? (Y/N)"  → gửi "y"
#   3. firmware wizard hỏi từng thông số → gửi giá trị lần lượt
#      (profile index, main ntc, sec ntc, tec mask, heater mask,
#       setpoint *100, delta *100, step count)
#   4. với mỗi step: gửi "start stop duration mode"  (start/stop *100)
#   5. firmware: "Save? (Y/N)" → gửi "y"
# ═══════════════════════════════════════════════════════════════════════════════

MAX_STEPS = 8

def _build_profile_wizard(parent) -> QGroupBox:
    grp = QGroupBox("PROFILE  WIZARD  —  AUTO SEND")
    outer = QVBoxLayout()
    outer.setSpacing(8)
    outer.setContentsMargins(8, 8, 8, 8)

    # ── Header row: Profile ID + Display + Validate ───────────────────────────
    hdr = QHBoxLayout()
    hdr.setSpacing(6)

    hdr.addWidget(_lbl("Profile ID"))
    parent.wiz_profile_id = QSpinBox()
    parent.wiz_profile_id.setRange(0, 7)
    parent.wiz_profile_id.setFixedHeight(26)
    parent.wiz_profile_id.setStyleSheet(_spinbox_style())
    parent.wiz_profile_id.setFixedWidth(60)
    hdr.addWidget(parent.wiz_profile_id)

    disp_btn = _small_btn("Display", ACCENT_CYAN)
    disp_btn.setToolTip("temp_profile_diplay <id>")
    disp_btn.clicked.connect(lambda: _send(
        parent, f"temp_profile_diplay {parent.wiz_profile_id.value()}"
    ))

    val_btn = _small_btn("Validate", ACCENT_WARN)
    val_btn.setToolTip("temp_profile_val")
    val_btn.clicked.connect(lambda: _send(parent, "temp_profile_val"))

    hdr.addWidget(disp_btn)
    hdr.addWidget(val_btn)
    hdr.addStretch()
    outer.addLayout(hdr)

    outer.addWidget(_hline())

    # ── Profile parameters ────────────────────────────────────────────────────
    outer.addWidget(_section_lbl("  Profile parameters"))

    param_grid = QGridLayout()
    param_grid.setSpacing(5)
    param_grid.setHorizontalSpacing(8)

    def _add_spin(row, col, label, attr, lo, hi, default, tip=""):
        param_grid.addWidget(_lbl(label), row, col*2)
        sp = QSpinBox()
        sp.setRange(lo, hi)
        sp.setValue(default)
        sp.setFixedHeight(26)
        sp.setFixedWidth(72)
        sp.setStyleSheet(_spinbox_style())
        if tip:
            sp.setToolTip(tip)
        setattr(parent, attr, sp)
        param_grid.addWidget(sp, row, col*2+1)

    # row 0
    _add_spin(0, 0, "Main NTC",  "wiz_main_ntc",  0, 7, 0, "0=NTC1 … 7=NTC8")
    _add_spin(0, 1, "Sec NTC",   "wiz_sec_ntc",   0, 7, 1, "0=NTC1 … 7=NTC8")

    # row 1 — mask fields (hex input)
    param_grid.addWidget(_lbl("TEC mask"), 1, 0)
    parent.wiz_tec_mask = QLineEdit("0x01")
    parent.wiz_tec_mask.setFixedHeight(26)
    parent.wiz_tec_mask.setFixedWidth(72)
    parent.wiz_tec_mask.setToolTip("e.g. 0x01 = TEC1 enabled")
    parent.wiz_tec_mask.setStyleSheet(_input_style())
    param_grid.addWidget(parent.wiz_tec_mask, 1, 1)

    param_grid.addWidget(_lbl("Heater mask"), 1, 2)
    parent.wiz_heater_mask = QLineEdit("0x02")
    parent.wiz_heater_mask.setFixedHeight(26)
    parent.wiz_heater_mask.setFixedWidth(72)
    parent.wiz_heater_mask.setToolTip("e.g. 0x02 = Heater2 enabled")
    parent.wiz_heater_mask.setStyleSheet(_input_style())
    param_grid.addWidget(parent.wiz_heater_mask, 1, 3)

    # row 2 — setpoint, delta  (nhập °C, tự *100 khi gửi)
    param_grid.addWidget(_lbl("Setpoint °C"), 2, 0)
    parent.wiz_setpoint = QDoubleSpinBox()
    parent.wiz_setpoint.setRange(-50.0, 150.0)
    parent.wiz_setpoint.setValue(25.0)
    parent.wiz_setpoint.setDecimals(2)
    parent.wiz_setpoint.setSingleStep(0.5)
    parent.wiz_setpoint.setFixedHeight(26)
    parent.wiz_setpoint.setFixedWidth(80)
    parent.wiz_setpoint.setStyleSheet(_spinbox_style())
    parent.wiz_setpoint.setToolTip("firmware nhận giá trị *100  (tự động)")
    param_grid.addWidget(parent.wiz_setpoint, 2, 1)

    param_grid.addWidget(_lbl("Delta °C"), 2, 2)
    parent.wiz_delta = QDoubleSpinBox()
    parent.wiz_delta.setRange(0.0, 50.0)
    parent.wiz_delta.setValue(0.0)
    parent.wiz_delta.setDecimals(2)
    parent.wiz_delta.setSingleStep(0.1)
    parent.wiz_delta.setFixedHeight(26)
    parent.wiz_delta.setFixedWidth(80)
    parent.wiz_delta.setStyleSheet(_spinbox_style())
    param_grid.addWidget(parent.wiz_delta, 2, 3)

    outer.addLayout(param_grid)
    outer.addWidget(_hline())

    # ── Step count ────────────────────────────────────────────────────────────
    sc_row = QHBoxLayout()
    sc_row.addWidget(_lbl("Step count"))
    parent.wiz_step_count = QSpinBox()
    parent.wiz_step_count.setRange(1, MAX_STEPS)
    parent.wiz_step_count.setValue(3)
    parent.wiz_step_count.setFixedHeight(26)
    parent.wiz_step_count.setFixedWidth(60)
    parent.wiz_step_count.setStyleSheet(_spinbox_style())
    parent.wiz_step_count.valueChanged.connect(
        lambda v: _refresh_step_rows(parent)
    )
    sc_row.addWidget(parent.wiz_step_count)
    sc_row.addStretch()
    outer.addLayout(sc_row)

    # ── Step rows container ───────────────────────────────────────────────────
    outer.addWidget(_section_lbl("  Steps  [ start°C   stop°C   dur(s)   mode ]"))

    parent._wiz_step_container = QVBoxLayout()
    parent._wiz_step_container.setSpacing(4)

    parent._wiz_steps = []   # list of (start, stop, dur, mode_combo)

    for i in range(MAX_STEPS):
        row_widget, widgets = _make_step_row(i)
        parent._wiz_steps.append(widgets)
        parent._wiz_step_container.addWidget(row_widget)

    outer.addLayout(parent._wiz_step_container)
    _refresh_step_rows(parent)   # show only step_count rows

    outer.addWidget(_hline())

    # ── Send button ───────────────────────────────────────────────────────────
    send_row = QHBoxLayout()
    send_row.setSpacing(6)

    send_btn = QPushButton("⟳  SEND PROFILE  (auto wizard)")
    send_btn.setFixedHeight(34)
    send_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
    send_btn.setStyleSheet(f"""
        QPushButton {{
            background-color: {ACCENT_TEAL}18;
            border: 1px solid {ACCENT_TEAL}60;
            border-radius: 7px;
            color: {ACCENT_TEAL};
            font-size: 12px; font-weight: 700; letter-spacing: 1px;
        }}
        QPushButton:hover {{
            background-color: {ACCENT_TEAL}30; border-color: {ACCENT_TEAL};
        }}
        QPushButton:pressed {{ background-color: {ACCENT_TEAL}10; }}
    """)
    send_btn.setToolTip(
        "Gửi toàn bộ wizard tự động:\n"
        "temp_profile_set → y → params → steps → y (save)"
    )
    send_btn.clicked.connect(lambda: _cmd_send_wizard(parent))

    # Manual wizard fallback
    parent.tc_wizard_input = QLineEdit()
    parent.tc_wizard_input.setPlaceholderText("Manual wizard line  (Y / value)")
    parent.tc_wizard_input.setFixedHeight(28)
    parent.tc_wizard_input.setStyleSheet(_input_style())
    parent.tc_wizard_input.returnPressed.connect(lambda: _cmd_wizard_send(parent))

    send_wiz_icon = _icon_btn("↵", ACCENT_CYAN)
    send_wiz_icon.setToolTip("Gửi dòng thủ công")
    send_wiz_icon.clicked.connect(lambda: _cmd_wizard_send(parent))

    send_row.addWidget(send_btn)
    outer.addLayout(send_row)

    manual_row = QHBoxLayout()
    manual_row.addWidget(_lbl("Manual:"))
    manual_row.addWidget(parent.tc_wizard_input)
    manual_row.addWidget(send_wiz_icon)
    outer.addLayout(manual_row)

    grp.setLayout(outer)
    return grp


def _make_step_row(index: int):
    """Tạo 1 hàng step với 4 field: start, stop, duration, mode."""
    widget = QFrame()
    widget.setStyleSheet(
        f"QFrame {{ background: {BG_SURFACE}; border: 1px solid {BORDER}; "
        f"border-radius: 5px; }}"
    )
    row = QHBoxLayout(widget)
    row.setContentsMargins(6, 3, 6, 3)
    row.setSpacing(6)

    idx_lbl = QLabel(f"[{index}]")
    idx_lbl.setFixedWidth(22)
    idx_lbl.setStyleSheet(f"color: {TEXT_DIM}; font-size: 10px; background: transparent; border: none;")
    row.addWidget(idx_lbl)

    def _dspin(default, lo=-50.0, hi=200.0):
        s = QDoubleSpinBox()
        s.setRange(lo, hi)
        s.setValue(default)
        s.setDecimals(2)
        s.setSingleStep(1.0)
        s.setFixedHeight(24)
        s.setStyleSheet(_spinbox_style_compact())
        return s

    def _ispin(default, lo=0, hi=86400):
        s = QSpinBox()
        s.setRange(lo, hi)
        s.setValue(default)
        s.setFixedHeight(24)
        s.setStyleSheet(_spinbox_style_compact())
        return s

    start = _dspin(25.0)
    stop  = _dspin(40.0)
    dur   = _ispin(60)

    mode  = QComboBox()
    mode.addItems(["0 – SOAK", "1 – HEAT", "2 – COOL"])
    mode.setFixedHeight(24)
    mode.setStyleSheet(f"""
        QComboBox {{
            background: {BG_CARD}; border: 1px solid {BORDER};
            border-radius: 4px; color: {ACCENT_CYAN};
            font-size: 10px; padding: 1px 4px;
        }}
        QComboBox QAbstractItemView {{
            background: {BG_CARD}; color: {TEXT_PRIM};
            selection-background-color: #1C2540;
        }}
        QComboBox::drop-down {{ border: none; width: 14px; }}
    """)

    for lbl_txt, w in [("start", start), ("stop", stop), ("dur s", dur), ("mode", mode)]:
        mini = QLabel(lbl_txt)
        mini.setStyleSheet(
            f"color: {TEXT_DIM}; font-size: 9px; background: transparent; border: none;"
        )
        row.addWidget(mini)
        row.addWidget(w)

    return widget, (start, stop, dur, mode)


def _refresh_step_rows(parent):
    """Show/hide step rows berdasarkan step_count."""
    n = parent.wiz_step_count.value()
    for i, (row_widget, _) in enumerate(
        _iter_step_row_widgets(parent)
    ):
        row_widget.setVisible(i < n)


def _iter_step_row_widgets(parent):
    """Yield (QFrame, widgets_tuple) for each step row."""
    lay = parent._wiz_step_container
    for i in range(lay.count()):
        item = lay.itemAt(i)
        if item and item.widget():
            yield item.widget(), parent._wiz_steps[i]


# ═══════════════════════════════════════════════════════════════════════════════
# D.  PID CONSTANTS
# ═══════════════════════════════════════════════════════════════════════════════

def _build_pid_section(parent) -> QGroupBox:
    grp = QGroupBox("PID  CONSTANTS")
    lay = QVBoxLayout()
    lay.setSpacing(6)
    lay.setContentsMargins(8, 8, 8, 8)

    sid_row = QHBoxLayout()
    sid_row.addWidget(_lbl("State ID"))
    parent.tc_pid_state = QSpinBox()
    parent.tc_pid_state.setRange(1, 8)
    parent.tc_pid_state.setValue(1)
    parent.tc_pid_state.setFixedHeight(28)
    parent.tc_pid_state.setStyleSheet(_spinbox_style())
    sid_row.addWidget(parent.tc_pid_state)
    sid_row.addStretch()
    lay.addLayout(sid_row)

    pid_grid = QGridLayout()
    pid_grid.setSpacing(6)
    for col, (lbl_txt, attr) in enumerate(
        [("Kp", "tc_kp"), ("Ki", "tc_ki"), ("Kd", "tc_kd")]
    ):
        l = _lbl(lbl_txt)
        l.setAlignment(Qt.AlignCenter)
        pid_grid.addWidget(l, 0, col)
        sp = QDoubleSpinBox()
        sp.setRange(0.0, 100.0)
        sp.setSingleStep(0.1)
        sp.setDecimals(2)
        sp.setValue(1.0)
        sp.setFixedHeight(28)
        sp.setStyleSheet(_spinbox_style())
        setattr(parent, attr, sp)
        pid_grid.addWidget(sp, 1, col)
    lay.addLayout(pid_grid)

    r = QHBoxLayout()
    r.setSpacing(6)
    g = _btn("GET", ACCENT_CYAN)
    s = _btn("SET", ACCENT_TEAL)
    g.setToolTip("temp_auto_pid_get <state_id>")
    s.setToolTip("temp_auto_pid_set <state_id> kp ki kd")
    g.clicked.connect(lambda: _cmd_pid_get(parent))
    s.clicked.connect(lambda: _cmd_pid_set(parent))
    r.addWidget(g)
    r.addWidget(s)
    lay.addLayout(r)

    grp.setLayout(lay)
    return grp


# ═══════════════════════════════════════════════════════════════════════════════
# E.  RUN CONTROL
# ═══════════════════════════════════════════════════════════════════════════════

def _build_run_section(parent) -> QGroupBox:
    grp = QGroupBox("RUN  CONTROL")
    lay = QVBoxLayout()
    lay.setSpacing(6)
    lay.setContentsMargins(8, 8, 8, 8)

    rid_row = QHBoxLayout()
    rid_row.addWidget(_lbl("Profile ID"))
    parent.tc_run_profile_id = QSpinBox()
    parent.tc_run_profile_id.setRange(0, 7)
    parent.tc_run_profile_id.setValue(0)
    parent.tc_run_profile_id.setFixedHeight(28)
    parent.tc_run_profile_id.setStyleSheet(_spinbox_style())

    # sync với wiz_profile_id
    parent.wiz_profile_id.valueChanged.connect(
        lambda v: parent.tc_run_profile_id.setValue(v)
    )
    parent.tc_run_profile_id.valueChanged.connect(
        lambda v: parent.wiz_profile_id.setValue(v)
    )

    rid_row.addWidget(parent.tc_run_profile_id)
    rid_row.addStretch()
    lay.addLayout(rid_row)

    r1 = QHBoxLayout()
    r1.setSpacing(6)
    ena = _btn("▶  AUTO ENA",    ACCENT_TEAL)
    sta = _btn("▶▶  AUTO START", ACCENT_CYAN)
    ena.setToolTip("temp_auto_ena <id>")
    sta.setToolTip("temp_auto_start <id>")
    ena.clicked.connect(lambda: _cmd_auto_ena(parent))
    sta.clicked.connect(lambda: _cmd_auto_start(parent))
    r1.addWidget(ena)
    r1.addWidget(sta)
    lay.addLayout(r1)

    r2 = QHBoxLayout()
    r2.setSpacing(6)
    mn  = _btn("⚙  MANUAL",     ACCENT_WARN)
    lg  = _btn("◉  TOGGLE LOG", ACCENT_PRP)
    mn.setToolTip("temp_manu <id>")
    lg.setToolTip("c")
    mn.clicked.connect(lambda: _cmd_manu(parent))
    lg.clicked.connect(lambda: _cmd_toggle_log(parent))
    r2.addWidget(mn)
    r2.addWidget(lg)
    lay.addLayout(r2)

    grp.setLayout(lay)
    return grp


# ═══════════════════════════════════════════════════════════════════════════════
# F.  RESPONSE BOX
# ═══════════════════════════════════════════════════════════════════════════════

def _build_response_box(parent) -> QGroupBox:
    grp = QGroupBox("FIRMWARE  RESPONSE")
    lay = QVBoxLayout()
    lay.setContentsMargins(6, 6, 6, 6)

    parent.tc_response_box = QTextEdit()
    parent.tc_response_box.setReadOnly(True)
    parent.tc_response_box.setFixedHeight(130)
    parent.tc_response_box.setStyleSheet(f"""
        QTextEdit {{
            background-color: {BG_SURFACE}; border: 1px solid {BORDER};
            border-radius: 6px; color: #8FBCD4;
            font-family: "Cascadia Code", "Consolas", monospace;
            font-size: 10px; padding: 4px;
        }}
    """)

    hdr = QHBoxLayout()
    hdr.addStretch()
    cb = QPushButton("Clear")
    cb.setFixedHeight(22)
    cb.setStyleSheet(
        f"QPushButton {{ background:transparent; border:none; "
        f"color:{TEXT_DIM}; font-size:10px; }}"
        f"QPushButton:hover {{ color:{ACCENT_ERR}; }}"
    )
    cb.clicked.connect(lambda: parent.tc_response_box.clear())
    hdr.addWidget(cb)
    lay.addLayout(hdr)
    lay.addWidget(parent.tc_response_box)
    grp.setLayout(lay)
    return grp


# ═══════════════════════════════════════════════════════════════════════════════
# REALTIME UPDATE  —  gọi từ protocol_parser sau mỗi dòng PID
# ═══════════════════════════════════════════════════════════════════════════════

def update_pid_display(parent):
    import global_var

    try:
        if hasattr(parent, "pid_step_badge"):
            parent.pid_step_badge.set_step(global_var.pid_step)

        if hasattr(parent, "pid_card_sp"):
            parent.pid_card_sp.set_value(global_var.pid_sp)
        if hasattr(parent, "pid_card_pv"):
            parent.pid_card_pv.set_value(global_var.pid_pv)
        if hasattr(parent, "pid_card_out"):
            parent.pid_card_out.set_value(global_var.pid_out)
        if hasattr(parent, "pid_card_err"):
            err    = global_var.pid_err
            accent = ACCENT_ERR if abs(err) > 5.0 else ACCENT_WARN
            parent.pid_card_err.set_value(err, accent_override=accent)

        # ── graph update (numpy arrays) ───────────────────────────────────
        if hasattr(parent, "pid_curve_pv") and global_var.pid_pv_history:
            xs  = np.arange(len(global_var.pid_pv_history), dtype=float)
            pv  = np.array(global_var.pid_pv_history,  dtype=float)
            sp  = np.array(global_var.pid_sp_history,  dtype=float)
            err = np.array(global_var.pid_err_history, dtype=float)

            parent.pid_curve_pv.setData(xs, pv)
            parent.pid_curve_sp.setData(xs, sp)
            parent.pid_curve_err.setData(xs, err)

    except Exception as e:
        print("PID display error:", e)


def _clear_pid_history(parent):
    import global_var
    global_var.pid_pv_history.clear()
    global_var.pid_sp_history.clear()
    global_var.pid_err_history.clear()
    if hasattr(parent, "pid_curve_pv"):
        empty = np.array([], dtype=float)
        parent.pid_curve_pv.setData(empty, empty)
        parent.pid_curve_sp.setData(empty, empty)
        parent.pid_curve_err.setData(empty, empty)


# ═══════════════════════════════════════════════════════════════════════════════
# WIZARD AUTO-SEND  —  gửi tuần tự theo flow firmware
# ═══════════════════════════════════════════════════════════════════════════════

def _cmd_send_wizard(parent):
    """
    Gửi toàn bộ profile wizard tự động với delay 150ms giữa mỗi dòng.

    Flow gửi (khớp với firmware log):
      temp_profile_set <id>
      y                          ← confirm continue
      <profile_id>               ← firmware hỏi profile index
      <main_ntc>
      <sec_ntc>
      <tec_mask>                 ← hex string, e.g. 0x01
      <heater_mask>
      <setpoint*100>             ← int, e.g. 2500 = 25.00°C
      <delta*100>
      <step_count>
      <start*100> <stop*100> <dur> <mode>   ← 1 dòng mỗi step
      y                          ← save
    """
    pid    = parent.wiz_profile_id.value()
    n_step = parent.wiz_step_count.value()

    # Build sequence
    seq = []
    seq.append(f"temp_profile_set {pid}")
    seq.append("y")                               # confirm continue
    seq.append(str(pid))                          # profile index
    seq.append(str(parent.wiz_main_ntc.value()))
    seq.append(str(parent.wiz_sec_ntc.value()))

    # hex mask — firmware nhận decimal hoặc hex đều được
    tec_raw    = parent.wiz_tec_mask.text().strip()    or "1"
    heater_raw = parent.wiz_heater_mask.text().strip() or "2"
    seq.append(tec_raw)
    seq.append(heater_raw)

    # setpoint & delta *100  (firmware: "| -> setpoint (0.01*C): 2500")
    seq.append(str(int(round(parent.wiz_setpoint.value() * 100))))
    seq.append(str(int(round(parent.wiz_delta.value()    * 100))))

    seq.append(str(n_step))

    # Steps
    for i in range(n_step):
        start_w, stop_w, dur_w, mode_w = parent._wiz_steps[i]
        start_v = int(round(start_w.value() * 100))
        stop_v  = int(round(stop_w.value()  * 100))
        dur_v   = dur_w.value()
        mode_v  = mode_w.currentIndex()           # 0=SOAK, 1=HEAT, 2=COOL
        seq.append(f"{start_v} {stop_v} {dur_v} {mode_v}")

    seq.append("y")                               # save

    # Log preview
    _log_resp(parent, f"[WIZ] Sending {len(seq)} lines for profile {pid}:")
    for line in seq:
        _log_resp(parent, f"  > {line}")

    # Send with 200ms delay between lines
    _send_sequence(parent, seq, delay_ms=200)


def _send_sequence(parent, seq: list, delay_ms: int = 200):
    """Gửi list lệnh tuần tự, mỗi lệnh cách nhau delay_ms."""
    if not seq:
        return

    cmd = seq[0]
    rest = seq[1:]

    _send(parent, cmd)

    if rest:
        QTimer.singleShot(delay_ms, lambda: _send_sequence(parent, rest, delay_ms))


# ═══════════════════════════════════════════════════════════════════════════════
# COMMAND HANDLERS
# ═══════════════════════════════════════════════════════════════════════════════

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
    _log_resp(parent, f"[UI] Auto ENA → profile {pid}")

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
    _log_resp(parent, "[UI] Toggle NTC log")


# ═══════════════════════════════════════════════════════════════════════════════
# UART HELPERS
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
    """Pipe mọi dòng UART → response box (gọi từ protocol_parser)."""
    if hasattr(parent, "tc_response_box"):
        parent.tc_response_box.append(f"  {line}")


# ═══════════════════════════════════════════════════════════════════════════════
# CUSTOM WIDGETS
# ═══════════════════════════════════════════════════════════════════════════════

class _StepBadge(QLabel):
    def __init__(self):
        super().__init__()
        self.setAlignment(Qt.AlignCenter)
        self.setFixedHeight(32)
        self.set_step("NONE")

    def set_step(self, step: str):
        su = step.upper()
        bg, fg = STEP_COLORS.get(su, STEP_COLORS["NONE"])
        sym = {"HEAT": "▲", "COOL": "▼", "SOAK": "◆"}.get(su, "·")
        self.setText(f"  {sym}  STEP : {su}  {sym}  ")
        self.setStyleSheet(f"""
            QLabel {{
                background-color: {bg}; border: 1px solid {fg}55;
                border-radius: 6px; color: {fg};
                font-family: "Cascadia Code","Consolas",monospace;
                font-size: 12px; font-weight: 700; letter-spacing: 3px;
            }}
        """)


class _MetricCard(QFrame):
    def __init__(self, label: str, unit: str, accent: str):
        super().__init__()
        self._accent = accent
        self._unit   = unit
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_SURFACE}; border: 1px solid {BORDER};
                border-radius: 8px;
            }}
        """)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setFixedHeight(62)

        lay = QVBoxLayout(self)
        lay.setSpacing(2)
        lay.setContentsMargins(6, 5, 6, 5)

        self._lbl_w = QLabel(label)
        self._lbl_w.setAlignment(Qt.AlignCenter)
        self._lbl_w.setStyleSheet(
            f"color:{TEXT_SEC}; font-size:10px; letter-spacing:1px;"
            f" background:transparent; border:none;"
        )
        self._val_w = QLabel("—")
        self._val_w.setAlignment(Qt.AlignCenter)
        self._val_w.setStyleSheet(
            f"color:{accent}; font-size:15px; font-weight:700;"
            f" background:transparent; border:none;"
        )
        lay.addWidget(self._lbl_w)
        lay.addWidget(self._val_w)

    def set_value(self, value: float, accent_override: str = None):
        accent = accent_override or self._accent
        self._val_w.setText(f"{value:+.2f} {self._unit}")
        self._val_w.setStyleSheet(
            f"color:{accent}; font-size:15px; font-weight:700;"
            f" background:transparent; border:none;"
        )


# ═══════════════════════════════════════════════════════════════════════════════
# STYLE HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def _btn(label: str, accent: str) -> QPushButton:
    b = QPushButton(label)
    b.setFixedHeight(30)
    b.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
    b.setStyleSheet(f"""
        QPushButton {{
            background-color:{accent}18; border:1px solid {accent}55;
            border-radius:6px; color:{accent};
            font-size:11px; font-weight:700; letter-spacing:0.8px;
        }}
        QPushButton:hover {{ background-color:{accent}30; border-color:{accent}; }}
        QPushButton:pressed {{ background-color:{accent}10; }}
    """)
    return b

def _small_btn(label: str, accent: str) -> QPushButton:
    b = QPushButton(label)
    b.setFixedHeight(26)
    b.setStyleSheet(f"""
        QPushButton {{
            background-color:{accent}12; border:1px solid {accent}44;
            border-radius:5px; color:{accent};
            font-size:10px; font-weight:600; padding: 0 8px;
        }}
        QPushButton:hover {{ background-color:{accent}25; border-color:{accent}; }}
    """)
    return b

def _icon_btn(icon: str, accent: str) -> QPushButton:
    b = QPushButton(icon)
    b.setFixedSize(28, 28)
    b.setStyleSheet(f"""
        QPushButton {{
            background-color:{BG_SURFACE}; border:1px solid {BORDER};
            border-radius:6px; color:{accent};
            font-size:14px; font-weight:700;
        }}
        QPushButton:hover {{ background-color:#1C2540; border-color:{accent}; }}
    """)
    return b

def _lbl(text: str) -> QLabel:
    l = QLabel(text)
    l.setStyleSheet(f"color:{TEXT_SEC}; font-size:11px;")
    return l

def _section_lbl(text: str) -> QLabel:
    l = QLabel(text)
    l.setStyleSheet(
        f"color:{ACCENT_CYAN}; font-size:10px; font-weight:600; "
        f"letter-spacing:1px; background:transparent;"
    )
    return l

def _hline() -> QFrame:
    f = QFrame()
    f.setFrameShape(QFrame.HLine)
    f.setStyleSheet(f"background:{BORDER}; max-height:1px; border:none;")
    return f

def _spinbox_style() -> str:
    return f"""
        QSpinBox, QDoubleSpinBox {{
            background:{BG_SURFACE}; border:1px solid {BORDER};
            border-radius:6px; color:{ACCENT_CYAN};
            font-size:12px; font-weight:600; padding:2px 6px;
        }}
        QSpinBox:focus, QDoubleSpinBox:focus {{ border-color:{ACCENT_CYAN}; }}
        QSpinBox::up-button, QDoubleSpinBox::up-button,
        QSpinBox::down-button, QDoubleSpinBox::down-button {{
            width:16px; border:none; background:transparent;
        }}
    """

def _spinbox_style_compact() -> str:
    return f"""
        QSpinBox, QDoubleSpinBox {{
            background:{BG_CARD}; border:1px solid {BORDER};
            border-radius:4px; color:{ACCENT_CYAN};
            font-size:10px; font-weight:600; padding:1px 4px;
        }}
        QSpinBox::up-button, QDoubleSpinBox::up-button,
        QSpinBox::down-button, QDoubleSpinBox::down-button {{
            width:12px; border:none; background:transparent;
        }}
    """

def _input_style() -> str:
    return f"""
        QLineEdit {{
            background:{BG_SURFACE}; border:1px solid {BORDER};
            border-radius:6px; color:{TEXT_PRIM};
            font-family:"Cascadia Code","Consolas",monospace;
            font-size:11px; padding:2px 8px;
        }}
        QLineEdit:focus {{ border-color:{ACCENT_CYAN}; }}
    """