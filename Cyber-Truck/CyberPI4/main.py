"""
==================================
            RASPBERRY PI 4
==================================

Controlador Raspberry Pi 4 - Comunicación con Pico W via UART
Sistema de Control Mejorado para Vehículo Embebido
"""

import serial
import time
import threading
import queue
import sys
import os

class PicoController:
    """Interfaz de control mejorada para Raspberry Pi Pico W via UART"""
    
    def __init__(self, port='/dev/ttyACM0', baudrate=115200, timeout=1):
        """
        Inicializar conexión UART
        
        Args:
            port: Puerto serial (ttyACM0 para USB, ttyAMA0 para GPIO)
            baudrate: Velocidad de comunicación (115200)
            timeout: Timeout de lectura en segundos
        """
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial = None
        self.running = False
        self.connected = False
        
        # Queues para mensajes
        self.message_queue = queue.Queue()
        self.response_callbacks = {}
        
        # Estadísticas
        self.messages_sent = 0
        self.messages_received = 0
        self.errors = 0
        
        # Thread de lectura
        self.read_thread = None
        
        # Inicializar conexión
        self.connect()
    
    def connect(self):
        """Establecer conexión serial con reintentos"""
        max_retries = 3
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                print(f"Intentando conectar a {self.port}... (intento {attempt + 1}/{max_retries})")
                
                self.serial = serial.Serial(
                    port=self.port,
                    baudrate=self.baudrate,
                    timeout=self.timeout,
                    write_timeout=self.timeout
                )
                
                self.connected = True
                self.running = True
                
                print(f"✓ Conectado a Pico W en {self.port} @ {self.baudrate} baud")
                
                # Limpiar buffer
                self.serial.reset_input_buffer()
                self.serial.reset_output_buffer()
                
                # Esperar estabilización
                time.sleep(2)
                
                # Iniciar thread de lectura
                self.read_thread = threading.Thread(target=self._read_loop, daemon=True)
                self.read_thread.start()
                
                # Verificar conexión con PING
                if self.ping():
                    print("✓ Comunicación verificada con PING")
                    return True
                else:
                    print("⚠️  PING falló, pero conexión establecida")
                    return True
                
            except serial.SerialException as e:
                print(f"✗ Error en intento {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    print(f"   Reintentando en {retry_delay} segundos...")
                    time.sleep(retry_delay)
                else:
                    print(f"✗ No se pudo conectar después de {max_retries} intentos")
                    self.connected = False
                    return False
            except Exception as e:
                print(f"✗ Error inesperado: {e}")
                self.connected = False
                return False
        
        return False
    
    def disconnect(self):
        """Cerrar conexión de forma segura"""
        print("\nCerrando conexión...")
        self.running = False
        
        # Esperar a que termine el thread de lectura
        if self.read_thread and self.read_thread.is_alive():
            self.read_thread.join(timeout=2)
        
        # Cerrar puerto serial
        if self.serial and self.serial.is_open:
            try:
                self.serial.close()
                print("✓ Desconectado de Pico W")
            except Exception as e:
                print(f"Error cerrando puerto: {e}")
        
        self.connected = False
        
        # Mostrar estadísticas
        print(f"\nEstadísticas:")
        print(f"  Mensajes enviados: {self.messages_sent}")
        print(f"  Mensajes recibidos: {self.messages_received}")
        print(f"  Errores: {self.errors}")
    
    def _read_loop(self):
        """Thread para leer mensajes continuamente"""
        buffer = ""
        consecutive_errors = 0
        max_consecutive_errors = 10
        
        while self.running:
            try:
                if self.serial and self.serial.is_open and self.serial.in_waiting:
                    data = self.serial.read(self.serial.in_waiting).decode('utf-8', errors='ignore')
                    buffer += data
                    
                    # Procesar líneas completas
                    while '\n' in buffer:
                        line, buffer = buffer.split('\n', 1)
                        line = line.strip()
                        if line:
                            self.messages_received += 1
                            self.message_queue.put(line)
                            self._process_message(line)
                    
                    # Resetear contador de errores consecutivos
                    consecutive_errors = 0
                
                time.sleep(0.01)  # 10ms
                
            except serial.SerialException as e:
                consecutive_errors += 1
                self.errors += 1
                print(f"✗ Error de lectura serial: {e}")
                
                if consecutive_errors >= max_consecutive_errors:
                    print(f"✗ Demasiados errores consecutivos ({consecutive_errors}). Deteniendo lectura.")
                    self.connected = False
                    break
                
                time.sleep(0.5)
                
            except Exception as e:
                self.errors += 1
                print(f"✗ Error inesperado en lectura: {e}")
                time.sleep(0.1)
    
    def _process_message(self, message):
        """Procesar mensajes recibidos"""
        print(f"← Pico: {message}")
        
        # Llamar callbacks registrados
        parts = message.split(':')
        if len(parts) > 0 and parts[0] in self.response_callbacks:
            try:
                callback = self.response_callbacks[parts[0]]
                callback(message)
            except Exception as e:
                print(f"✗ Error en callback: {e}")
    
    def send_command(self, command, wait_response=False, timeout=2):
        """
        Enviar comando a Pico W
        
        Args:
            command: String del comando (sin newline)
            wait_response: Si True, espera confirmación
            timeout: Tiempo máximo de espera para respuesta
        
        Returns:
            True si se envió correctamente, False en caso contrario
        """
        if not self.serial or not self.serial.is_open or not self.connected:
            print("✗ Serial no conectado")
            return False
        
        try:
            cmd = f"{command}\n"
            self.serial.write(cmd.encode('utf-8'))
            self.messages_sent += 1
            print(f"→ RPi4: {command}")
            
            if wait_response:
                start_time = time.time()
                while time.time() - start_time < timeout:
                    if not self.message_queue.empty():
                        response = self.message_queue.get()
                        return response
                    time.sleep(0.05)
                print(f"⚠️  Timeout esperando respuesta para: {command}")
                return None
            
            return True
            
        except serial.SerialTimeoutException:
            print(f"✗ Timeout enviando comando: {command}")
            self.errors += 1
            return False
        except Exception as e:
            print(f"✗ Error enviando comando: {e}")
            self.errors += 1
            return False
    
    def register_callback(self, message_type, callback):
        """
        Registrar callback para tipo de mensaje
        
        Args:
            message_type: Tipo de mensaje (ej: 'ALERT', 'STATUS', etc.)
            callback: Función a llamar cuando se reciba el mensaje
        """
        self.response_callbacks[message_type] = callback
        print(f"✓ Callback registrado para: {message_type}")
    
    def unregister_callback(self, message_type):
        """Eliminar callback registrado"""
        if message_type in self.response_callbacks:
            del self.response_callbacks[message_type]
            print(f"✓ Callback eliminado para: {message_type}")
    
    # ============== Comandos de Alto Nivel ==============
    
    def ping(self, timeout=2):
        """
        Verificar conexión con Pico W
        
        Returns:
            True si recibe PONG, False en caso contrario
        """
        self.send_command("PING")
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                msg = self.message_queue.get(timeout=0.1)
                if "PONG" in msg:
                    return True
            except queue.Empty:
                pass
        
        return False
    
    def switch_model(self, model):
        """
        Cambiar a modelo específico
        
        Args:
            model: 'A', 'B', 'C', o 'D'
        
        Returns:
            True si el cambio fue exitoso
        """
        if model not in ['A', 'B', 'C', 'D']:
            print(f"✗ Modelo inválido: {model}")
            return False
        
        return self.send_command(f"SWITCH_MODEL:{model}")
    
    def turn(self, angle, direction):
        """
        Realizar giro
        
        Args:
            angle: Grados a girar (0-360)
            direction: 'LEFT' o 'RIGHT'
        
        Returns:
            True si el comando fue enviado
        """
        if not 0 <= angle <= 360:
            print(f"✗ Ángulo inválido: {angle}")
            return False
        
        if direction.upper() not in ['LEFT', 'RIGHT']:
            print(f"✗ Dirección inválida: {direction}")
            return False
        
        return self.send_command(f"TURN:{angle}:{direction}")
    
    def set_speed(self, speed):
        """
        Establecer velocidad
        
        Args:
            speed: -100 a 100 (negativo = reversa)
        
        Returns:
            True si el comando fue enviado
        """
        if not -100 <= speed <= 100:
            print(f"✗ Velocidad inválida: {speed}")
            return False
        
        return self.send_command(f"SPEED:{speed}")
    
    def control_lights(self, light_type, state):
        """
        Control de luces
        
        Args:
            light_type: 'BRAKE', 'TURN_LEFT', 'TURN_RIGHT', 'TURN_BOTH', 'HIGH', 'LOW'
            state: 'ON' u 'OFF'
        
        Returns:
            True si el comando fue enviado
        """
        valid_types = ['BRAKE', 'TURN_LEFT', 'TURN_RIGHT', 'TURN_BOTH', 'HIGH', 'LOW']
        if light_type not in valid_types:
            print(f"✗ Tipo de luz inválido: {light_type}")
            return False
        
        if state.upper() not in ['ON', 'OFF']:
            print(f"✗ Estado inválido: {state}")
            return False
        
        return self.send_command(f"LIGHTS:{light_type}:{state}")
    
    def stop(self):
        """Detener vehículo inmediatamente"""
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
    
    def is_connected(self):
        """Verificar si está conectado"""
        return self.connected and self.serial and self.serial.is_open


# ============== Funciones de Utilidad ==============

def find_pico_port():
    """Buscar puerto de la Pico W automáticamente"""
    possible_ports = [
        '/dev/ttyACM0',  # USB en Linux
        '/dev/ttyACM1',
        '/dev/ttyUSB0',
        '/dev/ttyUSB1',
        '/dev/ttyAMA0',  # GPIO UART en RPi
        '/dev/serial0',  # Alias en RPi
        'COM3',          # Windows
        'COM4',
        'COM5',
    ]
    
    print("Buscando puerto de Pico W...")
    for port in possible_ports:
        if os.path.exists(port):
            print(f"  Encontrado: {port}")
            return port
    
    print("  No se encontró ningún puerto")
    return None


# ============== Ejemplos de Uso Mejorados ==============

def example_basic_control():
    """Ejemplo 1: Control básico del vehículo"""
    print("\n" + "="*60)
    print("EJEMPLO 1: Control Básico")
    print("="*60)
    
    # Buscar puerto automáticamente
    port = find_pico_port()
    if not port:
        port = input("Ingresa el puerto manualmente (ej: /dev/ttyACM0): ")
    
    controller = PicoController(port=port)
    
    if not controller.is_connected():
        print("✗ No se pudo conectar. Abortando.")
        return
    
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
        controller.stop()
    except Exception as e:
        print(f"\n✗ Error: {e}")
    finally:
        controller.disconnect()


def example_autonomous_mode():
    """Ejemplo 2: Modo autónomo con Modelo A"""
    print("\n" + "="*60)
    print("EJEMPLO 2: Modo Autónomo (Modelo A)")
    print("="*60)
    
    port = find_pico_port() or '/dev/ttyACM0'
    controller = PicoController(port=port)
    
    if not controller.is_connected():
        print("✗ No se pudo conectar. Abortando.")
        return
    
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
        print("   Presiona Ctrl+C para detener antes\n")
        
        for i in range(30):
            print(f"   Tiempo restante: {30-i:2d}s", end='\r')
            time.sleep(1)
        
        print("\n\n4. Deteniendo modo autónomo...")
        controller.stop()
        controller.control_lights('HIGH', 'OFF')
        
        print("\n✓ Ejemplo completado")
        
    except KeyboardInterrupt:
        print("\n\n✗ Interrumpido por usuario")
        controller.stop()
    except Exception as e:
        print(f"\n✗ Error: {e}")
    finally:
        controller.disconnect()


def example_manual_control():
    """Ejemplo 3: Control manual paso a paso"""
    print("\n" + "="*60)
    print("EJEMPLO 3: Control Manual Interactivo")
    print("="*60)
    
    port = find_pico_port() or '/dev/ttyACM0'
    controller = PicoController(port=port)
    
    if not controller.is_connected():
        print("✗ No se pudo conectar. Abortando.")
        return
    
    try:
        # Cambiar a Modelo B
        controller.switch_model('B')
        time.sleep(1)
        
        print("\nComandos disponibles:")
        print("  w - Avanzar")
        print("  s - Retroceder")
        print("  a - Girar izquierda")
        print("  d - Girar derecha")
        print("  x - Detener")
        print("  l - Toggle luces")
        print("  1-4 - Cambiar modelo")
        print("  q - Salir")
        print("\nPresiona Enter después de cada comando")
        
        lights_on = False
        
        while True:
            cmd = input("\nComando: ").strip().lower()
            
            if cmd == 'q':
                break
            elif cmd == 'w':
                controller.set_speed(50)
            elif cmd == 's':
                controller.set_speed(-50)
            elif cmd == 'a':
                controller.turn(30, 'LEFT')
            elif cmd == 'd':
                controller.turn(30, 'RIGHT')
            elif cmd == 'x':
                controller.stop()
            elif cmd == 'l':
                lights_on = not lights_on
                controller.control_lights('HIGH', 'ON' if lights_on else 'OFF')
            elif cmd in ['1', '2', '3', '4']:
                model = chr(ord('A') + int(cmd) - 1)
                controller.switch_model(model)
            else:
                print("Comando no reconocido")
        
        controller.stop()
        print("\n✓ Control manual finalizado")
        
    except KeyboardInterrupt:
        print("\n\n✗ Interrumpido por usuario")
        controller.stop()
    except Exception as e:
        print(f"\n✗ Error: {e}")
    finally:
        controller.disconnect()


def example_diagnostics():
    """Ejemplo 4: Diagnóstico y prueba de conexión"""
    print("\n" + "="*60)
    print("EJEMPLO 4: Diagnóstico del Sistema")
    print("="*60)
    
    port = find_pico_port() or '/dev/ttyACM0'
    controller = PicoController(port=port)
    
    if not controller.is_connected():
        print("✗ No se pudo conectar. Abortando.")
        return
    
    try:
        print("\n1. Prueba de PING...")
        if controller.ping():
            print("   ✓ PING exitoso")
        else:
            print("   ✗ PING falló")
        
        print("\n2. Solicitando estado...")
        controller.request_status()
        time.sleep(1)
        
        print("\n3. Probando cambio de modelos...")
        for model in ['A', 'B', 'C', 'D']:
            print(f"   Cambiando a Modelo {model}...")
            controller.switch_model(model)
            time.sleep(1)
        
        print("\n4. Probando luces...")
        for light in ['HIGH', 'LOW', 'BRAKE', 'TURN_LEFT', 'TURN_RIGHT']:
            print(f"   {light} ON")
            controller.control_lights(light, 'ON')
            time.sleep(0.5)
            print(f"   {light} OFF")
            controller.control_lights(light, 'OFF')
            time.sleep(0.5)
        
        print("\n5. Prueba de velocidad (sin movimiento real)...")
        for speed in [0, 25, 50, 75, 100, 0]:
            print(f"   Velocidad: {speed}%")
            controller.set_speed(speed)
            time.sleep(0.5)
        
        controller.stop()
        print("\n✓ Diagnóstico completado")
        
    except KeyboardInterrupt:
        print("\n\n✗ Interrumpido por usuario")
    except Exception as e:
        print(f"\n✗ Error: {e}")
    finally:
        controller.disconnect()


def interactive_menu():
    """Menú interactivo mejorado"""
    while True:
        print("\n" + "="*60)
        print("CONTROL RASPBERRY PI 4 → PICO W")
        print("="*60)
        print("\n1. Control Básico")
        print("2. Modo Autónomo (Modelo A)")
        print("3. Control Manual Interactivo")
        print("4. Diagnóstico del Sistema")
        print("0. Salir")
        print("\n" + "="*60)
        
        try:
            choice = input("\nSelecciona una opción: ").strip()
            
            if choice == '1':
                example_basic_control()
            elif choice == '2':
                example_autonomous_mode()
            elif choice == '3':
                example_manual_control()
            elif choice == '4':
                example_diagnostics()
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
    ║   Control Raspberry Pi 4 → Pico W (Mejorado)              ║
    ║   Sistema de Control para Vehículo Embebido                ║
    ╚════════════════════════════════════════════════════════════╝
    """)
    
    print("\nVerificando sistema...")
    
    # Verificar puerto serial
    port = find_pico_port()
    if port:
        print(f"✓ Puerto encontrado: {port}")
    else:
        print("⚠️  No se encontró puerto automáticamente")
        print("   Verifica que la Pico W esté conectada")
        print("   Puedes especificar el puerto manualmente en los ejemplos")
    
    print()
    
    try:
        interactive_menu()
    except Exception as e:
        print(f"\n✗ Error fatal: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n¡Hasta luego!\n")