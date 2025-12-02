from machine import UART, Pin, Timer
import utime

# UART1: RX = GP5
uart = UART(1, baudrate=115200, rx=Pin(5))

# Buzzer
buzzer = Pin(15, Pin.OUT)
buzzer.value(0)

# Timer para el buzzer
timer = Timer()
buzzer_activo = False

def buzzer_callback(t):
    buzzer.value(1)
    utime.sleep_ms(200)
    buzzer.value(0)

print("Esperando señal UART para activar buzzer...")

while True:
    if uart.any():
        dato = uart.read(1)

        if dato == b'B' and not buzzer_activo:
            print("Señal recibida: B → Activando buzzer cada 5s")
            timer.init(
                period=5000,
                mode=Timer.PERIODIC,
                callback=buzzer_callback
            )
            buzzer_activo = True

    utime.sleep_ms(10)
