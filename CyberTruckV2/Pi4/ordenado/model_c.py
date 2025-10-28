# model_c.py
import time
import threading

# --- Intenta usar un BaseModel compartido; si no existe, define uno mínimo ---
try:
    from model_base import BaseModel, clamp
    HAVE_SHARED_BASE = True
except Exception:
    HAVE_SHARED_BASE = False

    def clamp(v, lo, hi):
        return max(lo, min(hi, v))

    class BaseModel(threading.Thread):
        def __init__(self, ser):
            super().__init__(daemon=True)
            self.ser = ser
            self.stop_event = threading.Event()

        def stop(self):
            self.stop_event.set()

        def stopped(self):
            return self.stop_event.is_set()

        def send(self, pwm1, pwm2, servo):
            pwm1 = clamp(int(pwm1), -100, 100)
            pwm2 = clamp(int(pwm2), -100, 100)
            servo = clamp(int(servo), 30, 70)
            self.ser.send(f"{pwm1},{pwm2},{servo}")

# --- Constantes usadas por ModelC (idénticas a la versión que te funcionaba) ---
PWM_MIN, PWM_MAX = -100, 100
SERVO_MIN, SERVO_MAX = 30, 70
SERVO_CENTER = 50

LOOP_HZ = 30
DT = 1.0 / LOOP_HZ

# --- Utilidades ---
def mix_diff(speed, turn):
    left  = clamp(speed + turn, PWM_MIN, PWM_MAX)
    right = clamp(speed - turn, PWM_MIN, PWM_MAX)
    return int(left), int(right)

def servo_from_lx(lx):  # lx ∈ [-1..1]
    ang = int(round(SERVO_CENTER + 20 * lx))
    return clamp(ang, SERVO_MIN, SERVO_MAX)

# --- Clase principal: MISMA LÓGICA QUE TU VERSIÓN ANTERIOR ---
class ModelC(BaseModel):
    def __init__(self, ser, ps4):
        super().__init__(ser)
        self.ps4 = ps4

    def run(self):
        print("[ModelC] start")
        next_tick = time.monotonic()

        while not self.stopped():
            # Lee mando
            self.ps4.update()
            lx = self.ps4.get_axis(0)   # -1..1 (izq/der)
            ly = self.ps4.get_axis(1)   # -1..1 (arriba/abajo)

            # Mapas iguales a tu versión
            speed = int(round(-ly * 100))   # ly=-1 => +100 (adelante)
            turn  = int(round(lx * 100))    # -100..100
            left, right = mix_diff(speed, turn)
            servo = servo_from_lx(lx)

            # DEBUG
            print(f"[ModelC] LX={lx:.2f} LY={ly:.2f} -> L={left} R={right} S={servo}")

            # Enviar a la Pico
            self.send(left, right, servo)

            # Ritmo
            next_tick += DT
            sleep_t = next_tick - time.monotonic()
            if sleep_t > 0:
                time.sleep(sleep_t)
            else:
                next_tick = time.monotonic()

        # Salida segura
        self.send(0, 0, SERVO_CENTER)
        print("[ModelC] stop")
