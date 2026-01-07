from config import Config
from protocol import UARTProtocol
from sensors import Ultrasonido
from actuators import OmniDrive, Servo
from gyro_controller import GyroController
import time

def now_ms():
    try:
        return time.ticks_ms()
    except AttributeError:
        return int(time.time() * 1000)

# Inicialización
uart = UARTProtocol(Config.UART_ID, Config.UART_BAUDRATE, Config.TX_PIN, Config.RX_PIN)
uart.last_heartbeat = now_ms()
sensor_us = Ultrasonido(Config.TRIG_PIN, Config.ECHO_PIN)
chassis = OmniDrive(Config.MOTORS)
gyro = GyroController(scl=Config.IMU_SCL, sda=Config.IMU_SDA)

# Gimbal (2 Servos)
gimbal_pan = Servo(Config.SERVO_PAN_PIN)
gimbal_tilt = Servo(Config.SERVO_TILT_PIN)

print("Robot Omni-Gimbal listo...")

while True:
    # 1. Leer Sensores y enviar por UART
    dist = sensor_us.distancia_cm()
    yaw = gyro.update()
    uart.send("TELEMETRY", {"dist": dist, "yaw": yaw})
    
    # 2. Recibir Comandos
    # El comando esperado es: CMD|{"vx":50, "vy":0, "w":0, "pan":90, "tilt":45}|CHECKSUM
    msg = uart.receive()
    if msg and msg.get("type") == "CMD":
        data = msg.get("data", {})
        # actualizar heartbeat al recibir comando
        uart.last_heartbeat = now_ms()
        
        # Control de movimiento
        vx = data.get("vx", 0)
        vy = data.get("vy", 0)
        w = data.get("w", 0)
        chassis.drive_complex(vx, vy, w)
        
        # Control de Gimbal (Los 2 ángulos adicionales)
        if "pan" in data: gimbal_pan.set_angle(data["pan"])
        if "tilt" in data: gimbal_tilt.set_angle(data["tilt"])
        
    # 3. Seguridad: Stop si se pierde la conexión (2 segundos sin datos)
    if now_ms() - uart.last_heartbeat > 2000:
        chassis.stop()
        
    time.sleep(Config.LOOP_DELAY)