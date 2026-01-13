# protocol.py
import json
import time
from machine import UART, Pin
from config import Config
class UARTProtocol:
    """
    Frame: TYPE|JSON|CK\n
    CK = sum(bytes(JSON)) & 0xFF en hex 2 dígitos
    """
    def __init__(self, uart_id, baudrate, tx, rx):
        self.uart = UART(uart_id, baudrate=baudrate, tx=Pin(tx), rx=Pin(rx), timeout=0)
        self._buf = b""
        self._queue = []
        self.last_rx_ms = time.ticks_ms()

    @staticmethod
    def _checksum(payload_str: str) -> int:
        return sum(payload_str.encode()) & 0xFF

    def send(self, msg_type: str, data: dict):
        payload = json.dumps(data, separators=(",", ":"))  # compacto
        ck = self._checksum(payload)
        line = f"{msg_type}|{payload}|{ck:02X}\n"
        self.uart.write(line)

    def poll(self):
        """Lee bytes disponibles, arma líneas y mete mensajes válidos a la cola."""
        n = self.uart.any()
        if n:
            self._buf += self.uart.read(n)

        while b"\n" in self._buf:
            line, self._buf = self._buf.split(b"\n", 1)
            line = line.strip()
            if not line:
                continue

            try:
                parts = line.decode().split("|")
                if len(parts) != 3:
                    continue

                msg_type, payload, ck_rx = parts
                if self._checksum(payload) != int(ck_rx, 16):
                    continue

                self.last_rx_ms = time.ticks_ms()
                self._queue.append({"type": msg_type, "data": json.loads(payload)})
            except:
                # ignora frames rotos
                pass

    def recv(self):
        """Devuelve 1 mensaje de la cola o None."""
        self.poll()
        if self._queue:
            return self._queue.pop(0)
        return None

    def link_alive(self, timeout_ms: int) -> bool:
        return time.ticks_diff(time.ticks_ms(), self.last_rx_ms) <= timeout_ms