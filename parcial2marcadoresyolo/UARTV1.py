import serial
import time

# Puerto UART de la Raspberry Pi 5
PORT = "/dev/ttyAMA0"   # Si no funciona, prueba /dev/ttyAMA0 o /dev/ttyS0
BAUD = 115200

ser = serial.Serial(PORT, BAUD, timeout=1)

def detectar():
    """
    Aquí irá la lógica del modelo YOLO.
    Por ahora devolvemos False para simular 'no hay elementos'.
    """
    return False

print("Sistema iniciado. Enviará señal si NO se detectan elementos...")

while True:
    if not detectar():
        # ENVIAR UNA SOLA SEÑAL
        ser.write(b'B')
        print("Señal enviada: B")
        time.sleep(1)  # espera para evitar spam

    else:
        print("Elementos detectados. No se envía señal.")
        time.sleep(1)