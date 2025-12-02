# 3. modelo_cnn.py
# Define y entrena el modelo CNN
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense

class ModeloCNN:
    def __init__(self, tamaño_imagen, num_clases):
        self.tamaño_imagen = tamaño_imagen
        self.num_clases = num_clases
        self.modelo = self._construir_modelo()
    
    def _construir_modelo(self):
        # Arquitectura CNN
        modelo = Sequential([
            # Bloque 1
            Conv2D(32, (3, 3), activation='relu', 
                   input_shape=(self.tamaño_imagen[0], self.tamaño_imagen[1], 3)),
            MaxPooling2D((2, 2)),
            
            # Bloque 2
            Conv2D(64, (3, 3), activation='relu'),
            MaxPooling2D((2, 2)),
            
            # Bloque 3
            Conv2D(128, (3, 3), activation='relu'),
            MaxPooling2D((2, 2)),
            
            # Bloque 4
            Conv2D(256, (3, 3), activation='relu'),
            MaxPooling2D((2, 2)),
            
            # Bloque 5
            Conv2D(512, (3, 3), activation='relu'),
            MaxPooling2D((2, 2)),
            
            # Capas densas
            Flatten(),
            Dense(512, activation='relu'),
            Dense(self.num_clases, activation='softmax')
        ])
        
        return modelo
    
    def compilar(self):
        self.modelo.compile(
            optimizer='adam',
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )
        print("✓ Modelo compilado")
    
    def resumen(self):
        self.modelo.summary()
    
    def entrenar(self, train_ds, valid_ds, epochs=75):
        print(f"\n--- Iniciando entrenamiento ({epochs} épocas) ---")
        historial = self.modelo.fit(
            train_ds,
            validation_data=valid_ds,
            epochs=epochs
        )
        print("✓ Entrenamiento finalizado")
        return historial
    
    def evaluar(self, test_ds):
        print("\n--- Evaluando modelo en test ---")
        loss, accuracy = self.modelo.evaluate(test_ds)
        print(f"✓ Accuracy en test: {accuracy*100:.2f}%")
        return loss, accuracy
    
    def guardar(self, ruta='modelo_marcadores.h5'):
        self.modelo.save(ruta)
        print(f"✓ Modelo guardado en '{ruta}'")
    
    def cargar(self, ruta):
        self.modelo = tf.keras.models.load_model(ruta)
        print(f"✓ Modelo cargado desde '{ruta}'")