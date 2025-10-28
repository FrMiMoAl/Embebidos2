import time
import re
import threading
from serial_comm import SerialComm
PWM_MIN = 0
PWM_MAX = 100

# Límites y valores por defecto
ADELANTE = 1
ATRAS = 2
DERECHA=3
IZQUIERDA=4
DiagDerechaAdelante=5
DiagIzquierdaAdelante=6
DiagDerechaAtras=7
DiagIzquierdaAtras=8
Giroderecha=9
Giroizquierda=10


def clamp(v, lo, hi):
    return max(lo, min(hi, v))

class ModelA(threading.Thread):

    def __init__(self, serial_device):
        super().__init__(daemon=True)
        self.serial_device = serial_device
        self.stop_event = threading.Event()
        self.speed = 50  

    def send_command(self, speed, cmd):
        speed = clamp(int(speed), PWM_MIN, PWM_MAX)
        self.serial_device.send(f"S={speed}\n")
        self.serial_device.send(f"{int(cmd)}\n")

    def receive_distance(self):
        raw = self.serial_device.receive()
        if not raw:
            return None
        line = str(raw).strip()
        m = re.search(r"DIST:\s*([0-9]+(?:\.[0-9]+)?)\s*cm", line)
        if m:
            try:
                return float(m.group(1))
            except ValueError:
                return None
        return None

    def move_forward(self):
        self.send_command(50, ADELANTE)

    def move_backward(self): 
        self.send_command(50, ATRAS)

    def Go_right(self):
        self.send_command(50, DERECHA)

    def Go_left(self):
        self.send_command(50, IZQUIERDA)

    def Go_DiagRight_Forward(self):
        self.send_command(50, DiagDerechaAdelante)
    
    def Go_DiagLeft_Forward(self):
        self.send_command(50, DiagIzquierdaAdelante)
    
    def Go_DiagRight_Backward(self):
        self.send_command(50, DiagDerechaAtras)
    
    def Go_DiagLeft_Backward(self):
        self.send_command(50, DiagIzquierdaAtras)

    def Turn_right(self):
        self.send_command(50, Giroderecha)
    
    def Turn_left(self):
        self.send_command(50, Giroizquierda)


    def stop_movement(self):
        self.send_command(0, 0)

    def stop(self):
        self.stop_event.set()

def run(self):
        print("==== MODEL A (AUTÓNOMO) ====")
        try:
            while not self.stop_event.is_set():
                distance = self.receive_distance()
                if distance is not None:
                    print(f"Recibido: {distance:.1f} cm")
                    if distance < 30:
                        print("Objeto detectado (<30 cm) → girando derecha")
                        self.Turn_right()
                    else:
                        print("Avanzando")
                        self.move_forward()
                else:
                    self.move_forward()
                self._sleep_until(0.1)
        except KeyboardInterrupt:
            print("ModelA: interrumpido por usuario.")
        finally:
            self.stop_movement()
            print("ModelA: stop.")

if __name__ == "__main__":
    serial_device = SerialComm(port="/dev/serial0", baudrate=115200, timeout=0.1)
    model_a = ModelA(serial_device)
    model_a.run()