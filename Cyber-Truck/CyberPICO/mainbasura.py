"""
==================================
                PIPICO
==================================

Sistema de Control - Raspberry Pi Pico W
Auto Embebido con control modular (Sin threads)
"""

from machine import Pin, PWM, UART
import utime

# Intentar importar modelos, si fallan usar SimpleModel
try:
    from models import ModelA, ModelB, ModelC, ModelD
    MODELS_AVAILABLE = True
    print("Models imported successfully")
except Exception as e:
    print(f"Warning: Could not import models: {e}")
    MODELS_AVAILABLE = False

try:
    from hardware import HardwareController
    HARDWARE_AVAILABLE = True
    print("Hardware imported successfully")
except Exception as e:
    print(f"Warning: Could not import hardware: {e}")
    HARDWARE_AVAILABLE = False

class SimpleHardware:
    """Hardware simulado para pruebas sin hardware físico"""
    def __init__(self):
        print("SimpleHardware initialized (no real hardware)")
    
    def set_motor_speed(self, left, right):
        print(f"Motors: L={left}, R={right}")
    
    def stop_motors(self):
        print("Motors stopped")
    
    def set_steering_angle(self, angle):
        print(f"Steering: {angle}°")
    
    def center_steering(self):
        print("Steering centered")
    
    def set_brake_lights(self, state):
        print(f"Brake lights: {state}")
    
    def set_turn_signals(self, direction, state):
        print(f"Turn signals: {direction} = {state}")
    
    def set_headlights(self, mode):
        print(f"Headlights: {mode}")
    
    def control_lights(self, light_type, state):
        print(f"Light control: {light_type} = {state}")
    
    def get_distance(self):
        return 100.0  # Siempre devolver distancia segura
    
    def stop_all(self):
        print("All hardware stopped")

class SimpleModel:
    """Modelo de prueba básico para pruebas y depuración"""
    def __init__(self, hardware):
        self.hardware = hardware
        self.active = False
        print("SimpleModel initialized")

    def start(self):
        self.active = True
        print("SimpleModel started")
    
    def update(self):
        # No hacer nada para no saturar el output
        pass
    
    def stop(self):
        self.active = False
        self.hardware.stop_all()
        print("SimpleModel stopped")
    
    def set_speed(self, speed):
        print(f"SimpleModel speed: {speed}")
        self.hardware.set_motor_speed(speed, speed)
    
    def turn(self, angle, direction):
        print(f"SimpleModel turn: {angle}° {direction}")

