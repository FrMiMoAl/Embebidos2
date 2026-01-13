# main_pico.py — RC Ambulance Pico listo para Jetson (teleop/auto + smoothing + failsafe brake)
import time
from config import Config
from protocol import UARTProtocol
from sensors import Ultrasonido
from gyro_controller import GyroController
from omni_drive import motors_from_config, OmniDrive

from machine import Pin, PWM

# ---------------- Servo helper ----------------
class Servo:
    def __init__(self, pin, min_us=500, max_us=2500, freq=50):
        self.pwm = PWM(Pin(pin))
        self.pwm.freq(freq)
        self.period_us = int(1_000_000 / freq)
        self.min_us = int(min_us)
        self.max_us = int(max_us)
        self._us = (self.min_us + self.max_us) // 2
        self.write_us(self._us)

    def _clamp(self, x, a, b):
        return a if x < a else b if x > b else x

    def write_us(self, us):
        us = int(self._clamp(us, self.min_us, self.max_us))
        duty = int(us * 65535 / self.period_us)
        self.pwm.duty_u16(duty)

    def set_angle(self, deg):
        deg = self._clamp(float(deg), 0.0, 180.0)
        us = self.min_us + (self.max_us - self.min_us) * (deg / 180.0)
        self.write_us(us)


def clamp(x, a, b):
    return a if x < a else b if x > b else x

def approach(cur, target, step):
    # limita cuánto puede cambiar por ciclo (slew-rate limiter)
    if target > cur:
        return min(cur + step, target)
    if target < cur:
        return max(cur - step, target)
    return cur


def main():
    uart = UARTProtocol(Config.UART_ID, Config.UART_BAUDRATE, Config.UART_TX_PIN, Config.UART_RX_PIN)

    # Sensores
    usonic = Ultrasonido(Config.TRIG_PIN, Config.ECHO_PIN, timeout_us=Config.US_TIMEOUT_US)

    # Motores (según tu omni_drive.py)
    FL, FR, RL, RR = motors_from_config()
    drive = OmniDrive(FL, FR, RL, RR)

    # IMU (si falla, seguimos sin yaw)
    gyro = None
    try:
        gyro = GyroController(
            i2c_id=Config.I2C_ID,
            scl=Config.IMU_SCL,
            sda=Config.IMU_SDA,
            freq=Config.I2C_FREQ
        )
    except Exception as e:
        print("⚠️ IMU no disponible:", e)

    # Servos
    servo1 = Servo(Config.SERVO1_PIN, Config.SERVO_MIN_US, Config.SERVO_MAX_US)
    servo2 = Servo(Config.SERVO2_PIN, Config.SERVO_MIN_US, Config.SERVO_MAX_US)
    servo1.set_angle(90)
    servo2.set_angle(90)

    # Estado
    mode = "teleop"  # teleop/auto
    vx_t = vy_t = w_t = 0          # targets
    vx = vy = w = 0                # comandos suavizados

    # Ajustes de suavizado (sube/baja según tu chasis)
    SLEW_V = 8     # max cambio por ciclo para vx/vy
    SLEW_W = 10    # max cambio por ciclo para w

    # Telemetría
    tel_hz = 10
    tel_period_ms = int(1000 / tel_hz)
    last_tel = time.ticks_ms()

    print("✅ Pico listo (UART + OmniDrive + Servos + US + IMU opcional).")

    while True:
        # -------- RX --------
        msg = uart.recv()
        if msg and msg["type"] == "CMD":
            d = msg["data"]

            # modo (acordado)
            if "mode" in d:
                mode = d["mode"]

            # setpoints
            vx_t = int(d.get("vx", 0))
            vy_t = int(d.get("vy", 0))
            w_t  = int(d.get("w",  0))

            # servos
            if "s1" in d: servo1.set_angle(d["s1"])
            if "s2" in d: servo2.set_angle(d["s2"])

            # e-stop
            if int(d.get("stop", 0)) == 1:
                vx_t = vy_t = w_t = 0
                drive.brake()

        # -------- FAILSAFE --------
        if not uart.link_alive(Config.FAILSAFE_MS):
            vx_t = vy_t = w_t = 0
            drive.brake()  # más seguro que coast

        # -------- SUAVIZADO (setpoints suaves) --------
        vx = approach(vx, vx_t, SLEW_V)
        vy = approach(vy, vy_t, SLEW_V)
        w  = approach(w,  w_t,  SLEW_W)

        drive.drive(vx, vy, w)

        # -------- TELEMETRÍA --------
        now = time.ticks_ms()
        if time.ticks_diff(now, last_tel) >= tel_period_ms:
            last_tel = now

            dist = usonic.distancia_cm()
            yaw = gyro.update() if gyro else None

            uart.send("TEL", {
                "mode": mode,
                "vx": vx, "vy": vy, "w": w,
                "dist_cm": dist,
                "yaw_deg": yaw,
                "link_ms": time.ticks_diff(time.ticks_ms(), uart.last_rx_ms)
            })

        time.sleep(Config.LOOP_DELAY)


if __name__ == "__main__":
    main()
