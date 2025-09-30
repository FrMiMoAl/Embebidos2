# tests/test_steering.py
# Test para el módulo Steering.py en Raspberry Pi Pico W

from Steering.py import Steering
import time

# Ajusta al pin real de tu servo
SERVO_PIN = 15

def test_steering():
    print("== Test Steering (servo MG90S) ==")
    servo = Steering(SERVO_PIN)

    # Ir a centro (90°)
    print("Moviendo a 90° (centro)")
    servo.angle(90)
    time.sleep(2)

    # Ir a izquierda (0°)
    print("Moviendo a 0° (izquierda)")
    servo.angle(0)
    time.sleep(2)

    # Ir a derecha (180°)
    print("Moviendo a 180° (derecha)")
    servo.angle(180)
    time.sleep(2)

    # Volver al centro
    print("Regresando a 90° (centro)")
    servo.angle(90)
    time.sleep(2)

    print("== Test completado ==")

# Ejecutar el test
if __name__ == "__main__":
    test_steering()
