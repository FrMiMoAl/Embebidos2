from serial_comm import SerialComm
import time

serial_device = SerialComm(port="/dev/serial0", baudrate=115200)

try:
    print("Introduce valores de prueba en formato pwm1,pwm2,servoangle (ej. 50,-50,90)")
    while True:
        data = input("Enviar: ")
        if not data:
            continue
        serial_device.send(data)

        time.sleep(0.1)
        response = serial_device.receive()
        if response:
            print("Recibido desde Pico:", response)

except KeyboardInterrupt:
    serial_device.close()
    print("Programa terminado")
