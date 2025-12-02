import tensorflow as tf
from tensorflow import keras
import cv2
import numpy as np

# 1. Cargar el modelo
try:
    # Asegúrate de que la ruta sea correcta
    model = keras.models.load_model('/home/samuel/Downloads/Embebidos/embebidos.v11i.tensorflow/model.h5') 
    print("Modelo cargado exitosamente.")
except Exception as e:
    print(f"Error al cargar el modelo: {e}")
    exit()

# 2. Definir las etiquetas (en el orden que tu modelo las espera)
etiquetas = ["borrador", "marcador rojo", "marcador negro", "marcador azul"]

# Inicializar la captura de video (0 generalmente es la cámara por defecto)
cap = cv2.VideoCapture(2)

if not cap.isOpened():
    print("Error: No se pudo abrir la cámara.")
    exit()

# Definir el tamaño de entrada que tu modelo espera (esto es crucial)
# Ajusta 'input_size' al tamaño con el que entrenaste tu modelo (ej: 224, 224)
input_size = (256,256)

while True:
    # 1. Capturar frame por frame
    ret, frame = cap.read()
    if not ret:
        break # Si no se puede leer el frame, salimos del bucle

    # 2. Preprocesar el frame para la entrada del modelo
    # a) Redimensionar al tamaño esperado por el modelo
    input_frame = cv2.resize(frame, input_size) 
    # b) Convertir a un array de Numpy y añadir la dimensión de batch
    # El modelo espera una forma (1, alto, ancho, canales)
    input_data = np.expand_dims(input_frame, axis=0)
    
    # c) **NORMALIZACIÓN CRUCIAL**: Normaliza como lo hiciste en el entrenamiento
    # Si normalizaste a [0, 1]
    input_data = input_data / 255.0 

    # 3. Realizar la Predicción
    # El resultado dependerá de la salida de tu modelo (ej: YOLO, RetinaNet, clasificador simple)
    predicciones = model.predict(input_data)
    
    # 4. Interpretar y Mostrar Resultados
    
    # --- EJEMPLO para un modelo de CLASIFICACIÓN (si tu detección es a nivel de imagen) ---
    # Si tu modelo es un CLASIFICADOR que predice una de las 4 etiquetas:
    
    clase_predicha_idx = np.argmax(predicciones[0])
    confianza = np.max(predicciones[0])
    
    clase_predicha = etiquetas[clase_predicha_idx]
    
    texto_a_mostrar = f"Detectado: {clase_predicha} ({confianza:.2f})"
    
    # Mostrar el texto en el frame original
    cv2.putText(frame, texto_a_mostrar, (10, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
    
    # 5. Mostrar el frame
    cv2.imshow('Deteccion en Tiempo Real', frame)

    # 6. Salir del bucle con la tecla 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 7. Liberar recursos
cap.release()
cv2.destroyAllWindows()