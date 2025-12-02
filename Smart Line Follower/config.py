"""
config.py - Configuración centralizada del sistema

Todas las configuraciones de video, motores, red, etc.
Modifica estos valores según tu setup
"""

# ============================================================================
# CONFIGURACIÓN DE VIDEO
# ============================================================================

# Fuente de video - Opciones:
# - URL HLS: "https://example.com/stream/index.m3u8"
# - RTSP: "rtsp://192.168.1.10:8554/unicast"
# - Cámara USB: 0, 1, 2... (índice de cámara)
# - Archivo: "video.mp4"

#VIDEO_SOURCE = "https://finder-blogging-married-chocolate.trycloudflare.com/cam/index.m3u8"
VIDEO_SOURCE = 0  # Descomentar para usar cámara USB local
# VIDEO_SOURCE = "rtsp://192.168.1.10:8554/unicast"  # RTSP desde Raspberry Pi

# Resolución del video
VIDEO_WIDTH = 800
VIDEO_HEIGHT = 600

# Frames por segundo
VIDEO_FPS = 30

# Timeout de reconexión en segundos
VIDEO_RECONNECT_TIMEOUT = 5

# Habilitar grabación de video (requiere espacio en disco)
VIDEO_RECORDING_ENABLED = False
VIDEO_RECORDING_PATH = "recordings/"

# ============================================================================
# CONFIGURACIÓN DE CONTROL DE MOTORES
# ============================================================================

# Puerto serial para comunicación con Arduino/controlador de motores
MOTOR_UART_PORT = "/dev/ttyUSB0"  # Linux/macOS
# MOTOR_UART_PORT = "COM3"  # Windows

# Baudrate de comunicación serial
MOTOR_BAUDRATE = 115200

# Velocidad base de los motores (0-255)
BASE_SPEED = 50

# Velocidad máxima permitida
MAX_SPEED = 255

# Velocidad en modo turbo
TURBO_SPEED = 200

# Protocolo de comandos (personalizable según tu Arduino)
MOTOR_COMMANDS = {
    "forward": "F",
    "backward": "B",
    "left": "L",
    "right": "R",
    "stop": "S",
    "turbo": "T"
}

# ============================================================================
# CONFIGURACIÓN SSH (RASPBERRY PI)
# ============================================================================

# Dirección IP de la Raspberry Pi
SSH_HOST = "192.168.1.100"
# SSH_HOST = "raspberrypi.local"  # Usar hostname si está en la misma red

# Puerto SSH (default 22)
SSH_PORT = 22

# Usuario SSH
SSH_USERNAME = "pi"

# Contraseña SSH (dejar vacío si usas clave pública)
SSH_PASSWORD = ""

# Ruta a archivo de clave privada SSH (opcional)
SSH_KEY_FILE = None
# SSH_KEY_FILE = "/home/user/.ssh/id_rsa"

# Timeout de conexión SSH en segundos
SSH_TIMEOUT = 10

# Scripts remotos en la Raspberry Pi
SSH_SCRIPTS = {
    "autopilot": "/home/pi/scripts/autopilot.py",
    "sensors": "/home/pi/scripts/read_sensors.py",
    "calibrate": "/home/pi/scripts/calibrate.py"
}

# ============================================================================
# CONFIGURACIÓN DEL DASHBOARD
# ============================================================================

# Tamaño de ventana
WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 800

# Archivo de configuración de colores e imágenes
CONFIG_FILE = "cfg_dashboard.json"

# Archivo de sesión
SESSION_FILE = "session.json"

# Habilitar modo debug (muestra más información en consola)
DEBUG_MODE = True

# Intervalo de actualización de estadísticas de red (ms)
NETWORK_UPDATE_INTERVAL = 1000

# ============================================================================
# CONFIGURACIÓN DE FUNCIONES ESPECIALES
# ============================================================================

# Duración del modo turbo en segundos
TURBO_DURATION = 5

# Habilitar detección de obstáculos
OBSTACLE_DETECTION_ENABLED = True

# Distancia mínima de obstáculo en cm
OBSTACLE_MIN_DISTANCE = 20

# Habilitar seguimiento de línea automático
AUTO_LINE_FOLLOW = True

# Sensibilidad del seguimiento (1-10)
LINE_FOLLOW_SENSITIVITY = 7

# ============================================================================
# CONFIGURACIÓN DE SENSORES
# ============================================================================

# Pines GPIO para sensores (Raspberry Pi)
GPIO_PINS = {
    "ir_left": 17,
    "ir_center": 27,
    "ir_right": 22,
    "ultrasonic_trigger": 23,
    "ultrasonic_echo": 24,
    "led_status": 25
}

# Frecuencia de lectura de sensores (Hz)
SENSOR_READ_FREQUENCY = 50

