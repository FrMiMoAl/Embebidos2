# ========================================
# 1. detector_yolo.py
# Maneja la detección con YOLO
# ========================================
from ultralytics import YOLO
import cv2

class DetectorYOLO:
    def __init__(self, ruta_modelo, confianza=0.5):
        print(f"Cargando modelo: {ruta_modelo}")
        self.modelo = YOLO(ruta_modelo)
        self.confianza = confianza
        
        # Mapeo de IDs a nombres de colores
        self.colores = {
            0: "borrador",
            1: "azul",
            2: "negro",
            3: "rojo"
        }
    
    def detectar(self, frame):
        # Ejecutar detección
        resultados = self.modelo(frame, conf=self.confianza, verbose=False)[0]
        
        # Inicializar conteos
        conteos = {color: 0 for color in self.colores.values()}
        detecciones = []
        
        # Procesar cada detección
        for caja in resultados.boxes:
            x1, y1, x2, y2 = map(int, caja.xyxy[0].cpu().numpy())
            clase_id = int(caja.cls[0])
            conf = float(caja.conf[0])
            color = self.colores.get(clase_id, "desconocido")
            
            # Guardar detección
            detecciones.append({
                "color": color,
                "confianza": conf,
                "coordenadas": (x1, y1, x2, y2)
            })
            
            # Contar
            if color in conteos:
                conteos[color] += 1
        
        return detecciones, conteos
    
    def dibujar_detecciones(self, frame, detecciones):
        # Dibujar cada detección en el frame
        for det in detecciones:
            x1, y1, x2, y2 = det["coordenadas"]
            color = det["color"]
            conf = det["confianza"]
            
            # Dibujar rectángulo
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
            # Dibujar etiqueta
            etiqueta = f"{color} {conf:.2f}"
            cv2.putText(frame, etiqueta, (x1, y1 - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        return frame