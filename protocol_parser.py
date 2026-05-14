import re
import global_var

from uart_ui import auto_detect_state
from temp_ctrl import (
    update_pid_display,
    pipe_to_response
)

# ═══════════════════════════════════════════════════════════════════════════════
# PID REGEX
# ═══════════════════════════════════════════════════════════════════════════════

# FORMAT 1
# STEP=NONE | PID: SP=25.00 PV=28.41 OUT=-100.00 ERR=-3.41
_PID_RE_1 = re.compile(
    r"STEP=(\S+)\s*\|\s*PID:\s*"
    r"SP=([+-]?\d+\.\d+)\s+"
    r"PV=([+-]?\d+\.\d+)\s+"
    r"OUT=([+-]?\d+\.\d+)\s+"
    r"ERR=([+-]?\d+\.\d+)"
)

# FORMAT 2
# STEP=2 MODE=2 DUR=200 | PID:
# SP=28.90 PV=26.18 OUT=0.00 ERR=2.72
_PID_RE_2 = re.compile(
    r"STEP=(\d+)\s+MODE=(\d+)\s+DUR=(\d+)\s*\|\s*PID:\s*"
    r"SP=([+-]?\d+\.\d+)\s+"
    r"PV=([+-]?\d+\.\d+)\s+"
    r"OUT=([+-]?\d+\.\d+)\s+"
    r"ERR=([+-]?\d+\.\d+)"
)

MAX_HISTORY = 300


# ═══════════════════════════════════════════════════════════════════════════════
# PUSH HISTORY
# ═══════════════════════════════════════════════════════════════════════════════

def _push_history():

    global_var.pid_sp_history.append(global_var.pid_sp)
    global_var.pid_pv_history.append(global_var.pid_pv)
    global_var.pid_err_history.append(global_var.pid_err)

    # limit history
    while len(global_var.pid_pv_history) > MAX_HISTORY:
        global_var.pid_pv_history.pop(0)

    while len(global_var.pid_sp_history) > MAX_HISTORY:
        global_var.pid_sp_history.pop(0)

    while len(global_var.pid_err_history) > MAX_HISTORY:
        global_var.pid_err_history.pop(0)


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN PARSER
# ═══════════════════════════════════════════════════════════════════════════════

def parse_uart_line(line: str):

    line = line.strip()

    # ────────────────────────────────────────────────────────────────────────
    # 0. PIPE UART → RESPONSE BOX
    # ────────────────────────────────────────────────────────────────────────
    try:
        if global_var.window:
            pipe_to_response(global_var.window, line)
    except Exception:
        pass

    # ────────────────────────────────────────────────────────────────────────
    # 1. AUTO DETECT
    # ────────────────────────────────────────────────────────────────────────
    try:
        if global_var.window:
            auto_detect_state(global_var.window, line)
    except Exception:
        pass

    # ────────────────────────────────────────────────────────────────────────
    # 2. PID FORMAT 1
    # ────────────────────────────────────────────────────────────────────────
    try:

        m = _PID_RE_1.search(line)

        if m:

            global_var.pid_step = m.group(1)

            global_var.pid_sp  = float(m.group(2))
            global_var.pid_pv  = float(m.group(3))
            global_var.pid_out = float(m.group(4))
            global_var.pid_err = float(m.group(5))
                        # TARGET = stop temp of current step
            try:

                step_idx = int(global_var.pid_step)

                if hasattr(global_var.window, "_wiz_steps"):

                    if step_idx < len(global_var.window._wiz_steps):

                        _, stop_w, _, _ = global_var.window._wiz_steps[step_idx]

                        target = stop_w.value()

                    else:
                        target = global_var.pid_sp

                else:
                    target = global_var.pid_sp

            except:
                target = global_var.pid_sp

            global_var.pid_target_history.append(target)

            _push_history()

            try:
                if global_var.window:
                    update_pid_display(global_var.window)
            except Exception as e:
                print("PID UI update error:", e)

            return

    except Exception as e:
        print("PID parse 1 error:", e)

    # ────────────────────────────────────────────────────────────────────────
    # 3. PID FORMAT 2
    # ────────────────────────────────────────────────────────────────────────
    try:

        m = _PID_RE_2.search(line)

        if m:

            step = m.group(1)
            mode = m.group(2)

            mode_name = {
                "0": "SOAK",
                "1": "HEAT",
                "2": "COOL"
            }.get(mode, "NONE")

            global_var.pid_step = f"{step}:{mode_name}"

            global_var.pid_sp  = float(m.group(4))
            global_var.pid_pv  = float(m.group(5))
            global_var.pid_out = float(m.group(6))
            global_var.pid_err = float(m.group(7))

            _push_history()

            try:
                if global_var.window:
                    update_pid_display(global_var.window)
            except Exception as e:
                print("PID UI update error:", e)

            return

    except Exception as e:
        print("PID parse 2 error:", e)

    # ────────────────────────────────────────────────────────────────────────
    # 4. SENSOR PARSER
    # ────────────────────────────────────────────────────────────────────────
    try:

        # NTC
        if line.startswith("NTC"):

            key, val = line.split(":")
            global_var.ntc_temp[key] = int(val)

            return

        # BMP TEMP
        elif line.startswith("BMP_TEMP"):

            _, val = line.split(":")
            global_var.bmp390_temp = int(val)

            return

        # BMP PRESS
        elif line.startswith("BMP_PRESS"):

            _, val = line.split(":")
            global_var.bmp390_press = int(val)

            return

    except Exception as e:
        print("Sensor parse error:", e)