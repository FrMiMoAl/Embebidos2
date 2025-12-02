# 1. cargador_datos.py
# Maneja la carga de datos desde CSV 

import pandas as pd
import os

class CargadorDatos:
    def __init__(self, ruta_base):
        self.ruta_base = ruta_base
    
    def cargar_desde_csv(self, carpeta, archivo_csv='_annotations.csv'):
        # Cargar CSV
        ruta_csv = os.path.join(self.ruta_base, carpeta, archivo_csv)
        df = pd.read_csv(ruta_csv)
        
        # Obtener nombres de columnas
        columna_archivo = df.columns[0]  # Primera columna = nombre archivo
        columna_etiqueta = 'class'        # Columna de clases
        
        # Crear rutas completas
        df['full_path'] = df[columna_archivo].apply(
            lambda x: os.path.join(self.ruta_base, carpeta, x)
        )
        
        # Filtrar solo imágenes que existen
        df = df[df['full_path'].apply(os.path.exists)]
        
        imagenes = df['full_path'].tolist()
        etiquetas = df[columna_etiqueta].tolist()
        
        print(f"✓ Cargadas {len(imagenes)} imágenes de '{carpeta}'")
        return imagenes, etiquetas
    
    def cargar_todo(self):
        # Cargar train, valid y test
        print("Cargando datos...")
        train_imgs, train_lbls = self.cargar_desde_csv('train')
        valid_imgs, valid_lbls = self.cargar_desde_csv('valid')
        test_imgs, test_lbls = self.cargar_desde_csv('test')
        
        return {
            'train': (train_imgs, train_lbls),
            'valid': (valid_imgs, valid_lbls),
            'test': (test_imgs, test_lbls)
        }