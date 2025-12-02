import cv2
import numpy as np
import tensorflow as tf
from sklearn.preprocessing import LabelEncoder

class ClasificadorTiempoReal:
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
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = img / 255.0
        img = np.expand_dims(img, axis=0)
        return img
    
    def clasificar(self, frame):
        # Preprocesar
        img = self.preprocesar_frame(frame)
        
        # Predecir
        predicciones = self.modelo.predict(img, verbose=0)[0]
        clase_id = np.argmax(predicciones)
        confianza = predicciones[clase_id]
        clase_nombre = self.codificador.classes_[clase_id]
        
        return clase_nombre, confianza, predicciones
    
    def dibujar_clasificacion(self, frame, clase, confianza):
        # Dibujar resultado en el frame
        texto = f"Clase: {clase}"
        conf_texto = f"Confianza: {confianza*100:.1f}%"
        
        cv2.putText(frame, texto, (20, 50),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, conf_texto, (20, 90),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        return frame
    
    def dibujar_probabilidades(self, frame, predicciones):
        # Dibujar todas las probabilidades
        y = 140
        for i, clase in enumerate(self.codificador.classes_):
            prob = predicciones[i] * 100
            texto = f"{clase}: {prob:.1f}%"
            cv2.putText(frame, texto, (20, y),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
            y += 30
        return frame