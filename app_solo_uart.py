# ========================================
# 6. app_solo_uart.py
# Solo prueba de comunicación UART
# ========================================

from comunicacion_uart import ComunicacionUART
import time

PUERTO_SERIAL = "/dev/serial0"
BAUDRATE = 115200

def main():
    print("=== Prueba de Comunicación UART ===\n")
    
    try:
        uart = ComunicacionUART(PUERTO_SERIAL, BAUDRATE)
        
        print("Enviando datos de prueba...")
        print("Presiona Ctrl+C para detener\n")
        
        contador = 0
        while True:
            # Enviar conteos de prueba
            conteos = {
                "rojo": contador % 5,
                "azul": (contador + 1) % 5,
                "negro": (contador + 2) % 5,
                "borrador": (contador + 3) % 5
            }
            
            uart.enviar_conteos(conteos)
            print(f"Enviado: {conteos}")
            
            contador += 1
            time.sleep(1)  # Esperar 1 segundo
    
    except KeyboardInterrupt:
        print("\n\nPrueba finalizada")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        uart.cerrar()

if __name__ == "__main__":
    main()