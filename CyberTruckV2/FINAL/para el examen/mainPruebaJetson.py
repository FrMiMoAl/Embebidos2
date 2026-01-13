# main_uart_test.py (MicroPython en Pico)
import time
import json
from machine import Pin, PWM, I2C
from config import Config
from protocol import UARTProtocol


def clamp(x, a, b):
    return a if x < a else b if x > b else x


class Motor:
    def __init__(self, in1, in2, pwm, freq=1000, invert=False):
        self.in1 = Pin(in1, Pin.OUT)
        self.in2 = Pin(in2, Pin.OUT)
        self.pwm = PWM(Pin(pwm))
        self.pwm.freq(freq)
        self.invert = invert
        self.set_speed(0)

    def set_speed(self, speed):
        speed = clamp(int(speed), -100, 100)
        if self.invert:
            speed = -speed

        if speed == 0:
            self.in1.value(0)
            self.in2.value(0)
            self.pwm.duty_u16(0)
            return

        if speed > 0:
            self.in1.value(1); self.in2.value(0)
        else:
            self.in1.value(0); self.in2.value(1)

        duty = int(abs(speed) * 65535 / 100)
        self.pwm.duty_u16(duty)


class Servo:
    def __init__(self, pin, min_us=500, max_us=2500):
        self.pwm = PWM(Pin(pin))
        self.pwm.freq(50)
        self.min_us = min_us
        self.max_us = max_us
        self.set_angle(90)

    def set_angle(self, angle):
        angle = clamp(int(angle), 0, 180)
        us = self.min_us + (self.max_us - self.min_us) * angle // 180
        # Periodo 20ms = 20000us
        duty = int(us / 20000 * 65535)
        self.pwm.duty_u16(duty)


class MPU6050:
    # lectura mínima (accel+gyro)
    def __init__(self, i2c: I2C, addr=0x68):
        self.i2c = i2c
        self.addr = addr
        # Wake up
        self.i2c.writeto_mem(self.addr, 0x6B, b"\x00")
        time.sleep_ms(50)
        # Config gyro +-250 (0x00) y accel +-2g (0x00)
        self.i2c.writeto_mem(self.addr, 0x1B, b"\x00")
        self.i2c.writeto_mem(self.addr, 0x1C, b"\x00")
        time.sleep_ms(10)

    @staticmethod
    def _to_int16(h, l):
        v = (h << 8) | l
        return v - 65536 if v & 0x8000 else v

    def read(self):
        # 14 bytes desde ACCEL_XOUT_H (0x3B)
        data = self.i2c.readfrom_mem(self.addr, 0x3B, 14)
        ax = self._to_int16(data[0], data[1])
        ay = self._to_int16(data[2], data[3])
        az = self._to_int16(data[4], data[5])
        temp = self._to_int16(data[6], data[7])
        gx = self._to_int16(data[8], data[9])
        gy = self._to_int16(data[10], data[11])
        gz = self._to_int16(data[12], data[13])

        # escalas por defecto: accel LSB/g=16384, gyro LSB/(deg/s)=131
        return {
            "ax_g": ax / 16384.0,
            "ay_g": ay / 16384.0,
            "az_g": az / 16384.0,
            "gx_dps": gx / 131.0,
            "gy_dps": gy / 131.0,
            "gz_dps": gz / 131.0,
            "temp_c": (temp / 340.0) + 36.53
        }


# ---------- Setup ----------
proto = UARTProtocol(Config.UART_ID, Config.UART_BAUDRATE, Config.UART_TX_PIN, Config.UART_RX_PIN)

motors = {}
for name, (in1, in2, pwm, inv) in Config.MOTORS.items():
    motors[name] = Motor(in1, in2, pwm, freq=Config.MOTOR_PWM_FREQ, invert=inv)

servo1 = Servo(Config.SERVO1_PIN, Config.SERVO_MIN_US, Config.SERVO_MAX_US)
servo2 = Servo(Config.SERVO2_PIN, Config.SERVO_MIN_US, Config.SERVO_MAX_US)

# IMU
imu_ok = False
imu = None
try:
    i2c = I2C(Config.I2C_ID, scl=Pin(Config.IMU_SCL), sda=Pin(Config.IMU_SDA), freq=Config.I2C_FREQ)
    devices = i2c.scan()
    if 0x68 in devices:
        imu = MPU6050(i2c, 0x68)
        imu_ok = True
