# omni_drive.py - estructura esperada
from machine import Pin, PWM

class Motor:
    def __init__(self, pwm_pin, in1_pin, in2_pin):
        self.pwm = PWM(Pin(pwm_pin))
        self.pwm.freq(1000)
        self.in1 = Pin(in1_pin, Pin.OUT)
        self.in2 = Pin(in2_pin, Pin.OUT)
    
    def set_speed(self, speed):
        # speed: -100 a 100
        if speed > 0:
            self.in1.value(1)
            self.in2.value(0)
            self.pwm.duty_u16(int(abs(speed) * 655.35))
        elif speed < 0:
            self.in1.value(0)
            self.in2.value(1)
            self.pwm.duty_u16(int(abs(speed) * 655.35))
        else:
            self.in1.value(0)
            self.in2.value(0)
            self.pwm.duty_u16(0)

class OmniDrive:
    def __init__(self, m_fl, m_fr, m_rl, m_rr):
        self.m_fl = m_fl
        self.m_fr = m_fr
        self.m_rl = m_rl
        self.m_rr = m_rr
    
    def drive(self, vx, vy, omega):
        # Cinemática omni básica
        self.m_fl.set_speed(vx - vy - omega)
        self.m_fr.set_speed(vx + vy + omega)
        self.m_rl.set_speed(vx + vy - omega)
        self.m_rr.set_speed(vx - vy + omega)
    
    def stop(self):
        self.m_fl.set_speed(0)
        self.m_fr.set_speed(0)
        self.m_rl.set_speed(0)
        self.m_rr.set_speed(0)