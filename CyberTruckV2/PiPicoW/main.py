
from machine import Pin, PWM, UART
import utime

'''
=============================
                Clases y funciones
=============================
'''

class MotorController:
    def _init_(self, PWMA1=16,PWMB1=21, A1_IN1=18, A1_IN2=17, B1_IN1=19, B1_IN2=20, PWMA2=22, PWMB2=3, A2_IN1=7, A2_IN2=28, B2_IN1=6, B2_IN2=2):
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
        # # ---- Comportamiento especial ----
        # 1. Giro Antihorario
        # 2. Giro Horario
        # 3. ?????
        if active in (1, 2):
            duty = int(0.8 * 65535)  # Calibrar la vel de acorde al giro
            rot_dir = 1 if active == 1 else 0 
            # 1 = antihorario, 0 = horario
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
        # ----------------------------
        # ---- Comportamiento normal ----
        # ----------------------------
        # Direction FW,BW,LR,LL
        dirF = 1 if speedF >= 0 else -1;
        dirL = 1 if speedL >= 0 else -1;

        print(f'Debug: speedF={speedF}, speedL={speedL}')

        speedF = min(max(abs(speedF),0),100)
        speedL = min(max(abs(speedL),0),100)
        
        traction = 1 if traction == 1 else 0

        # ----- I am speed...
        duty = int((max(speedF, speedL) / 100) * 65535)
            # traccion delantera por defautl, OJO
        self.PWMA1.duty_u16(duty)  
        self.PWMB1.duty_u16(duty)
            # Sin 4x4 por consumo energetico
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

def read_distance(samples=3, timeout_us=30000):
    # Inicialización de los pines
    trig = Pin(26, Pin.OUT)
    echo = Pin(27, Pin.IN)

    # Pulso de 10µs
    def _pulse():
        trig.value(0)
        utime.sleep_us(2)
        trig.value(1)
        print("Pulsando Trigger...")
        utime.sleep_us(10)
        trig.value(0)

    # medición
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
motors = MotorController()
uart = UART(0, baudrate=115200, tx=0 , rx=1)

''' 
=============================
            Main loop
=============================
'''
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
                if len(parts) == 4:
                    try:

                        pwm1 = float(parts[0])
                        pwm2 = float(parts[1])
                        Trac = float(parts[2])
                        Actv  = float(parts[3])

                        print(f"pwm1={pwm1}, pwm2={pwm2}, traction={Trac}, active={Actv}")
                        motors.movement(pwm1, pwm2, Trac, Actv)
                    
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
