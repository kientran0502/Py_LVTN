# import global_var


# def parse_uart_line(line):

#     try:

#         if line.startswith("NTC"):

#             key, val = line.split(":")
#             global_var.ntc_temp[key] = int(val)

#         elif line.startswith("BMP_TEMP"):

#             _, val = line.split(":")
#             global_var.bmp390_temp = int(val)

#         elif line.startswith("BMP_PRESS"):

#             _, val = line.split(":")
#             global_var.bmp390_press = int(val)

#     except Exception as e:
#         print("Parse error:", e)


# def _detect_fw_state(line: str) -> str | None:

#     if "[xBLD]" in line:          # ← sửa ở đây nếu bootloader đổi prefix
#         return STATE_BOOTLOADER

#     if "DEBUG@MCU:~ $" in line \
#     or "System Started" in line:  # ← sửa ở đây nếu app đổi prompt
#         return STATE_APP

#     return None


# protocol_parser.py
# ─────────────────────────────────────────────────────────────────────────────
# Thêm 2 dòng import này vào đầu file protocol_parser hiện tại của bạn:

import re
import global_var
from uart_ui import auto_detect_state

# Regex parse dòng PID log
# Ví dụ: "STEP=NONE | PID: SP=25.00 PV=28.41 OUT=-100.00 ERR=-3.41"
_PID_RE = re.compile(
    r"STEP=(\S+)\s*\|\s*PID:\s*"
    r"SP=([+-]?\d+\.\d+)\s+"
    r"PV=([+-]?\d+\.\d+)\s+"
    r"OUT=([+-]?\d+\.\d+)\s+"
    r"ERR=([+-]?\d+\.\d+)"
)


def parse_uart_line(line):

    # ── 1. Auto-detect firmware state ─────────────────────────────────────────
    try:
        auto_detect_state(global_var.window, line)
    except Exception:
        pass

    # ── 2. Parse PID log ──────────────────────────────────────────────────────
    # Format: STEP=NONE | PID: SP=25.00 PV=28.41 OUT=-100.00 ERR=-3.41
    try:
        m = _PID_RE.search(line)
        if m:
            global_var.pid_step = m.group(1)            # "NONE" / "HEAT" / ...
            global_var.pid_sp   = float(m.group(2))     # setpoint
            global_var.pid_pv   = float(m.group(3))     # process value (nhiệt độ đo)
            global_var.pid_out  = float(m.group(4))     # output
            global_var.pid_err  = float(m.group(5))     # error = PV - SP

            # Append vào history cho graph
            global_var.pid_sp_history.append(global_var.pid_sp)
            global_var.pid_pv_history.append(global_var.pid_pv)
            global_var.pid_err_history.append(global_var.pid_err)

            # Giới hạn history 300 điểm (~5 phút nếu 1s/dòng)
            if len(global_var.pid_pv_history) > 300:
                global_var.pid_sp_history.pop(0)
                global_var.pid_pv_history.pop(0)
                global_var.pid_err_history.pop(0)

            # Notify UI update
            try:
                from temp_ctrl_ui import update_pid_display
                update_pid_display(global_var.window)
            except Exception:
                pass
            return
    except Exception as e:
        print("PID parse error:", e)

    # ── 3. Parse sensor data ──────────────────────────────────────────────────
    try:
        if line.startswith("NTC"):
            key, val = line.split(":")
            global_var.ntc_temp[key] = int(val)

        elif line.startswith("BMP_TEMP"):
            _, val = line.split(":")
            global_var.bmp390_temp = int(val)

        elif line.startswith("BMP_PRESS"):
            _, val = line.split(":")
            global_var.bmp390_press = int(val)

    except Exception as e:
        print("Parse error:", e)