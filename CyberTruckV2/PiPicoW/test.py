from machine import Pin, PWM, UART
import utime


'''
=============================
            Clases y funciones
=============================
'''

class MotorController:
    def __init__(self, PWMA1=16,PWMB1=21, A1_IN1=18, A1_IN2=17, B1_IN1=19, B1_IN2=20, PWMA2=22, PWMB2=3, A2_IN1=7, A2_IN2=28, B2_IN1=6, B2_IN2=2):
        ''' cfg:

              FRONT         // Motor A  IN1: 18 IN2: 17  PWM:16
            A-[   ]-B       // Motor B  IN1: 19 IN2: 20  PWM:21
               |    |
            C-[   ]-D       // Motor C  IN1: 7  IN2: 28  PWM:22
              REAR          // Motor D  IN1: 6  IN2: 2   PWM:3
        '''
        # --------------- FRONT MOTORS ---------------
        self.PWMA1 = PWM(Pin(PWMA1))
        self.PWMB1 = PWM(Pin(PWMB1))
        self.PWMA1.freq(1000)
        self.PWMB1.freq(1000)  

        # Motor A
        self.A1_IN1 = Pin(A1_IN1, Pin.OUT)
        self.A1_IN2 = Pin(A1_IN2, Pin.OUT)
        # Motor B
        self.B1_IN1 = Pin(B1_IN1, Pin.OUT)
        self.B1_IN2 = Pin(B1_IN2, Pin.OUT)

        # --------------- REAR MOTORS ---------------
        self.PWMA2 = PWM(Pin(PWMA2))
        self.PWMB2 = PWM(Pin(PWMB2))
        self.PWMA2.freq(1000)
        self.PWMB2.freq(1000)
        # Motor C
        self.A2_IN1 = Pin(A2_IN1, Pin.OUT)
        self.A2_IN2 = Pin(A2_IN2, Pin.OUT)
        # Motor D   
        self.B2_IN1 = Pin(B2_IN1, Pin.OUT)
        self.B2_IN2 = Pin(B2_IN2, Pin.OUT)

    def stop(self):
        # Front motors off
        self.PWMA1.duty_u16(0)
        self.PWMB1.duty_u16(0)
        # Rear motors off
        self.PWMA2.duty_u16(0)
        self.PWMB2.duty_u16(0)

    def movement(self, speedF,speedL, traction=0, active=0):
        if active in (1, 2):
            duty = int(0.8 * 65535)
            rot_dir = 1 if active == 1 else 0 
            print(f'Debug: Mov Especiales')
            # Motores A y D 
            self.A1_IN1.value(1 if rot_dir == 1 else 0)
            self.A1_IN2.value(0 if rot_dir == 1 else 1)
            self.B2_IN1.value(1 if rot_dir == 1 else 0)
            self.B2_IN2.value(0 if rot_dir == 1 else 1)
            # motores B y C 
            self.B1_IN1.value(0 if rot_dir == 1 else 1)
            self.B1_IN2.value(1 if rot_dir == 1 else 0)
            self.A2_IN1.value(0 if rot_dir == 1 else 1)
            self.A2_IN2.value(1 if rot_dir == 1 else 0)
            self.PWMA1.duty_u16(duty)
            self.PWMB1.duty_u16(duty)
            self.PWMA2.duty_u16(duty)
            self.PWMB2.duty_u16(duty)
            return
        
        dirF = 1 if speedF >= 0 else -1
        dirL = 1 if speedL >= 0 else -1

        print(f'Debug: speedF={speedF}, speedL={speedL}')

        speedF = min(max(abs(speedF),0),100)
        speedL = min(max(abs(speedL),0),100)
        
        traction = 1 if traction == 1 else 0

        duty = int((max(speedF, speedL) / 100) * 65535)

        self.PWMA1.duty_u16(duty)  
        self.PWMB1.duty_u16(duty)
        self.PWMA2.duty_u16(duty * (1 if traction==1 else 0))
        self.PWMB2.duty_u16(duty * (1 if traction==1 else 0))

        # Motors A and B
        self.A1_IN1.value((1 if (dirF== 1 and dirL >=0) else 0))
        self.A1_IN2.value((1 if (dirF==-1 and dirL <=0) else 0))
        self.B1_IN1.value((1 if (dirF== 1 and dirL <=0) else 0))
        self.B1_IN2.value((1 if (dirF==-1 and dirL >=0) else 0))

        # Motors C & D
        self.A2_IN1.value(1 if traction and dirF == 1 and dirL >= 0 else 0)
        self.A2_IN2.value(1 if traction and dirF == -1 and dirL <= 0 else 0)
        self.B2_IN1.value(1 if traction and dirF == 1 and dirL <= 0 else 0)
        self.B2_IN2.value(1 if traction and dirF == -1 and dirL >= 0 else 0)


# ------ Ultrasonic Sensor -----
trig = Pin(26, Pin.OUT)
echo = Pin(27, Pin.IN)


def read_distance(samples=3, timeout_us=30000):

    def pulse():
        trig.value(0)
        utime.sleep_us(2)
        trig.value(1)
        utime.sleep_us(10)
        trig.value(0)

    def _measure_once():
        pulse()
        t0 = utime.ticks_us()
        while echo.value() == 0:
            if utime.ticks_diff(utime.ticks_us(), t0) > timeout_us:
                return -1
        start = utime.ticks_us()
        while echo.value() == 1:
            if utime.ticks_diff(utime.ticks_us(), start) > timeout_us:
                return -1
        dur = utime.ticks_diff(utime.ticks_us(), start)
        return (dur * 0.0343) / 2

    distances = []
    for _ in range(max(1, samples)):
        dist = _measure_once()
        if dist >= 0:
            distances.append(dist)

    if distances:
        distances.sort()
        return distances[len(distances) // 2]
    return -1


# ===============================================
# CONFIGURACIÓN DE COMUNICACIÓN
# ===============================================
motors = MotorController()
uart = UART(0, baudrate=115200, tx=Pin(0), rx=Pin(1))  # UART por pines físicos

'''
=============================
            Main loop
=============================
'''

print("=== Pico W ejecutando secuencia automática ===")

dur = 60000  # Duración de la prueba en ms
start = utime.ticks_ms()

while True:

    dist = read_distance()
    print(f"Distancia: {dist} cm")
    #uart.write(f"{dist}\n")   # siempre envía la distancia por UART
    utime.sleep_ms(300)
    #utime.sleep_ms(30)
