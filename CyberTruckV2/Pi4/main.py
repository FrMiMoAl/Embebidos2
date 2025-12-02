import sys
import os
import time
from pathlib import Path
import threading

ROOT = os.path.dirname(__file__)
LIBS_DIR = os.path.join(ROOT, "libs")
if os.path.isdir(LIBS_DIR) and LIBS_DIR not in sys.path:
    sys.path.insert(0, LIBS_DIR)

try:
    import serial
except Exception as e:
    print("No se pudo importar 'serial' (pyserial).")
    raise

from controller import MyController

PORT = "/dev/serial0"
BAUD = 115200
FILE = Path("/home/raspberry/Documents/puerto/control.txt")


def clamp_speed(v):
    try:
        v = float(v)
    except:
        return 80
    v = int(round(v))
    return max(0, min(v, 100))


def send_speed(ser, speed):
    speed = clamp_speed(speed)
    msg = f"S={speed}\n".encode("utf-8")
    ser.write(msg)
    ser.flush()
    print(">> SPEED:", speed)


def speed_from_joystick(value):
    if value is None:
        return 80
    mag = abs(int(value))
    return int(round(100 * mag / 32767.0))


VALID_SEL = {"A", "B", "X", "Y", "N"}


def send_sel(ser, sel):
    sel = (sel or "N").strip()[:1].upper()
    if sel not in VALID_SEL:
        sel = "N"
    ser.write(f"{sel}\n".encode("utf-8"))
    ser.flush()
    print(">> SEL:", sel)


def enviar_info(ser, velocidad, instruccion):
    send_speed(ser, velocidad)
    time.sleep(0.02)
    send_sel(ser, instruccion)


def serial_reader_thread(ser):
    while True:
        try:
            data = ser.readline()
            if data:
                print("<<", data.decode(errors="ignore").strip())
        except Exception as e:
            print("Error leyendo serial:", e)
            time.sleep(0.2)


def read_speed_from_file():
    if FILE.exists():
        return clamp_speed(FILE.read_text().strip())
    return 80


def main():
    try:
        ser = serial.Serial(PORT, BAUD, timeout=0.2)
        print(f"Puerto serial abierto en {PORT} a {BAUD} baudios.")
    except Exception as e:
        print(f"Error al abrir el puerto serial {PORT}: {e}")
        return

    threading.Thread(target=serial_reader_thread, args=(ser,), daemon=True).start()
    controller = MyController(interface="/dev/input/js0", connecting_using_ds4drv=False)

    def cb_l3_up(value):
        velocidad = read_speed_from_file()
        enviar_info(ser, velocidad, "X")

    def cb_l3_down(value):
        velocidad = read_speed_from_file()
        enviar_info(ser, velocidad, "Y")

    def cb_l3_left(value):
        velocidad = read_speed_from_file()
        enviar_info(ser, velocidad, "A")

    def cb_l3_right(value):
        velocidad = read_speed_from_file()
        enviar_info(ser, velocidad, "B")

    def cb_l3_release():
        enviar_info(ser, 0, "N")

    def cb_r2_press(value):
        velocidad_max = 100
        enviar_info(ser, velocidad_max, "X")
        print(f"R2 presionado → velocidad {velocidad_max}%")

    def cb_r2_release():
        velocidad_normal = read_speed_from_file()
        enviar_info(ser, velocidad_normal, "N")
        print("R2 liberado → velocidad normal")

    controller.register_callback("l3_up", cb_l3_up)
    controller.register_callback("l3_down", cb_l3_down)
    controller.register_callback("l3_left", cb_l3_left)
    controller.register_callback("l3_right", cb_l3_right)
    controller.register_callback("l3_release", cb_l3_release)
    controller.register_callback("r2_press", cb_r2_press)
    controller.register_callback("r2_release", cb_r2_release)

    print("🎮 Escuchando mando PS4…")
    print("Presiona Ctrl+C para salir.")

    try:
        controller.listen(timeout=0.2)
    except KeyboardInterrupt:
        print("\n Saliendo del programa…")
        enviar_info(ser, 0, "N")
        ser.close()


if __name__ == "__main__":
    main()
