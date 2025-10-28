#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import threading
from math import copysign

# --- Módulos propios ---
from ps4_controller import PS4Controller
from serial_comm import SerialComm

# --- OpenCV para Model B ---
import cv2
import numpy as np

# =========================
# CONFIGURACIÓN GENERAL
# =========================
SERIAL_PORT = "/dev/serial0"
SERIAL_BAUD = 115200

LOOP_HZ = 30                 # Frecuencia del loop principal por modelo
DT = 1.0 / LOOP_HZ

# Límites de salida
PWM_MIN, PWM_MAX = -100, 100
SERVO_MIN, SERVO_MAX = 30, 70
SERVO_CENTER = 50

# ---- Model A (autónomo) ----
FWD_SPEED = 60               # velocidad de avance normal
TURN_SPEED = 70              # velocidad de giro en el lugar
DIST_THRESH_CM = 20          # umbral de distancia (Pico debe mandar distancia por UART)
TURN_SEC_PER_DEG = 0.008     # <-- CALIBRAR: segundos que tarda en girar 1° (motores opuestos)

# ---- Model B (visión) ----
CAM_INDEX = 0
HALF_SPEED = 50

# Rangos HSV (ajusta a tu iluminación)
HSV_RANGES = {
    "red1":  ((0,   100,  80),  (10,  255, 255)),
    "red2":  ((170, 100,  80),  (179, 255, 255)),
    "red3":  ((170, 130,  180),  (255, 255, 255)),
    "green": ((56,  161,  63),  (97,  255, 161)),
    "blue":  ((86, 142,  131),  (131, 255, 255)),

}

# =========================
# UTILIDADES
# =========================
def clamp(val, lo, hi):
    return max(lo, min(hi, val))

def mix_diff(speed, turn):  # speed [-100..100], turn [-100..100]
    left  = clamp(speed + turn, PWM_MIN, PWM_MAX)
    right = clamp(speed - turn, PWM_MIN, PWM_MAX)
    return left, right

def servo_from_lx(lx):  # lx en [-1..1]
    ang = int(round(SERVO_CENTER + 20 * lx))
    return clamp(ang, SERVO_MIN, SERVO_MAX)

def to_int(v):
    try:
        return int(float(v))
    except:
        return None

# =========================
# CLASE BASE DE MODELOS
# =========================
class BaseModel(threading.Thread):
    def __init__(self, ser: SerialComm):
        super().__init__(daemon=True)
        self.ser = ser
        self.stop_event = threading.Event()   # <-- nombre nuevo

    def stop(self):
        self.stop_event.set()

    def stopped(self):
        return self.stop_event.is_set()

    def send(self, pwm1, pwm2, servo):
        pwm1 = clamp(int(pwm1), PWM_MIN, PWM_MAX)
        pwm2 = clamp(int(pwm2), PWM_MIN, PWM_MAX)
        servo = clamp(int(servo), SERVO_MIN, SERVO_MAX)
        self.ser.send(f"{pwm1},{pwm2},{servo}")

