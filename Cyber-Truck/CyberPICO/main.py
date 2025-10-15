"""
==================================

                PIPICO

)==================================

Sistema de Control - Raspberry Pi Pico W
Auto Embebido con control modular
"""

from machine import Pin, PWM, UART
import utime
import _thread
from models import ModelA, ModelB, ModelC, ModelD
from hardware import HardwareController

class VehicleController:
    def __init__(self):
        # Inicializar hardware
        self.hardware = HardwareController()
        
        # Inicializar UART para comunicación con Raspberry Pi 4
        self.uart = UART(0, baudrate=115200, tx=Pin(0), rx=Pin(1))
        
        # Modelos disponibles
        self.models = {
            'A': ModelA(self.hardware),
            'B': ModelB(self.hardware),
            'C': ModelC(self.hardware),
            'D': ModelD(self.hardware)
        }
        
        # Modelo actual
        self.current_model = None
        self.active_model_name = None
        self.running = True
        
        # Lock para cambios de modelo
        self.model_lock = _thread.allocate_lock()
        
        print("Vehicle Controller initialized")
    
    def switch_model(self, model_name):
        """Cambiar entre modelos de forma segura"""
        with self.model_lock:
            if model_name not in self.models:
                print(f"Error: Model {model_name} not found")
                return False
            
            # Detener modelo actual
            if self.current_model:
                print(f"Stopping model {self.active_model_name}")
                self.current_model.stop()
                self.hardware.stop_all()
            
            # Activar nuevo modelo
            self.current_model = self.models[model_name]
            self.active_model_name = model_name
            print(f"Switched to Model {model_name}")
            
            # Enviar confirmación a Raspberry Pi 4
            self.send_response(f"MODEL_CHANGED:{model_name}")
            
            return True
    
    def send_response(self, message):
        """Enviar respuesta a Raspberry Pi 4 via UART"""
        if self.uart:
            self.uart.write(f"{message}\n")
    
    def parse_command(self, command):
        """Parsear comandos recibidos via UART"""
        command = command.strip()
        parts = command.split(':')
        
        if len(parts) < 1:
            return
        
        cmd_type = parts[0]
        
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
                except ValueError:
                    self.send_response("ERROR:INVALID_TURN_PARAMETERS")
        
        elif cmd_type == "LIGHTS":
            # Comando: LIGHTS:type:state
            if len(parts) >= 3:
                light_type = parts[1]  # 'BRAKE', 'TURN_LEFT', 'TURN_RIGHT', 'HIGH', 'LOW'
                state = parts[2]  # 'ON' o 'OFF'
                self.hardware.control_lights(light_type, state)
        
        elif cmd_type == "SPEED":
            # Comando: SPEED:value
            if len(parts) >= 2 and self.current_model:
                try:
                    speed = float(parts[1])
                    if hasattr(self.current_model, 'set_speed'):
                        self.current_model.set_speed(speed)
                except ValueError:
                    self.send_response("ERROR:INVALID_SPEED")
        
        elif cmd_type == "STOP":
            if self.current_model:
                self.current_model.stop()
                self.send_response("STOPPED")
        
        elif cmd_type == "STATUS":
            self.send_status()
        
        else:
            self.send_response(f"ERROR:UNKNOWN_COMMAND:{cmd_type}")
    
    def send_status(self):
        """Enviar estado actual del sistema"""
        distance = self.hardware.get_distance()
        status = {
            'model': self.active_model_name or 'NONE',
            'distance': distance,
            'running': self.running
        }
        self.send_response(f"STATUS:{status}")
    
    def uart_listener(self):
        """Thread para escuchar comandos via UART"""
        buffer = ""
        while self.running:
            if self.uart.any():
                data = self.uart.read()
                if data:
                    buffer += data.decode('utf-8', errors='ignore')
                    
                    # Procesar líneas completas
                    while '\n' in buffer:
                        line, buffer = buffer.split('\n', 1)
                        if line.strip():
                            print(f"Received: {line}")
                            self.parse_command(line)
            
            utime.sleep_ms(10)
    
    def run(self):
        """Loop principal del controlador"""
        # Iniciar thread de escucha UART
        _thread.start_new_thread(self.uart_listener, ())
        
        print("Vehicle Controller running. Waiting for commands...")
        self.send_response("SYSTEM_READY")
        
        # Loop principal
        while self.running:
            # Ejecutar modelo actual si existe
            if self.current_model and hasattr(self.current_model, 'update'):
                try:
                    self.current_model.update()
                except Exception as e:
                    print(f"Error in model update: {e}")
                    self.send_response(f"ERROR:MODEL_EXCEPTION:{e}")
            
            # Enviar telemetría periódica
            if self.current_model:
                distance = self.hardware.get_distance()
                if distance < 20:  # Objeto cercano
                    self.send_response(f"ALERT:OBSTACLE:{distance}")
            
            utime.sleep_ms(50)
    
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
    try:
        controller = VehicleController()
        controller.run()
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        controller.shutdown()
    except Exception as e:
        print(f"Fatal error: {e}")