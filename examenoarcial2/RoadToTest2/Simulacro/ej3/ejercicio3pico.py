from machine import UART, Pin, PWM
import utime

# UART1 - RX en GP5 (desde Raspberry Pi 5)
uart = UART(1, baudrate=115200, rx=Pin(5))

# Pines del motor
PIN_PWM = 19      # PWM motor (Enable A)
PIN_IN1 = 20      # Dirección 1
PIN_IN2 = 21      # Dirección 2

# Configuración de pines
in1 = Pin(PIN_IN1, Pin.OUT)
in2 = Pin(PIN_IN2, Pin.OUT)

pwm = PWM(Pin(PIN_PWM))
pwm.freq(1000)  # frecuencia PWM en Hz
pwm.duty_u16(0)


def motor_stop():
    """Detiene completamente el motor."""
    pwm.duty_u16(0)
    in1.value(0)
    in2.value(0)


def motor_forward_accelerate(duration=5):
    """
    Acelera el motor desde 0% hasta 100% durante 'duration' segundos.
    """

    print("Iniciando aceleración del motor...")

    # Definir sentido de giro forward
    in1.value(1)
    in2.value(0)

    # PWM de 0% a 100% en 100 pasos
    for i in range(101):
        duty = int(i * 65535 / 100)  # 0–65535
        pwm.duty_u16(duty)

        # tiempo entre incrementos = 5 segundos / 100 pasos
        utime.sleep(duration / 100)

    print("Aceleración completada. Deteniendo motor...")
    motor_stop()


print("Esperando comando UART 'M' para activar el motor...")

motor_stop()

while True:
    if uart.any():
        cmd = uart.read(1)
        print("RX:", cmd)

        if cmd == b'M':
            print("-> Comando recibido: Activar motor con aceleración 0–100% en 5s")
            motor_forward_accelerate(5)  # ejecutar ciclo completo
            print("Motor listo, esperando nueva señal...")

        else:
            print("Comando desconocido o inválido, motor detenido.")
            motor_stop()

    utime.sleep_ms(50)
