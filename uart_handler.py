import serial
import threading
import time

from PyQt5.QtCore import QObject, pyqtSignal, Qt


class UARTHandler(QObject):                    # ← kế thừa QObject

    # Signal emit từ thread phụ → Qt tự queue về main thread
    sig_log  = pyqtSignal(str)
    sig_data = pyqtSignal(str)

    def __init__(self, log_callback, data_callback):
        super().__init__()                     # ← bắt buộc khi dùng QObject

        self.ser     = None
        self.running = False

        # Connect signal → callback, Qt.QueuedConnection đảm bảo
        # callback luôn chạy trên main thread dù signal emit từ thread phụ
        self.sig_log.connect(log_callback,   Qt.QueuedConnection)
        self.sig_data.connect(data_callback, Qt.QueuedConnection)

    # ─────────────────────────────────────────────
    # CONNECT
    # ─────────────────────────────────────────────
    def connect(self, port, baudrate=115200):
        try:
            self.ser = serial.Serial(
                port=port,
                baudrate=baudrate,
                timeout=0.1
            )
            self.ser.reset_input_buffer()
            self.ser.reset_output_buffer()

            self.running = True

            threading.Thread(
                target=self.read_thread,
                daemon=True
            ).start()

            self.sig_log.emit(f"[UART] Connected {port}")
            return True

        except Exception as e:
            self.sig_log.emit(f"[UART ERROR] {e}")
            return False

    # ─────────────────────────────────────────────
    # DISCONNECT
    # ─────────────────────────────────────────────
    def disconnect(self):
        self.running = False
        try:
            if self.ser:
                self.ser.close()
                self.ser = None
        except Exception:
            pass
        self.sig_log.emit("[UART] Disconnected")

    # ─────────────────────────────────────────────
    # SEND COMMAND
    # ─────────────────────────────────────────────
    def send_command(self, cmd):
        if not self.ser:
            return
        try:
            self.ser.write((cmd + "\n").encode())
            self.sig_log.emit(f"[TX] {cmd}")
        except Exception as e:
            self.sig_log.emit(f"[UART TX ERROR] {e}")

    # ─────────────────────────────────────────────
    # RX THREAD
    # ─────────────────────────────────────────────
    def read_thread(self):
        buffer = ""
        while self.running:
            try:
                if self.ser and self.ser.in_waiting:
                    data = self.ser.read(
                        self.ser.in_waiting
                    ).decode(errors="ignore")

                    if not data:
                        continue

                    buffer += data

                    while "\n" in buffer:
                        line, buffer = buffer.split("\n", 1)
                        line = line.strip()
                        if line:
                            self.sig_log.emit(f"[RX] {line}")   # ← emit, không gọi trực tiếp
                            self.sig_data.emit(line)             # ← emit, không gọi trực tiếp

            except Exception as e:
                self.sig_log.emit(f"[UART RX ERROR] {e}")

            time.sleep(0.03)