# actuators.py
from machine import Pin, PWM
from motor_controller import Motor, clamp

class Servo:
    def __init__(self, pin, min_us=500, max_us=2500, freq=50):
        self.pwm = PWM(Pin(pin))
        self.pwm.freq(freq)
        self.min_us = min_us
        self.max_us = max_us

    def write_us(self, us: int):
        us = clamp(int(us), self.min_us, self.max_us)
        # duty_u16 = (us / 20000) * 65535 a 50Hz
        duty = int(us * 65535 / 20000)
        self.pwm.duty_u16(duty)

    def set_angle(self, angle: float):
        angle = clamp(float(angle), 0, 180)
        us = self.min_us + (self.max_us - self.min_us) * (angle / 180.0)
        self.write_us(int(us))

class OmniDrive:
    """
    Convención (consistente):
      vx: adelante(+) / atrás(-)
      vy: derecha(+) / izquierda(-)
      w : giro CW(+) / CCW(-)

    Mezcla mecanum/omni típica:
      FL = vx - vy - w
      FR = vx + vy + w
      RL = vx + vy - w
      RR = vx - vy + w
    """
    def __init__(self, motors_cfg, pwm_freq=1000):
        self.m = {}
        for k, (in1, in2, pwm, inv) in motors_cfg.items():
            self.m[k] = Motor(in1, in2, pwm, freq=pwm_freq, invert=inv)

    def stop(self):
        for mot in self.m.values():
            mot.stop()

    def drive(self, vx, vy, w):
        vx = clamp(int(vx), -100, 100)
        vy = clamp(int(vy), -100, 100)
        w  = clamp(int(w),  -100, 100)

        fl = vx - vy - w
        fr = vx + vy + w
        rl = vx + vy - w
        rr = vx - vy + w

        mmax = max(abs(fl), abs(fr), abs(rl), abs(rr), 1)
        if mmax > 100:
            scale = 100 / mmax
            fl = int(fl * scale)
            fr = int(fr * scale)
            rl = int(rl * scale)
            rr = int(rr * scale)

        self.m["FL"].set_speed(fl)
        self.m["FR"].set_speed(fr)
        self.m["RL"].set_speed(rl)
        self.m["RR"].set_speed(rr)
