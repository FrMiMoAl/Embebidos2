# ========================================
# 4. app_deteccion_simple.py
# Aplicación solo con detección (sin UART)
# ========================================
from detector_yolo import DetectorYOLO
from manejador_camara import ManejadorCamara

# Configuración
MODELO = "runs_marker/yolov8n_markers5/weights/best.pt"
CONFIANZA = 0.5
CAMARA = 0
def main():
    print("=== Detector de Marcadores (Solo visualización) ===\n")
    
    try:
        # Inicializar
        detector = DetectorYOLO(MODELO, CONFIANZA)
        camara = ManejadorCamara(CAMARA)
        
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
            
            # Dibujar detecciones
            frame = detector.dibujar_detecciones(frame, detecciones)
            
            # Mostrar conteos
            frame = camara.mostrar_conteos(frame, conteos)
            
            # Mostrar frame
            camara.mostrar_frame(frame, "Detector de Marcadores")
            
            # Verificar salida
            if camara.verificar_tecla_salida():
                break
    
    except Exception as e:
        print(f"Error: {e}")
    
    finally:
        camara.cerrar()
        print("✓ Programa finalizado")

if __name__ == "__main__":
    main()