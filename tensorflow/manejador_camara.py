import cv2

class ManejadorCamara:
    def __init__(self, indice_camara=0):
        print(f"Abriendo cámara {indice_camara}...")
        self.camara = cv2.VideoCapture(indice_camara)
        
        if not self.camara.isOpened():
            raise Exception("No se pudo abrir la cámara")
        
        print("✓ Cámara abierta")
    
    def leer_frame(self):
        # Lee un frame de la cámara
        ok, frame = self.camara.read()
        if not ok:
            return None
        return frame
    
    def mostrar_frame(self, frame, nombre_ventana="Camara"):
        # Muestra el frame en una ventana
        cv2.imshow(nombre_ventana, frame)
    
    def verificar_tecla_salida(self, espera_ms=1):
        # Verifica si se presionó 'q' o ESC
        tecla = cv2.waitKey(espera_ms) & 0xFF
        return tecla == ord('q') or tecla == 27
    
    def cerrar(self):
        self.camara.release()
        cv2.destroyAllWindows()
        print("✓ Cámara cerrada")