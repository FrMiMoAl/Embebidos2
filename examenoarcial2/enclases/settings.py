class Config:
    # Modelo
    MODEL_PATH = "mejor_modelo_multilabelND.pth"
    IMAGE_SIZE = 224 
    DEVICE = "cpu"
    
    # Umbrales de detección
    UMBRAL_DETECCION = 0.30
    UMBRAL_MINIMO = 0.3
    
    # Cámara
    CAMERA_INDEX = 0
    CAMERA_WIDTH = 640
    CAMERA_HEIGHT = 480
    
    # UART
    UART_PORT = "/dev/ttyUSB0"  # Cambiar según tu sistema
    UART_BAUDRATE = 9600
    UART_TIMEOUT = 1
    
    # modelo
    LABEL_COLUMNS = ["Borrador", "Azul", "Negro", "Rojo","ND"]
    
    # Visualización
    FONT = 3
    FONT_SCALE = 0.8
    FONT_THICKNESS = 2