import serial


class UARTModule:
    
    def __init__(self, port, baudrate=9600, timeout=0):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial_conn: serial.Serial | None = None
        self.is_connected: bool = False
    
    def connect(self) -> bool:
        try:
            self.serial_conn = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=0
            )
            self.is_connected = True
            print(f"UART conectado en {self.port} @ {self.baudrate} baudios")
            return True
            
        except serial.SerialException as e:
            print(f"Error al conectar UART: {e}")
            return False
    
    def send(self, data: str) -> bool:
        if not self.is_connected or self.serial_conn is None:
            print("UART no conectado. No se puede enviar.")
            return False
        
        try:
            if not data.endswith('\n'):
                data += '\n'
            
            self.serial_conn.write(data.encode('utf-8'))
            print(f"UART TX: {data.strip()}")
            return True
            
        except Exception as e:
            print(f"Error al enviar por UART: {e}")
            return False
    
    def receive_line(self) -> str | None:
        if not self.is_connected or self.serial_conn is None:
            return None
        
        try:
            if self.serial_conn.in_waiting > 0:
                data = self.serial_conn.readline().decode('utf-8', errors='ignore').strip()
                if data:
                    print(f"UART RX: {data}")
                    return data
        except Exception as e:
            print(f"Error en recepción UART: {e}")
        
        return None
    
    def disconnect(self):
        if self.serial_conn and self.is_connected:
            try:
                self.serial_conn.close()
            except Exception:
                pass
            self.is_connected = False
            print("UART desconectado")
    
    def __del__(self):
        self.disconnect()