# =========================
# MODEL A: AUTÓNOMO
# Avanza hasta detectar objeto (distancia por UART desde la Pico),
# luego gira 180° en el lugar y continúa. Además permite giros por grados
# sin bloquear usando una pequeña máquina de estados.
# =========================
class ModelA(BaseModel):
    def __init__(self, ser: SerialComm):
        super().__init__(ser)
        self.state = "forward"
        self.turn_end_t = 0.0
        self.turn_dir = 1                # +1 derecha, -1 izquierda
        self.pending_turn_deg = 0.0      # solicitud externa de giro (no-bloqueante)

    def request_turn(self, degrees):
        """Pedir un giro (positivo = derecha, negativo = izquierda) sin bloquear el bucle."""
        self.pending_turn_deg += degrees

    def _start_turn(self, degrees):
        dur = abs(degrees) * TURN_SEC_PER_DEG
        self.turn_dir = 1 if degrees >= 0 else -1
        self.turn_end_t = time.monotonic() + dur
        self.state = "turning"

    def _maybe_parse_distance(self, line):
        """
        Intenta obtener distancia en cm desde una línea UART.
        Acepta formatos tipo: '23', 'DIST:23.5', 'd=23'.
        """
        if not line:
            return None
        line = line.strip()
        # Saca el primer número que encuentre
        num = ""
        for ch in line:
            if ch.isdigit() or ch in ".-":
                num += ch
            elif num:
                break
        return float(num) if num not in ("", "-", ".", "-.") else None

    def run(self):
        print("[ModelA] start")
        next_tick = time.monotonic()
        while not self.stopped():
            now = time.monotonic()

            # 1) ¿hay pedido externo de giro?
            if self.state == "forward" and abs(self.pending_turn_deg) > 0.1:
                deg = self.pending_turn_deg
                self.pending_turn_deg = 0.0
                self._start_turn(deg)

            # 2) Lógica de estado
            if self.state == "forward":
                # Leer distancia desde Pico (si manda algo)
                line = self.ser.receive()
                dist = self._maybe_parse_distance(line)
                if dist is not None and dist <= DIST_THRESH_CM:
                    # objeto cerca → giro 180° derecha
                    self._start_turn(180)

                # avanzar recto
                self.send(FWD_SPEED, FWD_SPEED, SERVO_CENTER)

            elif self.state == "turning":
                if now >= self.turn_end_t:
                    self.state = "forward"
                # girar en el lugar
                pwm = TURN_SPEED * self.turn_dir
                self.send(pwm, -pwm, SERVO_CENTER)

            # Ritmo de loop
            next_tick += DT
            sleep_t = next_tick - time.monotonic()
            if sleep_t > 0:
                time.sleep(sleep_t)
            else:
                next_tick = time.monotonic()

        # al salir, frena
        self.send(0, 0, SERVO_CENTER)
        print("[ModelA] stop")

# =========================
# MODEL B: VISIÓN POR COLOR
# Rojo → avanza a media velocidad
# Verde → retrocede a media velocidad
# Azul → solo LEDs (motores en 0; Pico decide LEDs con otro canal si lo tienes)
# =========================
# ===== GPIO para LEDs (colócalo una sola vez arriba de la clase, fuera de ModelB) =====
try:
    import RPi.GPIO as GPIO
    _HAS_GPIO = True
except Exception:
    _HAS_GPIO = False
    print("No se pudo importar RPi.GPIO. Simularé LEDs por consola.")

# Asegura que LED_PINS sea lista
LED_PINS = [17, 27, 22, 23]
if isinstance(LED_PINS, int):
    LED_PINS = [LED_PINS]

# Parámetros usados por ModelB (ajusta si ya los tienes definidos)
CAM_INDEX = 0
LOOP_HZ = 30
DT = 1.0 / LOOP_HZ
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

def clamp(val, lo, hi):
    return max(lo, min(hi, val))


