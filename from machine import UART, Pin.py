from machine import UART, Pin
import time

# Configurar UART0 en GPIO0 (TX) y GPIO1 (RX)
uart = UART(0, baudrate=9600, tx=Pin(0), rx=Pin(1))

try:
    while True:
        # Enviar datos
        mensaje = "Hola desde Pico\n"
        uart.write(mensaje)
        print(f"Enviado: {mensaje.strip()}")

        # Recibir datos si hay disponibles
        if uart.any():
            datos = uart.read()
            if datos is not None:
                # Decodificar de forma segura
                try:
                    texto = datos.decode('utf-8')
                except UnicodeError:
                    texto = datos.decode('utf-8', errors='ignore')
                print(f"Recibido: {texto}")

        time.sleep(1)
except KeyboardInterrupt:
    print("Desconectado")