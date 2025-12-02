import tensorflow as tf
import cv2
import numpy as np
from datetime import datetime
import time

# --- Cargar modelo ---
model = tf.keras.models.load_model("model.h5")
classes = ['marcador_azul', 'marcador_rojo', 'marcador_negro', 'borrador']

# --- Función de predicción ---
def predict_frame(frame):
    # Redimensionar al tamaño esperado por el modelo
    img = cv2.resize(frame, (256, 256))  # Ajusta según el input de tu modelo
    img = img / 255.0  # Normalizar si el modelo fue entrenado así
    img = np.expand_dims(img, axis=0)  # Batch dimension
    preds = model.predict(img, verbose=0)[0]  # Salida: [prob_clase0, prob_clase1,...]
    return preds

# --- Inicialización cámara ---
cap = cv2.VideoCapture(0)  # 0 para webcam, o ruta a video
if not cap.isOpened():
    raise Exception("No se pudo abrir la cámara/video")

# --- Registro de detecciones ---
log_file = "detecciones.txt"

# Inicializar contador de tiempo
last_log_time = time.time()

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Predicción para el frame actual
    probs = predict_frame(frame)
    
    # Contar detecciones: por simplicidad, asumimos que si prob > 0.5 se cuenta
    counts = [int(p > 0.5) for p in probs]  # Ajusta el umbral si es necesario

    # Verificar si han pasado 2 segundos para registrar
    current_time = time.time()
    if current_time - last_log_time >= 2:
        last_log_time = current_time
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = (f">>Blue Markers: {counts[0]} Red Markers: {counts[1]} "
                     f"Black Markers: {counts[2]} Eraser: {counts[3]} Date: {now}")
        print(log_entry)
        with open(log_file, "a") as f:
            f.write(log_entry + "\n")

    # Salir si presionamos 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()