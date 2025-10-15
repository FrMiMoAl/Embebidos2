"""
==================================

                    PIPICO

==================================
Configuración del Sistema - Raspberry Pi Pico W
Centraliza todos los parámetros configurables
"""

# Configuración de Comunicación
class CommunicationConfig:
    # UART
    UART_ID = 0
    UART_TIMEOUT = 100  # ms
    BUFFER_SIZE = 1024
    
    # Protocolo de comandos
    COMMAND_DELIMITER = ':'
    LINE_ENDING = '\n'
    
    # Intervalo de telemetría
    TELEMETRY_INTERVAL_MS = 1000  # Enviar estado cada 1 segundo


# Configuración General del Sistema
class SystemConfig:
    # Threading
    MAIN_LOOP_DELAY_MS = 50  # Delay en loop principal
    UART_LISTENER_DELAY_MS = 10  # Delay en listener UART
    
    # Timeouts
    MODEL_SWITCH_TIMEOUT_MS = 5000
    COMMAND_TIMEOUT_MS = 3000
    
    # Seguridad
    WATCHDOG_ENABLED = False
    WATCHDOG_TIMEOUT_MS = 8000
    
    # Debug
    DEBUG_MODE = True
    VERBOSE_LOGGING = False # de Pines GPIO
class PinConfig:
    # UART
    UART_TX = 0
    UART_RX = 1
    UART_BAUDRATE = 115200
    
    # Motores (Motor Driver)
    MOTOR_LEFT_BIN1 = 20
    MOTOR_LEFT_BIN2 = 21
    MOTOR_LEFT_PWM = 22

    MOTOR_RIGHT_AIN1 = 18
    MOTOR_RIGHT_AIN2 = 17
    MOTOR_RIGHT_PWM = 16
    
    # Servomotor de dirección
    STEERING_SERVO = 8
    
    # Luces
    BRAKE_LIGHTS = 7
    TURN_LEFT = 8
    TURN_RIGHT = 9
    HEADLIGHTS = 10
    
    # Sensor ultrasónico
    ULTRASONIC_TRIGGER = 11
    ULTRASONIC_ECHO = 12


# Configuración de Motor
class MotorConfig:
    PWM_FREQUENCY = 1000  # Hz
    MAX_SPEED = 100  # Velocidad máxima (0-100)
    MIN_SPEED = 0
    
    # Calibración de motores
    LEFT_MOTOR_CALIBRATION = 1.0  # Factor de corrección
    RIGHT_MOTOR_CALIBRATION = 1.0


# Configuración de Servo
class ServoConfig:
    PWM_FREQUENCY = 50  # Hz (estándar para servos)
    CENTER_ANGLE = 0
    MAX_LEFT_ANGLE = -20
    MAX_RIGHT_ANGLE = 20
    
    # Pulsos en microsegundos
    MIN_PULSE_US = 1000  # 1ms
    CENTER_PULSE_US = 1500  # 1.5ms
    MAX_PULSE_US = 2000  # 2ms


# Configuración de Luces
class LightConfig:
    PWM_FREQUENCY = 1000  # Hz
    
    # Niveles de brillo PWM (0-65535)
    BRAKE_NORMAL = 32768  # 50%
    BRAKE_ACTIVE = 65535  # 100%
    
    HEADLIGHT_OFF = 0
    HEADLIGHT_LOW = 32768  # 50%
    HEADLIGHT_HIGH = 65535  # 100%
    
    # Intermitentes
    BLINK_FREQUENCY = 500  # ms entre parpadeos


# Configuración de Sensores
class SensorConfig:
    # Ultrasónico
    ULTRASONIC_TIMEOUT = 30000  # microsegundos
    SOUND_SPEED = 0.0343  # cm/us (velocidad del sonido / 2)
    
    # Umbrales
    OBSTACLE_DISTANCE_CM = 20  # Distancia mínima para detectar obstáculo
    WARNING_DISTANCE_CM = 50  # Distancia de advertencia


# Configuración de Modelos
class ModelConfig:
    # Modelo A
    MODEL_A_FORWARD_SPEED = 50  # Velocidad de avance
    MODEL_A_ROTATION_SPEED = 40  # Velocidad de rotación
    MODEL_A_ROTATION_TIME = 2000  # ms para rotar 180°
    MODEL_A_TURN_SPEED = 30  # Velocidad durante giros
    MODEL_A_MS_PER_DEGREE = 20  # ms necesarios por grado de giro
    
    # Modelo B
    MODEL_B_DEFAULT_SPEED = 0
    
    # Modelo C (por implementar)
    MODEL_C_ENABLED = False
    
    # Modelo D (por implementar)
    MODEL_D_ENABLED = False


# Configuración