except:
    imu_ok = False

imu_stream_hz = 0
imu_next_ms = time.ticks_ms()

def stop_all():
    for m in motors.values():
        m.set_speed(0)

def drive_mecanum(vx, vy, w):
    # mezcla típica
    fl = vy + vx - w
    fr = vy - vx + w
    rl = vy - vx - w
    rr = vy + vx + w

    m = max(abs(fl), abs(fr), abs(rl), abs(rr), 1)
    if m > 100:
        scale = 100 / m
        fl = int(fl * scale); fr = int(fr * scale); rl = int(rl * scale); rr = int(rr * scale)

    motors["FL"].set_speed(fl)
    motors["FR"].set_speed(fr)
    motors["RL"].set_speed(rl)
    motors["RR"].set_speed(rr)

proto.send("ACK", {"boot": True, "imu_ok": imu_ok, "motors": list(motors.keys())})


# ---------- Loop ----------
last_cmd_ms = time.ticks_ms()

while True:
    msg = proto.recv()
    if msg:
        last_cmd_ms = time.ticks_ms()
        mtype = msg["type"]
        data = msg["data"]

        if mtype == "CMD":
            cmd = data.get("cmd", "")

            try:
                if cmd == "ping":
                    proto.send("PONG", {"t": time.ticks_ms()})

                elif cmd == "status":
                    proto.send("STATUS", {
                        "imu_ok": imu_ok,
                        "imu_stream_hz": imu_stream_hz,
                        "failsafe_ms": Config.FAILSAFE_MS
                    })

                elif cmd == "stop":
                    stop_all()
                    proto.send("ACK", {"stop": True})

                elif cmd == "motor":
                    name = data.get("name", "")
                    speed = int(data.get("speed", 0))
                    if name in motors:
                        motors[name].set_speed(speed)
                        proto.send("ACK", {"motor": name, "speed": speed})
                    else:
                        proto.send("ERR", {"err": "bad_motor_name", "name": name})

                elif cmd == "drive":
                    vx = int(data.get("vx", 0))
                    vy = int(data.get("vy", 0))
                    w  = int(data.get("w", 0))
                    vx = clamp(vx, -100, 100)
                    vy = clamp(vy, -100, 100)
                    w  = clamp(w,  -100, 100)
                    drive_mecanum(vx, vy, w)
                    proto.send("ACK", {"drive": [vx, vy, w]})

                elif cmd == "servo":
                    sid = int(data.get("id", 1))
                    ang = int(data.get("angle", 90))
                    if sid == 1:
                        servo1.set_angle(ang)
                    elif sid == 2:
                        servo2.set_angle(ang)
                    else:
                        raise ValueError("bad servo id")
                    proto.send("ACK", {"servo": sid, "angle": ang})

                elif cmd == "imu":
                    mode = data.get("mode", "once")
                    if not imu_ok:
                        proto.send("ERR", {"err": "imu_not_found"})
                    else:
                        if mode == "once":
                            proto.send("IMU", imu.read())
                        elif mode == "stream":
                            hz = int(data.get("hz", 10))
                            hz = clamp(hz, 1, 50)
                            imu_stream_hz = hz
                            proto.send("ACK", {"imu_stream_hz": imu_stream_hz})
                        elif mode == "off":
                            imu_stream_hz = 0
                            proto.send("ACK", {"imu_stream_hz": 0})
                        else:
                            proto.send("ERR", {"err": "bad_imu_mode", "mode": mode})

                else:
                    proto.send("ERR", {"err": "unknown_cmd", "cmd": cmd})

            except Exception as e:
                proto.send("ERR", {"err": "exception", "msg": str(e)})

    # FAILSAFE: si no hay comandos por un rato, frenar
    if not proto.link_alive(Config.FAILSAFE_MS):
        stop_all()

    # IMU streaming
    if imu_stream_hz > 0 and imu_ok:
        period_ms = int(1000 / imu_stream_hz)
        if time.ticks_diff(time.ticks_ms(), imu_next_ms) >= 0:
            imu_next_ms = time.ticks_add(time.ticks_ms(), period_ms)
            try:
                proto.send("IMU", imu.read())
            except:
                pass

    time.sleep_ms(5)