class ModelB(threading.Thread):
    """
    Modelo B: Visión + LEDs en la RPi4.
    ROJO  -> avanza  (50, 50, 50)
    VERDE -> retrocede (-50, -50, 50)
    AZUL  -> STOP motores y enciende 0..4 LEDs según # de objetos azules
    """

    def __init__(self, ser):
        super().__init__(daemon=True)
        self.ser = ser
        self.stop_event = threading.Event()
        self.cap = None

        # Estado interno de LEDs / GPIO
        self._gpio_ready = False
        self._last_leds_on = -1

        if _HAS_GPIO:
            try:
                GPIO.setwarnings(False)
                GPIO.setmode(GPIO.BCM)
                for pin in LED_PINS:
                    GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)
                self._gpio_ready = True
            except Exception as e:
                print(f"GPIO init falló: {e}. Simularé LEDs por consola.")
                self._gpio_ready = False

    # ------------ utilidades ------------
    def stop(self):
        self.stop_event.set()

    def stopped(self):
        return self.stop_event.is_set()

    def send(self, pwm1, pwm2, servo):
        pwm1 = clamp(int(pwm1), -100, 100)
        pwm2 = clamp(int(pwm2), -100, 100)
        servo = clamp(int(servo), 30, 70)
        self.ser.send(f"{pwm1},{pwm2},{servo}")  # SerialComm ya imprime [TX]

    def _open_cam(self):
        # Usa backend V4L2 para evitar problemas con gstreamer
        self.cap = cv2.VideoCapture(CAM_INDEX, cv2.CAP_V4L2)
        if not self.cap.isOpened():
            # Fallback sin especificar backend
            self.cap = cv2.VideoCapture(CAM_INDEX)
        if not self.cap.isOpened():
            raise RuntimeError("No se pudo abrir la cámara (VideoCapture).")
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_FPS, 30)

    def _detect_masks(self, frame_bgr):
        hsv = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2HSV)
        red1 = cv2.inRange(hsv, np.array(HSV_RANGES["red1"][0]), np.array(HSV_RANGES["red1"][1]))
        red2 = cv2.inRange(hsv, np.array(HSV_RANGES["red2"][0]), np.array(HSV_RANGES["red2"][1]))
        mask_red = cv2.bitwise_or(red1, red2)
        mask_green = cv2.inRange(hsv, np.array(HSV_RANGES["green"][0]), np.array(HSV_RANGES["green"][1]))
        mask_blue  = cv2.inRange(hsv, np.array(HSV_RANGES["blue"][0]),  np.array(HSV_RANGES["blue"][1]))
        return mask_red, mask_green, mask_blue

    def _count_blue_objects(self, mask_blue):
        kernel = np.ones((3,3), np.uint8)
        mask = cv2.morphologyEx(mask_blue, cv2.MORPH_OPEN, kernel, iterations=1)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=1)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        count = 0
        for c in contours:
            if cv2.contourArea(c) >= MIN_BLUE_AREA:
                count += 1
        return count

    def _set_leds(self, n):
        n = clamp(int(n), 0, len(LED_PINS))
        if self._last_leds_on == n:
            return
        self._last_leds_on = n

        if _HAS_GPIO and self._gpio_ready:
            try:
                for i, pin in enumerate(LED_PINS):
                    GPIO.output(pin, GPIO.HIGH if i < n else GPIO.LOW)
            except Exception as e:
                print(f"GPIO.output falló: {e}. Desactivo GPIO.")
                self._gpio_ready = False

        estados = ["ON" if i < n else "OFF" for i in range(len(LED_PINS))]
        print(f"LEDs: {estados}")

    def _clear_leds(self):
        self._set_leds(0)

    # ------------ loop principal ------------
    def run(self):
        print("==== MODEL B (VISIÓN) ====")
        try:
            self._open_cam()
            next_tick = time.monotonic()

            while not self.stopped():
                ok, frame = self.cap.read()
                if not ok:
                    print("Cámara: frame inválido; STOP motores.")
                    self.send(0, 0, SERVO_CENTER)
                    time.sleep(0.2)
                    continue

                mask_red, mask_green, mask_blue = self._detect_masks(frame)
                red_area   = int(np.sum(mask_red   > 0))
                green_area = int(np.sum(mask_green > 0))
                blue_count = self._count_blue_objects(mask_blue)

                if red_area > AREA_THRESH_RG:
                    print(f"Color detectado: ROJO | area={red_area}")
                    self._clear_leds()
                    self.send(HALF_SPEED, HALF_SPEED, SERVO_CENTER)

                elif green_area > AREA_THRESH_RG:
                    print(f"Color detectado: VERDE | area={green_area}")
                    self._clear_leds()
                    self.send(-HALF_SPEED, -HALF_SPEED, SERVO_CENTER)

                elif blue_count > 0:
                    leds_on = min(blue_count, len(LED_PINS))
                    print(f"Color detectado: AZUL | objetos={blue_count} -> LEDs={leds_on}")
                    self._set_leds(leds_on)
                    self.send(0, 0, SERVO_CENTER)

                else:
                    print("Sin color relevante. STOP.")
                    self._clear_leds()
                    self.send(0, 0, SERVO_CENTER)

                # Mostrar cualquier RX de Pico (no bloquea)
                _ = self.ser.receive()

                next_tick += DT
                sleep_t = next_tick - time.monotonic()
                if sleep_t > 0:
                    time.sleep(sleep_t)
                else:
                    next_tick = time.monotonic()

        except KeyboardInterrupt:
            print("ModelB: Interrumpido por usuario.")
        finally:
            try:
                if self.cap is not None:
                    self.cap.release()
                cv2.destroyAllWindows()
            finally:
                # Limpieza segura de LEDs/GPIO
                try:
                    self._clear_leds()
                finally:
                    if _HAS_GPIO and self._gpio_ready:
                        try:
                            GPIO.cleanup()
                        except Exception as e:
                            print(f"GPIO.cleanup aviso: {e}")
            print("ModelB: stop (motores en 0).")
            self.send(0, 0, SERVO_CENTER)

