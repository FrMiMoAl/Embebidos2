import sys

import os
import time
from pathlib import Path
import threading

# Ensure local vendored packages in ./libs are importable (pyserial, pyPS4Controller, etc.)
ROOT = os.path.dirname(__file__)
LIBS_DIR = os.path.join(ROOT, "libs")
if os.path.isdir(LIBS_DIR) and LIBS_DIR not in sys.path:
    sys.path.insert(0, LIBS_DIR)

try:
    import serial
except Exception as e:
    print("\u26a0\ufe0f Warning: could not import 'serial' (pyserial).",
          "If you don't have pyserial installed system-wide,",
          "ensure the ./libs folder contains pyserial or install it with pip.")
    raise

from controller import MyController

PORT = "/dev/serial0"
BAUD = 115200
FILE = Path("/home/raspberry/Documents/puerto/control.txt")



def clamp_speed(v):
    try:
        v = float(v)
    except:
        return 80  # default
    v = int(round(v))
    if v < 0: v = 0
    if v > 100: v = 100
    return v

def send_speed(ser, speed):
    speed = clamp_speed(speed)
    msg = f"S={speed}\n".encode("utf-8")
    ser.write(msg)
    ser.flush()
    print(">> SPEED:", speed)

def speed_from_joystick(value):
    """
    Convierte el valor analógico del joystick (-32767..32767)
    a 0..100 tomando magnitud.
    """
    if value is None:
        return 80
    # normalizamos por magnitud
    mag = abs(int(value))
    return int(round(100 * mag / 32767.0))

VALID_SEL = {"A", "B", "X", "Y", "N"}
def send_sel(ser, sel):
    """Envía selección A/B/X/Y/N (una letra y \\n)."""
    sel = (sel or "N").strip()[:1].upper()
    if sel not in VALID_SEL:
        sel = "N"
    ser.write(f"{sel}\n".encode("utf-8"))
    ser.flush()
    print(">> SEL:", sel)

def enviarInfo(ser, velocidad, instruccion):
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
            print("Serial read error:", e)
            time.sleep(0.2)

def read_speed_from_file():
    if FILE.exists():
        return clamp_speed(FILE.read_text().strip())
    return 80


def main():
    ser = serial.Serial(PORT, BAUD, timeout=0.2)
    threading.Thread(target=serial_reader_thread, args=(ser,), daemon=True).start()
    controller = MyController(interface="/dev/input/js0", connecting_using_ds4drv=False)

    def cb_l3_up(value):
        velocidad = read_speed_from_file()
        enviarInfo(ser, velocidad, "X")   # ambos adelante
    
    def cb_l3_down(value):
        velocidad = read_speed_from_file()
        enviarInfo(ser, velocidad, "Y")   # ambos atrás
    
    def cb_l3_left(value):
        velocidad = read_speed_from_file()
        enviarInfo(ser, velocidad, "A")   # motor A
    
    def cb_l3_right(value):
        velocidad = read_speed_from_file()
        enviarInfo(ser, velocidad, "B")   # motor B
    
    def cb_l3_release():
        enviarInfo(ser, 0, "N")

    def cb_r2_press(value):
        velocidad_max = 100
        enviarInfo(ser, velocidad_max, "X")  # ambos motores adelante
        print(f"🚀 R2 presionado → velocidad {velocidad_max}%")

    def cb_r2_release():
        velocidad_normal = read_speed_from_file()
        enviarInfo(ser, velocidad_normal, "N")
        print("velocidad normal")


    controller.register_callback('l3_up', cb_l3_up)
    controller.register_callback('l3_down', cb_l3_down)
    controller.register_callback('l3_left', cb_l3_left)
    controller.register_callback('l3_right', cb_l3_right)
    controller.register_callback('l3_release', cb_l3_release)

    controller.register_callback('r2_press', cb_r2_press)
    controller.register_callback('r2_release', cb_r2_release)

    print("🎮 Escuchando mando PS4…")
    try:
        controller.start_listening()  # bloqueante
    except KeyboardInterrupt:
        print("\nSaliendo…")

if __name__ == "__main__":
    main()