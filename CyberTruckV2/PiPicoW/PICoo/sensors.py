# sensors.py
import time
from machine import Pin
from machine import time_pulse_us

class Ultrasonido:
    def __init__(self, trig_pin, echo_pin, timeout_us=30000):
        self.trig = Pin(trig_pin, Pin.OUT)
        self.echo = Pin(echo_pin, Pin.IN)
        self.timeout_us = timeout_us
        self.trig.value(0)

    def distancia_cm(self):
        # pulso trig
        self.trig.value(0)
        time.sleep_us(2)
        self.trig.value(1)
        time.sleep_us(10)
        self.trig.value(0)

        # mide pulso high del echo
        try:
            dur = time_pulse_us(self.echo, 1, self.timeout_us)
        except OSError:
            return -1

        if dur < 0:
            return -1

        # distancia = (dur_us * 0.0343) / 2
        return round((dur * 0.0343) / 2, 2)
