# 2. procesador_datos.py
# Procesa y prepara datos para TensorFlow
import tensorflow as tf
import numpy as np
from sklearn.preprocessing import LabelEncoder

class ProcesadorDatos:
    def __init__(self, tamaño_imagen=(256, 256), batch_size=32):
        self.tamaño_imagen = tamaño_imagen
        self.batch_size = batch_size
        self.codificador = LabelEncoder()
        self.num_clases = 0
    
    def codificar_etiquetas(self, etiquetas_dict):
        # Combinar todas las etiquetas
        todas_etiquetas = (
            etiquetas_dict['train'][1] + 
            etiquetas_dict['valid'][1] + 
            etiquetas_dict['test'][1]
        )
        
        # Entrenar el codificador
        self.codificador.fit(todas_etiquetas)
        self.num_clases = len(self.codificador.classes_)
        
        print(f"✓ Encontradas {self.num_clases} clases: {list(self.codificador.classes_)}")
        
        # Codificar cada conjunto
        train_encoded = self.codificador.transform(etiquetas_dict['train'][1])
        valid_encoded = self.codificador.transform(etiquetas_dict['valid'][1])
        test_encoded = self.codificador.transform(etiquetas_dict['test'][1])
        
        return train_encoded, valid_encoded, test_encoded
    
    def crear_dataset(self, rutas_imagenes, etiquetas_codificadas):
        # Función interna para cargar y preprocesar
        def cargar_y_preprocesar(ruta, etiqueta):
            # Leer imagen
            img = tf.io.read_file(ruta)
            img = tf.image.decode_jpeg(img, channels=3)
            # Redimensionar y normalizar
            img = tf.image.resize(img, self.tamaño_imagen)
            img = img / 255.0
            # One-hot encoding
            etiqueta = tf.one_hot(etiqueta, depth=self.num_clases)
            return img, etiqueta
        
        # Crear dataset
        dataset = tf.data.Dataset.from_tensor_slices((rutas_imagenes, etiquetas_codificadas))
        dataset = dataset.map(cargar_y_preprocesar, num_parallel_calls=tf.data.AUTOTUNE)
        dataset = dataset.shuffle(buffer_size=1000).batch(self.batch_size)
        dataset = dataset.prefetch(tf.data.AUTOTUNE)
        
        return dataset