# CubeSat_App/
# │
# ├── app.py
# ├── main_window.py
# ├── global_var.py
# ├── uart_handler.py
# ├── uart_ui.py
# ├── protocol_parser.py
# ├── bmp390.py
# ├── temp_ctrl.py
# ├── exp_manual.py
# ├── exp_auto.py
# │
# └── img/
#     └── S_logo.png

# app.py              ← Khởi động app
# main_window.py      ← Cửa sổ chính, layout tổng thể
# ├── uart_ui.py      ← Hộp UART (kết nối serial)
# ├── protocol_parser.py ← Xử lý dữ liệu nhận từ UART
# ├── bmp390.py       ← Hiển thị sensor áp suất/nhiệt độ BMP390
# ├── temp_ctrl.py    ← Hiển thị + vẽ graph nhiệt độ NTC
# ├── exp_manual.py   ← Tab Manual (24 laser)
# └── exp_auto.py     ← Tab Auto (chạy tự động)

import sys
from PyQt5.QtWidgets import QApplication
import global_var
from main_window import CubeSatMonitor

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = CubeSatMonitor()
    global_var.window = window

    window.show()

    sys.exit(app.exec_())