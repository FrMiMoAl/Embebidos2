# =============================================
#
#               Module Ultra Sonico
#
# =============================================


# Clase para manejar sensor ultrasónico HC-SR04

from machine import Pin, time_pulse_us
import utime

class USonic:
    def __init__(self, trig_pin, echo_pin, timeout_us=30000):
        self.trig = Pin(trig_pin, Pin.OUT)
        self.echo = Pin(echo_pin, Pin.IN)
        self.timeout = timeout_us

    def distance_cm(self):
        self.trig.off()
        utime.sleep_us(2)
        self.trig.on()
        utime.sleep_us(10)
        self.trig.off()
        try:
            pulse_time = time_pulse_us(self.echo, 1, self.timeout)
        except:
            return None
        dist_cm = (pulse_time / 2) / 29.1
        return dist_cm
