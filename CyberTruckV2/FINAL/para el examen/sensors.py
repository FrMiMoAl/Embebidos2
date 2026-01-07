from machine import Pin, I2C
import time
import struct

class Ultrasonido:
    def __init__(self, trig_pin, echo_pin):
        self.trig = Pin(trig_pin, Pin.OUT)
        self.echo = Pin(echo_pin, Pin.IN)

    def distancia_cm(self):
        self.trig.low()
        time.sleep_us(2)
        self.trig.high()
        time.sleep_us(10)
        self.trig.low()
        
        timeout = 30000
        start = time.ticks_us()
        while not self.echo.value():
            if time.ticks_diff(time.ticks_us(), start) > timeout: return -1
        
        t1 = time.ticks_us()
        while self.echo.value():
            if time.ticks_diff(time.ticks_us(), t1) > timeout: return -1
        
        duracion = time.ticks_diff(time.ticks_us(), t1)
        return round((duracion * 0.0343) / 2, 2)