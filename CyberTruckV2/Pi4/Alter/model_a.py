import time
import re
import threading
from serial_comm import SerialComm
PWM_MIN = 0
PWM_MAX = 100


def clamp(v, lo, hi):
    return max(lo, min(hi, v))

class ModelA(threading.Thread):

    def __init__(self, serial_device):
        super().__init__(daemon=True)
        self.serial_device = serial_device
        self.stop_event = threading.Event()
        self.speed = 50  

    def send_command(self, pwm1,pwm2, traction, Actv=0):
        pwm1 = clamp(int(pwm1), PWM_MIN, PWM_MAX)
        pwm2 = clamp(int(pwm2), PWM_MIN, PWM_MAX)
        self.serial_device.send(f"{pwm1},{pwm2},{traction},{Actv}\n")

    def receive_distance(self):
        raw = self.serial_device.receive()
        if not raw:
            return None
        line = str(raw).strip()
        m = re.search(r"DIST:\s*([0-9]+(?:\.[0-9]+)?)\s*cm", line)
        if m:
            try:
                return float(m.group(1))
            except ValueError:
                return None
        return None

    def stop_movement(self):
        self.send_command(0, 0, 0, 0)

    def stop(self):
        self.stop_event.set()

def run(self):
        print("==== MODEL A (AUTÓNOMO) ====")
        try:
            while not self.stop_event.is_set():
                distance = self.receive_distance()
                if distance is not None:
                    print(f"Recibido: {distance:.1f} cm")
                    if distance < 20:
                        self.send_command(0, 0, 0, 1)
                    else:
                        self.send_command(50, 0, 0, 0)
                else:
                    self.send_command(50, 0, 0, 0)
                self._sleep_until(0.1)
        except KeyboardInterrupt:
            print("ModelA: interrumpido por usuario.")
        finally:
            self.stop_movement()
            print("ModelA: stop.")

if __name__ == "__main__":
    serial_device = SerialComm(port="/dev/serial0", baudrate=115200, timeout=0.1)
    model_a = ModelA(serial_device)
    model_a.run()