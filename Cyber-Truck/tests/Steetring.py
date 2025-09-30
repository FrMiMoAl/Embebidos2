# =============================================
#
#               Module Steering
#
# =============================================


# Clase para manejar el servo MG90S (dirección)

from machine import Pin, PWM

class Steering:
    def __init__(self, pin, freq=50):
        self.pwm = PWM(Pin(pin))
        self.pwm.freq(freq)
        self.MIN = 1638   # 0.5 ms
        self.MAX = 8192   # 2.5 ms
        self.angle(90)    # centro por defecto

    def angle(self, deg):
        deg = max(0, min(180, int(deg)))
        duty = int(self.MIN + (deg / 180.0) * (self.MAX - self.MIN))
        self.pwm.duty_u16(duty)
