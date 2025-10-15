import serial

class SerialComm:
    def __init__(self, port="/dev/serial0", baudrate=115200, timeout=0.1):
        self.ser = serial.Serial(port, baudrate, timeout=timeout)
        if self.ser.is_open:
            print(f"✅ Serial abierto en {port} a {baudrate} baudios")
        else:
            self.ser.open()

    def send(self, data_str):
        """
        Envía la cadena directamente por UART, formato: 'pwm1,pwm2,servoangle'
        """
        msg = data_str.strip() + "\n"
        self.ser.write(msg.encode())

    def receive(self):
        """
        Retorna datos recibidos desde la Pico (ej. distancia ultrasonido)
        """
        if self.ser.in_waiting > 0:
            return self.ser.readline().decode().strip()
        return None

    def close(self):
        self.ser.close()
        print("Serial cerrado")
