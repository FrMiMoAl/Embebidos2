
# model_b.py
import threading
import time
from typing import Callable

# Este módulo representa tu "visión". Aquí puedes usar OpenCV, YOLO, etc.
# Debe producir ángulos de servo en [30..70] sin bloquear el programa.

SERVO_MIN, SERVO_MAX = 30, 70

def clamp(v, lo, hi): return max(lo, min(hi, v))

class VisionModule:
    def __init__(self, publish_servo: Callable[[int], None]):
        """
        publish_servo: función que recibe un int (ángulo 30..70) para actualizar el servo.
        En main_program.py se inyecta Motion.set_servo.
        """
        self.publish_servo = publish_servo
        self.stop_flag = False
        self.thread = None

    def start(self):
        def _loop():
            # Stub de demostración: barre el servo entre 40..60 cada 2s
            angle = 40
            step = +5
            while not self.stop_flag:
                self.publish_servo(int(clamp(angle, SERVO_MIN, SERVO_MAX)))
                angle += step
                if angle >= 60 or angle <= 40:
                    step *= -1
                time.sleep(0.5)
        self.thread = threading.Thread(target=_loop, daemon=True)
        self.thread.start()

    def stop(self):
        self.stop_flag = True
