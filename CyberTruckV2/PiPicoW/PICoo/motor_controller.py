# motor_controller.py
from machine import Pin, PWM

def clamp(x, a, b):
    return a if x < a else b if x > b else x

class Motor:
    """
    L298N: IN1, IN2 + PWM en ENx
    speed: -100..100
    """
    def __init__(self, in1_pin, in2_pin, pwm_pin, freq=1000, invert=False):
        self.in1 = Pin(in1_pin, Pin.OUT)
        self.in2 = Pin(in2_pin, Pin.OUT)
        self.pwm = PWM(Pin(pwm_pin))
        self.pwm.freq(freq)
        self.invert = invert
        self.set_speed(0)

    def stop(self):
        self.set_speed(0)

    def set_speed(self, speed):
        speed = clamp(int(speed), -100, 100)
        if self.invert:
            speed = -speed

        if speed == 0:
            self.in1.value(0)
            self.in2.value(0)
            self.pwm.duty_u16(0)
            return

        if speed > 0:
            self.in1.value(1)
            self.in2.value(0)
        else:
            self.in1.value(0)
            self.in2.value(1)

        duty = int(abs(speed) * 65535 / 100)
        self.pwm.duty_u16(duty)
