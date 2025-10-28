import time, cv2, numpy as np

# --- Constantes ---
LED_PINS = [17, 27, 22, 23]
CAM_INDEX = 0
LOOP_HZ = 30
AREA_THRESH_RG = 2000
MIN_BLUE_AREA = 1200
HALF_SPEED = 50

STOP=0; 
ADELANTE=1 
ATRAS=2
DERECHA=3
IZQUIERDA=4
DiagDerechaAdelante=5
DiagIzquierdaAdelante=6
DiagDerechaAtras=7
DiagIzquierdaAtras=8
Giroderecha=9
Giroizquierda=10

HSV = {
    "red1":  (np.array((  0,100, 80), np.uint8), np.array(( 10,255,255), np.uint8)),
    "red2":  (np.array((170,100, 80), np.uint8), np.array((179,255,255), np.uint8)),
    "green": (np.array(( 45, 80, 80), np.uint8), np.array(( 85,255,255), np.uint8)),
    "blue":  (np.array((100,100, 80), np.uint8), np.array((130,255,255), np.uint8)),
}
K33 = np.ones((3,3), np.uint8)

def clamp(v, lo, hi): return max(lo, min(hi, v))

class LEDs:
    def __init__(self, pins):
        self.pins = pins; self.last = -1
        try:
            import RPi.GPIO as GPIO
            self.GPIO = GPIO; GPIO.setwarnings(False); GPIO.setmode(GPIO.BCM)
            for p in pins: GPIO.setup(p, GPIO.OUT, initial=GPIO.LOW)
            self.hw = True
        except Exception as e:
            print(f"[LEDs] GPIO no disponible ({e}). Simulando."); self.hw=False; self.GPIO=None
    def set(self, n):
        n = clamp(int(n), 0, len(self.pins))
        if n == self.last: return
        self.last = n
        if self.hw:
            for i,p in enumerate(self.pins):
                self.GPIO.output(p, self.GPIO.HIGH if i < n else self.GPIO.LOW)
        print(f"[LEDs] {['ON' if i<n else 'OFF' for i in range(len(self.pins))]}")
    def clear(self): self.set(0)
    def cleanup(self):
        if self.hw:
            try: self.GPIO.cleanup()
            except Exception as e: print(f"[LEDs] cleanup: {e}")

def send(ser, speed, cmd):
    speed = clamp(int(speed), 0, 100)
    ser.send(f"S={speed}\n")
    ser.send(f"{int(cmd)}\n")

def open_cam(index=0):
    cap = cv2.VideoCapture(index, cv2.CAP_V4L2)
    if not cap.isOpened(): cap = cv2.VideoCapture(index)
    if not cap.isOpened(): raise RuntimeError("No se pudo abrir la cámara.")
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT,480)
    cap.set(cv2.CAP_PROP_FPS,30)
    return cap

def analyze(frame_bgr):
    hsv = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2HSV)

    red_low1,  red_high1  = HSV["red1"]
    red_low2,  red_high2  = HSV["red2"]
    green_low, green_high = HSV["green"]
    blue_low,  blue_high  = HSV["blue"]

    mask_red   = cv2.inRange(hsv, red_low1,  red_high1) | cv2.inRange(hsv, red_low2,  red_high2)
    mask_green = cv2.inRange(hsv, green_low, green_high)
    mask_blue  = cv2.inRange(hsv, blue_low,  blue_high)

    red_area   = int(cv2.countNonZero(mask_red))
    green_area = int(cv2.countNonZero(mask_green))

    mask_blue = cv2.morphologyEx(mask_blue, cv2.MORPH_OPEN,  K33, iterations=1)
    mask_blue = cv2.morphologyEx(mask_blue, cv2.MORPH_CLOSE, K33, iterations=1)

    contours, _ = cv2.findContours(mask_blue, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    blue_count = 0
    for contour in contours:
        area = cv2.contourArea(contour)
        if area >= MIN_BLUE_AREA:
            blue_count += 1

    return red_area, green_area, blue_count


if __name__ == "__main__":
    from serial_comm import SerialComm
    ser = SerialComm(port="/dev/serial0", baudrate=115200, timeout=0.1)
    leds = LEDs(LED_PINS)
    cap = None
    try:
        cap = open_cam(CAM_INDEX)
        next_t = time.monotonic()
        while True:
            ok, frame = cap.read()
            if not ok:
                print("[Cam] sin frame → STOP"); leds.clear(); send(ser, 0, STOP)
                time.sleep(0.2); continue

            red_area, green_area, blue_count = analyze(frame)

            if red_area > AREA_THRESH_RG:
                print(f"ROJO {red_area} → ADELANTE")
                leds.clear(); send(ser, HALF_SPEED, ADELANTE)
            elif green_area > AREA_THRESH_RG:
                print(f"VERDE {green_area} → ATRAS")
                leds.clear(); send(ser, HALF_SPEED, ATRAS)
            elif blue_count > 0:
                leds_n = min(blue_count, len(LED_PINS))
                print(f"AZUL objs={blue_count} → STOP, LEDs={leds_n}")
                leds.set(leds_n); send(ser, 0, STOP)
            else:
                print("Sin color → STOP")
                leds.clear(); send(ser, 0, STOP)

            try: _ = ser.receive()
            except: pass

            next_t += 1.0/LOOP_HZ
            delay = next_t - time.monotonic()
            time.sleep(delay if delay > 0 else 0)
            if delay <= 0: next_t = time.monotonic()

    except KeyboardInterrupt:
        print("Ctrl+C → STOP")
    finally:
        if cap is not None: cap.release()
        cv2.destroyAllWindows()
        leds.clear(); leds.cleanup()
        send(ser, 0, STOP)
        print("Fin.")
