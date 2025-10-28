import threading, time
from math import copysign

PWM_MIN, PWM_MAX = -100, 100
SERVO_MIN, SERVO_MAX, SERVO_CENTER = 30, 70, 50

FWD_SPEED = 60
TURN_SPEED = 70
DIST_THRESH_CM = 20
TURN_SEC_PER_DEG = 0.008   # CALIBRAR

LOOP_HZ = 30
DT = 1.0 / LOOP_HZ

def clamp(v, lo, hi): return max(lo, min(hi, v))

class ModelA(threading.Thread):
    """
    Avanza hasta detectar objeto (distancia llega por UART desde la Pico),
    gira 180° en el lugar y sigue. Permite request_turn(deg) no bloqueante.
    """
    def __init__(self, ser):
        super().__init__(daemon=True)
        self.ser = ser
        self.stop_event = threading.Event()
        self.state = "forward"
        self.turn_end_t = 0.0
        self.turn_dir = 1
        self.pending_turn_deg = 0.0

    def stop(self): self.stop_event.set()
    def stopped(self): return self.stop_event.is_set()

    def send(self, p1, p2, s):
        p1, p2 = clamp(int(p1), PWM_MIN, PWM_MAX), clamp(int(p2), PWM_MIN, PWM_MAX)
        s = clamp(int(s), SERVO_MIN, SERVO_MAX)
        self.ser.send(f"{p1},{p2},{s}")

    def request_turn(self, degrees):
        self.pending_turn_deg += degrees

    def _start_turn(self, degrees):
        self.turn_dir = 1 if degrees >= 0 else -1
        self.turn_end_t = time.monotonic() + abs(degrees) * TURN_SEC_PER_DEG
        self.state = "turning"
        print(f"Solicitado giro: {degrees}°  (dur={abs(degrees)*TURN_SEC_PER_DEG:.2f}s)")

    def _maybe_parse_distance(self, line):
        if not line: return None
        line = line.strip()
        num = ""
        for ch in line:
            if ch.isdigit() or ch in ".-": num += ch
            elif num: break
        try: return float(num)
        except: return None

    def run(self):
        print("==== MODEL A (AUTÓNOMO) ====")
        next_tick = time.monotonic()
        while not self.stopped():
            # giros solicitados
            if self.state == "forward" and abs(self.pending_turn_deg) > 0.1:
                deg = self.pending_turn_deg
                self.pending_turn_deg = 0.0
                self._start_turn(deg)

            if self.state == "forward":
                dist = self._maybe_parse_distance(self.ser.receive())
                if dist is not None:
                    print(f"[RX] Distancia: {dist} cm")
                    if dist <= DIST_THRESH_CM:
                        print("Objeto detectado → giro 180°")
                        self._start_turn(180)
                self.send(FWD_SPEED, FWD_SPEED, SERVO_CENTER)

            elif self.state == "turning":
                if time.monotonic() >= self.turn_end_t:
                    self.state = "forward"
                pwm = TURN_SPEED * self.turn_dir
                self.send(pwm, -pwm, SERVO_CENTER)

            next_tick += DT
            t = next_tick - time.monotonic()
            if t > 0: time.sleep(t)
            else: next_tick = time.monotonic()

        self.send(0,0,SERVO_CENTER)
        print("ModelA: stop.")
