from machine import Pin, PWM, UART
import time

# Configurar UART
uart = UART(0, baudrate=115200, tx=Pin(0), rx=Pin(1))  # UART0 en GP0 y GP1

# Pines Motor A
AIN1 = Pin(21, Pin.OUT)
AIN2 = Pin(28, Pin.OUT)
PWMA = PWM(Pin(27))

# Pines Motor B
BIN1 = Pin(18, Pin.OUT)
BIN2 = Pin(12, Pin.OUT)
PWMB = PWM(Pin(13))

# Pin STBY
STBY = Pin(19, Pin.OUT)
STBY.value(1)

# Configurar PWM
PWMA.freq(1000)
PWMB.freq(1000)

# Funciones control motor
def motorA(speed):
    if speed > 0:
        AIN1.value(1); AIN2.value(0)
    elif speed < 0:
        AIN1.value(0); AIN2.value(1)
    else:
        AIN1.value(0); AIN2.value(0)
    PWMA.duty_u16(int(abs(speed) * 65535 / 100))

def motorB(speed):
    if speed > 0:
        BIN1.value(1); BIN2.value(0)
    elif speed < 0:
        BIN1.value(0); BIN2.value(1)
    else:
        BIN1.value(0); BIN2.value(0)
    PWMB.duty_u16(int(abs(speed) * 65535 / 100))

# Loop principal
while True:
    if uart.any():
        try:
            data = uart.readline().decode().strip()
            # Espera formato: A:vel,B:vel
            if data:
                partes = data.split(",")
                velA = int(partes[0].split(":")[1])
                velB = int(partes[1].split(":")[1])

                motorA(velA)
                motorB(velB)

                print("Recibido:", velA, velB)
        except Exception as e:
            print("Error:", e)
