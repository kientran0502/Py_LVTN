# global_var.py
# Thêm các biến PID vào file global_var hiện có của bạn
# Nếu đã có ntc_temp, bmp390_temp, bmp390_press thì chỉ cần thêm phần PID

window = None

# ── Sensor data (giữ nguyên cũ) ──────────────────────────────────────────────
ntc_temp     = {}       # {"NTC1": 2841, "NTC2": ...}  (x100 °C)
bmp390_temp  = 0
bmp390_press = 0

# ── PID realtime (thêm mới) ───────────────────────────────────────────────────
pid_step = "NONE"       # tên bước hiện tại: NONE / HEAT / COOL / SOAK / ...
pid_sp   = 0.0          # setpoint (°C)
pid_pv   = 0.0          # process value – nhiệt độ đo được (°C)
pid_out  = 0.0          # output PID (-100 … +100)
pid_err  = 0.0          # error = PV - SP

# History cho graph (tối đa 300 điểm)
pid_sp_history  = []
pid_pv_history  = []
pid_err_history = []

# Target profile lookup table (full pre-computed, revealed per sample)
pid_target_lookup   = []   # toàn bộ profile tính sẵn khi nhấn START
pid_target_history  = []   # phần đã reveal theo sample thực tế