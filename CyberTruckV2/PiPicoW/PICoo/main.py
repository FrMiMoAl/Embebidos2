# main.py
import time
from config import Config
from protocol import UARTProtocol
from sensors import Ultrasonido
from actuators import OmniDrive, Servo
from gyro_controller import GyroController

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

    # posiciones iniciales
    servo1.set_angle(90)
    servo2.set_angle(90)
    chassis.stop()

    print("✅ RC Ambulance Pico listo (UART+Motores+Servos+US+IMU).")

    last_tel = time.ticks_ms()
    tel_period_ms = int(1000 / Config.LOOP_HZ)

    while True:
        # ====== RX comandos ======
        msg = uart.recv()
        if msg and msg["type"] == "CMD":
            d = msg["data"]

            vx = d.get("vx", 0)
            vy = d.get("vy", 0)
            w  = d.get("w", 0)
            chassis.drive(vx, vy, w)

            if "s1" in d: servo1.set_angle(d["s1"])
            if "s2" in d: servo2.set_angle(d["s2"])

            # comando de emergencia
            if d.get("stop", 0) == 1:
                chassis.stop()

        # ====== FAILSAFE ======
        if not uart.link_alive(Config.FAILSAFE_MS):
            chassis.stop()

        # ====== TELEMETRÍA ======
        now = time.ticks_ms()
        if time.ticks_diff(now, last_tel) >= tel_period_ms:
            last_tel = now
            dist = sensor_us.distancia_cm()
            yaw = gyro.update()

            uart.send("TEL", {
                "dist_cm": dist,
                "yaw_deg": yaw,
                "link_ms": time.ticks_diff(time.ticks_ms(), uart.last_rx_ms)
            })

        time.sleep(Config.LOOP_DELAY)

if __name__ == "__main__":
    main()
