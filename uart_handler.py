# import serial
# import threading
# import time


# class UARTHandler:

#     def __init__(self, log_callback, data_callback):

#         self.ser = None
#         self.running = False

#         self.log = log_callback
#         self.data_callback = data_callback

#     def connect(self, port, baudrate=115200):

#         try:
#             self.ser = serial.Serial(
#                 port=port,
#                 baudrate=baudrate,
#                 timeout=0.1
#             )

#             self.running = True

#             threading.Thread(
#                 target=self.read_thread,
#                 daemon=True
#             ).start()

#             self.log(f"[UART] Connected {port}")

#             return True

#         except Exception as e:
#             self.log(f"[UART ERROR] {e}")
#             return False

#     def disconnect(self):

#         self.running = False

#         if self.ser:
#             self.ser.close()
#             self.ser = None

#         self.log("[UART] Disconnected")

#     def send_command(self, cmd):

#         if not self.ser:
#             return

#         try:
#             packet = cmd + "\n"

#             self.ser.write(packet.encode())

#             self.log(f"[TX] {cmd}")

#         except Exception as e:
#             self.log(f"[UART TX ERROR] {e}")

#     def read_thread(self):

#         buffer = ""

#         while self.running:

#             try:

#                 if self.ser.in_waiting:

#                     data = self.ser.read(
#                         self.ser.in_waiting
#                     ).decode(errors="ignore")

#                     buffer += data

#                     while "\n" in buffer:

#                         line, buffer = buffer.split("\n", 1)

#                         line = line.strip()

#                         if line:

#                             self.log(f"[RX] {line}")

#                             self.data_callback(line)

#             except Exception as e:

#                 self.log(f"[UART RX ERROR] {e}")

#             time.sleep(0.01)



import serial
import threading
import time


class UARTHandler:

    def __init__(self, log_callback, data_callback):

        self.ser = None
        self.running = False

        self.log = log_callback
        self.data_callback = data_callback

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

            # clear old boot garbage
            self.ser.reset_input_buffer()
            self.ser.reset_output_buffer()

            self.running = True

            threading.Thread(
                target=self.read_thread,
                daemon=True
            ).start()

            self.log(f"[UART] Connected {port}")

            return True

        except Exception as e:

            self.log(f"[UART ERROR] {e}")

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

        self.log("[UART] Disconnected")

    # ─────────────────────────────────────────────
    # SEND COMMAND
    # ─────────────────────────────────────────────
    def send_command(self, cmd):

        if not self.ser:
            return

        try:

            packet = cmd + "\n"

            self.ser.write(packet.encode())

            self.log(f"[TX] {cmd}")

        except Exception as e:

            self.log(f"[UART TX ERROR] {e}")

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

                            # chỉ giữ log gần nhất
                            self.log(f"[RX] {line}")

                            # parser callback
                            self.data_callback(line)

            except Exception as e:

                self.log(f"[UART RX ERROR] {e}")

            # giảm CPU + tránh spam GUI
            time.sleep(0.03)