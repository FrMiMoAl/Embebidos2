# =============================================
#
#                       MAIN
#
# =============================================


# Integra Steering, Motores, USonic y UARTHandler

from Steering import Steering
from Motore import DCMotor
from USonic import USonic
from UARTHandler import UARTHandler
import time

# Configuración de pines (ajusta según tu wiring)
MOTOR_A_PWM, MOTOR_A_IN1, MOTOR_A_IN2 = 0, 1, 2
MOTOR_B_PWM, MOTOR_B_IN1, MOTOR_B_IN2 = 3, 4, 5
SERVO_PIN = 15
TRIG_PIN, ECHO_PIN = 10, 11

# Inicialización
motorA = DCMotor(MOTOR_A_PWM, MOTOR_A_IN1, MOTOR_A_IN2)
motorB = DCMotor(MOTOR_B_PWM, MOTOR_B_IN1, MOTOR_B_IN2)
steer = Steering(SERVO_PIN)
sonic = USonic(TRIG_PIN, ECHO_PIN)
uart = UARTHandler()

uart.send("BOOT OK")

reporting = False
last_report = time.time()

while True:
    cmd = uart.read_command()
    if cmd:
        if cmd.lower().startswith("motora:"):
            val = int(cmd.split(":",1)[1])
            motorA.set_speed(val)
            uart.send(f"OK motora {val}")
        elif cmd.lower().startswith("motorb:"):
            val = int(cmd.split(":",1)[1])
            motorB.set_speed(val)
            uart.send(f"OK motorb {val}")
        elif cmd.lower().startswith("steer:"):
            ang = int(cmd.split(":",1)[1])
            steer.angle(ang)
            uart.send(f"OK steer {ang}")
        elif cmd.lower() in ("distance?","dist?"):
            d = sonic.distance_cm()
            if d: uart.send(f"DIST:{d:.2f}cm")
            else: uart.send("DIST:ERR")
        elif cmd.lower() == "report:on":
            reporting = True
            uart.send("REPORT:ON")
        elif cmd.lower() == "report:off":
            reporting = False
            uart.send("REPORT:OFF")
        else:
            uart.send("UNKNOWN_CMD")

    if reporting and (time.time() - last_report) >= 1.0:
        d = sonic.distance_cm()
        if d: uart.send(f"DIST:{d:.2f}cm")
        else: uart.send("DIST:ERR")
        last_report = time.time()

    time.sleep(0.01)
