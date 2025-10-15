"""
==================================
                PIPICO
==================================

Sistema de Control - Raspberry Pi Pico W
Auto Embebido con control modular (Sin threads)
"""

from machine import Pin, PWM, UART
import utime
from models import ModelA, ModelB, ModelC, ModelD
from hardware import HardwareController

class SimpleModel:
    """Modelo de prueba básico para pruebas y depuración"""
    def __init__(self, hardware):
        self.hardware = hardware
        self.active = False

    def start(self):
        self.active = True
        print("Simple Model started.")
    
    def update(self):
        if self.active:
            print("Updating Simple Model.")
    
    def stop(self):
        self.active = False
        print("Simple Model stopped.")

class VehicleController:
    def __init__(self):
        # Inicializar hardware
        self.hardware = HardwareController()
        
        # Inicializar UART para comunicación con Raspberry Pi 4
        self.uart = UART(0, baudrate=115200, tx=Pin(0), rx=Pin(1))
        
        # Modelos disponibles (usamos el SimpleModel por ahora)
        self.models = {
            'A': SimpleModel(self.hardware),
            'B': SimpleModel(self.hardware),
            'C': SimpleModel(self.hardware),
            'D': SimpleModel(self.hardware)
        }
        
        # Modelo actual
        self.current_model = None
        self.active_model_name = None
        self.running = True
        
        # Buffer para lectura UART
        self.uart_buffer = ""
        
        # Telemetría
        self.last_telemetry_time = utime.ticks_ms()
        self.telemetry_interval = 1000  # 1 segundo
        
        print("Vehicle Controller initialized")
    
    def switch_model(self, model_name):
        """Cambiar entre modelos de forma segura"""
        if model_name not in self.models:
            print(f"Error: Model {model_name} not found")
            self.send_response(f"ERROR:MODEL_NOT_FOUND:{model_name}")
            return False
        
        # Detener modelo actual
        if self.current_model:
            print(f"Stopping model {self.active_model_name}")
            self.current_model.stop()
            self.hardware.stop_all()
        
        # Activar nuevo modelo
        self.current_model = self.models[model_name]
        self.active_model_name = model_name
        
        # Iniciar nuevo modelo
        if hasattr(self.current_model, 'start'):
            self.current_model.start()
        
        print(f"Switched to Model {model_name}")
        
        # Enviar confirmación a Raspberry Pi 4
        self.send_response(f"MODEL_CHANGED:{model_name}")
        
        return True
    
    def send_response(self, message):
        """Enviar respuesta a Raspberry Pi 4 via UART"""
        try:
            self.uart.write(f"{message}\n")
        except Exception as e:
            print(f"Error sending response: {e}")
    
    def parse_command(self, command):
        """Parsear comandos recibidos via UART"""
        command = command.strip()
        if not command:
            return
        
        parts = command.split(':')
        cmd_type = parts[0]
        
        print(f"Processing command: {cmd_type}")
        
        if cmd_type == "SWITCH_MODEL":
            if len(parts) >= 2:
                model_name = parts[1]
                self.switch_model(model_name)
        
        elif cmd_type == "TURN":
            # Comando: TURN:angle:direction
            if len(parts) >= 3 and self.current_model:
                try:
                    angle = float(parts[1])
                    direction = parts[2]  # 'LEFT' o 'RIGHT'
                    if hasattr(self.current_model, 'turn'):
                        self.current_model.turn(angle, direction)
                        self.send_response(f"TURN_EXECUTED:{angle}:{direction}")
                    else:
                        self.send_response("ERROR:TURN_NOT_SUPPORTED")
                except ValueError:
                    self.send_response("ERROR:INVALID_TURN_PARAMETERS")
        
        elif cmd_type == "LIGHTS":
            # Comando: LIGHTS:type:state
            if len(parts) >= 3:
                light_type = parts[1]
                state = parts[2]
                self.hardware.control_lights(light_type, state)
                self.send_response(f"LIGHTS_SET:{light_type}:{state}")
        
        elif cmd_type == "SPEED":
            # Comando: SPEED:value
            if len(parts) >= 2 and self.current_model:
                try:
                    speed = float(parts[1])
                    if hasattr(self.current_model, 'set_speed'):
                        self.current_model.set_speed(speed)
                        self.send_response(f"SPEED_SET:{speed}")
                    else:
                        # Control directo de hardware si el modelo no lo soporta
                        self.hardware.set_motor_speed(speed, speed)
                        self.send_response(f"SPEED_SET:{speed}")
                except ValueError:
                    self.send_response("ERROR:INVALID_SPEED")
        
        elif cmd_type == "STOP":
            if self.current_model:
                self.current_model.stop()
            self.hardware.stop_all()
            self.send_response("STOPPED")
        
        elif cmd_type == "STATUS":
            self.send_status()
        
        elif cmd_type == "PING":
            # Comando para verificar conexión
            self.send_response("PONG")
        
        else:
            self.send_response(f"ERROR:UNKNOWN_COMMAND:{cmd_type}")
    
    def send_status(self):
        """Enviar estado actual del sistema"""
        distance = self.hardware.get_distance()
        model_name = self.active_model_name if self.active_model_name else 'NONE'
        self.send_response(f"STATUS:{model_name}:{distance:.1f}:{self.running}")
    
    def process_uart(self):
        """Procesar datos recibidos por UART (no bloqueante)"""
        if self.uart.any():
            # Leer datos disponibles
            data = self.uart.read()
            if data:
                try:
                    self.uart_buffer += data.decode('utf-8', errors='ignore')
                except:
                    print("Error decoding UART data")
                    return
                
                # Procesar líneas completas
                while '\n' in self.uart_buffer:
                    line, self.uart_buffer = self.uart_buffer.split('\n', 1)
                    line = line.strip()
                    if line:
                        print(f"Received: {line}")
                        try:
                            self.parse_command(line)
                        except Exception as e:
                            print(f"Error parsing command: {e}")
                            self.send_response(f"ERROR:PARSE_ERROR:{e}")
    
    def send_telemetry(self):
        """Enviar telemetría periódica"""
        current_time = utime.ticks_ms()
        if utime.ticks_diff(current_time, self.last_telemetry_time) >= self.telemetry_interval:
            self.last_telemetry_time = current_time
            
            # Enviar alertas de obstáculos
            if self.current_model:
                distance = self.hardware.get_distance()
                if 0 < distance < 20:  # Objeto cercano
                    self.send_response(f"ALERT:OBSTACLE:{distance:.1f}")
    
    def run(self):
        """Loop principal del controlador (sin threads)"""
        print("Vehicle Controller running. Waiting for commands...")
        self.send_response("SYSTEM_READY")
        
        # Loop principal
        loop_count = 0
        while self.running:
            try:
                # 1. Procesar comandos UART (alta prioridad)
                self.process_uart()
                
                # 2. Actualizar modelo actual
                if self.current_model and hasattr(self.current_model, 'update'):
                    try:
                        self.current_model.update()
                    except Exception as e:
                        print(f"Error in model update: {e}")
                        self.send_response(f"ERROR:MODEL_EXCEPTION:{e}")
                
                # 3. Enviar telemetría periódica
                self.send_telemetry()
                
                # 4. Debug: mostrar info cada 100 iteraciones (~5 segundos)
                loop_count += 1
                if loop_count >= 100:
                    if self.active_model_name:
                        print(f"Running: Model {self.active_model_name}")
                    else:
                        print("Running: No model selected")
                    loop_count = 0
                
                # Pequeño delay para no saturar la CPU
                utime.sleep_ms(50)
                
            except Exception as e:
                print(f"Error in main loop: {e}")
                utime.sleep_ms(100)
    
    def shutdown(self):
        """Apagar sistema de forma segura"""
        print("Shutting down...")
        self.running = False
        if self.current_model:
            self.current_model.stop()
        self.hardware.stop_all()
        self.send_response("SYSTEM_SHUTDOWN")

# Punto de entrada
if __name__ == "__main__":
    controller = None
    try:
        controller = VehicleController()
        controller.run()
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        if controller:
            controller.shutdown()
    except Exception as e:
        print(f"Fatal error: {e}")
        if controller:
            controller.shutdown()