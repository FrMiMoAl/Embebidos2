"""
==================================

                    PIPICO

==================================

Controlador de Hardware - Raspberry Pi Pico W
Maneja todos los componentes físicos del vehículo

"""

from machine import Pin, PWM
from config import MotorConfig, PinConfig, ServoConfig, LightConfig, SensorConfig
import utime

class HardwareController:
    def __init__(self):
        # Motores TB6612 ; LOS PINES SE CONFIGURAN EN "config.py"
        self.motor_left_BIN1 = Pin(PinConfig.MOTOR_LEFT_BIN1, Pin.OUT)
        self.motor_left_BIN2 = Pin(PinConfig.MOTOR_LEFT_BIN2, Pin.OUT)
        self.motor_left_pwm = PWM(Pin(PinConfig.MOTOR_LEFT_PWM))

        self.motor_right_AIN1 = Pin(PinConfig.MOTOR_RIGHT_AIN1, Pin.OUT)
        self.motor_right_AIN2 = Pin(PinConfig.MOTOR_RIGHT_AIN2, Pin.OUT)
        self.motor_right_pwm = PWM(Pin(PinConfig.MOTOR_RIGHT_PWM))

        self.motor_left_pwm.freq(MotorConfig.PWM_FREQUENCY)
        self.motor_right_pwm.freq(MotorConfig.PWM_FREQUENCY)


        # Configurar frecuencia PWM para motores
        for motor in [self.motor_left_BIN1, self.motor_left_BIN2,
                      self.motor_right_AIN1, self.motor_right_AIN2]:
            motor.value(0)

        
        # Servomotor de dirección - CALIBRAR PLS
        self.steering_servo = PWM(Pin(PinConfig.STEERING_SERVO))
        self.steering_servo.freq(ServoConfig.PWM_FREQUENCY)  # 50Hz para servos
        self.center_steering()
        
        # Luces de freno (PWM) - 50% normal, 100% al frenar
        self.brake_lights = PWM(Pin(PinConfig.BRAKE_LIGHTS))
        self.brake_lights.freq(LightConfig.PWM_FREQUENCY)
        self.brake_lights.duty_u16(LightConfig.BRAKE_NORMAL)  # 50% por defecto
        
        # Luces intermitentes y direccionales 
        self.turn_left = Pin(PinConfig.TURN_LEFT, Pin.OUT)
        self.turn_right = Pin(PinConfig.TURN_RIGHT, Pin.OUT)
        self.turn_left.value(0)
        self.turn_right.value(0)
        
        # Faroles (luces altas y bajas)
        self.headlights = PWM(Pin(PinConfig.HEADLIGHTS))
        self.headlights.freq(LightConfig.PWM_FREQUENCY)
        self.headlights.duty_u16(LightConfig.HEADLIGHT_OFF)  # Apagados por defecto
        
        # Sensor ultrasónico
        self.ultrasonic_trigger = Pin(PinConfig.ULTRASONIC_TRIGGER, Pin.OUT)
        self.ultrasonic_echo = Pin(PinConfig.ULTRASONIC_ECHO, Pin.IN)

        # Variables de estado
        self.current_speed = 0
        self.braking = False
        self.turn_signal_active = False
        
        print("Hardware initialized")
    
    def set_motor_speed(self, left_speed, right_speed):
        """
        Establecer velocidad de motores
        left_speed, right_speed: -100 a 100 (negativo = reversa)
        """
        self.current_speed = (left_speed + right_speed) / 2
        
        # Motor izquierdo
        if left_speed > 0:
            self.motor_left_BIN1.value(1)
            self.motor_left_BIN2.value(0)
        elif left_speed < 0:
            self.motor_left_BIN1.value(0)
            self.motor_left_BIN2.value(1)
        else:
            self.motor_left_BIN1.value(0)
            self.motor_left_BIN2.value(0)

        # Motor derecho
        if right_speed > 0:
            self.motor_right_AIN1.value(1)
            self.motor_right_AIN2.value(0)
        elif right_speed < 0:
            self.motor_right_AIN1.value(0)
            self.motor_right_AIN2.value(1)
        else:
            self.motor_right_AIN1.value(0)
            self.motor_right_AIN2.value(0)

    def stop_motors(self):
        """Detener todos los motores"""
        self.set_motor_speed(0, 0)
        self.current_speed = 0
    
    def set_steering_angle(self, angle):
        """
        Establecer ángulo de dirección
        angle: -20 a 20 grados (-20 = máximo izquierda, 0 = centro, 20 = máximo derecha)
        """
        # Convertir ángulo a duty cycle para servo
        # Típicamente: 1ms = -20°, 1.5ms = 0°, 2ms = 20°
        # duty_u16: 0-65535, para 50Hz: 1ms=3276, 1.5ms=4915, 2ms=6553
        angle = max(-20, min(20, angle))
        pulse_width = 1500 + (angle * 500 / 40)  # 1000-2000 microsegundos
        duty = int((pulse_width / 20000) * 65535)
        self.steering_servo.duty_u16(duty)
    
    def center_steering(self):
        self.set_steering_angle(ServoConfig.CENTER_ANGLE)
    
    def set_brake_lights(self, braking):
        """
        Control de luces de freno
        braking: True = frenando (100%), False = normal (50%)
        """
        self.braking = braking
        if braking:
            self.brake_lights.duty_u16(LightConfig.BRAKE_ACTIVE)  # 100%
        else:
            self.brake_lights.duty_u16(LightConfig.BRAKE_NORMAL)  # 50%
    
    def set_turn_signals(self, direction, state):
        """
        Control de luces direccionales
        direction: 'LEFT', 'RIGHT', 'BOTH', 'OFF'
        state: True/False para intermitente
        """
        if direction == 'LEFT':
            self.turn_left.value(1 if state else 0)
            self.turn_right.value(0)
        elif direction == 'RIGHT':
            self.turn_left.value(0)
            self.turn_right.value(1 if state else 0)
        elif direction == 'BOTH':
            self.turn_left.value(1 if state else 0)
            self.turn_right.value(1 if state else 0)
        else:  # OFF
            self.turn_left.value(0)
            self.turn_right.value(0)
    
    def set_headlights(self, mode):
        """
        Control de faroles
        mode: 'OFF', 'LOW' (50%), 'HIGH' (100%)
        """
        if mode == 'HIGH':
            self.headlights.duty_u16(LightConfig.HEADLIGHT_HIGH)  # 100%
        elif mode == 'LOW':
            self.headlights.duty_u16(LightConfig.HEADLIGHT_LOW)  # 50%
        else:
            self.headlights.duty_u16(LightConfig.HEADLIGHT_OFF)  # OFF

    def control_lights(self, light_type, state):
        """Control general de luces"""
        if light_type == 'BRAKE':
            self.set_brake_lights(state == 'ON')
        elif light_type == 'TURN_LEFT':
            self.set_turn_signals('LEFT', state == 'ON')
        elif light_type == 'TURN_RIGHT':
            self.set_turn_signals('RIGHT', state == 'ON')
        elif light_type == 'TURN_BOTH':
            self.set_turn_signals('BOTH', state == 'ON')
        elif light_type == 'HIGH':
            self.set_headlights('HIGH' if state == 'ON' else 'OFF')
        elif light_type == 'LOW':
            self.set_headlights('LOW' if state == 'ON' else 'OFF')
    
    def get_distance(self):
        """
        Leer distancia del sensor ultrasónico
        Retorna: distancia en centímetros
        """
        # Enviar pulso de trigger
        self.ultrasonic_trigger.value(0)
        utime.sleep_us(2)
        self.ultrasonic_trigger.value(1)
        utime.sleep_us(10)
        self.ultrasonic_trigger.value(0)
        
        # Medir tiempo de eco
        timeout = 30000  # 30ms timeout
        pulse_start = utime.ticks_us()
        
        # Esperar inicio del pulso
        while self.ultrasonic_echo.value() == 0:
            pulse_start = utime.ticks_us()
            if utime.ticks_diff(utime.ticks_us(), pulse_start) > timeout:
                return -1  # Timeout
        
        # Esperar fin del pulso
        pulse_end = utime.ticks_us()
        while self.ultrasonic_echo.value() == 1:
            pulse_end = utime.ticks_us()
            if utime.ticks_diff(pulse_end, pulse_start) > timeout:
                return -1  # Timeout
        
        # Calcular distancia
        pulse_duration = utime.ticks_diff(pulse_end, pulse_start)
        distance = (pulse_duration * 0.0343) / 2  # Velocidad del sonido
        
        return distance
    
    def stop_all(self):
        """Detener todo y resetear a estado seguro"""
        self.stop_motors()
        self.center_steering()
        self.set_brake_lights(True)
        self.set_turn_signals('OFF', False)
        self.set_headlights('OFF')
        print("All hardware stopped")