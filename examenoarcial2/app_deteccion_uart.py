# ========================================
# 5. app_deteccion_uart.py
# Aplicación con detección y envío UART
# ========================================
from detector_yolo import DetectorYOLO
from manejador_camara import ManejadorCamara
from comunicacion_uart import ComunicacionUART

# Configuración
MODELO = "runs_marker/yolov8n_markers5/weights/best.pt"
CONFIANZA = 0.5
CAMARA = 0
PUERTO_SERIAL = "/dev/ttyAMA0"#"/dev/ttyUSB0"
BAUDRATE = 115200

def main():
    print("=== Detector de Marcadores + UART ===\n")
    
    try:
        # Inicializar componentes
        detector = DetectorYOLO(MODELO, CONFIANZA)
        camara = ManejadorCamara(CAMARA)
        uart = ComunicacionUART(PUERTO_SERIAL, BAUDRATE)
        
        print("\n✓ Sistema listo")
        print("Presiona 'q' o ESC para salir\n")
        
        # Bucle principal
        while True:
            # Leer frame
            frame = camara.leer_frame()
            if frame is None:
                break
            
            # Detectar marcadores
            detecciones, conteos = detector.detectar(frame)
            
            # Enviar por UART
            uart.enviar_conteos(conteos)
            
            # Dibujar detecciones
            frame = detector.dibujar_detecciones(frame, detecciones)
            
            # Mostrar conteos
            frame = camara.mostrar_conteos(frame, conteos)
            
            # Mostrar frame
            camara.mostrar_frame(frame, "Detector + UART")
            
            # Verificar salida
            if camara.verificar_tecla_salida():
                break
    
    except KeyboardInterrupt:
        print("\nInterrumpido por usuario")
    except Exception as e:
        print(f"Error: {e}")
    
    finally:
        uart.cerrar()
        camara.cerrar()
        print("✓ Programa finalizado")

if __name__ == "__main__":
    main()
