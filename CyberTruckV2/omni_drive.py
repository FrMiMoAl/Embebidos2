# omni_drive.py
from machine import Pin, PWM
import time

def _clamp(x, a, b):
    return a if x < a else b if x > b else x

class Motor:
    """
    Motor con puente H: IN1, IN2 + PWM(ENA)
    speed: -100..100
    """
    def __init__(self, in1_pin, in2_pin, pwm_pin, freq=1000, invert=False):
        self.in1 = Pin(in1_pin, Pin.OUT)
        self.in2 = Pin(in2_pin, Pin.OUT)
        self.pwm = PWM(Pin(pwm_pin))
        self.pwm.freq(freq)
        self.invert = invert
        self.set_speed(0)

    def set_speed(self, speed):
        speed = _clamp(int(speed), -100, 100)
        if self.invert:
            speed = -speed

        if speed == 0:
            self.in1.value(0)
            self.in2.value(0)
            self.pwm.duty_u16(0)
            return

        # Dirección
        if speed > 0:
            self.in1.value(1)
            self.in2.value(0)
        else:
            self.in1.value(0)
            self.in2.value(1)

        duty = int(abs(speed) * 65535 / 100)
        self.pwm.duty_u16(duty)

class OmniDrive:
    """
    4 ruedas omni/mecanum:
      FL = delantero izquierdo
      FR = delantero derecho
      RL = trasero izquierdo
      RR = trasero derecho

    Mezcla holonómica (vx, vy, w):
      vy: adelante(+)/atrás(-)
      vx: derecha(+)/izquierda(-)  (strafe)
      w : giro CW(+)/CCW(-)        (rotación)

    Nota: según tu montaje, puede requerir invertir algún motor.
    """
    def __init__(self, fl, fr, rl, rr, rot_time_90=0.55):
        self.fl = fl
        self.fr = fr
        self.rl = rl
        self.rr = rr

        self.speed = 60           # velocidad base 0..100
        self.rot_time_90 = rot_time_90  # segundos para girar ~90° (CALIBRAR)

    def stop(self):
        self.fl.set_speed(0)
        self.fr.set_speed(0)
        self.rl.set_speed(0)
        self.rr.set_speed(0)

    def set_base_speed(self, s):
        self.speed = _clamp(int(s), 0, 100)

    def drive(self, vx, vy, w):
        """
        vx, vy, w en rango -100..100 (se normaliza internamente).
        """
        vx = _clamp(int(vx), -100, 100)
        vy = _clamp(int(vy), -100, 100)
        w  = _clamp(int(w),  -100, 100)

        # Mezcla típica mecanum/omni (puede variar por orientación)
        fl = vy + vx - w
        fr = vy - vx + w
        rl = vy - vx - w
        rr = vy + vx + w

        # Normalizar para no pasar de 100
        m = max(abs(fl), abs(fr), abs(rl), abs(rr), 1)
        scale = 100 / m if m > 100 else 1

        fl = int(fl * scale)
        fr = int(fr * scale)
        rl = int(rl * scale)
        rr = int(rr * scale)

        self.fl.set_speed(fl)
        self.fr.set_speed(fr)
        self.rl.set_speed(rl)
        self.rr.set_speed(rr)

    # ======== MOVIMIENTOS DIRECTOS (CONTINUOS) ========
    def forward(self):  self.drive(0,  self.speed, 0)
    def back(self):     self.drive(0, -self.speed, 0)
    def right(self):    self.drive(self.speed, 0, 0)
    def left(self):     self.drive(-self.speed, 0, 0)

    def diag_fr(self):  self.drive(self.speed,  self.speed, 0)   # adelante-derecha
    def diag_fl(self):  self.drive(-self.speed, self.speed, 0)   # adelante-izquierda
    def diag_br(self):  self.drive(self.speed, -self.speed, 0)   # atrás-derecha
    def diag_bl(self):  self.drive(-self.speed,-self.speed,0)    # atrás-izquierda

    def cw(self):       self.drive(0, 0,  self.speed)   # girar derecha
    def ccw(self):      self.drive(0, 0, -self.speed)   # girar izquierda

    # ======== GIROS POR TIEMPO (CALIBRABLE) ========
    def rotate_right_90(self):
        self.cw()
        time.sleep(self.rot_time_90)
        self.stop()

    def rotate_left_90(self):
        self.ccw()
        time.sleep(self.rot_time_90)
        self.stop()

    def rotate_right_180(self):
        self.cw()
        time.sleep(self.rot_time_90 * 2)
        self.stop()

    def rotate_left_180(self):
        self.ccw()
        time.sleep(self.rot_time_90 * 2)
        self.stop()
