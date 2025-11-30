# ========================================
# 11. app_prueba_uart.py
# Solo prueba de comunicación UART
# ========================================

from comunicacion_uart import ComunicacionUART
import time

PUERTO_SERIAL = '/dev/ttyUSB0'
BAUDRATE = 115200

def main():
    print("="*50)
    print("PRUEBA DE COMUNICACIÓN UART")
    print("="*50)
    
    try:
        uart = ComunicacionUART(PUERTO_SERIAL, BAUDRATE)
        
        print("\nEnviando datos de prueba...")
        print("Presiona Ctrl+C para detener\n")
        
        contador = 0
        clases = ['rojo', 'azul', 'negro', 'borrador']
        
        while True:
            # Prueba 1: Enviar predicción individual
            clase = clases[contador % len(clases)]
            confianza = 0.95
            uart.enviar_prediccion(clase, confianza)
            print(f"Enviado: {clase}, {confianza:.2f}")
            
            time.sleep(1)
            
            # Prueba 2: Enviar conteos
            conteos = {
                'rojo': contador % 5,
                'azul': (contador + 1) % 5,
                'negro': (contador + 2) % 5,
                'borrador': (contador + 3) % 5
            }
            uart.enviar_conteos(conteos)
            print(f"Enviado: {conteos}")
            
            contador += 1
            time.sleep(2)
    
    except KeyboardInterrupt:
        print("\n\nPrueba finalizada")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        uart.cerrar()

if __name__ == "__main__":
    main()