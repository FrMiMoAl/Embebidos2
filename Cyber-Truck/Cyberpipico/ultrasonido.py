# ultrasonido.py — MicroPython (Raspberry Pi Pico W)
from machine import Pin
import time

class Ultrasonido:
    def _init_(self, trig_pin, echo_pin, *, timeout_us=30000):
        self.trig = Pin(trig_pin, Pin.OUT)
        self.echo = Pin(echo_pin, Pin.IN)
        self.timeout_us = timeout_us
        self.trig.value(0)

    def _pulse(self):
        # Pulso de 10 µs en TRIG
        self.trig.value(0); time.sleep_us(2)
        self.trig.value(1); time.sleep_us(10)
        self.trig.value(0)

    def _measure_once(self):
        self._pulse()

        t0 = time.ticks_us()
        # Espera flanco de subida
        while self.echo.value() == 0:
            if time.ticks_diff(time.ticks_us(), t0) > self.timeout_us:
                return -1

        start = time.ticks_us()
        # Espera flanco de bajada
        while self.echo.value() == 1:
            if time.ticks_diff(time.ticks_us(), start) > self.timeout_us:
                return -1

        dur = time.ticks_diff(time.ticks_us(), start)  # µs
        # Distancia en cm (vel. sonido ~343 m/s → 0.0343 cm/µs, ida y vuelta /2)
        return (dur * 0.0343) / 2

    def distancia_cm(self, samples=3):
        """ Devuelve la mediana de 'samples' mediciones (o -1 si todas fallan). """
        vals = []
        for _ in range(max(1, samples)):
            d = self._measure_once()
            if d >= 0:
                vals.append(d)
        if not vals:
            return -1
        vals.sort()
        return vals[len(vals)//2]


# --- API funcional opcional ---
def medir_cm(trig_pin, echo_pin, *, samples=3, timeout_us=30000):
    sensor = Ultrasonido(trig_pin, echo_pin, timeout_us=timeout_us)
    return sensor.distancia_cm(samples=samples)