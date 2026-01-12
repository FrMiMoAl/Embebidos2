# omni_drive.py
from machine import Pin, PWM
import time
from config import Config

def _clamp(x, a, b):
    return a if x < a else b if x > b else x

class Motor:
    """
    Motor con puente H (L298N típico): IN1, IN2 + PWM(ENA)
    speed: -100..100
    """
    def __init__(self, in1_pin, in2_pin, pwm_pin, freq=None, invert=False):
        self.in1 = Pin(in1_pin, Pin.OUT, value=0)
        self.in2 = Pin(in2_pin, Pin.OUT, value=0)
        self.pwm = PWM(Pin(pwm_pin))
        self.freq = freq if freq is not None else getattr(Config, "MOTOR_PWM_FREQ", 1000)
        self.pwm.freq(self.freq)
        self.invert = invert
        self._last_speed = 0
        self.set_speed(0)

    def _apply_dir(self, forward):
        # L298N: dirección por IN1/IN2
        if forward:
            self.in1.value(1); self.in2.value(0)
        else:
            self.in1.value(0); self.in2.value(1)

    def set_speed(self, speed):
        """
        Set inmediato (sin rampa). speed en [-100..100]
        """
        speed = _clamp(int(speed), -100, 100)
        if self.invert:
            speed = -speed

        if speed == 0:
            # COAST por defecto: suelta el motor
            self.in1.value(0); self.in2.value(0)
            self.pwm.duty_u16(0)
            self._last_speed = 0
            return

        self._apply_dir(speed > 0)
        duty = int(abs(speed) * 65535 / 100)
        self.pwm.duty_u16(duty)
        self._last_speed = speed

    def ramp_to(self, target, ms=400, step_ms=20):
        """
        Rampa lineal desde _last_speed a target en 'ms' totales.
        """
        target = _clamp(int(target), -100, 100)
        if self.invert:
            target = -target

        start = self._last_speed
        steps = max(1, ms // step_ms)
        for i in range(1, steps + 1):
            s = start + (target - start) * i // steps
            if s == 0:
                self.in1.value(0); self.in2.value(0); self.pwm.duty_u16(0)
            else:
                self._apply_dir(s > 0)
                duty = int(abs(s) * 65535 / 100)
                self.pwm.duty_u16(duty)
            time.sleep_ms(step_ms)
        self._last_speed = target

    def brake(self):
        """
        Freno activo (ambas líneas en 1). Útil en L298N.
        """
        self.in1.value(1); self.in2.value(1)
        self.pwm.duty_u16(0)
        self._last_speed = 0

    def coast(self):
        """
        High-Z (coast). Motor libre.
        """
        self.in1.value(0); self.in2.value(0)
        self.pwm.duty_u16(0)
        self._last_speed = 0


class OmniDrive:
    """
    4 ruedas omni/mecanum:
      FL (Front-Left), FR (Front-Right), RL (Rear-Left), RR (Rear-Right)

    Mezcla (vx, vy, w):
      vy: adelante(+)/atrás(-)
      vx: derecha(+)/izquierda(-)
      w : giro CW(+)/CCW(-)
    """
    def __init__(self, fl, fr, rl, rr, rot_time_90=0.55):
        self.fl = fl; self.fr = fr; self.rl = rl; self.rr = rr
        self.speed = 60
        self.rot_time_90 = rot_time_90

    def stop(self):
        self.fl.coast(); self.fr.coast(); self.rl.coast(); self.rr.coast()

    def brake(self):
        self.fl.brake(); self.fr.brake(); self.rl.brake(); self.rr.brake()

    def set_base_speed(self, s):
        self.speed = _clamp(int(s), 0, 100)

    def _apply_speeds(self, fl, fr, rl, rr):
        self.fl.set_speed(fl)
        self.fr.set_speed(fr)
        self.rl.set_speed(rl)
        self.rr.set_speed(rr)

    def drive(self, vx, vy, w):
        vx = _clamp(int(vx), -100, 100)
        vy = _clamp(int(vy), -100, 100)
        w  = _clamp(int(w),  -100, 100)

        fl = vy + vx - w
        fr = vy - vx + w
        rl = vy - vx - w
        rr = vy + vx + w

        m = max(abs(fl), abs(fr), abs(rl), abs(rr), 1)
        scale = 100 / m if m > 100 else 1

        self._apply_speeds(int(fl*scale), int(fr*scale), int(rl*scale), int(rr*scale))

    # Movimientos directos
    def forward(self):  self.drive(0,  self.speed, 0)
    def back(self):     self.drive(0, -self.speed, 0)
    def right(self):    self.drive(self.speed, 0, 0)
    def left(self):     self.drive(-self.speed, 0, 0)

    def diag_fr(self):  self.drive(self.speed,  self.speed, 0)
    def diag_fl(self):  self.drive(-self.speed, self.speed, 0)
    def diag_br(self):  self.drive(self.speed, -self.speed, 0)
    def diag_bl(self):  self.drive(-self.speed,-self.speed,0)

    def cw(self):       self.drive(0, 0,  self.speed)
    def ccw(self):      self.drive(0, 0, -self.speed)

    # Giros por tiempo
    def rotate_right_90(self):
        self.cw();  time.sleep(self.rot_time_90); self.stop()

    def rotate_left_90(self):
        self.ccw(); time.sleep(self.rot_time_90); self.stop()

    def rotate_right_180(self):
        self.cw();  time.sleep(self.rot_time_90*2); self.stop()

    def rotate_left_180(self):
        self.ccw(); time.sleep(self.rot_time_90*2); self.stop()


def motors_from_config():
    """
    Construye (FL, FR, RL, RR) a partir de Config.MOTORS (FL/FR/RL/RR).
    Formato de cada entrada: (IN1, IN2, PWM, invert)
    """
    def _build(tup):
        in1, in2, pwm, inv = tup
        return Motor(in1, in2, pwm, freq=getattr(Config, "MOTOR_PWM_FREQ", 1000), invert=inv)

    FL = _build(Config.MOTORS["FL"])
    FR = _build(Config.MOTORS["FR"])
    RL = _build(Config.MOTORS["RL"])
    RR = _build(Config.MOTORS["RR"])
    return FL, FR, RL, RR
