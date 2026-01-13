# main.py — Prueba autónoma de motores (usa config.py y omni_drive.py)
from machine import Pin
import time
from omni_drive import OmniDrive, motors_from_config

# ========= util LED =========
def led_blink(times=3, t=0.1):
    try:
        led = Pin("LED", Pin.OUT)
        for _ in range(times):
            led.on(); time.sleep(t)
            led.off(); time.sleep(t)
    except:
        pass

def led_heartbeat():
    try:
        led = Pin("LED", Pin.OUT)
        while True:
            led.on();  time.sleep(0.12)
            led.off(); time.sleep(0.7)
    except:
        while True:
            time.sleep(1)

# ========= secuencias =========
def sec_avance(drive, t=1.6):
    drive.set_base_speed(60)
    drive.forward(); time.sleep(t)
    drive.brake();   time.sleep(0.4)

def sec_reversa(drive, t=1.6):
    drive.set_base_speed(60)
    drive.back();    time.sleep(t)
    drive.brake();   time.sleep(0.4)

def sec_strafe(drive, t=1.2):
    drive.set_base_speed(65)
    drive.right(); time.sleep(t)
    drive.brake(); time.sleep(0.35)
    drive.left();  time.sleep(t)
    drive.brake(); time.sleep(0.35)

def sec_diagonales(drive, t=1.0):
    drive.set_base_speed(65)
    drive.diag_fr(); time.sleep(t)
    drive.brake();   time.sleep(0.3)
    drive.diag_fl(); time.sleep(t)
    drive.brake();   time.sleep(0.3)
    drive.diag_br(); time.sleep(t)
    drive.brake();   time.sleep(0.3)
    drive.diag_bl(); time.sleep(t)
    drive.brake();   time.sleep(0.3)

def sec_giros(drive, t=0.9):
    drive.set_base_speed(70)
    drive.cw();  time.sleep(t)
    drive.brake(); time.sleep(0.35)
    drive.ccw(); time.sleep(t)
    drive.brake(); time.sleep(0.35)

def main():
    led_blink()
    FL, FR, RL, RR = motors_from_config()
    drive = OmniDrive(fl=FL, fr=FR, rl=RL, rr=RR, rot_time_90=0.55)

    # PRUEBA: 2 ciclos
    for _ in range(2):
        sec_avance(drive)
        sec_reversa(drive)
        sec_strafe(drive)
        sec_diagonales(drive)
        sec_giros(drive)

    drive.stop()
    # Indicador de fin
    led_heartbeat()

if __name__ == "__main__":
    main()
