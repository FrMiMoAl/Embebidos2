from ultrasonido import Ultrasonido
from machine import Pin, PWM, UART
import time

uart = UART(1, baudrate=115200, tx=4, rx=5)
sensor = Ultrasonido(trig_pin=19, echo_pin=18, timeout_us=30000)

velocidad = 0
sel = "N"
msgg = f"Pared"

def ajustar_velocidad(dist, s):
    if dist < 4: 
        uart.write((msgg + "\n").encode())
        return 0
    if dist < 20: 
        return int(s * (dist/20))
    return s

# Motores
AIN1, AIN2, PWMA = Pin(21, Pin.OUT), Pin(20, Pin.OUT), PWM(Pin(28))
BIN1, BIN2, PWMB = Pin(22, Pin.OUT), Pin(26, Pin.OUT), PWM(Pin(27))
PWMA.freq(1000); PWMB.freq(1000)

def motorA(s):
    AIN1.value(s>0); AIN2.value(s<0)
    PWMA.duty_u16(int(max(0,min(65535,abs(s)*655))))  # s: 0..100 aprox.

def motorB(s):
    BIN1.value(s>0); BIN2.value(s<0)
    PWMB.duty_u16(int(max(0,min(65535,abs(s)*655))))

def stop():
    motorA(0); motorB(0)


PRINT_PERIOD_MS = 200
last_print = time.ticks_ms()

while True:
    if uart.any():
        raw = uart.readline()
        if raw:
            if isinstance(raw, (bytes, bytearray, memoryview)):
                line = bytes(raw).decode('utf-8', 'ignore').strip()
            else:
                line = raw.strip()
            # Ver lo recibido en consola
            #print("RX:", line)
            if line.startswith("S="):
                try: velocidad = int(line.split("=", 1)[1])
                except: pass
            elif line in ("A","B","X","Y","N"):
                sel = line

    # Medición y control
    d = sensor.distancia_cm(samples=3)
    v = ajustar_velocidad(d, velocidad)

    if sel=="A":
        motorA(v)
        motorB(0)
    elif sel=="B":
        motorA(0)
        motorB(v)
    elif sel=="X":
        motorA(v)
        motorB(v)
    elif sel=="Y":
        motorA(-v)
        motorB(-v)
    else:
        stop()

    # --- Mostrar en pantalla (consola USB/Thonny) y enviar por UART ---
    now = time.ticks_ms()
    if time.ticks_diff(now, last_print) >= PRINT_PERIOD_MS:
        if d >= 0:
            msg = f"DIST: {d:.1f} cm | SPEED: {v} | SEL: {sel}"
            #msg=". "
        else:
            msg = f"DIST: -- (timeout) | SPEED: {v} | SEL: {sel}"
            #msg=". "
        print(msg)  # => visible en la consola del Pico
        # si también quieres verlo en la Raspberry por el mismo UART:
        #uart.write((msg + "\n").encode())
        last_print = now

    time.sleep(0.05)