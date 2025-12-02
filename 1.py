# uart_receptor_pico.py
#
# Raspberry Pi Pico que recibe por UART mensajes del tipo:
# (N_rojos,N_azules,N_negros,N_borradores)
# y los muestra por el puerto USB (print en Thonny).

from machine import UART, Pin
import time

# ================== CONFIGURACIÓN UART ==================
# UART0 en los pines por defecto:
#   GP0 = TX (no lo usamos, pero queda configurado)
#   GP1 = RX (aquí conectas el TX del otro dispositivo)
UART_ID = 0
BAUDRATE = 115200

uart = UART(
    UART_ID,
    baudrate=BAUDRATE,
    tx=Pin(0),
    rx=Pin(1),
    timeout=100   # ms
)
# =======================================================

print("Receptor UART Pico iniciado")
print("Esperando datos en formato: (rojos,azules,negros,borradores)\n")


def parsear_mensaje(linea: str):
    """
    Recibe un string como '(2,1,0,3)' y devuelve
    una tupla (rojos, azules, negros, borradores) como enteros.
    Si hay error, devuelve None.
    """
    linea = linea.strip()
    if not (linea.startswith("(") and linea.endswith(")")):
        return None

    contenido = linea[1:-1]  # quitar paréntesis
    partes = contenido.split(",")

    if len(partes) != 4:
        return None

    try:
        rojos = int(partes[0])
        azules = int(partes[1])
        negros = int(partes[2])
        borradores = int(partes[3])
        return rojos, azules, negros, borradores
    except ValueError:
        return None


while True:
    # Ver si hay datos disponibles en el UART
    if uart.any():
        # Leer una línea completa (hasta '\n')
        linea_bytes = uart.readline()
        if linea_bytes is None:
            continue

        try:
            linea = linea_bytes.decode("utf-8").strip()
        except UnicodeError:
            # Si llega basura, la ignoramos
            continue

        if not linea:
            continue

        # Intentar parsear el mensaje
        resultado = parsear_mensaje(linea)
        if resultado is None:
            print("Mensaje inválido:", linea)
            continue

        rojos, azules, negros, borradores = resultado

        # Aquí ya tienes los 4 valores como enteros
        print("Recibido:")
        print(f"  Rojos      : {rojos}")
        print(f"  Azules     : {azules}")
        print(f"  Negros     : {negros}")
        print(f"  Borradores : {borradores}")
        print("-----------------------------")

        # Aquí podrías tomar decisiones, por ejemplo:
        # - mover motores
        # - encender LEDs
        # - mandar respuesta de vuelta, etc.

    # Pequeña pausa para no saturar la CPU
    time.sleep_ms(10)
