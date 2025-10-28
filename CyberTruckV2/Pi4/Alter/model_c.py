# model_c.py (versión adaptada para omniwheels con protocolo analog1,analog2,traction,special)
import time
import threading
import math

def clamp(v, lo, hi): 
    return max(lo, min(hi, v))

class ModelC(threading.Thread):
    def __init__(self, ser, ps4, loop_hz=30, deadzone=0.15):
        super().__init__(daemon=True)
        self.ser = ser
        self.ps4 = ps4
        self.loop_hz = loop_hz
        self.deadzone = deadzone
        self.stop_event = threading.Event()

    def stop(self): 
        self.stop_event.set()
    
    def stopped(self): 
        return self.stop_event.is_set()

    def _send_cmd(self, analog1, analog2, traction, special):
        """
        Envía comando en formato: analog1,analog2,traction,special
        analog1: -100 a 100 (adelante/atrás)
        analog2: -100 a 100 (lateral izq/der)
        traction: 0 o 1 (4x4)
        special: 0=normal, 1=giro antihorario, 2=giro horario
        """
        analog1 = clamp(int(analog1), -100, 100)
        analog2 = clamp(int(analog2), -100, 100)
        traction = 1 if traction else 0
        special = clamp(int(special), 0, 2)
        
        try:
            cmd = f"{analog1},{analog2},{traction},{special}\n"
            self.ser.send(cmd)
            # print(f"[Serial] Enviado: {cmd.strip()}")
        except Exception as e:
            print(f"[Serial] Error enviando: {e}")
    
    def _axes_to_movement(self, lx, ly, r2_pressed, l1_pressed, r1_pressed):
        """
        Convierte los ejes del joystick a comandos de movimiento
        lx: eje X del stick izquierdo (-1 a 1, negativo=izquierda, positivo=derecha)
        ly: eje Y del stick izquierdo (-1 a 1, negativo=arriba, positivo=abajo)
        r2_pressed: activar tracción 4x4
        l1_pressed: giro antihorario en su propio eje
        r1_pressed: giro horario en su propio eje
        """
        # Aplicar zona muerta
        ax = lx if abs(lx) >= self.deadzone else 0.0
        ay = ly if abs(ly) >= self.deadzone else 0.0
        
        # Detectar giros especiales (L1 o R1)
        if l1_pressed:
            return 0, 0, 0, 1  # Giro antihorario
        if r1_pressed:
            return 0, 0, 0, 2  # Giro horario
        
        # Convertir a valores -100 a 100
        # ay negativo = adelante, ay positivo = atrás
        analog1 = int(-ay * 100)  # Invertido porque en joystick arriba es negativo
        
        # ax negativo = izquierda, ax positivo = derecha
        analog2 = int(ax * 100)
        
        # Tracción 4x4 si se presiona R2
        traction = 1 if r2_pressed else 0
        
        return analog1, analog2, traction, 0

    def run(self):
        print("[ModelC] Iniciando control de omniwheels")
        print("[ModelC] Stick izquierdo: Movimiento | R2: Tracción 4x4 | L1/R1: Giros")
        tick = time.monotonic()
        
        try:
            while not self.stopped():
                self.ps4.update()
                
                # Leer ejes del stick izquierdo
                lx = float(self.ps4.get_axis(0))  # Eje X
                ly = float(self.ps4.get_axis(1))  # Eje Y
                
                # Leer botones (ajusta según tu implementación de ps4)
                # Asumiendo que tienes métodos get_button(n) donde:
                # R2 suele ser botón 7 o axis 5
                # L1 suele ser botón 4
                # R1 suele ser botón 5
                try:
                    r2_pressed = self.ps4.get_button(7) > 0.5  # o get_axis(5)
                except:
                    r2_pressed = False
                    
                try:
                    l1_pressed = self.ps4.get_button(4) > 0
                except:
                    l1_pressed = False
                    
                try:
                    r1_pressed = self.ps4.get_button(5) > 0
                except:
                    r1_pressed = False
                
                # Convertir a comandos
                analog1, analog2, traction, special = self._axes_to_movement(
                    lx, ly, r2_pressed, l1_pressed, r1_pressed
                )
                
                # Debug opcional
                # if analog1 != 0 or analog2 != 0 or special != 0:
                #     print(f"LX={lx:+.2f} LY={ly:+.2f} -> A1={analog1:+4d} A2={analog2:+4d} T={traction} S={special}")
                
                # Enviar comando
                self._send_cmd(analog1, analog2, traction, special)
                
                # Control de timing
                tick += 1.0/self.loop_hz
                dt = tick - time.monotonic()
                if dt > 0: 
                    time.sleep(dt)
                else: 
                    tick = time.monotonic()

        except KeyboardInterrupt:
            print("[ModelC] Interrupción del usuario")
        finally:
            # Detener motores al salir
            self._send_cmd(0, 0, 0, 0)
            print("[ModelC] Detenido")