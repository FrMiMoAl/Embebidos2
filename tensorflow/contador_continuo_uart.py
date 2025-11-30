# 10. contador_continuo_uart.py
# Contador continuo que envía conteos por UART
# (útil si detectas múltiples marcadores en el frame)

import cv2
import time
from collections import defaultdict
from predictor_tiempo_real import PredictorTiempoReal
from comunicacion_uart import ComunicacionUART

# Configuración
RUTA_MODELO = 'modelo_marcadores.h5'
CLASES = ['azul', 'borrador', 'negro', 'rojo']
CAMARA = 0
PUERTO_SERIAL = '/dev/ttyUSB0'
BAUDRATE = 115200
TIEMPO_ACUMULACION = 2  # segundos para acumular conteos

def main():
    print("="*50)
    print("CONTADOR CONTINUO + UART")
    print("="*50)
    
    try:
        # Inicializar
        predictor = PredictorTiempoReal(RUTA_MODELO, CLASES)
        uart = ComunicacionUART(PUERTO_SERIAL, BAUDRATE)
        camara = cv2.VideoCapture(CAMARA)
        
        if not camara.isOpened():
            raise Exception("No se pudo abrir la cámara")
        
        print("\n✓ Sistema listo")
        print("Presiona 'q' para salir\n")
        
        # Variables para acumulación
        conteos_acumulados = defaultdict(int)
        tiempo_inicio = time.time()
        
        while True:
            ret, frame = camara.read()
            if not ret:
                break
            
            # Predecir
            clase, confianza = predictor.predecir(frame)
            
            # Acumular conteo si la confianza es alta
            if confianza > 0.7:
                conteos_acumulados[clase] += 1
            
            # Verificar si pasó el tiempo de acumulación
            tiempo_actual = time.time()
            if tiempo_actual - tiempo_inicio >= TIEMPO_ACUMULACION:
                # Preparar conteos en formato estándar
                conteos = {
                    'rojo': conteos_acumulados.get('rojo', 0),
                    'azul': conteos_acumulados.get('azul', 0),
                    'negro': conteos_acumulados.get('negro', 0),
                    'borrador': conteos_acumulados.get('borrador', 0)
                }
                
                # Enviar por UART
                uart.enviar_conteos(conteos)
                print(f"Enviado: {conteos}")
                
                # Reiniciar contadores
                conteos_acumulados.clear()
                tiempo_inicio = tiempo_actual
            
            # Dibujar predicción actual
            frame = predictor.dibujar_prediccion(frame, clase, confianza)
            
            # Mostrar conteos acumulados
            y = 100
            for color in ['rojo', 'azul', 'negro', 'borrador']:
                texto = f"{color}: {conteos_acumulados.get(color, 0)}"
                cv2.putText(frame, texto, (20, y),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
                y += 30
            
            # Mostrar
            cv2.imshow("Contador Continuo", frame)
            
            # Salir con 'q'
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    
    except KeyboardInterrupt:
        print("\nInterrumpido por usuario")
    except Exception as e:
        print(f"Error: {e}")
    
    finally:
        uart.cerrar()
        camara.release()
        cv2.destroyAllWindows()
        print("✓ Programa finalizado")

if __name__ == "__main__":
    main()