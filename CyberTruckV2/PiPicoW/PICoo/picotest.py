import json
import time
import serial

PORT = "COM4"      # <-- CAMBIA ESTO
BAUD = 115200

def checksum(payload: str) -> int:
    return sum(payload.encode("utf-8")) & 0xFF

def send_frame(ser, msg_type: str, data: dict):
    payload = json.dumps(data, separators=(",", ":"))
    ck = checksum(payload)
    line = f"{msg_type}|{payload}|{ck:02X}\n".encode("utf-8")
    ser.write(line)

def read_lines(ser, seconds=0.6):
    t_end = time.time() + seconds
    while time.time() < t_end:
        line = ser.readline().decode("utf-8", errors="ignore").strip()
        if line:
            print("RX:", line)

def cmd(ser, **d):
    # defaults
    base = {"mode":"teleop", "vx":0, "vy":0, "w":0, "s1":90, "s2":90, "stop":0}
    base.update(d)
    send_frame(ser, "CMD", base)

def step(ser, name, vx, vy, w, secs=1.0):
    print(f"\n== {name} ==")
    cmd(ser, stop=0, vx=vx, vy=vy, w=w)
    read_lines(ser, secs)
    cmd(ser, stop=1, vx=0, vy=0, w=0)
    time.sleep(0.3)

def main():
    ser = serial.Serial(PORT, BAUD, timeout=0.1)
    print("Abierto:", ser.name)

    # stop inicial
    cmd(ser, stop=1)
    time.sleep(0.3)

    # Secuencia
    step(ser, "FORWARD",  25, 0, 0, secs=1.2)
    step(ser, "BACK",    -25, 0, 0, secs=1.2)
    step(ser, "STRAFE RIGHT", 0, 25, 0, secs=1.2)
    step(ser, "STRAFE LEFT",  0,-25, 0, secs=1.2)
    step(ser, "ROTATE CW",    0, 0, 25, secs=1.2)
    step(ser, "ROTATE CCW",   0, 0,-25, secs=1.2)

    print("\n✅ Terminado")
    cmd(ser, stop=1)
    ser.close()

if __name__ == "__main__":
    main()
