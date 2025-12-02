from machine import UART, Pin

class UARTComm:
    def __init__(self, uart_id=0, baudrate=115200, tx_pin=0, rx_pin=1):
        self.uart = UART(
            uart_id,
            baudrate=baudrate,
            tx=Pin(tx_pin),
            rx=Pin(rx_pin)
        )
        self.buffer = ""  # Buffer para mensajes incompletos
        print(f"UART{uart_id} inicializado: {baudrate} baud")
    
    def hay_datos(self):
        return self.uart.any()
    
    def leer_linea(self):
        # Leer datos disponibles
        if self.uart.any():
            datos = self.uart.read()
            if datos:
                self.buffer += datos.decode("utf-8", "ignore")
        
        # completa?
        if "\n" in self.buffer:
            linea, self.buffer = self.buffer.split("\n", 1)
            return linea.strip()
        
        return None
    
    def enviar(self, mensaje):
        if not mensaje.endswith("\n"):
            mensaje += "\n"
        self.uart.write(mensaje.encode("utf-8"))
    
    def parsear_mensaje(self, linea):
        linea = linea.strip()
        
        if not (linea.startswith("(") and linea.endswith(")")):
            return None
        
        try:
            contenido = linea[1:-1]  
            valores = contenido.split(",")
            
            if len(valores) != 4:
                return None
            
            return [int(v) for v in valores]
            
        except ValueError:
            return None