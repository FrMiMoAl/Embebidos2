# main.py (Pico) - mode teleop/auto + failsafe + rampa ligera en AUTO
import time
from config import Config
from protocol import UARTProtocol
from sensors import Ultrasonido
from actuators import OmniDrive, Servo
from gyro_controller import GyroController

def clamp(v, a, b):
    return a if v < a else b if v > b else v

def slew_to(current: float, target: float, step: float) -> float:
    if current < target:
        return min(current + step, target)
    if current > target:
        return max(current - step, target)
    return current

def main():
    uart = UARTProtocol(Config.UART_ID, Config.UART_BAUDRATE, Config.UART_TX_PIN, Config.UART_RX_PIN)

    sensor_us = Ultrasonido(Config.TRIG_PIN, Config.ECHO_PIN, timeout_us=Config.US_TIMEOUT_US)
    chassis = OmniDrive(Config.MOTORS, pwm_freq=Config.MOTOR_PWM_FREQ)

    gyro = GyroController(
        i2c_id=Config.I2C_ID,
        scl=Config.IMU_SCL,
        sda=Config.IMU_SDA,
        freq=Config.I2C_FREQ
    )

    servo1 = Servo(Config.SERVO1_PIN, min_us=Config.SERVO_MIN_US, max_us=Config.SERVO_MAX_US)
    servo2 = Servo(Config.SERVO2_PIN, min_us=Config.SERVO_MIN_US, max_us=Config.SERVO_MAX_US)

    servo1.set_angle(90)
    servo2.set_angle(90)
    chassis.stop()

    # estado actual (para rampa en auto)
    mode = "teleop"
    vx_o, vy_o, w_o = 0.0, 0.0, 0.0

    # rampa en AUTO: paso por ciclo (20Hz)
    # 100 unidades en ~0.7s => step ~7 por ciclo
    auto_step_v = 7.0
    auto_step_w = 10.0

    print("✅ Pico listo: modo teleop/auto + sensores + failsafe.")

    last_tel = time.ticks_ms()
    tel_period_ms = int(1000 / Config.LOOP_HZ)

    while True:
        # ===== RX =====
        msg = uart.receive()
        if msg and msg["type"] == "CMD":
            d = msg["data"]

            mode = str(d.get("mode", mode)).lower()
            mode = "auto" if mode == "auto" else "teleop"

            stop = 1 if int(d.get("stop", 0)) == 1 else 0

            vx_t = float(clamp(d.get("vx", 0), -100, 100))
            vy_t = float(clamp(d.get("vy", 0), -100, 100))
            w_t  = float(clamp(d.get("w",  0), -100, 100))

            if stop == 1:
                vx_o, vy_o, w_o = 0.0, 0.0, 0.0
                chassis.stop()
            else:
                if mode == "auto":
                    vx_o = slew_to(vx_o, vx_t, auto_step_v)
                    vy_o = slew_to(vy_o, vy_t, auto_step_v)
                    w_o  = slew_to(w_o,  w_t,  auto_step_w)
                    chassis.drive(int(vx_o), int(vy_o), int(w_o))
                else:
                    vx_o, vy_o, w_o = vx_t, vy_t, w_t
                    chassis.drive(int(vx_o), int(vy_o), int(w_o))

            if "s1" in d: servo1.set_angle(d["s1"])
            if "s2" in d: servo2.set_angle(d["s2"])

        # ===== FAILSAFE si se pierde UART =====
        if time.ticks_diff(time.ticks_ms(), uart.last_heartbeat) > Config.FAILSAFE_MS:
            chassis.stop()
            vx_o, vy_o, w_o = 0.0, 0.0, 0.0

        # ===== TELEMETRÍA =====
        now = time.ticks_ms()
        if time.ticks_diff(now, last_tel) >= tel_period_ms:
            last_tel = now
            dist = sensor_us.distancia_cm()
            yaw = gyro.update()

            uart.send("TEL", {
                "mode": mode,
                "dist_cm": dist,
                "yaw_deg": yaw,
                "vx": int(vx_o),
                "vy": int(vy_o),
                "w":  int(w_o),
            })

        time.sleep(Config.LOOP_DELAY)

if __name__ == "__main__":
    main()
