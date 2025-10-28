#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Control automático por UART con ultrasonido remoto:
- Avanza continuamente hasta que recibe una distancia menor a umbral.
- Cuando detecta obstáculo, se detiene, gira 180° y vuelve a avanzar.
"""

import serial
import time
import threading
from pathlib import Path

# ======= CONFIGURACIÓN UART =======
PORT = "/dev/serial0"    # UART principal
BAUD = 115200
FILE = Path("/home/raspberry/Documents/puerto/control.txt")

# ======= PARÁMETROS DE CONTROL =======
DIST_THRESHOLD = 20.0   # cm - distancia mínima para girar
TURN_SPEED = 60         # velocidad de giro
TURN_DURATION = 1.6     # s - ajustar según hardware
FORWARD_SPEED = 100
DELAY_CHECK = 0.1       # s entre lecturas de UART

# ======= FUNCIONES DE COMUNICACIÓN =======
def clamp_speed(v):
    try:
        v = float(v)
    except:
        return 100
    v = int(round(v))
    if v < 0: v = 0
    if v > 100: v = 100
    return v

def send_speed(ser, speed):
    speed = clamp_speed(speed)
    ser.write(f"S={speed}\n".encode("utf-8"))
    ser.flush()
    return speed

def send_sel(ser, sel):
    sel = (sel or "N").strip()[:1].upper()
    if sel not in {"A", "B", "X", "Y", "N"}:
        sel = "N"
    ser.write(f"{sel}\n".encode("utf-8"))
    ser.flush()
    return sel

def enviar_y_log(ser, velocidad, instruccion, tag="auto"):
    v = send_speed(ser, velocidad)
    s = send_sel(ser, instruccion)
    print(f"[{tag}] speed={v}, sel={s}")

# ======= HILO PARA LECTURA DE DISTANCIA =======
class DistanceReader(threading.Thread):
    def __init__(self, ser):
        super().__init__(daemon=True)
        self.ser = ser
        self.distance = None
        self.running = True

    def run(self):
        buffer = ""
        while self.running:
            try:
                if self.ser.in_waiting > 0:
                    data = self.ser.read(self.ser.in_waiting).decode(errors="ignore")
                    buffer += data

                    # Buscar líneas completas (finalizan en \n)
                    if "\n" in buffer:
                        lines = buffer.split("\n")
                        buffer = lines[-1]  # lo que queda sin cerrar
                        for line in lines[:-1]:
                            self._process_line(line.strip())
            except Exception as e:
                print("[UART] Error leyendo:", e)
                time.sleep(0.1)

    def _process_line(self, line):
        # Espera recibir algo como "D=23.5"
        if line.startswith("D="):
            try:
                self.distance = float(line.split("=")[1])
            except ValueError:
                pass

    def stop(self):
        self.running = False


# ======= PROGRAMA PRINCIPAL =======
def main():
    print("[Sistema] Iniciando UART...")
    ser = serial.Serial(PORT, BAUD, timeout=0.1)
    reader = DistanceReader(ser)
    reader.start()

    try:
        print("[Sistema] Modo automático iniciado.")
        enviar_y_log(ser, FORWARD_SPEED, "X", "inicio_avance")

        while True:
            dist = reader.distance
            if dist is not None:
                print(f"[Sensor] Distancia: {dist:.1f} cm")

                if dist < DIST_THRESHOLD:
                    # Obstáculo detectado
                    print("[Acción] Obstáculo detectado → Detener y girar 180°")
                    enviar_y_log(ser, 0, "N", "detener")
                    time.sleep(0.3)

                    # Girar
                    enviar_y_log(ser, TURN_SPEED, "A", "girar")
                    time.sleep(TURN_DURATION)
                    enviar_y_log(ser, 0, "N", "fin_giro")

                    # Reanudar avance
                    enviar_y_log(ser, FORWARD_SPEED, "X", "reanudar")
                    time.sleep(0.5)

            time.sleep(DELAY_CHECK)

    except KeyboardInterrupt:
        print("\n[Sistema] Interrupción por teclado. Finalizando...")
    finally:
        reader.stop()
        enviar_y_log(ser, 0, "N", "detener_final")
        ser.close()

if __name__ == "__main__":
    main()
