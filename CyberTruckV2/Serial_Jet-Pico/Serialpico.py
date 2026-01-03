from machine import Pin, PWM, UART, I2C
import time
import struct
import json

# ================= CONFIGURACIÓN =================
class Config:
    UART_BAUDRATE = 115200
    UART_TX = 16
    UART_RX = 17
    LOOP_DELAY = 0.05  # 20 Hz
    TIMEOUT_MS = 5000
    
# ================= UART CON PROTOCOLO =================
class UARTProtocol:
    def __init__(self, uart_id=0, baudrate=115200, tx_pin=16, rx_pin=17):
        self.uart = UART(uart_id, baudrate=baudrate, tx=Pin(tx_pin), rx=Pin(rx_pin))
        self.buffer = ""
        self.last_heartbeat = time.ticks_ms()
        
    def send_message(self, msg_type, data):
        """Envía mensaje con checksum"""
        payload = json.dumps(data)
        checksum = sum(payload.encode()) & 0xFF
        message = f"{msg_type}|{payload}|{checksum:02X}\n"
        self.uart.write(message)
    
    def read_message(self):
        """Lee y valida mensajes"""
        if not self.uart.any():
            return None
        
        line = self.uart.readline()
        if not line:
            return None
            
        line = line.decode().strip()
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
        self.last_heartbeat = time.ticks_ms()
        return {"type": msg_type, "data": data}
    
    def is_connected(self):
        """Verifica si hay conexión activa"""
        return time.ticks_diff(time.ticks_ms(), self.last_heartbeat) < Config.TIMEOUT_MS

# ================= SENSOR ULTRASONIDO =================
class Ultrasonic:
    def __init__(self, trig_pin=21, echo_pin=20):
        self.trig = Pin(trig_pin, Pin.OUT)
        self.echo = Pin(echo_pin, Pin.IN)
        self.last_distance = 0
        
    def measure(self):
        """Mide distancia"""
        self.trig.low()
        time.sleep_us(2)
        self.trig.high()
        time.sleep_us(10)
        self.trig.low()
        
        while not self.echo.value():
            pass
        start = time.ticks_us()
        
        while self.echo.value():
            pass
        end = time.ticks_us()
        
        duration = time.ticks_diff(end, start)
        distance = (duration * 0.0343) / 2
        
        if 2 <= distance <= 400:
            self.last_distance = round(distance, 2)
        
        return self.last_distance

# ================= IMU (MPU6050) =================
class IMU:
    def __init__(self, sda_pin=26, scl_pin=27):
        self.i2c = I2C(1, sda=Pin(sda_pin), scl=Pin(scl_pin))
        self.MPU_ADDR = 0x68
        self.i2c.writeto_mem(self.MPU_ADDR, 0x6B, b'\x00')  # Wake up
        time.sleep_ms(100)
    
    def read(self):
        """Lee acelerómetro y giroscopio"""
        # Leer acelerómetro
        accel_data = self.i2c.readfrom_mem(self.MPU_ADDR, 0x3B, 6)
        ax, ay, az = struct.unpack(">hhh", accel_data)
        
        # Leer giroscopio
        gyro_data = self.i2c.readfrom_mem(self.MPU_ADDR, 0x43, 6)
        gx, gy, gz = struct.unpack(">hhh", gyro_data)
        
        return {
            "ax": round(ax / 16384.0, 3),
            "ay": round(ay / 16384.0, 3),
            "az": round(az / 16384.0, 3),
            "gx": round(gx / 131.0, 2),
            "gy": round(gy / 131.0, 2),
            "gz": round(gz / 131.0, 2)
        }

# ================= SERVO CONTROLLER =================
class Servo:
    def __init__(self, pin, min_angle=0, max_angle=180):
        self.pwm = PWM(Pin(pin))
        self.pwm.freq(50)
        self.min_angle = min_angle
        self.max_angle = max_angle
        self.current_angle = 90
        self.set_angle(90)
    
    def set_angle(self, angle):
        """Establece ángulo del servo"""
        angle = max(self.min_angle, min(self.max_angle, angle))
        duty = int((angle / 180) * 65535 / 20 + 3277)
        self.pwm.duty_u16(duty)
        self.current_angle = angle
        
