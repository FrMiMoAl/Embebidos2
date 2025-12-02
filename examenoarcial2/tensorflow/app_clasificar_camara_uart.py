from manejador_camara import ManejadorCamara
from clasificador_tiempo_real import ClasificadorTiempoReal
from comunicacion_uart import ComunicacionUART

# Configuración
RUTA_MODELO = 'modelo_marcadores.h5'
CLASES = ['marcador azul', 'borrador', 'marcador negro', 'marcador rojo']  # Ajustar según tu dataset
TAMAÑO_IMAGEN = (256, 256)
CAMARA = 0
PUERTO_SERIAL = '/dev/ttyUSB0'  # Cambiar según tu sistema
BAUDRATE = 115200

def main():
    print("="*50)
    print("CLASIFICACIÓN EN TIEMPO REAL + UART")
    print("="*50)
    
    try:
        # Inicializar componentes
        clasificador = ClasificadorTiempoReal(RUTA_MODELO, CLASES, TAMAÑO_IMAGEN)
        camara = ManejadorCamara(CAMARA)
        uart = ComunicacionUART(PUERTO_SERIAL, BAUDRATE)
        
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
            
            # Enviar por UART
            uart.enviar_clasificacion(clase, confianza)
            
            # Dibujar clasificación
            frame = clasificador.dibujar_clasificacion(frame, clase, confianza)
            frame = clasificador.dibujar_probabilidades(frame, probabilidades)
            
            # Mostrar frame
            camara.mostrar_frame(frame, "Clasificador + UART")
            
            # Verificar salida
            if camara.verificar_tecla_salida():
                break
    
    except KeyboardInterrupt:
        print("\nInterrumpido por usuario")
    except Exception as e:
        print(f"Error: {e}")
    
    finally:
        uart.cerrar()
        camara.cerrar()
        print("✓ Programa finalizado")

if __name__ == "__main__":
    main()