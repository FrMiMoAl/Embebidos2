class Config:
    # UART
    UART_ID = 0
    BAUDRATE = 115200
    TX_PIN = 16
    RX_PIN = 17
    
    # Motores (PWM, IN1, IN2)
    MOTORS = {
        "FL": (2, 3, 4),   # Front Left
        "FR": (5, 6, 7),   # Front Right
        "RL": (8, 9, 10),  # Rear Left
        "RR": (11, 12, 13) # Rear Right
    }
    
    # Servos Gimbal
    SERVO_PAN_PIN = 18
    SERVO_TILT_PIN = 19
    
    # Sensores
    TRIG_PIN = 21
    ECHO_PIN = 20
    IMU_SDA = 16 # Ajustado para no chocar con UART si es necesario
    IMU_SCL = 17
    
    LOOP_DELAY = 0.05  # 20Hz