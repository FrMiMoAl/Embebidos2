import serial
import time
from pathlib import Path


# Configuración UART
PORT = "/dev/serial0"
BAUD = 115200
FILE = Path("/home/raspberry/Desktop/pruebageneral/speed.txt")    
TIEMPO_FILE = Path("/home/raspberry/Desktop/pruebageneral/tiempo.txt") #3 tiempos: parada,espera y giro


def clamp_speed(v):
    try:
        v = float(v)
    except:
        return 80  
    v = int(round(v))
    if v < 0: v = 0
    if v > 100: v = 100
    return v

def send_speed(ser, speed):
    speed = clamp_speed(speed)
    msg = f"S={speed}\n".encode()
    ser.write(msg)
    ser.flush()
    print(f">> SPEED: {speed}")

def send_sel(ser, sel):
    sel = (sel or "N").strip()[:1].upper()
    if sel not in {"A", "B", "X", "Y", "N"}:
        sel = "N"
    ser.write(f"{sel}\n".encode())
    ser.flush()
    print(f">> SEL: {sel}")

def darlavuelta(ser, tiempos):
	
	stop_delay, y_delay, rotation_time = tiempos
	send_speed(ser, 0)
	send_sel(ser, "N")
	time.sleep(stop_delay)
	send_sel(ser, "Y")
	time.sleep(y_delay)
	send_sel(ser, "A")
	time.sleep(rotation_time)
	send_sel(ser, "N")

def read_speed_from_file():
	try:
		if FILE.exists():
			return clamp_speed(FILE.read_text().strip())
	except Exception:
		pass
	return 80

def read_tiempos_from_file():
	try:
		if TIEMPO_FILE.exists():
			txt = TIEMPO_FILE.read_text().strip()
			import re
			nums = re.findall(r"[-+]?\d*\.?\d+", txt)
			vals = [float(x) for x in nums]
			for i, v in enumerate(vals[:3]):
				defaults[i] = v
	except Exception:
		pass
	return tuple(defaults)

def main():
	ser = serial.Serial(PORT, BAUD, timeout=0.2)
	velocidad = read_speed_from_file()
	tiempos = read_tiempos_from_file()

	while True:
		try:
			raw = ser.readline()
			try:
				data = raw.decode(errors="ignore").strip()
			except:
				data = raw.decode('utf-8', 'ignore').strip()
			if not data:
				continue
			if data.lower() == "pared":
				print("Pared detectada")
				darlavuelta(ser, tiempos)
				time.sleep(0.05)
				continue

			time.sleep(0.05)

		except KeyboardInterrupt:
			print("\nSaliendo...")
			send_speed(ser, 0)
			send_sel(ser, "N")
			break
		except Exception as e:
			print("Error:", e)
			time.sleep(0.2)

if __name__ == "__main__":
    main()