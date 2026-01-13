# main.py — Test autónomo de motores (L298N) usando Config.py
from machine import Pin, PWM
import time
from config import Config

# =======================
# CLASE MOTOR L298N
# =======================
class Motor:
    def __init__(self, in1, in2, pwm_pin, invert=False):
        self.in1 = Pin(in1, Pin.OUT, value=0)
        self.in2 = Pin(in2, Pin.OUT, value=0)
        self.pwm = PWM(Pin(pwm_pin))
        self.pwm.freq(Config.MOTOR_PWM_FREQ)
        self.pwm.duty_u16(0)
        self.invert = invert

    def _apply(self, forward, duty):
        duty = max(0, min(65535, duty))
        if self.invert:
            forward = not forward
        if forward:
            self.in1.value(1)
            self.in2.value(0)
        else:
            self.in1.value(0)
            self.in2.value(1)
        self.pwm.duty_u16(duty)

    def forward(self, duty=40000):
        self._apply(True, duty)

    def reverse(self, duty=40000):
        self._apply(False, duty)

    def brake(self):
        self.in1.value(1)
        self.in2.value(1)
        self.pwm.duty_u16(0)

    def stop(self):
        self.in1.value(0)
        self.in2.value(0)
        self.pwm.duty_u16(0)


# =======================
# UTILIDADES
# =======================
def led_blink(n=3, t=0.1):
    try:
        led = Pin("LED", Pin.OUT)
        for _ in range(n):
            led.on(); time.sleep(t)
            led.off(); time.sleep(t)
    except:
        pass


# =======================
# SECUENCIA DE PRUEBA
# =======================
def test_motors():
    led_blink()
    motors = {}
    for name, (in1, in2, pwm, inv) in Config.MOTORS.items():
        motors[name] = Motor(in1, in2, pwm, inv)

    duty = 45000
    delay = 1.5

    for i in range(3):
        print(f"🔹 Ciclo {i+1}/3: Avance")
        for m in motors.values():
            m.forward(duty)
        time.sleep(delay)

        print("🔹 Freno")
        for m in motors.values():
            m.brake()
        time.sleep(0.6)

        print("🔹 Reversa")
        for m in motors.values():
            m.reverse(duty)
        time.sleep(delay)

        print("🔹 Freno")
        for m in motors.values():
            m.brake()
        time.sleep(0.6)

    # Detener todo
    for m in motors.values():
        m.stop()
    print("✅ Prueba completada")
    while True:
        led_blink(n=1, t=0.15)
        time.sleep(0.7)


# =======================
# EJECUCIÓN PRINCIPAL
# =======================
if __name__ == "__main__":
    test_motors()
