from cargador_datos import CargadorDatos
from procesador_datos import ProcesadorDatos
from modelo_cnn import ModeloCNN
from evaluador_modelo import EvaluadorModelo

# Configuración
RUTA_BASE = '/home/samuel/Downloads/Embebidos/embebidos.v11i.tensorflow'
TAMAÑO_IMAGEN = (256, 256)
BATCH_SIZE = 32
RUTA_MODELO = 'modelo_marcadores.h5'

def main():
    print("="*50)
    print("EVALUACIÓN DE MODELO PRE-ENTRENADO")
    print("="*50)
    
    # 1. Cargar datos
    cargador = CargadorDatos(RUTA_BASE)
    datos = cargador.cargar_todo()
    
    # 2. Procesar datos
    procesador = ProcesadorDatos(TAMAÑO_IMAGEN, BATCH_SIZE)
    train_enc, valid_enc, test_enc = procesador.codificar_etiquetas(datos)
    test_ds = procesador.crear_dataset(datos['test'][0], test_enc)
    
    # 3. Cargar modelo
    modelo = ModeloCNN(TAMAÑO_IMAGEN, procesador.num_clases)
    modelo.cargar(RUTA_MODELO)
    
    # 4. Evaluar
    modelo.evaluar(test_ds)
    
    # 5. Métricas detalladas
    evaluador = EvaluadorModelo(modelo.modelo, procesador.codificador)
    y_true, y_pred = evaluador.obtener_predicciones(test_ds)
    evaluador.generar_matriz_confusion(y_true, y_pred)
    evaluador.calcular_metricas(y_true, y_pred)
    
    print("\n✓ Evaluación completada")

if __name__ == "__main__":
    main()