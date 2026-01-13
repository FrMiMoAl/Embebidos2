from machine import UART, Pin
import time

# Ajusta según tu cableado REAL:
TX_PIN = 16   # Pico TX (sale hacia Jetson RX)
RX_PIN = 17   # Pico RX (entra desde Jetson TX)

uart = UART(0, baudrate=115200, tx=Pin(TX_PIN), rx=Pin(RX_PIN), timeout=0)

uart.write(b"PICO_UART_READY\n")

buf = b""
while True:
    n = uart.any()
    if n:
        buf += uart.read(n)
        while b"\n" in buf:
            line, buf = buf.split(b"\n", 1)
            line = line.strip()
            if line:
                uart.write(b"ECHO:" + line + b"\n")
    time.sleep_ms(5)
