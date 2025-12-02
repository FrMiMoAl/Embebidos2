import cv2
from color_detector import ColorDetector
from serial_comm import SerialComm

serial_device = SerialComm("/dev/serial0",115200)

# ===== GPIO para LEDs (opcional) =====
try:
    import RPi.GPIO as GPIO
    _HAS_GPIO = True
except Exception:
    _HAS_GPIO = False
    print("⚠️  No se pudo importar RPi.GPIO. Simularé LEDs por consola.")

# Rango HSV (ajústalo si hace falta)
color_ranges = {
    "red":   [(170, 130, 180), (255, 255, 255)],
    "green": [(56, 161, 63),    (97, 255, 161)],
    "blue":  [(86, 142, 131), (131, 255, 255)]
}

detector = ColorDetector(color_ranges)
cap = cv2.VideoCapture(0)

LED_PINS = [17, 27, 22, 23]  # 4 LEDs máx.
if _HAS_GPIO:
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    for pin in LED_PINS:
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, GPIO.LOW)

blue_detected = 0

def count_blue_objects(detections):
    """
    Devuelve cuántos objetos 'blue' hay, soportando:
      - dict: {'blue': [...], 'red': [...]}  -> len(d['blue'])
      - list: [{'color':'blue',...}, ('blue', ...), 'blue', ...]
    """
    if detections is None:
        return 0

    # Caso 1: diccionario por color
    if isinstance(detections, dict):
        lst = detections.get("blue", [])
        try:
            return len(lst)
        except TypeError:
            return int(bool(lst))

    # Caso 2: lista/tupla genérica de detecciones
    if isinstance(detections, (list, tuple)):
        cnt = 0
        for d in detections:
            if isinstance(d, dict) and d.get("color", "").lower() == "blue":
                cnt += 1
            elif isinstance(d, (list, tuple)) and len(d) > 0 and isinstance(d[0], str) and d[0].lower() == "blue":
                cnt += 1
            elif isinstance(d, str) and d.lower() == "blue":
                cnt += 1
        return cnt

    return 0

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        result_frame, detections = detector.detect_colors(frame)

        blue_count = count_blue_objects(detections)
        blue_detected = 1 if blue_count > 0 else 0
        if blue_detected:
        #mandar algo por serial
            serial_device.send("0,0,50")

        leds_on = min(blue_count, len(LED_PINS))
        if _HAS_GPIO:
            for i, pin in enumerate(LED_PINS):
                GPIO.output(pin, GPIO.HIGH if i < leds_on else GPIO.LOW)
        else:
            estados = ["ON" if i < leds_on else "OFF" for i in range(len(LED_PINS))]
            print(f"LEDs(sim): {estados}")

        # Logs útiles
        print(f"blue_detected={blue_detected} | blue_count={blue_count} | detections={detections}")

        cv2.imshow("Color Detection", result_frame)

        # Salir con 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
finally:
    cap.release()
    cv2.destroyAllWindows()
    if _HAS_GPIO:
        for pin in LED_PINS:
            GPIO.output(pin, GPIO.LOW)
        GPIO.cleanup()

