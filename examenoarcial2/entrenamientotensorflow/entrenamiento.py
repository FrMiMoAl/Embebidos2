import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import confusion_matrix, accuracy_score
import matplotlib.pyplot as plt
import seaborn as sns
import os

BASE_PATH = '/home/samuel/Downloads/Embebidos/embebidos.v11i.tensorflow' 
IMAGE_SIZE = (256, 256) # Tamaño de imagen para entrenamiento rápido
BATCH_SIZE = 32
#########################################
# --- 2. Cargar Datos desde CSV ---
def load_data_from_csv(folder, csv_filename):
    """Carga rutas de imagen y etiquetas desde el CSV."""
    csv_path = os.path.join(BASE_PATH, folder, csv_filename)
    df = pd.read_csv(csv_path)
    LABEL_COLUMN_NAME = 'class' # Nombre correcto de la columna de etiquetas
    FILE_COLUMN_NAME = df.columns[0] # Asume que la primera columna es el nombre del archivo
    
    df['full_path'] = df[FILE_COLUMN_NAME].apply(lambda x: os.path.join(BASE_PATH, folder, x))

    # Filtra por imágenes que realmente existen (opcional pero recomendado)
    df = df[df['full_path'].apply(os.path.exists)]
    
    return df['full_path'].tolist(), df[LABEL_COLUMN_NAME].tolist()

# Cargar datos para entrenamiento y validación
train_images, train_labels = load_data_from_csv('train', '_annotations.csv')
valid_images, valid_labels = load_data_from_csv('valid', '_annotations.csv')
test_images, test_labels = load_data_from_csv('test', '_annotations.csv')

# --- 3. Codificación de Etiquetas (Label Encoding) ---
# Combina todas las etiquetas para un codificador consistente
all_labels = train_labels + valid_labels + test_labels
le = LabelEncoder()
le.fit(all_labels)

# Transforma las etiquetas
train_labels_encoded = le.transform(train_labels)
valid_labels_encoded = le.transform(valid_labels)
test_labels_encoded = le.transform(test_labels)

NUM_CLASSES = len(le.classes_)

# --- 4. Crear Generadores de Datos de TensorFlow (para Clasificación) ---
def create_dataset(image_paths, labels_encoded):
    """Crea un tf.data.Dataset para cargar y preprocesar imágenes."""
    
    def load_and_preprocess_image(path, label):
        # Carga la imagen
        img = tf.io.read_file(path)
        img = tf.image.decode_jpeg(img, channels=3)
        # Redimensiona y normaliza
        img = tf.image.resize(img, IMAGE_SIZE)
        img = img / 255.0
        # Convierte la etiqueta a formato One-Hot
        label = tf.one_hot(label, depth=NUM_CLASSES)
        return img, label

    dataset = tf.data.Dataset.from_tensor_slices((image_paths, labels_encoded))
    dataset = dataset.map(load_and_preprocess_image, num_parallel_calls=tf.data.AUTOTUNE)
    dataset = dataset.shuffle(buffer_size=1000).batch(BATCH_SIZE).prefetch(tf.data.AUTOTUNE)
    return dataset

train_ds = create_dataset(train_images, train_labels_encoded)
valid_ds = create_dataset(valid_images, valid_labels_encoded)
test_ds = create_dataset(test_images, test_labels_encoded)
##########################################

model = Sequential([

    Conv2D(32, (3, 3), activation='relu', input_shape=(IMAGE_SIZE[0], IMAGE_SIZE[1], 3)),
    MaxPooling2D((2, 2)),
    
    Conv2D(64, (3, 3), activation='relu'),
    MaxPooling2D((2, 2)),
    
    Conv2D(128, (3, 3), activation='relu'),
    MaxPooling2D((2, 2)),

    Conv2D(256, (3, 3), activation='relu'),
    MaxPooling2D((2, 2)),

    Conv2D(512, (3, 3), activation='relu'),
    MaxPooling2D((2, 2)),


    Flatten(),
    Dense(512, activation='relu'),
    Dense(NUM_CLASSES, activation='softmax') # La capa de salida debe tener el número de clases
])

# --- 6. Compilación del Modelo ---
model.compile(optimizer='adam',
              loss='categorical_crossentropy',
              metrics=['accuracy'])

print("Resumen del Modelo:")
model.summary()

# --- 7. Entrenamiento del Modelo ---
# Usa los conjuntos de entrenamiento y validación
EPOCHS = 75 # Se recomienda aumentar las épocas para mejor rendimiento

print("\n--- Iniciando Entrenamiento ---")
history = model.fit(
    train_ds,
    validation_data=valid_ds,
    epochs=EPOCHS
)

print("\n--- Entrenamiento Finalizado ---")


# --- 8. Evaluación en el Conjunto de Prueba ---
print("\n--- Evaluación en el Conjunto de Prueba ---")
loss, accuracy = model.evaluate(test_ds)
print(f"Accuracy del Modelo en Test: {accuracy*100:.2f}%")

# --- 9. Generar Matriz de Confusión ---

def get_labels_and_predictions(dataset, model):
    """Obtiene las etiquetas verdaderas y predicciones del dataset."""
    y_true = []
    y_pred_probs = []
    
    for images, labels in dataset:
        # Obtener etiquetas verdaderas
        y_true.extend(np.argmax(labels.numpy(), axis=1))
        # Obtener predicciones
        y_pred_probs.extend(model.predict(images, verbose=0))
    
    y_true_int = np.array(y_true)
    y_pred_int = np.argmax(np.array(y_pred_probs), axis=1)
    
    return y_true_int, y_pred_int

# Obtener predicciones
y_true_final, y_pred_final = get_labels_and_predictions(test_ds, model)

# Generar matriz de confusión
cm = confusion_matrix(y_true_final, y_pred_final)
class_names = le.classes_

print("\n--- Matriz de Confusión ---")
print(cm)

# Visualizar matriz de confusión
plt.figure(figsize=(10, 8))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
            xticklabels=class_names, yticklabels=class_names)
plt.title('Matriz de Confusión - Conjunto de Prueba')
plt.ylabel('Etiqueta Verdadera')
plt.xlabel('Etiqueta Predicha')
plt.tight_layout()
plt.show()


# Calcular accuracy final
final_accuracy = accuracy_score(y_true_final, y_pred_final)
print(f"\nAccuracy Final: {final_accuracy*100:.2f}%")

model.save('model.h5')
print("Model saved as 'model.h5'")