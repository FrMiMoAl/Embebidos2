from machine import Pin, PWM, UART
import utime

FREQ   = 50      
MIN_US = 500     
MAX_US = 2500 

class PinConfig:
    UART_TX = 0
    UART_RX = 1
    UART_BAUDRATE = 115200

    MOTOR_LEFT_BIN1 = 20
    MOTOR_LEFT_BIN2 = 21
    MOTOR_LEFT_PWM = 22

    MOTOR_RIGHT_AIN1 = 18
    MOTOR_RIGHT_AIN2 = 17
    MOTOR_RIGHT_PWM = 16

    STEERING_SERVO = 8

    ULTRASONIC_TRIGGER = 26
    ULTRASONIC_ECHO = 27

class SensorConfig:
    ULTRASONIC_TIMEOUT = 30000
    SOUND_SPEED = 0.0343  # cm/us

uart = UART(0, baudrate=PinConfig.UART_BAUDRATE, tx=PinConfig.UART_TX, rx=PinConfig.UART_RX)

# Motores
left_in1 = Pin(PinConfig.MOTOR_LEFT_BIN1, Pin.OUT)
left_in2 = Pin(PinConfig.MOTOR_LEFT_BIN2, Pin.OUT)
left_pwm = PWM(Pin(PinConfig.MOTOR_LEFT_PWM))
left_pwm.freq(1000)

right_in1 = Pin(PinConfig.MOTOR_RIGHT_AIN1, Pin.OUT)
right_in2 = Pin(PinConfig.MOTOR_RIGHT_AIN2, Pin.OUT)
right_pwm = PWM(Pin(PinConfig.MOTOR_RIGHT_PWM))
right_pwm.freq(1000)

# Servo
servo = PWM(Pin(PinConfig.STEERING_SERVO))
servo.freq(50)

# Ultrasónico
trigger = Pin(PinConfig.ULTRASONIC_TRIGGER, Pin.OUT)
echo = Pin(PinConfig.ULTRASONIC_ECHO, Pin.IN)

def motors(pwm1, pwm2):
    dir_left = 1
    if pwm1 < 0:
        dir_left = -1
        pwm1 = -pwm1
    if pwm1 > 100: pwm1 = 100
    duty = int((pwm1 / 100) * 65535)
    left_pwm.duty_u16(duty)
    left_in1.value(1 if dir_left == 1 else 0)
    left_in2.value(0 if dir_left == 1 else 1)

    dir_right = 1
    if pwm2 < 0:
        dir_right = -1
        pwm2 = -pwm2
    if pwm2 > 100: pwm2 = 100
    duty = int((pwm2 / 100) * 65535)
    right_pwm.duty_u16(duty)
    right_in1.value(1 if dir_right == 1 else 0)
    right_in2.value(0 if dir_right == 1 else 1)

def set_servo(angle):

    angle = max(0, min(180, angle))
    pulse = MIN_US + (MAX_US - MIN_US) * (angle / 180.0)

    pwm = PWM(Pin(PinConfig.STEERING_SERVO))
    pwm.freq(FREQ)
    period_us = 1_000_000 // FREQ
    duty = int(pulse * 65535 // period_us)

    pwm.duty_u16(duty)


def read_distance(samples=3, timeout_us=30000):
    # Inicialización de los pines
    trig = Pin(PinConfig.ULTRASONIC_TRIGGER, Pin.OUT)
    echo = Pin(PinConfig.ULTRASONIC_ECHO, Pin.IN)

    # Función para enviar el pulso de 10µs
    def _pulse():
        trig.value(0)
        utime.sleep_us(2)
        trig.value(1)
        print("Pulsando Trigger...")
        utime.sleep_us(10)
        trig.value(0)


    # Función para realizar una medición
    def _measure_once():
        _pulse()

        t0 = utime.ticks_us()
        # Espera flanco de subida
        while echo.value() == 0:
            if utime.ticks_diff(utime.ticks_us(), t0) > timeout_us:
                return -1

        start = utime.ticks_us()
        # Espera flanco de bajada
        while echo.value() == 1:
            if utime.ticks_diff(utime.ticks_us(), start) > timeout_us:
                return -1

        dur = utime.ticks_diff(utime.ticks_us(), start)  # µs
        # Distancia en cm (vel. sonido ~343 m/s → 0.0343 cm/µs, ida y vuelta /2)
        return (dur * 0.0343) / 2

    # Tomamos varias mediciones
    distances = []
    for _ in range(max(1, samples)):
        dist = _measure_once()
        if dist >= 0:
            distances.append(dist)

    # Si hay mediciones válidas, devolver la mediana
    if distances:
        distances.sort()
        return distances[len(distances) // 2]
    
    return -1  # Si todas las mediciones fallan


last_ultrasonic_time = utime.ticks_ms()

while True:
    try:
        if uart.any():
            raw = uart.readline()
            if raw:
                if isinstance(raw, (bytes, bytearray, memoryview)):
                    line = raw.decode('utf-8', 'ignore').strip()
                else:
                    line = str(raw).strip()

                print("RX:", line)

                parts = line.split(",")
                if len(parts) == 3:
                    try:
                        pwm1 = float(parts[0])
                        pwm2 = float(parts[1])
                        servo_angle = float(parts[2])
                        print(f"pwm1={pwm1}, pwm2={pwm2}, servo={servo_angle}")
                        motors(pwm1, pwm2)
                        set_servo(servo_angle)
                    except ValueError:
                        print("Error: los valores deben ser numéricos")
                else:
                    print("Error: los datos recibidos no tienen el formato esperado")
    except Exception as e:
        print(f"Error en la lectura o procesamiento de datos: {e}")

    # Ultrasonido
    if utime.ticks_diff(utime.ticks_ms(), last_ultrasonic_time) > 500:
        dist = read_distance()
        print(f"Distancia: {dist} cm")
        if dist != -1:
            uart.write(f"{dist}\n")
        last_ultrasonic_time = utime.ticks_ms()

    # Pequeña pausa para evitar sobrecargar el CPU
    utime.sleep_ms(10)
