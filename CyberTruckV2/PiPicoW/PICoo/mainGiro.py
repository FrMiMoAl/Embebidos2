# main_turn_test.py
# Prueba de control de giro (roll) usando MPU6050 + OmniDrive
# Requiere: config.py, gyro_controller.py, omni_drive.py

import time
from config import Config
from gyro_controller import GyroController
from omni_drive import motors_from_config, OmniDrive

# ================= Ajustes de control =================
TARGETS_DEG = [45, 15, 60, -180]   # secuencia de giros a probar
LOOP_HZ = 50                        # control loop
DT_MS = int(1000 / LOOP_HZ)

TOL_DEG = 3.0                       # tolerancia final
STABLE_CYCLES = 12                  # ciclos consecutivos dentro de tolerancia para "terminar"

KP = 1.2                            # ganancia proporcional (ajústala)
MAX_W = 55                          # comando max de giro (w en -100..100)
MIN_W = 18                          # comando mínimo para vencer fricción

SLOW_BAND = 20.0                    # debajo de este error, baja la agresividad
SLEW_PER_STEP = 6                   # suavizado: cuánto puede cambiar w por ciclo (0..100)

MAX_TIME_S = 6.0                    # seguridad por giro

INVERT_roll = False                  # si gira al revés, pon True

# ================= Helpers =================
def clamp(x, a, b):
    return a if x < a else b if x > b else x

def sign(x):
    return 1 if x > 0 else (-1 if x < 0 else 0)

def angle_diff_deg(a, b):
    """
    Diferencia angular a-b en rango [-180, 180], útil por el wrap.
    Tu GyroController hace wrap a [-180,180]. :contentReference[oaicite:6]{index=6}
    """
    d = (a - b + 180) % 360 - 180
    return d

def rotate_relative(drive: OmniDrive, gyro: GyroController, target_deg: float):
    """
    Gira el robot target_deg (relativo) usando roll del gyro (closed-loop).
    """
    print("\n==============================")
    print("🎯 Giro objetivo:", target_deg, "deg")
    print("⛔ Mantén el auto quieto 0.5s antes de empezar")
    time.sleep_ms(500)

    # "ancla" de roll inicial
    gyro.update()
    roll0 = gyro.roll

    w_smooth = 0
    stable = 0
    t0 = time.ticks_ms()
    last_print = time.ticks_ms()

    while True:
        # Tiempo
        now = time.ticks_ms()
        if time.ticks_diff(now, t0) > int(MAX_TIME_S * 1000):
            print("⛔ Timeout de seguridad")
            break

        # Sensor
        gyro.update()
        roll = gyro.roll
        if INVERT_roll:
            roll = -roll

        delta = angle_diff_deg(roll, roll0)          # cuánto giró desde el inicio
        err = target_deg - delta                   # error a corregir

        # Condición de llegada
        if abs(err) <= TOL_DEG:
            stable += 1
        else:
            stable = 0

        if stable >= STABLE_CYCLES:
            print("✅ OK. delta=", round(delta, 2), "roll=", round(roll, 2))
            break

        # Control P + mínimos + desaceleración cerca del target
        w_cmd = KP * err
        w_cmd = clamp(w_cmd, -MAX_W, MAX_W)

        # zona lenta: reduce agresividad cuando está cerca
        if abs(err) < SLOW_BAND:
            w_cmd *= (abs(err) / SLOW_BAND)

        # vence fricción si aún falta girar
        if abs(err) > TOL_DEG and abs(w_cmd) < MIN_W:
            w_cmd = sign(w_cmd) * MIN_W

        # Suavizado (slew-rate limiter) para que no haya “saltos”
        dw = clamp(w_cmd - w_smooth, -SLEW_PER_STEP, SLEW_PER_STEP)
        w_smooth += dw
        w_smooth = int(clamp(w_smooth, -MAX_W, MAX_W))

        # Aplica giro puro (vx=0, vy=0, w=w)
        # En OmniDrive, w controla giro CW(+) / CCW(-). :contentReference[oaicite:7]{index=7}
        drive.drive(0, 0, w_smooth)

        # Debug cada ~200ms
        if time.ticks_diff(now, last_print) > 200:
            last_print = now
            print("delta=", round(delta, 1),
                  "err=", round(err, 1),
                  "w=", w_smooth,
                  "roll=", round(roll, 1))

        time.sleep_ms(DT_MS)

    # stop + freno para que no se siga yendo
    drive.stop()
    time.sleep_ms(150)
    drive.brake()
    time.sleep_ms(200)
    drive.stop()

def main():
    print("🚗 Test control de giro con MPU6050 + OmniDrive")
    print("I2C:", Config.I2C_ID, "SCL:", Config.IMU_SCL, "SDA:", Config.IMU_SDA)  # :contentReference[oaicite:8]{index=8}
    print("Motores:", Config.MOTORS)  # :contentReference[oaicite:9]{index=9}

    # Motores desde tu config :contentReference[oaicite:10]{index=10}
    FL, FR, RL, RR = motors_from_config()
    drive = OmniDrive(FL, FR, RL, RR)

    # GyroController integra gyro Z a roll :contentReference[oaicite:11]{index=11}
    # y calibra en __init__ :contentReference[oaicite:12]{index=12}
    print("\n🧊 Calibración: NO muevas el auto mientras inicializa el MPU...")
    gyro = GyroController(
        i2c_id=Config.I2C_ID,
        scl=Config.IMU_SCL,
        sda=Config.IMU_SDA,
        freq=Config.I2C_FREQ
    )

    print("✅ MPU listo. roll inicial:", gyro.roll)
    print("▶️ Empezando secuencia de giros:", TARGETS_DEG)
    time.sleep_ms(500)

    try:
        for deg in TARGETS_DEG:
            rotate_relative(drive, gyro, deg)
            print("⏸️ pausa 1s...")
            time.sleep_ms(1000)

        print("\n✅ Fin de pruebas.")
    except KeyboardInterrupt:
        print("\n🛑 Cancelado por usuario.")
    finally:
        drive.stop()

main()
