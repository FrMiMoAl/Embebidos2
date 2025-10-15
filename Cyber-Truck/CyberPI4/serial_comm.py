# serial_comm.py
# Comunicación serial simple para Raspberry Pi <-> Pico
# Protocolo por defecto: "CODE:SPEED\n" (p.ej., "A:120\n", "N:0\n")

from __future__ import annotations
import threading
from typing import Optional

try:
    import serial  # pyserial
except ImportError as e:
    raise ImportError("pyserial no está instalado. Instálalo con: pip install pyserial") from e


class SerialComm:
    def __init__(self, port: str = "/dev/serial0", baud: int = 115200,
                 timeout: float = 0.1, eol: str = "\n", open_on_init: bool = True):
        self.port = port
        self.baud = int(baud)
        self.eol = eol.encode()
        self._timeout_default = float(timeout)
        self._ser: Optional[serial.Serial] = None
        self._lock = threading.Lock()
        if open_on_init:
            self.connect()

    # ---------- Conexión ----------
    def connect(self) -> bool:
        """Abre el puerto si no está abierto. Devuelve True si queda conectado."""
        with self._lock:
            if self._ser and getattr(self._ser, "is_open", False):
                return True
            try:
                self._ser = serial.Serial(self.port, self.baud, timeout=self._timeout_default)
                # Limpia buffers para evitar basura inicial
                self._ser.reset_input_buffer()
                self._ser.reset_output_buffer()
                return True
            except Exception as e:
                print(f"❌ SerialComm.connect: no se pudo abrir {self.port} @ {self.baud}: {e}")
                self._ser = None
                return False

    def is_connected(self) -> bool:
        return bool(self._ser and getattr(self._ser, "is_open", False))

    def disconnect(self):
        with self._lock:
            if self._ser:
                try:
                    self._ser.close()
                except Exception as e:
                    print(f"⚠️ SerialComm.disconnect: {e}")
                finally:
                    self._ser = None

    # ---------- IO ----------
    def send_instruction(self, speed: int, code: str) -> None:
        """
        Envía 'CODE:SPEED\\n'. No valida el significado de CODE (A,B,X,N); lo decide el firmware.
        speed se envía como entero tal cual.
        """
        if not self.is_connected() and not self.connect():
            raise RuntimeError("Puerto serial no conectado")

        if not isinstance(code, str) or not code:
            raise ValueError("code debe ser un string no vacío")

        try:
            s = int(speed)
        except Exception:
            raise ValueError("speed debe ser convertible a int")

        payload = f"{code}:{s}".encode() + self.eol
        with self._lock:
            try:
                self._ser.write(payload)
                self._ser.flush()
            except Exception as e:
                print(f"❌ SerialComm.send_instruction error al enviar {payload!r}: {e}")
                raise

    def read_response(self, timeout: Optional[float] = None) -> Optional[str]:
        """
        Lee una línea terminada en \\n. Devuelve texto sin salto o None si no hay datos en 'timeout' segundos.
        """
        if not self.is_connected():
            return None

        to = self._timeout_default if timeout is None else float(timeout)
        with self._lock:
            old_to = self._ser.timeout
            self._ser.timeout = to
            try:
                data = self._ser.readline()
            finally:
                self._ser.timeout = old_to

        if not data:
            return None

        try:
            return data.decode("utf-8", errors="ignore").strip()
        except Exception:
            # Si hay bytes no UTF-8, al menos devuelve su repr
            return repr(data)

    # ---------- Utilidades ----------
    def send_raw(self, text: str) -> None:
        """Envía texto crudo terminando en \\n (para pruebas/diagnóstico)."""
        if not self.is_connected() and not self.connect():
            raise RuntimeError("Puerto serial no conectado")
        if not text.endswith("\n"):
            text += "\n"
        with self._lock:
            self._ser.write(text.encode("utf-8", errors="ignore"))
            self._ser.flush()