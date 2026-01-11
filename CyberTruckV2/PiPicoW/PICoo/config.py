# config.py
class Config:
    # ================= UART Jetson <-> Pico =================
    UART_ID = 0
    UART_BAUDRATE = 115200
    UART_TX_PIN = 17  # TX net en tu PCB -> GP17
    UART_RX_PIN = 16  # RX net en tu PCB -> GP16

    # ================= Motores (L298N) =================
    # Formato: (IN1, IN2, PWM, invert)
    # OJO: FL/FR/RL/RR puede requerir re-mapeo según tu cableado real
    MOTORS = {
        "FL": (7, 8, 6,  False),  # Motor A: AIN1=GP7, AIN2=GP8, PWMA=GP6
        "FR": (3, 4, 2,  True),   # Motor B: BIN1=GP3, BIN2=GP4, PWMB=GP2
        "RL": (13, 14, 15, False),# Motor C: CIN1=GP13, CIN2=GP14, PWMC=GP15
        "RR": (11, 12, 10, True), # Motor D: DIN1=GP11, DIN2=GP12, PWMD=GP10
    }

    MOTOR_PWM_FREQ = 1000
    LOOP_HZ = 20
    LOOP_DELAY = 1 / LOOP_HZ
    FAILSAFE_MS = 2000

    # ================= Servos =================
    SERVO1_PIN = 19  # SERVO1 net -> GP19
    SERVO2_PIN = 18  # SERVO2 net -> GP18

    SERVO_MIN_US = 500
    SERVO_MAX_US = 2500

    # ================= Ultrasonido =================
    TRIG_PIN = 20     # TRIG net -> GP20
    ECHO_PIN = 21     # ECHO net -> GP21
    US_TIMEOUT_US = 30000

    # ================= IMU (MPU-6050 por I2C) =================
    I2C_ID = 1
    IMU_SDA = 26      # SDA net -> GP26
    IMU_SCL = 27      # SCL net -> GP27
    I2C_FREQ = 400000