class VehicleController:
    def __init__(self):
        print("\n=== Initializing Vehicle Controller ===")
        
        # Inicializar hardware (real o simulado)
        if HARDWARE_AVAILABLE:
            try:
                self.hardware = HardwareController()
                print("✓ Real hardware initialized")
            except Exception as e:
                print(f"✗ Hardware init failed: {e}")
                self.hardware = SimpleHardware()
        else:
            self.hardware = SimpleHardware()
        
        # Inicializar UART para comunicación con Raspberry Pi 4
        try:
            self.uart = UART(0, baudrate=115200, tx=Pin(0), rx=Pin(1))
            self.uart.init(bits=8, parity=None, stop=1)
            print("✓ UART initialized on GPIO 0/1")
        except Exception as e:
            print(f"✗ UART init failed: {e}")
            self.uart = None
        
        # Modelos disponibles
        if MODELS_AVAILABLE:
            try:
                self.models = {
                    'A': ModelA(self.hardware),
                    'B': ModelB(self.hardware),
                    'C': ModelC(self.hardware),
                    'D': ModelD(self.hardware)
                }
                print("✓ Real models loaded")
            except Exception as e:
                print(f"✗ Models init failed: {e}")
                self.models = self._create_simple_models()
        else:
            self.models = self._create_simple_models()
        
        # Modelo actual
        self.current_model = None
        self.active_model_name = None
        self.running = True
        
        # Buffer para lectura UART
        self.uart_buffer = ""
        
        # Telemetría
        self.last_telemetry_time = utime.ticks_ms()
        self.telemetry_interval = 5000  # 5 segundos (reducido para no saturar)
        
        # Debug
        self.last_debug_time = utime.ticks_ms()
        self.debug_interval = 10000  # 10 segundos
        
        print("=== Vehicle Controller Ready ===\n")
    
    def _create_simple_models(self):
        """Crear modelos simples si no se pueden cargar los reales"""
        print("Using SimpleModel for all models")
        return {
            'A': SimpleModel(self.hardware),
            'B': SimpleModel(self.hardware),
            'C': SimpleModel(self.hardware),
            'D': SimpleModel(self.hardware)
        }
    
    def switch_model(self, model_name):
        """Cambiar entre modelos de forma segura"""
        print(f"\n--- Switching to Model {model_name} ---")
        
        if model_name not in self.models:
            print(f"✗ Model {model_name} not found")
            self.send_response(f"ERROR:MODEL_NOT_FOUND:{model_name}")
            return False
        
        # Detener modelo actual
        if self.current_model:
            print(f"Stopping current model: {self.active_model_name}")
            try:
                self.current_model.stop()
            except Exception as e:
                print(f"Error stopping model: {e}")
            
            try:
                self.hardware.stop_all()
            except Exception as e:
                print(f"Error stopping hardware: {e}")
        
        # Activar nuevo modelo
        self.current_model = self.models[model_name]
        self.active_model_name = model_name
        
        # Iniciar nuevo modelo
        if hasattr(self.current_model, 'start'):
            try:
                self.current_model.start()
                print(f"✓ Model {model_name} started")
            except Exception as e:
                print(f"✗ Error starting model: {e}")
        
        # Enviar confirmación a Raspberry Pi 4
        self.send_response(f"MODEL_CHANGED:{model_name}")
        
        return True
    
    def send_response(self, message):
        """Enviar respuesta a Raspberry Pi 4 via UART"""
        if not self.uart:
            return
        
        try:
            self.uart.write(f"{message}\n")
            # No imprimir cada mensaje para no saturar
        except Exception as e:
            print(f"✗ Error sending: {e}")
    
    def parse_command(self, command):
        """Parsear comandos recibidos via UART"""
        command = command.strip()
        if not command:
            return
        
        parts = command.split(':')
        cmd_type = parts[0]
        
        print(f"\n→ Command: {cmd_type}")
        
        if cmd_type == "SWITCH_MODEL":
            if len(parts) >= 2:
                model_name = parts[1]
                self.switch_model(model_name)
        
        elif cmd_type == "TURN":
            if len(parts) >= 3:
                try:
                    angle = float(parts[1])
                    direction = parts[2]
                    if self.current_model and hasattr(self.current_model, 'turn'):
                        self.current_model.turn(angle, direction)
                        self.send_response(f"TURN_EXECUTED:{angle}:{direction}")
                        print(f"✓ Turn executed: {angle}° {direction}")
                    else:
                        self.send_response("ERROR:TURN_NOT_SUPPORTED")
                        print("✗ Turn not supported by current model")
                except ValueError as e:
                    self.send_response("ERROR:INVALID_TURN_PARAMETERS")
                    print(f"✗ Invalid turn parameters: {e}")
        
        elif cmd_type == "LIGHTS":
            if len(parts) >= 3:
                light_type = parts[1]
                state = parts[2]
                try:
                    self.hardware.control_lights(light_type, state)
                    self.send_response(f"LIGHTS_SET:{light_type}:{state}")
                    print(f"✓ Lights: {light_type} = {state}")
                except Exception as e:
                    print(f"✗ Light control error: {e}")
        
        elif cmd_type == "SPEED":
            if len(parts) >= 2:
                try:
                    speed = float(parts[1])
                    if self.current_model and hasattr(self.current_model, 'set_speed'):
                        self.current_model.set_speed(speed)
                        self.send_response(f"SPEED_SET:{speed}")
                        print(f"✓ Speed set: {speed}")
                    else:
                        # Control directo de hardware
                        self.hardware.set_motor_speed(speed, speed)
                        self.send_response(f"SPEED_SET:{speed}")
                        print(f"✓ Speed set (direct): {speed}")
                except ValueError as e:
                    self.send_response("ERROR:INVALID_SPEED")
                    print(f"✗ Invalid speed: {e}")
        
        elif cmd_type == "STOP":
            print("STOP command received")
            if self.current_model:
                self.current_model.stop()
            self.hardware.stop_all()
            self.send_response("STOPPED")
            print("✓ Stopped")
        
        elif cmd_type == "STATUS":
            print("STATUS request")
            self.send_status()
        
        elif cmd_type == "PING":
            print("PING received")
            self.send_response("PONG")
            print("✓ PONG sent")
        
        else:
            self.send_response(f"ERROR:UNKNOWN_COMMAND:{cmd_type}")
            print(f"✗ Unknown command: {cmd_type}")
    
    def send_status(self):
        """Enviar estado actual del sistema"""
        try:
            distance = self.hardware.get_distance()
        except:
            distance = -1
        
        model_name = self.active_model_name if self.active_model_name else 'NONE'
        self.send_response(f"STATUS:{model_name}:{distance:.1f}:{self.running}")
        print(f"Status sent: Model={model_name}, Distance={distance:.1f}")
    
    def process_uart(self):
        """Procesar datos recibidos por UART (no bloqueante)"""
        if not self.uart:
            return
        
        try:
            if self.uart.any():
                # Leer datos disponibles
                data = self.uart.read()
                if data:
                    try:
                        self.uart_buffer += data.decode('utf-8', errors='ignore')
                    except Exception as e:
                        print(f"✗ Decode error: {e}")
                        return
                    
                    # Procesar líneas completas
                    while '\n' in self.uart_buffer:
                        line, self.uart_buffer = self.uart_buffer.split('\n', 1)
                        line = line.strip()
                        if line:
                            try:
                                self.parse_command(line)
                            except Exception as e:
                                print(f"✗ Parse error: {e}")
                                self.send_response(f"ERROR:PARSE_ERROR")
        except Exception as e:
            print(f"✗ UART process error: {e}")
    
    def send_telemetry(self):
        """Enviar telemetría periódica"""
        current_time = utime.ticks_ms()
        if utime.ticks_diff(current_time, self.last_telemetry_time) >= self.telemetry_interval:
            self.last_telemetry_time = current_time
            
            # Enviar alertas de obstáculos solo si hay modelo activo
            if self.current_model:
                try:
                    distance = self.hardware.get_distance()
                    if 0 < distance < 20:
                        self.send_response(f"ALERT:OBSTACLE:{distance:.1f}")
                except:
                    pass
    
    def run(self):
        """Loop principal del controlador (sin threads)"""
        print("\n*** Vehicle Controller Running ***")
        print("Waiting for commands via UART...\n")
        
        # Enviar mensaje de inicio
        self.send_response("SYSTEM_READY")
        print("SYSTEM_READY sent\n")
        
        # Loop principal
        while self.running:
            try:
                # 1. Procesar comandos UART (alta prioridad)
                self.process_uart()
                
                # 2. Actualizar modelo actual
                if self.current_model and hasattr(self.current_model, 'update'):
                    try:
                        self.current_model.update()
                    except Exception as e:
                        print(f"✗ Model update error: {e}")
                        self.send_response(f"ERROR:MODEL_EXCEPTION")
                
                # 3. Enviar telemetría periódica
                self.send_telemetry()
                
                # 4. Debug periódico
                current_time = utime.ticks_ms()
                if utime.ticks_diff(current_time, self.last_debug_time) >= self.debug_interval:
                    self.last_debug_time = current_time
                    if self.active_model_name:
                        print(f"[{utime.ticks_ms()}] Active: Model {self.active_model_name}")
                    else:
                        print(f"[{utime.ticks_ms()}] No model selected - waiting for SWITCH_MODEL command")
                
                # Pequeño delay para no saturar la CPU
                utime.sleep_ms(50)
                
            except KeyboardInterrupt:
                print("\nKeyboard interrupt detected")
                break
            except Exception as e:
                print(f"✗ Main loop error: {e}")
                utime.sleep_ms(100)
        
        print("\nExiting main loop")
    
    def shutdown(self):
        """Apagar sistema de forma segura"""
        print("\n=== Shutting down ===")
        self.running = False
        
        if self.current_model:
            try:
                self.current_model.stop()
            except:
                pass
        
        try:
            self.hardware.stop_all()
        except:
            pass
        
        self.send_response("SYSTEM_SHUTDOWN")
        print("✓ Shutdown complete")

# Punto de entrada
if __name__ == "__main__":
    print("\n" + "="*50)
    print("RASPBERRY PI PICO W - VEHICLE CONTROLLER")
    print("="*50 + "\n")
    
    controller = None
    try:
        controller = VehicleController()
        controller.run()
    except KeyboardInterrupt:
        print("\n\n✗ Interrupted by user")
    except Exception as e:
        print(f"\n✗ Fatal error: {e}")
        import sys
        sys.print_exception(e)
    finally:
        if controller:
            controller.shutdown()
    
    print("\n" + "="*50)
    print("SYSTEM HALTED")
    print("="*50 + "\n")