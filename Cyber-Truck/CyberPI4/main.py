"""
Controlador Raspberry Pi 4 - Ejemplo de Comunicación con Pico W
Este es un ejemplo básico de cómo la RPi4 puede controlar la Pico W via UART
"""

import serial
import time
import threading
import queue

class PicoController:
    """Interfaz de control para Raspberry Pi Pico W via UART"""
    
    def __init__(self, port='/dev/ttyAMA0', baudrate=115200):
        """
        Inicializar conexión UART
        
        Args:
            port: Puerto serial (/dev/ttyAMA0 en RPi4)
            baudrate: Velocidad de comunicación (115200)
        """
        self.port = port
        self.baudrate = baudrate
        self.serial = None
        self.running = False
        self.message_queue = queue.Queue()
        self.response_callbacks = {}
        
        # Inicializar conexión
        self.connect()
    
    def connect(self):
        """Establecer conexión serial"""
        try:
            self.serial = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=1,
                write_timeout=1
            )
            print(f"✓ Conectado a Pico W en {self.port}")
            time.sleep(2)  # Esperar estabilización
            
            # Iniciar thread de lectura
            self.running = True
            self.read_thread = threading.Thread(target=self._read_loop, daemon=True)
            self.read_thread.start()
            
            return True
        except Exception as e:
            print(f"✗ Error conectando: {e}")
            return False
    
    def disconnect(self):
        """Cerrar conexión"""
        self.running = False
        if self.serial and self.serial.is_open:
            self.serial.close()
            print("✓ Desconectado de Pico W")
    
    def _read_loop(self):
        """Thread para leer mensajes continuamente"""
        buffer = ""
        while self.running:
            try:
                if self.serial and self.serial.in_waiting:
                    data = self.serial.read(self.serial.in_waiting).decode('utf-8', errors='ignore')
                    buffer += data
                    
                    # Procesar líneas completas
                    while '\n' in buffer:
                        line, buffer = buffer.split('\n', 1)
                        line = line.strip()
                        if line:
                            self.message_queue.put(line)
                            self._process_message(line)
                
                time.sleep(0.01)  # 10ms
            except Exception as e:
                print(f"Error en lectura: {e}")
                time.sleep(0.1)
    
    def _process_message(self, message):
        """Procesar mensajes recibidos"""
        print(f"← Pico: {message}")
        
        # Llamar callbacks registrados
        parts = message.split(':')
        if parts[0] in self.response_callbacks:
            callback = self.response_callbacks[parts[0]]
            callback(message)
    
    def send_command(self, command):
        """
        Enviar comando a Pico W
        
        Args:
            command: String del comando (sin newline)
        """
        if not self.serial or not self.serial.is_open:
            print("✗ Serial no conectado")
            return False
        
        try:
            cmd = f"{command}\n"
            self.serial.write(cmd.encode('utf-8'))
            print(f"→ RPi4: {command}")
            return True
        except Exception as e:
            print(f"✗ Error enviando comando: {e}")
            return False
    
    def register_callback(self, message_type, callback):
        """Registrar callback para tipo de mensaje"""
        self.response_callbacks[message_type] = callback
    
    # ============== Comandos de Alto Nivel ==============
    
    def switch_model(self, model):
        """
        Cambiar a modelo específico
        
        Args:
            model: 'A', 'B', 'C', o 'D'
        """
        return self.send_command(f"SWITCH_MODEL:{model}")
    
    def turn(self, angle, direction):
        """
        Realizar giro
        
        Args:
            angle: Grados a girar (0-360)
            direction: 'LEFT' o 'RIGHT'
        """
        return self.send_command(f"TURN:{angle}:{direction}")
    
    def set_speed(self, speed):
        """
        Establecer velocidad
        
        Args:
            speed: -100 a 100 (negativo = reversa)
        """
        return self.send_command(f"SPEED:{speed}")
    
    def control_lights(self, light_type, state):
        """
        Control de luces
        
        Args:
            light_type: 'BRAKE', 'TURN_LEFT', 'TURN_RIGHT', 'TURN_BOTH', 'HIGH', 'LOW'
            state: 'ON' u 'OFF'
        """
        return self.send_command(f"LIGHTS:{light_type}:{state}")
    
    def stop(self):
        """Detener vehículo"""
        return self.send_command("STOP")
    
    def request_status(self):
        """Solicitar estado del sistema"""
        return self.send_command("STATUS")
    
    def wait_for_message(self, timeout=5):
        """
        Esperar mensaje de Pico W
        
        Args:
            timeout: Tiempo máximo de espera en segundos
        
        Returns:
            Mensaje recibido o None si timeout
        """
        try:
            return self.message_queue.get(timeout=timeout)
        except queue.Empty:
            return None


# ============== Ejemplos de Uso ==============

