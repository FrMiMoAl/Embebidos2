from machine import Pin, PWM

class Servo:
    def __init__(self, pin):
        self.pwm = PWM(Pin(pin))
        self.pwm.freq(50)
    
    def set_angle(self, angle):
        angle = max(0, min(180, angle))
        # Mapeo: 0° (1638 duty) a 180° (8192 duty)
        duty = int((angle / 180) * 6553 + 1638)
        self.pwm.duty_u16(duty)

class OmniDrive:
    def __init__(self, motors_dict):
        from motor_controller import Motor # Reutiliza tu clase Motor existente
        self.m = {k: Motor(*v) for k, v in motors_dict.items()}

    def drive_complex(self, vx, vy, omega):
        """vx: adelante, vy: lateral, omega: rotación"""
        self.m["FL"].set_speed(vx - vy - omega)
        self.m["FR"].set_speed(vx + vy + omega)
        self.m["RL"].set_speed(vx + vy - omega)
        self.m["RR"].set_speed(vx - vy + omega)

    def stop(self):
        for motor in self.m.values(): motor.stop()