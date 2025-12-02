# 4. evaluador_modelo.py
# Evalúa el modelo y genera métricas

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix, accuracy_score, classification_report

class EvaluadorModelo:
    def __init__(self, modelo, codificador):
        self.modelo = modelo
        self.codificador = codificador
    
    def obtener_predicciones(self, dataset):
        # Obtener etiquetas verdaderas y predicciones
        y_true = []
        y_pred_probs = []
        
        print("Generando predicciones...")
        for imagenes, etiquetas in dataset:
            # Etiquetas verdaderas
            y_true.extend(np.argmax(etiquetas.numpy(), axis=1))
            # Predicciones
            y_pred_probs.extend(self.modelo.predict(imagenes, verbose=0))
        
        y_true = np.array(y_true)
        y_pred = np.argmax(np.array(y_pred_probs), axis=1)
        
        return y_true, y_pred
    
    def generar_matriz_confusion(self, y_true, y_pred, mostrar=True):
        # Calcular matriz de confusión
        cm = confusion_matrix(y_true, y_pred)
        nombres_clases = self.codificador.classes_
        
        print("\n--- Matriz de Confusión ---")
        print(cm)
        
        if mostrar:
            plt.figure(figsize=(10, 8))
            sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                       xticklabels=nombres_clases, 
                       yticklabels=nombres_clases)
            plt.title('Matriz de Confusión')
            plt.ylabel('Etiqueta Verdadera')
            plt.xlabel('Etiqueta Predicha')
            plt.tight_layout()
            plt.show()
        
        return cm
    
    def calcular_metricas(self, y_true, y_pred):
        # Accuracy
        accuracy = accuracy_score(y_true, y_pred)
        print(f"\n✓ Accuracy final: {accuracy*100:.2f}%")
        
        # Reporte de clasificación
        print("\n--- Reporte de Clasificación ---")
        nombres_clases = self.codificador.classes_
        print(classification_report(y_true, y_pred, target_names=nombres_clases))
        
        return accuracy