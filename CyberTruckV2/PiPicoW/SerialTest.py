import serial
import time
import threading

# === CONFIGURACIÓN ===
# Ajusta el puerto según tu sistema:
#   Windows: "COM3" o "COM5"
#   Linux/Mac: "/dev/ttyUSB0" o "/dev/ttyACM0"
PORT = "COM7"         
BAUDRATE = 115200

# === CONEXIÓN UART ===
ser = serial.Serial(PORT, BAUDRATE, timeout=0.1)

# === LECTURA ASÍNCRONA DEL PUERTO ===
def reader():
    while True:
        try:
            if ser.in_waiting > 0:
                data = ser.readline().decode(errors='ignore').strip()
                if data:
                    print(f"[PICO] {data}")
        except Exception as e:
            print(f"Error de lectura: {e}")
            break

# Lanzamos hilo para escuchar continuamente
thread = threading.Thread(target=reader, daemon=True)
thread.start()

# === LOOP PRINCIPAL ===
print("=== Consola UART Pico W ===")
print("Ejemplo de comando: 50,30,1,0")
print("Escribe 'exit' para salir.\n")

try:
    while True:
        cmd = input(">>> ").strip()
        if cmd.lower() == "exit":
            break
        if cmd:
            ser.write((cmd + "\n").encode())
            print(f"[PC] Enviado: {cmd}")
        time.sleep(0.05)

except KeyboardInterrupt:
    pass

finally:
    ser.close()
    print("\nConexión cerrada.")
