import json
import time
from machine import UART, Pin

class UARTProtocol:
    def __init__(self, uart_id, baudrate, tx, rx):
        self.uart = UART(uart_id, baudrate=baudrate, tx=Pin(tx), rx=Pin(rx))
        self.last_heartbeat = time.ticks_ms()

    def send(self, msg_type, data):
        """Envía telemetría en formato TIPO|JSON|CHECKSUM"""
        payload = json.dumps(data)
        checksum = sum(payload.encode()) & 0xFF
        message = f"{msg_type}|{payload}|{checksum:02X}\n"
        self.uart.write(message)

    def receive(self):
        """Lee y valida comandos entrantes"""
        if not self.uart.any(): return None
        line = self.uart.readline()
        try:
            line = line.decode().strip()
            parts = line.split("|")
            if len(parts) != 3: return None
            
            msg_type, payload, ck_rx = parts
            if (sum(payload.encode()) & 0xFF) == int(ck_rx, 16):
                self.last_heartbeat = time.ticks_ms()
                return {"type": msg_type, "data": json.loads(payload)}
        except: return None