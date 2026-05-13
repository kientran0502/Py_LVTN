import re
import global_var

from uart_ui import auto_detect_state
from temp_ctrl import (
    update_pid_display,
    pipe_to_response
)

# ═══════════════════════════════════════════════════════════════════════════════
# PID REGEX
# Format:
# STEP=NONE | PID: SP=25.00 PV=28.41 OUT=-100.00 ERR=-3.41
# ═══════════════════════════════════════════════════════════════════════════════

_PID_RE = re.compile(
    r"STEP=(\S+)\s*\|\s*PID:\s*"
    r"SP=([+-]?\d+\.\d+)\s+"
    r"PV=([+-]?\d+\.\d+)\s+"
    r"OUT=([+-]?\d+\.\d+)\s+"
    r"ERR=([+-]?\d+\.\d+)"
)

MAX_HISTORY = 300


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN PARSER
# ═══════════════════════════════════════════════════════════════════════════════

def parse_uart_line(line: str):

    # Remove whitespace/newline
    line = line.strip()

    # ────────────────────────────────────────────────────────────────────────
    # 0. PIPE UART LINE → RESPONSE BOX
    # ────────────────────────────────────────────────────────────────────────
    try:
        pipe_to_response(global_var.window, line)
    except Exception:
        pass

    # ────────────────────────────────────────────────────────────────────────
    # 1. AUTO DETECT FIRMWARE STATE
    # ────────────────────────────────────────────────────────────────────────
    try:
        auto_detect_state(global_var.window, line)
    except Exception:
        pass

    # ────────────────────────────────────────────────────────────────────────
    # 2. PID PARSER
    # ────────────────────────────────────────────────────────────────────────
    try:
        m = _PID_RE.search(line)

        if m:

            # STEP
            global_var.pid_step = m.group(1)

            # FLOAT VALUES
            global_var.pid_sp  = float(m.group(2))
            global_var.pid_pv  = float(m.group(3))
            global_var.pid_out = float(m.group(4))
            global_var.pid_err = float(m.group(5))

            # ── HISTORY APPEND ────────────────────────────────────────────
            global_var.pid_sp_history.append(global_var.pid_sp)
            global_var.pid_pv_history.append(global_var.pid_pv)
            global_var.pid_err_history.append(global_var.pid_err)

            # ── LIMIT HISTORY SIZE ───────────────────────────────────────
            while len(global_var.pid_pv_history) > MAX_HISTORY:
                global_var.pid_pv_history.pop(0)

            while len(global_var.pid_sp_history) > MAX_HISTORY:
                global_var.pid_sp_history.pop(0)

            while len(global_var.pid_err_history) > MAX_HISTORY:
                global_var.pid_err_history.pop(0)

            # ── UPDATE UI ────────────────────────────────────────────────
            try:
                update_pid_display(global_var.window)
            except Exception as e:
                print("PID UI update error:", e)

            return

    except Exception as e:
        print("PID parse error:", e)

    # ────────────────────────────────────────────────────────────────────────
    # 3. SENSOR PARSER
    # ────────────────────────────────────────────────────────────────────────
    try:

        # ── NTC TEMPERATURE ───────────────────────────────────────────────
        if line.startswith("NTC"):

            # Example:
            # NTC1:25
            key, val = line.split(":")

            global_var.ntc_temp[key] = int(val)

            return

        # ── BMP390 TEMPERATURE ────────────────────────────────────────────
        elif line.startswith("BMP_TEMP"):

            # Example:
            # BMP_TEMP:32
            _, val = line.split(":")

            global_var.bmp390_temp = int(val)

            return

        # ── BMP390 PRESSURE ───────────────────────────────────────────────
        elif line.startswith("BMP_PRESS"):

            # Example:
            # BMP_PRESS:100231
            _, val = line.split(":")

            global_var.bmp390_press = int(val)

            return

    except Exception as e:
        print("Sensor parse error:", e)