# ================= MOTOR CONTROLLER =================
class Motor:
    def __init__(self, in1_pin, in2_pin, pwm_pin, name="Motor"):
        self.in1 = Pin(in1_pin, Pin.OUT)
        self.in2 = Pin(in2_pin, Pin.OUT)
        self.pwm = PWM(Pin(pwm_pin))
        self.pwm.freq(1000)
        self.name = name
        self.current_speed = 0
        self.stop()
    
    def set_speed(self, speed):
        """Establece velocidad (-100 a 100)"""
        speed = max(-100, min(100, speed))
        
        if speed > 0:
            self.in1.value(1)
            self.in2.value(0)
        elif speed < 0:
            self.in1.value(0)
            self.in2.value(1)
        else:
            self.in1.value(0)
            self.in2.value(0)
        
        self.pwm.duty_u16(int(abs(speed) * 655.35))
        self.current_speed = speed
    
    def stop(self):
        """Detiene el motor"""
        self.set_speed(0)

# ================= ROBOT CONTROLLER =================
class RobotController:
    def __init__(self):
        # Comunicación
        self.uart = UARTProtocol(0, Config.UART_BAUDRATE, Config.UART_TX, Config.UART_RX)
        
        # Sensores
        self.ultrasonic = Ultrasonic(21, 20)
        self.imu = IMU(26, 27)
        
        # Actuadores
        self.servos = {
            "S1": Servo(19),
            "S2": Servo(18)
        }
        
        self.motors = {
            "M1": Motor(2, 3, 4, "Motor1"),
            "M2": Motor(5, 6, 7, "Motor2"),
            "M3": Motor(8, 9, 10, "Motor3"),
            "M4": Motor(11, 12, 13, "Motor4")
        }
        
        self.status_led = Pin(25, Pin.OUT)
        self.emergency_stop = False
        
    def read_sensors(self):
        """Lee todos los sensores"""
        distance = self.ultrasonic.measure()
        imu_data = self.imu.read()
        
        return {
            "distance": distance,
            "imu": imu_data,
            "connected": self.uart.is_connected(),
            "emergency": self.emergency_stop
        }
    
    def process_command(self, cmd):
        """Procesa comandos recibidos"""
        if not cmd or cmd["type"] != "CMD":
            return
        
        data = cmd["data"]
        
        # Emergency stop
        if data.get("STOP"):
            self.emergency_stop = True
            self.stop_all()
            return
        
        if data.get("RESUME"):
            self.emergency_stop = False
            return
        
        if self.emergency_stop:
            return
        
        # Procesar motores
        for motor_id, motor in self.motors.items():
            if motor_id in data:
                motor.set_speed(data[motor_id])
        
        # Procesar servos
        for servo_id, servo in self.servos.items():
            if servo_id in data:
                servo.set_angle(data[servo_id])
    
    def stop_all(self):
        """Detiene todos los actuadores"""
        for motor in self.motors.values():
            motor.stop()
        for servo in self.servos.values():
            servo.set_angle(90)
    
    def send_status(self):
        """Envía estado del robot"""
        sensor_data = self.read_sensors()
        self.uart.send_message("SENS", sensor_data)
    
    def run(self):
        """Loop principal"""
        print("Robot iniciado")
        self.status_led.value(1)
        
        while True:
            # Recibir comandos
            cmd = self.uart.read_message()
            if cmd:
                self.process_command(cmd)
            
            # Enviar sensores
            self.send_status()
            
            # LED de estado
            self.status_led.toggle()
            
            # Verificar conexión
            if not self.uart.is_connected() and not self.emergency_stop:
                self.emergency_stop = True
                self.stop_all()
            
            time.sleep(Config.LOOP_DELAY)

# ================= INICIO =================
if __name__ == "__main__":
    robot = RobotController()
    robot.run()