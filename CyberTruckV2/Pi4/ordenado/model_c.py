# model_c.py (versión protocolo S=<vel> + <cmd>, mapping 0..10 conservado)
import time
import threading
import math

STOP=0; 
ADELANTE=1 
ATRAS=2
DERECHA=3
IZQUIERDA=4
DiagDerechaAdelante=5
DiagIzquierdaAdelante=6
DiagDerechaAtras=7
DiagIzquierdaAtras=8
Giroderecha=9
Giroizquierda=10


def clamp(v, lo, hi): return max(lo, min(hi, v))

class ModelC(threading.Thread):
    def __init__(self, ser, ps4, loop_hz=30, deadzone=0.20):
        super().__init__(daemon=True)
        self.ser = ser
        self.ps4 = ps4
        self.loop_hz = loop_hz
        self.deadzone = deadzone
        self.stop_event = threading.Event()

    def stop(self): self.stop_event.set()
    def stopped(self): return self.stop_event.is_set()

    def _send_cmd(self, speed, cmd):
        speed = clamp(int(speed), 0, 100)
        try:
            self.ser.send(f"S={speed}\n")
            self.ser.send(f"{int(cmd)}\n")
        except Exception as e:
            print(f"[Serial] Error enviando: {e}")
    
    def _axes_to_cmd(self, lx, ly):
        speed = int(round(100.0 * math.sqrt(lx*lx + ly*ly)))
        if speed == 0: 
            return STOP, 0

        ax = lx if abs(lx) >= self.deadzone else 0.0
        ay = ly if abs(ly) >= self.deadzone else 0.0

        if ax == 0.0 and ay == 0.0:
            return STOP, 0

        forward  = (ay < 0) 
        backward = (ay > 0)
        right    = (ax > 0)
        left     = (ax < 0)

        if forward and right:   return DiagDerechaAdelante, speed
        if forward and left:    return DiagIzquierdaAdelante, speed
        if backward and right:  return DiagDerechaAtras, speed
        if backward and left:   return DiagIzquierdaAtras, speed

        if forward:  return ADELANTE, speed
        if backward: return ATRAS, speed
        if right:    return DERECHA, speed   
        if left:     return IZQUIERDA, speed

        return STOP, 0

    def run(self):
        print("[ModelC] start")
        tick = time.monotonic()
        try:
            while not self.stopped():
                self.ps4.update()
                lx = float(self.ps4.get_axis(0))
                ly = float(self.ps4.get_axis(1)) 

                cmd, speed = self._axes_to_cmd(lx, ly)
                # print(f"LX={lx:+.2f} LY={ly:+.2f} -> CMD={cmd} SPEED={speed}")

                self._send_cmd(speed, cmd)


                tick += 1.0/self.loop_hz
                dt = tick - time.monotonic()
                if dt > 0: time.sleep(dt)
                else: tick = time.monotonic()

        except KeyboardInterrupt:
            print("[ModelC] user interrupt")
        finally:
            # Salida segura
            self._send_cmd(0, STOP)
            print("[ModelC] stop")
