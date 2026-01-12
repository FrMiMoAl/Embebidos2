# main_ultra_servos_test.py
# Prueba: Ultrasonido (HC-SR04) + 2 servos
# Usa: config.py + sensors.py

import time
from machine import Pin, PWM
from config import Config
from sensors import Ultrasonido

# ---------------- Servo helper ----------------
class Servo:
    """
    Servo estándar 50Hz:
      - pulso ~500..2500 us (configurable)
      - ángulo 0..180
    """
    def __init__(self, pin, min_us=500, max_us=2500, freq=50):
        self.pwm = PWM(Pin(pin))
        self.pwm.freq(freq)
        self.freq = freq
        self.period_us = int(1_000_000 / freq)
        self.min_us = int(min_us)
        self.max_us = int(max_us)
        self._us = (self.min_us + self.max_us) // 2
        self.write_us(self._us)

    def _clamp(self, x, a, b):
        return a if x < a else b if x > b else x

    def write_us(self, us):
        us = int(self._clamp(us, self.min_us, self.max_us))
        self._us = us
        duty = int(us * 65535 / self.period_us)
        self.pwm.duty_u16(duty)

    def write_angle(self, deg):
        deg = self._clamp(float(deg), 0.0, 180.0)
        us = self.min_us + (self.max_us - self.min_us) * (deg / 180.0)
        self.write_us(us)

    def deinit(self):
        try:
            self.pwm.deinit()
        except:
            pass


# ---------------- Ultrasonido helper ----------------
def median(vals):
    vals = sorted(vals)
    n = len(vals)
    return vals[n // 2]

def read_distance_cm(usonic, samples=3, delay_ms=25):
    """
    Lee varias veces, ignora -1 (timeout) y devuelve mediana.
    """
    good = []
    for _ in range(samples):
        d = usonic.distancia_cm()
        if d != -1:
            good.append(d)
        time.sleep_ms(delay_ms)
    if not good:
        return None
    return median(good)


# ---------------- Main test ----------------
def main():
    print("🔧 Test Ultrasonido + 2 Servos")
    print("Servos:", Config.SERVO1_PIN, Config.SERVO2_PIN, "min/max(us)=", Config.SERVO_MIN_US, Config.SERVO_MAX_US)
    print("Ultrasonido TRIG/ECHO:", Config.TRIG_PIN, Config.ECHO_PIN, "timeout(us)=", Config.US_TIMEOUT_US)

    # Instancias desde tu config
    servo1 = Servo(Config.SERVO1_PIN, Config.SERVO_MIN_US, Config.SERVO_MAX_US, freq=50)  # :contentReference[oaicite:2]{index=2}
    servo2 = Servo(Config.SERVO2_PIN, Config.SERVO_MIN_US, Config.SERVO_MAX_US, freq=50)  # :contentReference[oaicite:3]{index=3}
    usonic = Ultrasonido(Config.TRIG_PIN, Config.ECHO_PIN, timeout_us=Config.US_TIMEOUT_US)  # :contentReference[oaicite:4]{index=4} :contentReference[oaicite:5]{index=5}

    # Centrar servos
    servo1.write_angle(90)
    servo2.write_angle(90)
    time.sleep_ms(500)

    print("\n➡️ Barrido: servo1 0→180→0 y servo2 al revés. Ctrl+C para parar.\n")

    deg = 0
    step = 5
    direction = 1

    last_print = time.ticks_ms()

    try:
        while True:
            # mover servos
            servo1.write_angle(deg)
            servo2.write_angle(180 - deg)

            # ultrasonido (no cada loop para que no se trabe)
            now = time.ticks_ms()
            if time.ticks_diff(now, last_print) >= 250:  # 4 Hz
                last_print = now
                dist = read_distance_cm(usonic, samples=3, delay_ms=15)
                if dist is None:
                    print("deg=", deg, " | dist= TIMEOUT (-1)")
                else:
                    print("deg=", deg, " | dist=", dist, "cm")

            # actualizar ángulo
            deg += direction * step
            if deg >= 180:
                deg = 180
                direction = -1
            elif deg <= 0:
                deg = 0
                direction = 1

            time.sleep_ms(40)  # velocidad de barrido

    except KeyboardInterrupt:
        print("\n🛑 Stop por usuario.")
    finally:
        # deja servos centrados
        try:
            servo1.write_angle(90)
            servo2.write_angle(90)
            time.sleep_ms(300)
        except:
            pass
        servo1.deinit()
        servo2.deinit()

main()
