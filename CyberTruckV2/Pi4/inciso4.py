import cv2
from color_detector import ColorDetector
from serial_comm import SerialComm

serial_device = SerialComm("/dev/serial0",115200)

# Rango HSV (ajústalos si hace falta)
color_ranges = {
    "red":   [(170, 130, 180), (255, 255, 255)],
    "green": [(56, 161, 63),    (97, 255, 161)],
    "blue":  [(86, 142, 131), (131, 255, 255)]
}

detector = ColorDetector(color_ranges)
cap = cv2.VideoCapture(0)

# --------- Helpers robustos ----------
def _item_color(item):
    """
    Intenta extraer el nombre de color de un item de detección, en minúsculas.
    Soporta: dicts {'color': 'red'...}, tuplas/listas ('red', ...), strings 'red'.
    Retorna None si no se reconoce.
    """
    c = None
    if isinstance(item, dict):
        c = item.get("color")
    elif isinstance(item, (list, tuple)) and len(item) > 0 and isinstance(item[0], str):
        c = item[0]
    elif isinstance(item, str):
        c = item
    return c.lower() if isinstance(c, str) else None

def has_color(detections, color_name):
    """True si hay al menos un objeto del color dado."""
    cname = color_name.lower()
    if detections is None:
        return False

    # Caso dict por color: {'red': [...], 'green': [...]}  o {'Red': 1}
    if isinstance(detections, dict):
        # tolerante a mayúsculas: busca clave sin sensibilidad
        key = None
        for k in detections.keys():
            if isinstance(k, str) and k.lower() == cname:
                key = k
                break
        if key is None:
            return False
        val = detections[key]
        try:
            return len(val) > 0  # si es lista/tupla
        except TypeError:
            return bool(val)     # si es contador/flag
    # Caso lista de detecciones heterogéneas
    if isinstance(detections, (list, tuple)):
        for it in detections:
            c = _item_color(it)
            if c == cname:
                return True
        return False
    return False

def count_color(detections, color_name):
    """Cuenta cuántos objetos del color dado hay (si no se puede, al menos 1/0)."""
    cname = color_name.lower()
    if detections is None:
        return 0
    if isinstance(detections, dict):
        key = None
        for k in detections.keys():
            if isinstance(k, str) and k.lower() == cname:
                key = k
                break
        if key is None:
            return 0
        val = detections[key]
        try:
            return len(val)
        except TypeError:
            return int(bool(val))
    if isinstance(detections, (list, tuple)):
        return sum(1 for it in detections if _item_color(it) == cname)
    return 0
# -------------------------------------

# Banderas de control
red_detected   = 0
green_detected = 0
blue_detected  = 0

while True:
    ok, frame = cap.read()
    if not ok:
        break

    result_frame, detections = detector.detect_colors(frame)

    # Actualiza banderas
    red_detected   = 1 if has_color(detections, "red")   else 0
    green_detected = 1 if has_color(detections, "green") else 0
    blue_detected  = 1 if has_color(detections, "blue")  else 0
    
    if red_detected:
        #mandar algo por serial
        serial_device.send("50,50,50")
    if green_detected:
        #mandar algo por serial
        serial_device.send("-50,-50,50")
    if blue_detected:
        #mandar algo por serial
        serial_device.send("0,0,50")
    
    # (Opcional) cuentas por color
    n_red   = count_color(detections, "red")
    n_green = count_color(detections, "green")
    n_blue  = count_color(detections, "blue")

    # Debug claro
    print("Detections(raw):", detections)
    print(f"Flags -> 🔴{red_detected} 🟢{green_detected} 🔵{blue_detected} | "
          f"Counts -> R:{n_red} G:{n_green} B:{n_blue}")

    cv2.imshow("Color Detection", result_frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()