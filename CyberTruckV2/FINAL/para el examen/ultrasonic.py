# ultra_pin_test.py
# Prueba de ultrasonido (HC-SR04 / similar) con pines configurables
# MicroPython (Raspberry Pi Pico / Pico W)

import time
from machine import Pin, time_pulse_us

# ========= CAMBIA ESTO =========
TRIG_PIN = 20      # <-- pon aquí tu pin TRIG (GPIO)
ECHO_PIN = 21      # <-- pon aquí tu pin ECHO (GPIO)
TIMEOUT_US = 30000 # <-- aumenta si mides lejos (ej 60000)
# ===============================

trig = Pin(TRIG_PIN, Pin.OUT, value=0)
echo = Pin(ECHO_PIN, Pin.IN)

def ping_once():
    # asegurar TRIG bajo
    trig.value(0)
    time.sleep_us(2)

    # pulso de 10us
    trig.value(1)
    time.sleep_us(10)
    trig.value(0)

    # medir pulso en HIGH
    return time_pulse_us(echo, 1, TIMEOUT_US)

def dur_to_cm(dur_us):
    # distancia cm = (dur_us * velocidad_sonido_cm_us) / 2
    # velocidad sonido ≈ 0.0343 cm/us
    return (dur_us * 0.0343) / 2

print("🔍 Ultrasonido test (pines configurables)")
print("TRIG_PIN =", TRIG_PIN, "ECHO_PIN =", ECHO_PIN, "TIMEOUT_US =", TIMEOUT_US)
print("⚠️ Nota: si usas HC-SR04, ECHO suele ser 5V. Usa divisor/level shifter para 3.3V.\n")

# warm-up
for _ in range(3):
    try:
        ping_once()
    except:
        pass
    time.sleep_ms(80)

try:
    while True:
        echo_before = echo.value()

        try:
            dur = ping_once()
        except OSError as e:
            print("❌ OSError:", e, "| echo_before=", echo_before)
            time.sleep_ms(200)
            continue

        echo_after = echo.value()

        if dur < 0:
            # -1/-2: timeout o fallo
            print(f"⚠️ dur={dur} | echo_before={echo_before} echo_after={echo_after}")
        else:
            cm = dur_to_cm(dur)
            print(f"✅ dur={dur} us | dist={cm:.2f} cm | echo_before={echo_before} echo_after={echo_after}")

        time.sleep_ms(150)

except KeyboardInterrupt:
    print("\n🛑 Stop")
