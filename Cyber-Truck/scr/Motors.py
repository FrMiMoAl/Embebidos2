# =============================================
#
#               Module MOTORS
#
# =============================================


# Clase para manejar motores DC con puente H (L298N)

from machine import Pin, PWM

class DCMotor:
    def __init__(self, pin_pwm, pin_in1, pin_in2, freq=1000):
        self.pwm = PWM(Pin(pin_pwm))
        self.pwm.freq(freq)
        self.in1 = Pin(pin_in1, Pin.OUT)
        self.in2 = Pin(pin_in2, Pin.OUT)
        self.set_speed(0)

    def set_speed(self, percent):
        # percent: -100..100
        percent = max(-100, min(100, int(percent)))
        if percent == 0:
            self.in1.off(); self.in2.off()
            self.pwm.duty_u16(0)
            return
        if percent > 0:
            self.in1.on(); self.in2.off()
        else:
            self.in1.off(); self.in2.on()
        duty = int(abs(percent) / 100 * 65535)
        self.pwm.duty_u16(duty)
