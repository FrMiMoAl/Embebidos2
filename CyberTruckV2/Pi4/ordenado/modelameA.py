#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import threading
from serial_comm import SerialComm

# Límites y valores por defecto
PWM_MIN, PWM_MAX = -100, 100
SERVO_MIN, SERVO_MAX = 30, 70
SERVO_CENTER = 50

def clamp(v, lo, hi):
    return max(lo, min(hi, v))

class ModelA(threading.Thread):
    """
    Versión integrada de tu Model A, compatible con el Supervisor:
      - Hilo daemon (start/stop)
      - Usa tu lógica de avanzar y girar 180°
      - Lee distancia por UART (SerialComm.receive())
      - Envía comandos 'pwm1,pwm2,servo' (SerialComm.send()), con DEBUG en serial_comm.py
      - Stop seguro (no se queda bloqueado en sleeps largos)
    """

    def __init__(self, serial_device):
        super().__init__(daemon=True)
        self.serial_device = serial_device
        self.stop_event = threading.Event()

    # ===== Helpers de protocolo =====
    def send_command(self, pwm1, pwm2, servo_angle):
        pwm1 = clamp(int(pwm1), PWM_MIN, PWM_MAX)
        pwm2 = clamp(int(pwm2), PWM_MIN, PWM_MAX)
        servo_angle = clamp(int(servo_angle), SERVO_MIN, SERVO_MAX)
        self.serial_device.send(f"{pwm1},{pwm2},{servo_angle}")  # [TX] lo muestra serial_comm

    def receive_distance(self):
        """
        Intenta leer una línea desde la Pico y convertirla a float (cm).
        Retorna None si no hay dato o si el valor no es válido.
        """
        raw = self.serial_device.receive()  # [RX] ya se imprime dentro de SerialComm
        if raw is None:
            # print("No se recibió distancia válida.")  # DEBUG opcional
            return None
        try:
            return float(raw)
        except ValueError:
            print(f"Valor de distancia no válido: {raw}")
            return None

    # ===== Acciones de movimiento =====
    def move_forward(self):
        """Avanzar recto con tu setpoint."""
        self.send_command(50, 50, SERVO_CENTER)

    def stop_movement(self):
        """Frenar y servo centrado."""
        self.send_command(0, 0, SERVO_CENTER)

    # ===== Giro 180° (tu secuencia), con stop seguro =====
    def _sleep_until(self, seconds):
        """Sleep fraccionado para permitir detener el hilo durante esperas largas."""
        end = time.monotonic() + seconds
        while time.monotonic() < end and not self.stop_event.is_set():
            time.sleep(0.02)

    def rotate_180(self):
        """
        Tu secuencia exacta, respetando servo en 30 (izq) y 70 (der),
        y con sleeps fraccionados para poder parar si el supervisor cambia de modo.
        """
        # Primera mitad (giro hacia izquierda)
        self.send_command(0, 0, 30)
        self._sleep_until(1.0)
        if self.stop_event.is_set(): 
            return

        self.send_command(-50, -40, 30)
        self._sleep_until(3.0)
        if self.stop_event.is_set(): 
            return

        self.stop_movement()
        self._sleep_until(1.0)
        if self.stop_event.is_set(): 
            return

        # Segunda mitad (giro hacia derecha)
        self.send_command(0, 0, 70)
        self._sleep_until(1.0)
        if self.stop_event.is_set(): 
            return

        self.send_command(40, 50, 70)
        self._sleep_until(3.0)

        # Finaliza deteniendo
        self.stop_movement()

    # ===== API Supervisor =====
    def stop(self):
        self.stop_event.set()

    def run(self):
        print("==== MODEL A (AUTÓNOMO) ====")
        try:
            while not self.stop_event.is_set():
                distance = self.receive_distance()
                if distance is not None:
                    print(f"Recibido: {distance} cm")
                    if distance < 30:
                        print("Objeto detectado, girando 180°")
                        self.rotate_180()
                    else:
                        print("Avanzando")
                        self.move_forward()
                else:
                    # Sin dato, puedes optar por mantener último comando o frenar.
                    # Aquí mantenemos avance suave para no quedarnos estáticos sin RX:
                    self.move_forward()

                # Cadencia de ciclo
                self._sleep_until(0.1)

        except KeyboardInterrupt:
            print("ModelA: interrumpido por usuario.")
        finally:
            self.stop_movement()
            print("ModelA: stop.")



serial_device = SerialComm(port="/dev/serial0", baudrate=115200)
model_a = ModelA(serial_device)
model_a.run()