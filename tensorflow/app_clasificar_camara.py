from manejador_camara import ManejadorCamara
from clasificador_tiempo_real import ClasificadorTiempoReal

# Configuración
RUTA_MODELO = 'modelo_marcadores.h5'
CLASES = ['azul', 'borrador', 'negro', 'rojo']  # Ajustar según tu dataset
TAMAÑO_IMAGEN = (256, 256)
CAMARA = 0

def main():
    print("="*50)
    print("CLASIFICACIÓN EN TIEMPO REAL (SIN UART)")
    print("="*50)
    
    try:
        # Inicializar componentes
        clasificador = ClasificadorTiempoReal(RUTA_MODELO, CLASES, TAMAÑO_IMAGEN)
        camara = ManejadorCamara(CAMARA)
        
        print("\n✓ Sistema listo")
        print("Presiona 'q' o ESC para salir\n")
        
        # Bucle principal
        while True:
            # Leer frame
            frame = camara.leer_frame()
            if frame is None:
                break
            
            # Clasificar
            clase, confianza, probabilidades = clasificador.clasificar(frame)
            
            # Dibujar clasificación
            frame = clasificador.dibujar_clasificacion(frame, clase, confianza)
            frame = clasificador.dibujar_probabilidades(frame, probabilidades)
            
            # Mostrar frame
            camara.mostrar_frame(frame, "Clasificador en Tiempo Real")
            
            # Verificar salida
            if camara.verificar_tecla_salida():
                break
    
    except Exception as e:
        print(f"Error: {e}")
    
    finally:
        camara.cerrar()
        print("✓ Programa finalizado")

if __name__ == "__main__":
    main()