# =========================
# MODEL C: MANUAL POR PS4
# Joystick izquierdo:
#   LY → velocidad (-1 = adelante, +1 = atrás)  → speed = -LY*100
#   LX → servo 30..70                            → servo = 50 + 20*LX
# Mezcla diferencial para pwm1/pwm2
# =========================
class ModelC(BaseModel):
    def __init__(self, ser: SerialComm, ps4: PS4Controller):
        super().__init__(ser)
        self.ps4 = ps4

    def run(self):
        print("[ModelC] start")
        next_tick = time.monotonic()

        while not self.stopped():
            self.ps4.update()

            lx = self.ps4.get_axis(0)  # -1..1
            ly = self.ps4.get_axis(1)  # -1..1

            speed = int(round(-ly * 100))           # arriba (ly=-1) = +100
            turn  = int(round(lx * 100))            # -100..100
            left, right = mix_diff(speed, turn)
            servo = servo_from_lx(lx)

            self.send(left, right, servo)

            # Ritmo
            next_tick += DT
            sleep_t = next_tick - time.monotonic()
            if sleep_t > 0:
                time.sleep(sleep_t)
            else:
                next_tick = time.monotonic()

        # al salir, frena
        self.send(0, 0, SERVO_CENTER)
        print("[ModelC] stop")

# =========================
# SUPERVISOR DE MODOS
# =========================
class Supervisor:
    """
    Mantiene un único modelo activo. Cambia por botones del PS4:
      Triangle(3) -> ModelA
      Circle(1)   -> ModelB
      Cross(0)    -> ModelC
      Square(2)   -> STOP
    """
    def __init__(self):
        self.ser = SerialComm(port=SERIAL_PORT, baudrate=SERIAL_BAUD)
        self.ps4 = PS4Controller(deadzone=0.15)

        self.active = None
        self.active_name = "STOP"

        # para detectar flancos (press event)
        self.last_btn = {0:0, 1:0, 2:0, 3:0}

    def _start_model(self, name):
        self._stop_active()

        if name == "A":
            self.active = ModelA(self.ser)
        elif name == "B":
            self.active = ModelB(self.ser)
        elif name == "C":
            self.active = ModelC(self.ser, self.ps4)
        else:
            self.active = None

        self.active_name = name
        if self.active:
            self.active.start()
            print(f"[Supervisor] Modelo {name} activo")
        else:
            # STOP
            self.ser.send(f"0,0,{SERVO_CENTER}")
            print("[Supervisor] STOP")

    def _stop_active(self):
        if self.active and self.active.is_alive():
            self.active.stop()
            self.active.join(timeout=1.0)
        self.active = None

    def loop(self):
        print("\n=== Controles de modo (PS4) ===")
        print("🔺 Triángulo → Model A  |  ⭕ Círculo → Model B  |  ❌ Cruz → Model C  |  🔳 Cuadrado → STOP")
        print("Siempre se envía: pwm1,pwm2,servo (30–70)")

        self._start_model("C")  # arranca en manual por comodidad

        try:
            while True:
                # leer estado del control
                self.ps4.update()
                for idx in (0,1,2,3):  # Cross=0, Circle=1, Square=2, Triangle=3
                    cur = self.ps4.get_button(idx)
                    if cur == 1 and self.last_btn[idx] == 0:
                        # Evento de PRESIÓN
                        if idx == 3:      # Triangle
                            self._start_model("A")
                        elif idx == 1:    # Circle
                            self._start_model("B")
                        elif idx == 0:    # Cross
                            self._start_model("C")
                        elif idx == 2:    # Square
                            self._start_model("STOP")
                    self.last_btn[idx] = cur

                # Ejemplo: en Model A puedes pedir giros finos con el stick derecho o algo similar
                # (si quieres, aquí podrías leer otros ejes y llamar a request_turn)
                # if isinstance(self.active, ModelA):
                #     rx = self.ps4.get_axis(2)  # si tu driver expone RX
                #     if abs(rx) > 0.5:
                #         self.active.request_turn(15 * copysign(1, rx))

                time.sleep(0.02)

        except KeyboardInterrupt:
            print("\n[Supervisor] Saliendo...")
        finally:
            self._stop_active()
            self.ser.close()

# =========================
# MAIN
# =========================
if __name__ == "__main__":
    Supervisor().loop()
