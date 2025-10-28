import threading, time
import cv2, numpy as np

# GPIO en RPi4
try:
    import RPi.GPIO as GPIO
    _HAS_GPIO = True
except Exception:
    _HAS_GPIO = False
    print("No se pudo importar RPi.GPIO. Simularé LEDs por consola.")

LED_PINS = [17, 27, 22, 23]
if isinstance(LED_PINS, int): LED_PINS = [LED_PINS]

CAM_INDEX = 0
LOOP_HZ = 30; DT = 1.0/LOOP_HZ
AREA_THRESH_RG = 2000
MIN_BLUE_AREA = 1200
HALF_SPEED = 50
SERVO_CENTER = 50

HSV_RANGES = {
    "red1":  ((0,   100, 80),  (10,  255, 255)),
    "red2":  ((170, 100, 80),  (179, 255, 255)),
    "green": ((45,   80, 80),  (85,  255, 255)),
    "blue":  ((100, 100, 80),  (130, 255, 255)),
}

def clamp(v, lo, hi): return max(lo, min(hi, v))

class ModelB(threading.Thread):
    """Rojo avanza, Verde retrocede, Azul → STOP y enciende LEDs locales según cantidad de objetos."""
    def __init__(self, ser):
        super().__init__(daemon=True)
        self.ser = ser
        self.stop_event = threading.Event()
        self.cap = None
        self._gpio_ready = False
        self._last_leds_on = -1

        if _HAS_GPIO:
            try:
                GPIO.setwarnings(False)
                GPIO.setmode(GPIO.BCM)
                for p in LED_PINS: GPIO.setup(p, GPIO.OUT, initial=GPIO.LOW)
                self._gpio_ready = True
            except Exception as e:
                print(f"GPIO init falló: {e}. Simularé LEDs.")
                self._gpio_ready = False

    def stop(self): self.stop_event.set()
    def stopped(self): return self.stop_event.is_set()

    def send(self, p1, p2, s):
        p1, p2 = clamp(int(p1), -100, 100), clamp(int(p2), -100, 100)
        s = clamp(int(s), 30, 70)
        self.ser.send(f"{p1},{p2},{s}")

    def _open_cam(self):
        self.cap = cv2.VideoCapture(CAM_INDEX, cv2.CAP_V4L2)
        if not self.cap.isOpened():
            self.cap = cv2.VideoCapture(CAM_INDEX)
        if not self.cap.isOpened():
            raise RuntimeError("No se pudo abrir la cámara.")
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT,480)
        self.cap.set(cv2.CAP_PROP_FPS,30)

    def _detect_masks(self, bgr):
        hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
        red1 = cv2.inRange(hsv, np.array(HSV_RANGES["red1"][0]), np.array(HSV_RANGES["red1"][1]))
        red2 = cv2.inRange(hsv, np.array(HSV_RANGES["red2"][0]), np.array(HSV_RANGES["red2"][1]))
        mask_red = cv2.bitwise_or(red1, red2)
        mask_green = cv2.inRange(hsv, np.array(HSV_RANGES["green"][0]), np.array(HSV_RANGES["green"][1]))
        mask_blue  = cv2.inRange(hsv, np.array(HSV_RANGES["blue"][0]),  np.array(HSV_RANGES["blue"][1]))
        return mask_red, mask_green, mask_blue

    def _count_blue(self, mask_blue):
        k = np.ones((3,3), np.uint8)
        m = cv2.morphologyEx(mask_blue, cv2.MORPH_OPEN, k, iterations=1)
        m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, k, iterations=1)
        cs, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        return sum(1 for c in cs if cv2.contourArea(c) >= MIN_BLUE_AREA)

    def _set_leds(self, n):
        n = clamp(int(n), 0, len(LED_PINS))
        if self._last_leds_on == n: return
        self._last_leds_on = n
        if _HAS_GPIO and self._gpio_ready:
            try:
                for i,p in enumerate(LED_PINS):
                    GPIO.output(p, GPIO.HIGH if i < n else GPIO.LOW)
            except Exception as e:
                print(f"GPIO.output falló: {e}. Desactivo GPIO.")
                self._gpio_ready = False
        estados = ["ON" if i < n else "OFF" for i in range(len(LED_PINS))]
        print(f"LEDs: {estados}")

    def _clear_leds(self): self._set_leds(0)

    def run(self):
        print("==== MODEL B (VISIÓN) ====")
        try:
            self._open_cam()
            next_t = time.monotonic()
            while not self.stopped():
                ok, frame = self.cap.read()
                if not ok:
                    print("Cámara sin frame; STOP.")
                    self.send(0,0,SERVO_CENTER); time.sleep(0.2); continue

                mr, mg, mb = self._detect_masks(frame)
                red_area, green_area = int(np.sum(mr>0)), int(np.sum(mg>0))
                blue_count = self._count_blue(mb)

                if red_area > AREA_THRESH_RG:
                    print(f"Color: ROJO area={red_area}")
                    self._clear_leds()
                    self.send(HALF_SPEED, HALF_SPEED, SERVO_CENTER)
                elif green_area > AREA_THRESH_RG:
                    print(f"Color: VERDE area={green_area}")
                    self._clear_leds()
                    self.send(-HALF_SPEED, -HALF_SPEED, SERVO_CENTER)
                elif blue_count > 0:
                    leds = min(blue_count, len(LED_PINS))
                    print(f"Color: AZUL objs={blue_count} -> LEDs={leds}")
                    self._set_leds(leds)
                    self.send(0,0,SERVO_CENTER)
                else:
                    print("Sin color. STOP.")
                    self._clear_leds()
                    self.send(0,0,SERVO_CENTER)

                _ = self.ser.receive()  # muestra RX si llega algo
                next_t += 1.0/LOOP_HZ
                dt = next_t - time.monotonic()
                if dt > 0: time.sleep(dt)
                else: next_t = time.monotonic()
        except KeyboardInterrupt:
            print("ModelB: interrumpido.")
        finally:
            try:
                if self.cap is not None: self.cap.release()
                cv2.destroyAllWindows()
            finally:
                try: self._clear_leds()
                finally:
                    if _HAS_GPIO and self._gpio_ready:
                        try: GPIO.cleanup()
                        except Exception as e: print(f"GPIO.cleanup: {e}")
            print("ModelB: stop.")
            self.send(0,0,SERVO_CENTER)
