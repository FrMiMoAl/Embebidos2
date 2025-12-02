import tensorflow as tf
import cv2
import numpy as np
from sklearn.preprocessing import LabelEncoder

# Configuración
RUTA_MODELO = 'modelo_marcadores.h5'
TAMAÑO_IMAGEN = (256, 256)
CLASES = ['azul', 'borrador', 'negro', 'rojo']  # Ajustar según tu dataset

def clasificar_imagen(ruta_imagen):
    # Cargar modelo
    print("Cargando modelo...")
    modelo = tf.keras.models.load_model(RUTA_MODELO)
    
    # Configurar codificador
    codificador = LabelEncoder()
    codificador.fit(CLASES)
    
    # Cargar y preprocesar imagen
    print(f"Clasificando: {ruta_imagen}")
    img = cv2.imread(ruta_imagen)
    if img is None:
        print("Error: No se pudo cargar la imagen")
        return
    
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = cv2.resize(img, TAMAÑO_IMAGEN)
    img = img / 255.0
    img = np.expand_dims(img, axis=0)
    
    # Predecir
    predicciones = modelo.predict(img, verbose=0)[0]
    clase_id = np.argmax(predicciones)
    confianza = predicciones[clase_id]
    clase_nombre = codificador.classes_[clase_id]
    
    # Mostrar resultado
    print(f"\n✓ Clase: {clase_nombre}")
    print(f"✓ Confianza: {confianza*100:.2f}%")
    print("\nProbabilidades por clase:")
    for i, clase in enumerate(codificador.classes_):
        print(f"  {clase}: {predicciones[i]*100:.2f}%")

def main():
    import sys
    
    if len(sys.argv) < 2:
        print("Uso: python app_clasificar_imagen.py <ruta_imagen>")
        print("Ejemplo: python app_clasificar_imagen.py imagen.jpg")
        return
    
    ruta_imagen = sys.argv[1]
    clasificar_imagen('/home/samuel/Downloads/20251122_202408.jpg')

if __name__ == "__main__":
    main()