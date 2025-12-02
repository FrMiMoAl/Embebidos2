# 8. predictor_tiempo_real.py
# Predicción en tiempo real con cámara (SIN UART)
import cv2
import numpy as np
import tensorflow as tf
from sklearn.preprocessing import LabelEncoder

class PredictorTiempoReal:
    def __init__(self, ruta_modelo, clases, tamaño_imagen=(256, 256)):
        print("Cargando modelo...")
        self.modelo = tf.keras.models.load_model(ruta_modelo)
        self.tamaño_imagen = tamaño_imagen
        
        # Configurar codificador de etiquetas
        self.codificador = LabelEncoder()
        self.codificador.fit(clases)
        
        print("✓ Modelo cargado")
    
    def preprocesar_frame(self, frame):
        # Redimensionar y normalizar
        img = cv2.resize(frame, self.tamaño_imagen)
        img = img / 255.0
        img = np.expand_dims(img, axis=0)  # Agregar dimensión de batch
        return img
    
    def predecir(self, frame):
        # Preprocesar
        img = self.preprocesar_frame(frame)
        
        # Predecir
        predicciones = self.modelo.predict(img, verbose=0)[0]
        clase_id = np.argmax(predicciones)
        confianza = predicciones[clase_id]
        clase_nombre = self.codificador.classes_[clase_id]
        
        return clase_nombre, confianza
    
    def dibujar_prediccion(self, frame, clase, confianza):
        # Dibujar resultado en el frame
        texto = f"{clase}: {confianza*100:.1f}%"
        cv2.putText(frame, texto, (20, 50),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        return frame

def main():
    # Configuración
    RUTA_MODELO = 'modelo_marcadores.h5'
    CLASES = ['azul', 'borrador', 'negro', 'rojo']  # Ajustar según tu dataset
    CAMARA = 0
    
    print("="*50)
    print("PREDICCIÓN EN TIEMPO REAL (SIN UART)")
    print("="*50)
    
    # Inicializar predictor
    predictor = PredictorTiempoReal(RUTA_MODELO, CLASES)
    
    # Abrir cámara
    camara = cv2.VideoCapture(CAMARA)
    if not camara.isOpened():
        print("Error: No se pudo abrir la cámara")
        return
    
    print("\n✓ Sistema listo")
    print("Presiona 'q' para salir\n")
    
    while True:
        ret, frame = camara.read()
        if not ret:
            break
        
        # Predecir
        clase, confianza = predictor.predecir(frame)
        
        # Dibujar
        frame = predictor.dibujar_prediccion(frame, clase, confianza)
        
        # Mostrar
        cv2.imshow("Clasificador en Tiempo Real", frame)
        
        # Salir con 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    camara.release()
    cv2.destroyAllWindows()
    print("✓ Programa finalizado")

if __name__ == "__main__":
    main()