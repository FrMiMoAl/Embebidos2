from machine import UART, Pin
import time

UART_ID = 0
BAUDRATE = 115200

uart = UART(
    UART_ID,
    baudrate=BAUDRATE,
    tx=Pin(0),
    rx=Pin(1),
    timeout=100   # ms
)

# LED integrado de la Pico
led_1 = Pin(18, Pin.OUT)
led_2 = Pin(19, Pin.OUT)
led_3 = Pin(20, Pin.OUT)
led_4 = Pin(21, Pin.OUT)

print("(rojos,azules,negros,borradores)\n")


def parsear_mensaje(linea: str):
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
    if uart.any():
        linea_bytes = uart.readline()
        if linea_bytes is None:
            continue

        try:
            linea = linea_bytes.decode("utf-8").strip()
        except UnicodeError:
            continue

        if not linea:
            continue

        resultado = parsear_mensaje(linea)
        if resultado is None:
            print("Mensaje inválido:", linea)
            continue

        rojos, azules, negros, borradores = resultado

        print("Recibido:")
        print(f"  Rojos      : {rojos}")
        print(f"  Azules     : {azules}")
        print(f"  Negros     : {negros}")
        print(f"  Borradores : {borradores}")
        print("-----------------------------")

        if rojos > 0:
            led_1.value(1)
        else:
            led_1.value(0)

        if azules > 0:
            led_2.value(1)
        else:
            led_2.value(0)

        if negros > 0:
            led_3.value(1)
        else:
            led_3.value(0)

        if borradores > 0:
            led_4.value(1)
        else:
            led_4.value(0)

    time.sleep_ms(10)
