# main.py
import sys
import select
import time
from omni_drive import Motor, OmniDrive


# ====== TUS PINES (IGUAL A TU CÓDIGO) ======
# Trasero izquierdo:
RL = Motor(in1_pin=2,  in2_pin=3,  pwm_pin=4,  freq=1000, invert=False)
# Trasero derecho:
RR = Motor(in1_pin=6,  in2_pin=7,  pwm_pin=8,  freq=1000, invert=False)
# Delantero izquierdo:
FL = Motor(in1_pin=10, in2_pin=11, pwm_pin=12, freq=1000, invert=False)
# Delantero derecho:
FR = Motor(in1_pin=13, in2_pin=14, pwm_pin=15, freq=1000, invert=False)

drive = OmniDrive(fl=FL, fr=FR, rl=RL, rr=RR, rot_time_90=0.55)  # <-- CALIBRA este valor

HELP = """
Comandos:
  f            -> adelante
  b            -> atras
  l            -> strafe izquierda
  r            -> strafe derecha
  fr / fl      -> diagonal adelante-derecha / adelante-izquierda
  br / bl      -> diagonal atras-derecha / atras-izquierda
  cw / ccw     -> girar derecha / girar izquierda (continuo)
  s            -> stop

  sp <0-100>   -> set velocidad base (ej: sp 70)

  r90 / l90    -> giro 90° derecha/izquierda (por tiempo)
  r180 / l180  -> giro 180° derecha/izquierda (por tiempo)

  vec vx vy w  -> control directo (ej: vec 40 60 0)
                  vx derecha(+), vy adelante(+), w CW(+)

  t90 <seg>    -> calibrar tiempo de 90° (ej: t90 0.60)

  h            -> help
"""

def non_blocking_readline():
    # Lee una línea sin bloquear (útil en REPL / terminal)
    if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
        return sys.stdin.readline().strip()
    return None

print("=== Control OmniDrive por Terminal ===")
print(HELP)

last_cmd = "stop"
drive.stop()

while True:
    cmdline = non_blocking_readline()
    if cmdline:
        parts = cmdline.split()
        cmd = parts[0].lower()

        try:
            if cmd == "h":
                print(HELP)

            elif cmd == "f":
                drive.forward(); last_cmd = "f"
            elif cmd == "b":
                drive.back(); last_cmd = "b"
            elif cmd == "l":
                drive.left(); last_cmd = "l"
            elif cmd == "r":
                drive.right(); last_cmd = "r"

            elif cmd == "fr":
                drive.diag_fr(); last_cmd = "fr"
            elif cmd == "fl":
                drive.diag_fl(); last_cmd = "fl"
            elif cmd == "br":
                drive.diag_br(); last_cmd = "br"
            elif cmd == "bl":
                drive.diag_bl(); last_cmd = "bl"

            elif cmd == "cw":
                drive.cw(); last_cmd = "cw"
            elif cmd == "ccw":
                drive.ccw(); last_cmd = "ccw"

            elif cmd == "s" or cmd == "stop":
                drive.stop(); last_cmd = "stop"

            elif cmd == "sp" and len(parts) == 2:
                drive.set_base_speed(int(parts[1]))
                print("Velocidad base =", drive.speed)

            elif cmd == "t90" and len(parts) == 2:
                drive.rot_time_90 = float(parts[1])
                print("rot_time_90 =", drive.rot_time_90)

            elif cmd == "r90":
                drive.rotate_right_90(); last_cmd = "stop"
            elif cmd == "l90":
                drive.rotate_left_90(); last_cmd = "stop"
            elif cmd == "r180":
                drive.rotate_right_180(); last_cmd = "stop"
            elif cmd == "l180":
                drive.rotate_left_180(); last_cmd = "stop"

            elif cmd == "vec" and len(parts) == 4:
                vx = int(parts[1]); vy = int(parts[2]); w = int(parts[3])
                drive.drive(vx, vy, w)
                last_cmd = f"vec {vx} {vy} {w}"

            else:
                print("Comando no reconocido. Escribe 'h' para ayuda.")

            print("OK ->", cmdline)

        except Exception as e:
            print("ERROR:", e)

    # Pequeño delay para no saturar CPU
    time.sleep(0.02)
