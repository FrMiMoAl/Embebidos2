import serial
import time

ser = serial.Serial('/dev/serial0', 115200, timeout=1)

def enviar_velocidades(vA, vB):
    mensaje = f"A:{vA},B:{vB}\n"
    ser.write(mensaje.encode('utf-8'))
    print("Enviado:", mensaje.strip())

while True:
    enviar_velocidades(80, 80)  
    time.sleep(2)

    enviar_velocidades(50, 100)  
    time.sleep(2)

    enviar_velocidades(0, 0)   
    time.sleep(2)
