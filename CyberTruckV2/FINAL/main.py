# main_control.py - TEST AUTOMÁTICO ACTIVADO
from omni_drive import Motor, OmniDrive
from gyro_controller import GyroController
from machine import UART, Pin
import time
import sys

# ==== Inicialización ====
print("\n" + "="*50)
print("🤖 CONTROL OMNI + GIROSCOPIO")
print("="*50 + "\n")

# Motores
print("Inicializando motores...")
m_fl = Motor(2, 3, 4)
m_fr = Motor(5, 6, 7)
m_rl = Motor(8, 9, 10)
m_rr = Motor(11, 12, 13)
robot = OmniDrive(m_fl, m_fr, m_rl, m_rr)
print("✅ Motores OK\n")

# Giroscopio
print("Inicializando giroscopio...")
try:
    gyro = GyroController(scl=17, sda=16)
    gyro_ok = True
    print("✅ Giroscopio OK\n")
except Exception as e:
    print(f"❌ Error: {e}\n")
    gyro_ok = False
    sys.exit()

# LED indicador
led = Pin(25, Pin.OUT)
led.value(1)

# ==== Control PID ====
class PIDController:
    def __init__(self, kp=2.0, ki=0.1, kd=0.5):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.integral = 0.0
        self.last_error = 0.0
        self.max_integral = 50
    
    def reset(self):
        self.integral = 0.0
        self.last_error = 0.0
    
    def calculate(self, error, dt):
        self.integral += error * dt
        self.integral = max(min(self.integral, self.max_integral), -self.max_integral)
        
        derivative = (error - self.last_error) / dt
        self.last_error = error
        
        output = self.kp * error + self.ki * self.integral + self.kd * derivative
        return max(min(output, 100), -100)

pid = PIDController()

# ==== Función de giro ====
def rotate_to(target_angle, base_speed=60, tolerance=3, timeout=10):
    """Rota el robot al ángulo objetivo"""
    if not gyro_ok:
        print("❌ Giroscopio no disponible")
        return False
    
    pid.reset()
    gyro.reset()
    
    print(f"\n🎯 Objetivo: {target_angle}°")
    led.value(0)
    time.sleep(0.3)
    
    start_time = time.ticks_ms()
    dt = 0.02
    settled_count = 0
    last_print = 0
    
    while True:
        current_angle = gyro.update()
        
        # Error con camino más corto
        error = target_angle - current_angle
        if error > 180:
            error -= 360
        elif error < -180:
            error += 360
        
        # Control PID
        control = pid.calculate(error, dt)
        
        # Verificar si llegamos
        if abs(error) <= tolerance:
            settled_count += 1
            if settled_count >= 15:  # 0.3s estable
                robot.stop()
                led.value(1)
                print(f"✅ Completado: {current_angle:.1f}° (error: {error:.1f}°)\n")
                return True
        else:
            settled_count = 0
        
        # Aplicar movimiento
        speed = base_speed * (abs(control) / 100)
        speed = max(speed, 30)  # Velocidad mínima
        
        if control > 0:
            robot.drive(0, 0, speed)
        else:
            robot.drive(0, 0, -speed)
        
        # Print cada 0.3s
        now = time.ticks_ms()
        if time.ticks_diff(now, last_print) > 300:
            print(f"  {current_angle:6.1f}° | error: {error:6.1f}° | ctrl: {control:5.1f}")
            last_print = now
            led.toggle()
        
        # Timeout
        if time.ticks_diff(now, start_time) > timeout * 1000:
            robot.stop()
            led.value(1)
            print(f"⏱️  Timeout: {current_angle:.1f}°\n")
            return False
        
        time.sleep(dt)

# ==== Secuencia de pruebas ====
def quick_test_menu():
    """Menú de pruebas automáticas"""
    print("\n" + "="*50)
    print("🧪 SECUENCIA DE PRUEBAS AUTOMÁTICA")
    print("="*50)
    
    tests = [
        ("Test 1: Giro 90°", 90),
        ("Test 2: Giro 180°", 180),
        ("Test 3: Giro 270°", 270),
        ("Test 4: Vuelta completa (360°)", 0),  # 360° = 0°
    ]
    
    for i, (name, angle) in enumerate(tests, 1):
        print(f"\n{'='*50}")
        print(f"📍 {name}")
        print(f"{'='*50}")
        print("Iniciando en 2 segundos...")
        
        # Parpadeo de preparación
        for _ in range(4):
            led.toggle()
            time.sleep(0.5)
        led.value(1)
        
        # Ejecutar giro
        rotate_to(angle)
        
        # Pausa entre tests
        if i < len(tests):
            print("⏳ Siguiente test en 3 segundos...")
            time.sleep(3)
    
    print("\n" + "="*50)
    print("🎉 TODOS LOS TESTS COMPLETADOS")
    print("="*50)
    
    # Celebración con LED
    for _ in range(10):
        led.toggle()
        time.sleep(0.15)
    led.value(1)
    
    print("\n💡 El programa continuará esperando comandos UART...")
    print("   Escribe 'test' para repetir, o un ángulo como '90'\n")

# ==== INICIO DEL TEST AUTOMÁTICO ====
print("="*50)
print("🚀 MODO TEST AUTOMÁTICO")
print("="*50)
print("\n⏳ El test comenzará en 3 segundos...")
print("   (Asegúrate de que el robot esté en un espacio libre)\n")

time.sleep(3)
quick_test_menu()

# ==== Comandos manuales (después del test) ====
def process_command(cmd):
    """Procesa comandos desde UART"""
    cmd = cmd.strip().lower()
    
    if cmd == 'test' or cmd == 't':
        quick_test_menu()
    
    elif cmd == 'reset' or cmd == 'r':
        if gyro_ok:
            gyro.reset()
            print("🔄 Giroscopio reiniciado\n")
    
    elif cmd == 'stop' or cmd == 's':
        robot.stop()
        print("🛑 Detenido\n")
    
    elif cmd == 'help' or cmd == 'h':
        print("\n📖 COMANDOS:")
        print("  número → Girar (ej: 90, 180)")
        print("  test   → Repetir pruebas")
        print("  reset  → Reiniciar gyro")
        print("  stop   → Detener\n")
    
    elif cmd:
        try:
            angle = float(cmd)
            if -360 <= angle <= 720:
                rotate_to(angle % 360)
            else:
                print("⚠️  Ángulo: -360 a 720\n")
        except ValueError:
            print(f"⚠️  Comando desconocido: '{cmd}'\n")

# ==== Loop UART (opcional después del test) ====
uart = UART(0, baudrate=115200, timeout=10)
buffer = ""

while True:
    if uart.any():
        try:
            data = uart.read()
            text = data.decode('utf-8', 'ignore')
            
            for char in text:
                if char == '\n' or char == '\r':
                    if buffer.strip():
                        process_command(buffer)
                        buffer = ""
                else:
                    buffer += char
        except:
            buffer = ""
    
    time.sleep(0.01)
    
    # LED de vida
    if time.ticks_ms() % 2000 < 50:
        led.toggle()