def example_basic_control():
    """Ejemplo: Control básico del vehículo"""
    print("\n" + "="*60)
    print("EJEMPLO 1: Control Básico")
    print("="*60)
    
    # Crear controlador
    controller = PicoController()
    time.sleep(1)
    
    try:
        # Encender luces bajas
        print("\n1. Encendiendo luces bajas...")
        controller.control_lights('LOW', 'ON')
        time.sleep(2)
        
        # Cambiar a Modelo B (control manual)
        print("\n2. Cambiando a Modelo B...")
        controller.switch_model('B')
        time.sleep(2)
        
        # Avanzar a velocidad media
        print("\n3. Avanzando a velocidad 50%...")
        controller.set_speed(50)
        time.sleep(3)
        
        # Girar a la derecha
        print("\n4. Girando 45° a la derecha...")
        controller.control_lights('TURN_RIGHT', 'ON')
        controller.turn(45, 'RIGHT')
        time.sleep(2)
        controller.control_lights('TURN_RIGHT', 'OFF')
        
        # Detener
        print("\n5. Deteniendo vehículo...")
        controller.stop()
        controller.control_lights('BRAKE', 'ON')
        time.sleep(1)
        
        # Apagar luces
        controller.control_lights('LOW', 'OFF')
        controller.control_lights('BRAKE', 'OFF')
        
        print("\n✓ Ejemplo completado")
        
    except KeyboardInterrupt:
        print("\n\n✗ Interrumpido por usuario")
    finally:
        controller.disconnect()


def example_autonomous_mode():
    """Ejemplo: Modo autónomo con Modelo A"""
    print("\n" + "="*60)
    print("EJEMPLO 2: Modo Autónomo (Modelo A)")
    print("="*60)
    
    controller = PicoController()
    time.sleep(1)
    
    # Callback para alertas de obstáculos
    def obstacle_alert(message):
        parts = message.split(':')
        if len(parts) >= 3:
            distance = parts[2]
            print(f"⚠️  ALERTA: Obstáculo detectado a {distance} cm")
    
    # Registrar callback
    controller.register_callback('ALERT', obstacle_alert)
    
    try:
        # Encender faroles altos
        print("\n1. Encendiendo faroles altos...")
        controller.control_lights('HIGH', 'ON')
        time.sleep(1)
        
        # Activar Modelo A (autónomo)
        print("\n2. Activando Modelo A (autónomo)...")
        controller.switch_model('A')
        time.sleep(2)
        
        # Dejar funcionar 30 segundos
        print("\n3. Modo autónomo activo por 30 segundos...")
        print("   El vehículo evitará obstáculos automáticamente")
        
        for i in range(30):
            print(f"   Tiempo restante: {30-i}s", end='\r')
            time.sleep(1)
        
        print("\n\n4. Deteniendo modo autónomo...")
        controller.stop()
        controller.control_lights('HIGH', 'OFF')
        
        print("\n✓ Ejemplo completado")
        
    except KeyboardInterrupt:
        print("\n\n✗ Interrumpido por usuario")
        controller.stop()
    finally:
        controller.disconnect()


def example_keyboard_control():
    """Ejemplo: Control por teclado"""
    print("\n" + "="*60)
    print("EJEMPLO 3: Control por Teclado")
    print("="*60)
    print("\nControles:")
    print("  W/S: Adelante/Atrás")
    print("  A/D: Izquierda/Derecha")
    print("  Q/E: Velocidad -/+")
    print("  L: Alternar luces")
    print("  Space: Frenar")
    print("  1-4: Cambiar modelo")
    print("  ESC: Salir")
    print("\nPresiona Enter para comenzar...")
    input()
    
    controller = PicoController()
    time.sleep(1)
    
    # Cambiar a Modelo B
    controller.switch_model('B')
    time.sleep(1)
    
    current_speed = 0
    lights_on = False
    steering_angle = 0
    
    try:
        import sys
        import tty
        import termios
        
        # Configurar terminal para lectura sin buffer
        old_settings = termios.tcgetattr(sys.stdin)
        tty.setcbreak(sys.stdin.fileno())
        
        print("\n✓ Control por teclado activo\n")
        
        while True:
            # Leer tecla (no bloqueante)
            if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
                key = sys.stdin.read(1)
                
                if key == '\x1b':  # ESC
                    break
                
                elif key.lower() == 'w':  # Adelante
                    current_speed = min(100, current_speed + 10)
                    controller.set_speed(current_speed)
                    print(f"Velocidad: {current_speed}%")
                
                elif key.lower() == 's':  # Atrás
                    current_speed = max(-100, current_speed - 10)
                    controller.set_speed(current_speed)
                    print(f"Velocidad: {current_speed}%")
                
                elif key.lower() == 'a':  # Izquierda
                    steering_angle = max(-45, steering_angle - 15)
                    controller.turn(abs(steering_angle), 'LEFT')
                    print(f"Dirección: {steering_angle}°")
                
                elif key.lower() == 'd':  # Derecha
                    steering_angle = min(45, steering_angle + 15)
                    controller.turn(abs(steering_angle), 'RIGHT')
                    print(f"Dirección: {steering_angle}°")
                
                elif key.lower() == 'q':  # Velocidad -
                    current_speed = max(-100, current_speed - 5)
                    controller.set_speed(current_speed)
                
                elif key.lower() == 'e':  # Velocidad +
                    current_speed = min(100, current_speed + 5)
                    controller.set_speed(current_speed)
                
                elif key.lower() == 'l':  # Toggle luces
                    lights_on = not lights_on
                    controller.control_lights('HIGH', 'ON' if lights_on else 'OFF')
                    print(f"Luces: {'ON' if lights_on else 'OFF'}")
                
                elif key == ' ':  # Frenar
                    current_speed = 0
                    steering_angle = 0
                    controller.stop()
                    print("FRENADO")
                
                elif key in ['1', '2', '3', '4']:
                    model = chr(ord('A') + int(key) - 1)
                    controller.switch_model(model)
                    print(f"Modelo: {model}")
            
            time.sleep(0.05)
        
        # Restaurar configuración de terminal
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
        
    except ImportError:
        print("✗ Módulos de teclado no disponibles")
        print("   Usa los otros ejemplos o instala: pip install select")
    except Exception as e:
        print(f"✗ Error: {e}")
    finally:
        controller.stop()
        controller.disconnect()


