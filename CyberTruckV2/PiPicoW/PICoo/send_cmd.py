#!/usr/bin/env python3
import argparse, json, time
import serial

def checksum(payload: str) -> int:
    return sum(payload.encode("utf-8")) & 0xFF

def send_frame(ser, msg_type: str, data: dict):
    payload = json.dumps(data, separators=(",", ":"))
    ck = checksum(payload)
    line = f"{msg_type}|{payload}|{ck:02X}\n".encode("utf-8")
    ser.write(line)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", required=True)
    ap.add_argument("--baud", type=int, default=115200)
    ap.add_argument("--mode", default="teleop", choices=["teleop", "auto"])
    ap.add_argument("--vx", type=int, default=0)
    ap.add_argument("--vy", type=int, default=0)
    ap.add_argument("--w",  type=int, default=0)
    ap.add_argument("--s1", type=int, default=90)
    ap.add_argument("--s2", type=int, default=90)
    ap.add_argument("--stop", type=int, default=0)
    ap.add_argument("--listen", type=float, default=0.0, help="segundos para leer TEL")
    args = ap.parse_args()

    ser = serial.Serial(args.port, args.baud, timeout=0.1)
    cmd = {"mode": args.mode, "vx": args.vx, "vy": args.vy, "w": args.w,
           "s1": args.s1, "s2": args.s2, "stop": 1 if args.stop else 0}
    send_frame(ser, "CMD", cmd)
    print("Sent CMD:", cmd)

    if args.listen > 0:
        t_end = time.time() + args.listen
        print("Listening...")
        while time.time() < t_end:
            line = ser.readline().decode("utf-8", errors="ignore").strip()
            if line:
                print("RX:", line)

    ser.close()

if __name__ == "__main__":
    main()
