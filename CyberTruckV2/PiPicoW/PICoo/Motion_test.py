#!/usr/bin/env python3
import json, time
import serial
import argparse

def checksum(payload: str) -> int:
    return sum(payload.encode("utf-8")) & 0xFF

def send_cmd(ser, **d):
    payload = json.dumps(d, separators=(",", ":"))
    ck = checksum(payload)
    line = f"CMD|{payload}|{ck:02X}\n".encode()
    ser.write(line)

def step(ser, name, vx, vy, w, secs=1.0, mode="teleop", s1=90, s2=90):
    print(f"\n== {name} ==")
    send_cmd(ser, mode=mode, vx=vx, vy=vy, w=w, s1=s1, s2=s2, stop=0)
    t0 = time.time()
    while time.time() - t0 < secs:
        line = ser.readline().decode("utf-8", errors="ignore").strip()
        if line:
            print("RX:", line)
    send_cmd(ser, mode=mode, vx=0, vy=0, w=0, s1=s1, s2=s2, stop=1)
    time.sleep(0.3)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", required=True)
    ap.add_argument("--baud", type=int, default=115200)
    ap.add_argument("--speed", type=int, default=30)
    ap.add_argument("--secs", type=float, default=1.2)
    args = ap.parse_args()

    sp = max(10, min(60, args.speed))
    ser = serial.Serial(args.port, args.baud, timeout=0.1)

    # stop inicial
    send_cmd(ser, mode="teleop", vx=0, vy=0, w=0, s1=90, s2=90, stop=1)
    time.sleep(0.3)

    step(ser, "FORWARD",  sp, 0, 0, secs=args.secs)
    step(ser, "BACK",    -sp, 0, 0, secs=args.secs)
    step(ser, "STRAFE RIGHT", 0,  sp, 0, secs=args.secs)
    step(ser, "STRAFE LEFT",  0, -sp, 0, secs=args.secs)
    step(ser, "ROTATE CW",     0, 0,  sp, secs=args.secs)
    step(ser, "ROTATE CCW",    0, 0, -sp, secs=args.secs)

    print("\n✅ Done.")
    ser.close()

if __name__ == "__main__":
    main()