# ============================================================================
# CONFIGURACIÓN DE LOGGING
# ============================================================================

# Habilitar logging a archivo
LOG_TO_FILE = True

# Archivo de log
LOG_FILE = "dashboard.log"

# Nivel de logging: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL = "INFO"

# Formato del log
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Habilitar telemetría (guardar datos de sensores)
TELEMETRY_ENABLED = True
TELEMETRY_FILE = "telemetry.csv"

# ============================================================================
# CONFIGURACIÓN DE RED
# ============================================================================

# Puerto para servidor web de control (opcional)
WEB_SERVER_PORT = 8080

# Habilitar API REST para control remoto
REST_API_ENABLED = False

# Puerto de API REST
REST_API_PORT = 5000

# ============================================================================
# CONFIGURACIÓN AVANZADA
# ============================================================================

# Límite de FPS para ahorro de recursos
FPS_LIMIT = 30

# Calidad de compresión de video (1-100, 100=máxima calidad)
VIDEO_QUALITY = 85

# Buffer de frames de video
VIDEO_FRAME_BUFFER = 5

# Timeout de comandos en ms
COMMAND_TIMEOUT = 500

# Número de intentos de reconexión
MAX_RECONNECT_ATTEMPTS = 3

# ============================================================================
# FUNCIONES DE UTILIDAD
# ============================================================================

def get_video_config():
    """Retorna configuración de video como diccionario"""
    return {
        "source": VIDEO_SOURCE,
        "width": VIDEO_WIDTH,
        "height": VIDEO_HEIGHT,
        "fps": VIDEO_FPS,
        "reconnect_timeout": VIDEO_RECONNECT_TIMEOUT
    }

def get_motor_config():
    """Retorna configuración de motores como diccionario"""
    return {
        "port": MOTOR_UART_PORT,
        "baudrate": MOTOR_BAUDRATE,
        "base_speed": BASE_SPEED,
        "max_speed": MAX_SPEED,
        "commands": MOTOR_COMMANDS
    }

def get_ssh_config():
    """Retorna configuración SSH como diccionario"""
    return {
        "host": SSH_HOST,
        "port": SSH_PORT,
        "username": SSH_USERNAME,
        "password": SSH_PASSWORD,
        "key_file": SSH_KEY_FILE,
        "timeout": SSH_TIMEOUT
    }

def print_config():
    """Imprime toda la configuración (útil para debug)"""
    print("=" * 60)
    print("CONFIGURACIÓN DEL SISTEMA")
    print("=" * 60)
    print(f"\n[VIDEO]")
    print(f"  Source: {VIDEO_SOURCE}")
    print(f"  Resolution: {VIDEO_WIDTH}x{VIDEO_HEIGHT}")
    print(f"  FPS: {VIDEO_FPS}")
    
    print(f"\n[MOTORES]")
    print(f"  Puerto: {MOTOR_UART_PORT}")
    print(f"  Baudrate: {MOTOR_BAUDRATE}")
    print(f"  Velocidad base: {BASE_SPEED}")
    
    print(f"\n[SSH]")
    print(f"  Host: {SSH_HOST}:{SSH_PORT}")
    print(f"  Usuario: {SSH_USERNAME}")
    
    print(f"\n[DASHBOARD]")
    print(f"  Ventana: {WINDOW_WIDTH}x{WINDOW_HEIGHT}")
    print(f"  Debug: {DEBUG_MODE}")
    
    print("=" * 60)

# ============================================================================
# VALIDACIÓN DE CONFIGURACIÓN
# ============================================================================

def validate_config():
    """
    Valida que la configuración sea correcta
    Retorna (es_valida, lista_de_errores)
    """
    errors = []
    
    # Validar resolución de video
    if VIDEO_WIDTH <= 0 or VIDEO_HEIGHT <= 0:
        errors.append("Resolución de video inválida")
    
    # Validar FPS
    if VIDEO_FPS <= 0 or VIDEO_FPS > 120:
        errors.append("FPS debe estar entre 1 y 120")
    
    # Validar velocidades de motor
    if not (0 <= BASE_SPEED <= MAX_SPEED <= 255):
        errors.append("Velocidades de motor inválidas")
    
    # Validar puerto SSH
    if not (1 <= SSH_PORT <= 65535):
        errors.append("Puerto SSH inválido")
    
    return len(errors) == 0, errors


if __name__ == "__main__":
    """Test de configuración"""
    print_config()
    
    print("\n[VALIDACIÓN]")
    is_valid, errors = validate_config()
    
    if is_valid:
        print("✅ Configuración válida")
    else:
        print("❌ Errores encontrados:")
        for error in errors:
            print(f"  - {error}")