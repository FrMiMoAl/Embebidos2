# Solo un placeholder para integrarse con el dashboard
class MotorControl:
    def __init__(self):
        self.speed = 0

    def set_speed(self, speed):
        self.speed = speed
        print(f"[MotorControl] Velocidad establecida a {speed}")

    def stop(self):
        self.speed = 0
        print("[MotorControl] Motor detenido")