def example_event_based_switching():
    """Ejemplo: Cambio automático entre modelos por eventos"""
    print("\n" + "="*60)
    print("EJEMPLO 4: Cambio Automático de Modelos")
    print("="*60)
    
    controller = PicoController()
    time.sleep(1)
    
    current_model = 'B'
    obstacle_count = 0
    
    # Callback para cambiar modelo según obstáculos
    def handle_obstacle(message):
        nonlocal current_model, obstacle_count
        parts = message.split(':')
        if len(parts) >= 3:
            distance = float(parts[2])
            
            if distance < 15:
                obstacle_count += 1
                print(f"\n⚠️  Obstáculo cercano: {distance} cm (#{obstacle_count})")
                
                # Cambiar a Modelo A después de 3 obstáculos
                if obstacle_count >= 3 and current_model != 'A':
                    print("→ Cambiando a Modelo A (autónomo)")
                    controller.switch_model('A')
                    current_model = 'A'
                    obstacle_count = 0
    
    controller.register_callback('ALERT', handle_obstacle)
    
    try:
        # Iniciar en Modelo B
        print("\n1. Iniciando en Modelo B (control manual)...")
        controller.switch_model('B')
        controller.control_lights('LOW', 'ON')
        time.sleep(2)
        
        print("\n2. Avanzando...")
        print("   Si detecta 3 obstáculos, cambiará a Modelo A automáticamente")
        controller.set_speed(40)
        
        # Monitorear por 60 segundos
        for i in range(60):
            print(f"\n   Tiempo: {i+1}s | Modelo actual: {current_model} | Obstáculos: {obstacle_count}", end='\r')
            time.sleep(1)
            
            # Simular cambio manual después de 30s si sigue en A
            if i == 30 and current_model == 'A':
                print("\n\n→ Volviendo a Modelo B manualmente...")
                controller.switch_model('B')
                current_model = 'B'
                obstacle_count = 0
                controller.set_speed(40)
        
        print("\n\n3. Finalizando...")
        controller.stop()
        controller.control_lights('LOW', 'OFF')
        
        print("\n✓ Ejemplo completado")
        
    except KeyboardInterrupt:
        print("\n\n✗ Interrumpido por usuario")
        controller.stop()
    finally:
        controller.disconnect()


def interactive_menu():
    """Menú interactivo para seleccionar ejemplos"""
    while True:
        print("\n" + "="*60)
        print("EJEMPLOS DE CONTROL - Raspberry Pi 4 → Pico W")
        print("="*60)
        print("\n1. Control Básico")
        print("2. Modo Autónomo (Modelo A)")
        print("3. Control por Teclado")
        print("4. Cambio Automático de Modelos")
        print("0. Salir")
        print("\n" + "="*60)
        
        try:
            choice = input("\nSelecciona un ejemplo: ").strip()
            
            if choice == '1':
                example_basic_control()
            elif choice == '2':
                example_autonomous_mode()
            elif choice == '3':
                example_keyboard_control()
            elif choice == '4':
                example_event_based_switching()
            elif choice == '0':
                print("\n✓ Saliendo...")
                break
            else:
                print("\n✗ Opción inválida")
        
        except KeyboardInterrupt:
            print("\n\n✗ Interrumpido por usuario")
            break
        except Exception as e:
            print(f"\n✗ Error: {e}")


# ============== Punto de Entrada ==============

if __name__ == "__main__":
    print("""
    ╔════════════════════════════════════════════════════════════╗
    ║   Control Raspberry Pi 4 → Pico W                          ║
    ║   Sistema de Control para Vehículo Embebido                ║
    ╚════════════════════════════════════════════════════════════╝
    """)
    
    # Verificar puerto serial
    import os
    if not os.path.exists('/dev/ttyAMA0'):
        print("⚠️  Advertencia: /dev/ttyAMA0 no encontrado")
        print("   Asegúrate de haber habilitado UART en /boot/config.txt")
        print("   Agrega: enable_uart=1")
        print()
    
    try:
        interactive_menu()
    except Exception as e:
        print(f"\n✗ Error fatal: {e}")
    
    print("\n¡Hasta luego!\n")