import serial
import json
import time
from collections import deque

# ================= CONFIGURACIÓN =================
class Config:
    SERIAL_PORT = '/dev/ttyTHS1'
    BAUDRATE = 115200
    TIMEOUT = 1.0

# ================= PROTOCOLO UART =================
class UARTProtocol:
    def __init__(self, port, baudrate=115200, timeout=1.0):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.ser = serial.Serial(port, baudrate, timeout=timeout)
        self.connected = True
        print(f"Conectado a {port} @ {baudrate}")
        time.sleep(2)  # Esperar inicialización
    
    def send_message(self, msg_type, data):
        """Envía mensaje con checksum"""
        payload = json.dumps(data)
        checksum = sum(payload.encode()) & 0xFF
        message = f"{msg_type}|{payload}|{checksum:02X}\n"
        self.ser.write(message.encode())
    
    def read_message(self):
        """Lee y valida mensajes"""
        if not self.ser.in_waiting:
            return None
        
        line = self.ser.readline().decode().strip()
        if not line:
            return None
        
        # Formato: TIPO|{json}|CHECKSUM
        parts = line.split("|")
        if len(parts) != 3:
            return None
        
        msg_type, payload, checksum_rx = parts
        
        # Validar checksum
        checksum_calc = sum(payload.encode()) & 0xFF
        if checksum_calc != int(checksum_rx, 16):
            return None
        
        data = json.loads(payload)
        return {"type": msg_type, "data": data}
    
    def is_connected(self):
        """Verifica estado de conexión"""
        return self.connected and self.ser and self.ser.is_open

# ================= CONTROL DEL ROBOT =================
class RobotControl:
    def __init__(self, uart_protocol):
        self.uart = uart_protocol
        self.sensor_data = {}
        self.sensor_history = deque(maxlen=100)
        self.running = False
        self.emergency_stop = False
        
    def send_command(self, motors={}, servos={}):
        """Envía comando de control"""
        cmd = {}
        
        # Agregar motores (M1-M4: -100 a 100)
        for motor_id, speed in motors.items():
            speed = max(-100, min(100, speed))
            cmd[motor_id] = speed
        
        # Agregar servos (S1-S2: 0 a 180)
        for servo_id, angle in servos.items():
            angle = max(0, min(180, angle))
            cmd[servo_id] = angle
        
        if self.emergency_stop:
            cmd["STOP"] = True
        
        self.uart.send_message("CMD", cmd)
    
    def stop_all(self):
        """Detiene todos los actuadores"""
        self.emergency_stop = True
        self.send_command()
        print("EMERGENCY STOP activado")
    
    def resume(self):
        """Reanuda operación"""
        self.emergency_stop = False
        self.uart.send_message("CMD", {"RESUME": True})
        print("Operación reanudada")
    
    def update_sensors(self, sensor_msg):
        """Actualiza datos de sensores"""
        if sensor_msg and sensor_msg["type"] == "SENS":
            self.sensor_data = sensor_msg["data"]
            self.sensor_data['timestamp'] = time.time()
            self.sensor_history.append(self.sensor_data.copy())
    
    def get_distance(self):
        """Obtiene distancia del ultrasonido"""
        return self.sensor_data.get("distance", 0)
    
    def get_imu(self):
        """Obtiene datos del IMU"""
        return self.sensor_data.get("imu", {})
    
    def is_robot_connected(self):
        """Verifica si el robot responde"""
        return self.sensor_data.get("connected", False)

# ================= EJEMPLO DE CONTROL AUTÓNOMO =================
class AutonomousController:
    def __init__(self, robot_control):
        self.robot = robot_control
        self.mode = "manual"  # manual, auto, follow_wall
        
    def obstacle_avoidance(self):
        """Evita obstáculos simples"""
        distance = self.robot.get_distance()
        
        if distance < 20:
            # Obstáculo cerca - retroceder y girar
            self.robot.send_command(
                motors={"M1": -50, "M2": -50, "M3": -50, "M4": -50}
            )
            time.sleep(0.5)
            self.robot.send_command(
                motors={"M1": 50, "M2": -50, "M3": 50, "M4": -50}
            )
            time.sleep(0.7)
        elif distance < 40:
            # Obstáculo medio - reducir velocidad
            self.robot.send_command(
                motors={"M1": 40, "M2": 40, "M3": 40, "M4": 40}
            )
        else:
            # Camino libre - velocidad normal
            self.robot.send_command(
                motors={"M1": 70, "M2": 70, "M3": 70, "M4": 70}
            )
    
    def follow_wall(self):
        """Sigue una pared (ejemplo básico)"""
        distance = self.robot.get_distance()
        target_distance = 25  # cm de la pared
        
        error = distance - target_distance
        correction = int(error * 2)  # Ganancia proporcional simple
        
        left_speed = 60 + correction
        right_speed = 60 - correction
        
        self.robot.send_command(
            motors={
                "M1": left_speed,
                "M2": left_speed,
                "M3": right_speed,
                "M4": right_speed
            }
        )
    
    def run_mode(self):
        """Ejecuta el modo actual"""
        if self.mode == "auto":
            self.obstacle_avoidance()
        elif self.mode == "follow_wall":
            self.follow_wall()

# ================= MAIN =================
def main():
    print("=== Iniciando sistema de control ===")
    
    # Conectar UART
    uart = UARTProtocol(Config.SERIAL_PORT, Config.BAUDRATE)
    
    # Crear controladores
    robot = RobotControl(uart)
    auto = AutonomousController(robot)
    
    # Variables de control
    robot.running = True
    last_command_time = time.time()
    command_interval = 0.1  # 10 Hz
    
    print("Sistema activo - Presiona Ctrl+C para salir")
    
    while robot.running:
        # Leer sensores
        msg = uart.read_message()
        if msg:
            robot.update_sensors(msg)
            
            # Mostrar info cada 5 segundos
            if int(time.time()) % 5 == 0:
                distance = robot.get_distance()
                imu = robot.get_imu()
                print(f"Dist: {distance:.1f}cm | IMU: ax={imu.get('ax',0):.2f}")
        
        # Enviar comandos periódicamente
        current_time = time.time()
        if current_time - last_command_time >= command_interval:
            
            # MODO MANUAL - Ejemplo de control directo
            if auto.mode == "manual":
                robot.send_command(
                    motors={"M1": 60, "M2": 60, "M3": 60, "M4": 60},
                    servos={"S1": 90, "S2": 90}
                )
            
            # MODO AUTÓNOMO
            else:
                auto.run_mode()
            
            last_command_time = current_time
        
        # Verificar conexión
        if not robot.is_robot_connected():
            print("Robot desconectado")
            robot.stop_all()
        
        time.sleep(0.02)  # 50 Hz loop

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nSistema detenido")