"""
==================================

                    PIPICO

==================================
Utilidades y Funciones Helper - Raspberry Pi Pico W
Funciones comunes reutilizables en todo el sistema
"""

import utime
from machine import Pin
from config import LightConfig

class Timer:
    """Timer simple para operaciones no bloqueantes"""
    def __init__(self, duration_ms):
        self.duration_ms = duration_ms
        self.start_time = None
        self.running = False
    
    def start(self):
        """Iniciar timer"""
        self.start_time = utime.ticks_ms()
        self.running = True
    
    def reset(self):
        """Reiniciar timer"""
        self.start()
    
    def elapsed(self):
        """Tiempo transcurrido en ms"""
        if not self.running or self.start_time is None:
            return 0
        return utime.ticks_diff(utime.ticks_ms(), self.start_time)
    
    def is_expired(self):
        """Verificar si el timer expiró"""
        if not self.running:
            return False
        return self.elapsed() >= self.duration_ms
    
    def stop(self):
        """Detener timer"""
        self.running = False


class Blinker:
    """Controlador de intermitencia para LEDs"""
    def __init__(self, pin, interval_ms=LightConfig.BLINK_FREQUENCY):
        self.pin = pin
        self.interval_ms = interval_ms
        self.timer = Timer(interval_ms)
        self.state = False
        self.active = False
    
    def start(self):
        """Iniciar intermitencia"""
        self.active = True
        self.timer.start()
        self.state = True
        self.pin.value(1)
    
    def stop(self):
        """Detener intermitencia"""
        self.active = False
        self.state = False
        self.pin.value(0)
    
    def update(self):
        """Actualizar estado (llamar en loop)"""
        if not self.active:
            return
        
        if self.timer.is_expired():
            self.state = not self.state
            self.pin.value(1 if self.state else 0)
            self.timer.reset()


class MovingAverage:
    """Filtro de promedio móvil para suavizar lecturas de sensores"""
    def __init__(self, window_size=5):
        self.window_size = window_size
        self.values = []
    
    def add(self, value):
        """Agregar nuevo valor"""
        self.values.append(value)
        if len(self.values) > self.window_size:
            self.values.pop(0)
    
    def get_average(self):
        """Obtener promedio actual"""
        if not self.values:
            return 0
        return sum(self.values) / len(self.values)
    
    def reset(self):
        """Limpiar valores"""
        self.values = []


class RateLimiter:
    """Limitador de tasa para envío de mensajes"""
    def __init__(self, min_interval_ms):
        self.min_interval_ms = min_interval_ms
        self.last_time = 0
    
    def can_execute(self):
        """Verificar si puede ejecutar acción"""
        now = utime.ticks_ms()
        if utime.ticks_diff(now, self.last_time) >= self.min_interval_ms:
            self.last_time = now
            return True
        return False
    
    def reset(self):
        """Resetear limitador"""
        self.last_time = 0


class Logger:
    """Logger simple con niveles"""
    LEVEL_DEBUG = 0
    LEVEL_INFO = 1
    LEVEL_WARNING = 2
    LEVEL_ERROR = 3
    
    def __init__(self, level=LEVEL_INFO):
        self.level = level
        self.enabled = True
    
    def debug(self, message):
        """Log nivel DEBUG"""
        if self.enabled and self.level <= self.LEVEL_DEBUG:
            print(f"[DEBUG] {message}")
    
    def info(self, message):
        """Log nivel INFO"""
        if self.enabled and self.level <= self.LEVEL_INFO:
            print(f"[INFO] {message}")
    
    def warning(self, message):
        """Log nivel WARNING"""
        if self.enabled and self.level <= self.LEVEL_WARNING:
            print(f"[WARNING] {message}")
    
    def error(self, message):
        """Log nivel ERROR"""
        if self.enabled and self.level <= self.LEVEL_ERROR:
            print(f"[ERROR] {message}")
    
    def set_level(self, level):
        """Cambiar nivel de logging"""
        self.level = level


def clamp(value, min_val, max_val):
    """Limitar valor entre mínimo y máximo"""
    return max(min_val, min(max_val, value))


def map_range(value, in_min, in_max, out_min, out_max):
    """Mapear valor de un rango a otro"""
    return (value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


def angle_to_duty(angle, min_angle=-90, max_angle=90, min_pulse=1000, max_pulse=2000):
    """Convertir ángulo a duty cycle para servo"""
    angle = clamp(angle, min_angle, max_angle)
    pulse_width = map_range(angle, min_angle, max_angle, min_pulse, max_pulse)
    duty = int((pulse_width / 20000) * 65535)  # Para 50Hz
    return duty


def speed_to_duty(speed):
    """
    Convertir velocidad (-100 a 100) a duty cycle
    Retorna: (duty, direction) donde direction es 'FORWARD' o 'BACKWARD'
    """
    speed = clamp(speed, -100, 100)
    duty = int(abs(speed) * 655.35)  # 0-65535
    direction = 'FORWARD' if speed >= 0 else 'BACKWARD'
    return duty, direction


class CommandParser:
    """Parser de comandos UART"""
    @staticmethod
    def parse(command_str):
        """
        Parsear string de comando
        Formato: COMANDO:arg1:arg2:...
        Retorna: dict con 'command' y 'args'
        """
        parts = command_str.strip().split(':')
        if not parts:
            return None
        
        return {
            'command': parts[0].upper(),
            'args': parts[1:] if len(parts) > 1 else []
        }
    
    @staticmethod
    def build(command, *args):
        """
        Construir string de comando
        """
        parts = [str(command)] + [str(arg) for arg in args]
        return ':'.join(parts)


class StateMachine:
    """Máquina de estados simple"""
    def __init__(self, initial_state):
        self.current_state = initial_state
        self.previous_state = None
        self.state_enter_time = utime.ticks_ms()
    
    def change_state(self, new_state):
        """Cambiar a nuevo estado"""
        if new_state != self.current_state:
            self.previous_state = self.current_state
            self.current_state = new_state
            self.state_enter_time = utime.ticks_ms()
            return True
        return False
    
    def get_state(self):
        """Obtener estado actual"""
        return self.current_state
    
    def time_in_state(self):
        """Tiempo en estado actual (ms)"""
        return utime.ticks_diff(utime.ticks_ms(), self.state_enter_time)
    
    def is_state(self, state):
        """Verificar si está en estado específico"""
        return self.current_state == state


def format_status_message(model, distance, speed, steering):
    """Formatear mensaje de estado para envío"""
    return f"STATUS:{model}:{distance:.1f}:{speed}:{steering}"


def safe_float(value, default=0.0):
    """Convertir a float de forma segura"""
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def safe_int(value, default=0):
    """Convertir a int de forma segura"""
    try:
        return int(value)
    except (ValueError, TypeError):
        return default