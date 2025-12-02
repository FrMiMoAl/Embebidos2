from machine import UART, Pin
import utime

# UART1: solo RX en GP5 (desde la Pi 5)
uart = UART(1, baudrate=115200, rx=Pin(5))

# LEDs (ajusta los pines si usas otros)
led_red   = Pin(16, Pin.OUT)
led_blue  = Pin(17, Pin.OUT)
led_black = Pin(18, Pin.OUT)

def all_off():
    led_red.value(0)
    led_blue.value(0)
    led_black.value(0)

all_off()
print("Esperando color por UART...")

while True:
    if uart.any():
        data = uart.read(1)   # leemos 1 byte
        print("RX:", data)

        all_off()  # apagar todo antes de encender el nuevo

        if data == b'R':
            print("-> Encendiendo LED ROJO por 5s")
            led_red.value(1)
            utime.sleep(5)
            led_red.value(0)

        elif data == b'A':
            print("-> Encendiendo LED AZUL por 5s")
            led_blue.value(1)
            utime.sleep(5)
            led_blue.value(0)

        elif data == b'N':
            print("-> Encendiendo LED NEGRO por 5s")
            led_black.value(1)
            utime.sleep(5)
            led_black.value(0)

        else:
            print("Código desconocido, LEDs apagados")

        # después de los 5 segundos siempre volvemos al estado de espera
        all_off()

    utime.sleep_ms(50)
