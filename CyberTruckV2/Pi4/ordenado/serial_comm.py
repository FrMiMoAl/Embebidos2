import serial
import time

class SerialComm:
    def __init__(self, port="/dev/serial0", baudrate=115200, timeout=0.1):
        try:
            self.ser = serial.Serial(port, baudrate, timeout=timeout)
            if self.ser.is_open:
                print(f"[UART] ✅ Serial abierto en {port} a {baudrate} baudios")
            else:
                self.ser.open()
        except Exception as e:
            print(f"[UART] ❌ Error abriendo UART: {e}")
            self.ser = None

    def send(self, data_str):
        """
        Envía cadena directa: 'pwm1,pwm2,servo'
        """
        if self.ser:
            msg = data_str.strip() + "\n"
            try:
                self.ser.write(msg.encode())
                print(f"[TX] {msg.strip()}")
            except Exception as e:
                print(f"[UART] Error enviando: {e}")
        else:
            print("[TX] (UART no disponible)")

    def receive(self):
        """
        Lee datos desde la Pico (por ejemplo '23' de distancia)
        """
        if self.ser and self.ser.in_waiting > 0:
            try:
                data = self.ser.readline().decode().strip()
                if data:
                    print(f"[RX] {data}")
                return data
            except:
                return None
        return None

    def close(self):
        if self.ser:
            try:
                self.ser.close()
                print("[UART] 🔌 Serial cerrado")
            except:
                pass
