# =============================================
#
#               Module UART Handler
#
# =============================================


# Clase para manejar comunicación UART y parsing de comandos

from machine import UART
import time

class UARTHandler:
    def __init__(self, uart_id=0, baudrate=115200):
        self.uart = UART(uart_id, baudrate)
        self.uart.init(baudrate, bits=8, parity=None, stop=1)

    def send(self, msg):
        self.uart.write(msg + "\n")

    def read_command(self):
        if self.uart.any():
            line = self.uart.readline()
            if line:
                try:
                    return line.decode("utf-8").strip()
                except:
                    return str(line)
        return None
