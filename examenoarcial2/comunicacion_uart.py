# ========================================
# 2. comunicacion_uart.py
# Maneja el envío de datos por UART
# ========================================

import serial

class ComunicacionUART:
    def __init__(self, puerto, baudrate=115200):
        print(f"Abriendo puerto: {puerto} @ {baudrate} bps")
        try:
            self.serial = serial.Serial(puerto, baudrate, timeout=1)
            print("✓ Puerto serial abierto")
        except Exception as e:
            raise Exception(f"Error al abrir puerto: {e}")
    
    def enviar_conteos(self, conteos):
        # Formato: (rojo,azul,negro,borrador)\n
        mensaje = f"({conteos['rojo']},{conteos['azul']},{conteos['negro']},{conteos['borrador']})\n"
        try:
            self.serial.write(mensaje.encode("utf-8"))
            return True
        except Exception as e:
            print(f"Error al enviar: {e}")
            return False
    
    def enviar_texto(self, texto):
        # Enviar cualquier texto
        try:
            self.serial.write(f"{texto}\n".encode("utf-8"))
            return True
        except Exception as e:
            print(f"Error al enviar: {e}")
            return False
    
    def cerrar(self):
        try:
            self.serial.close()
            print("✓ Puerto serial cerrado")
        except:
            pass