from serial_comm import SerialComm
import time

serial_device = SerialComm()  # usa el puerto definido en el módulo

print("Escuchando datos del ultrasonido desde la Pico...")

try:
    while True:
        data = serial_device.receive()
        if data:
            print("Ultrasonido:", data)
        time.sleep(0.05)

except KeyboardInterrupt:
    serial_device.close()
    print("Programa terminado")
