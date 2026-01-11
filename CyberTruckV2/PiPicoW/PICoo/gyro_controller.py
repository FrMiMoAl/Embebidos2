# gyro_controller.py
import time
from machine import I2C, Pin

class GyroController:
    """
    MPU-6050 yaw aproximado integrando gyro Z.
    OJO: deriva con el tiempo (normal), pero sirve para estabilización básica.
    """
    def __init__(self, i2c_id=1, scl=27, sda=26, freq=400000, addr=0x68):
        self.addr = addr
        self.i2c = I2C(i2c_id, scl=Pin(scl), sda=Pin(sda), freq=freq)

        # Wake up
        self.i2c.writeto_mem(self.addr, 0x6B, b"\x00")
        time.sleep_ms(50)

        # Gyro range ±250 dps (FS_SEL=0)
        self.i2c.writeto_mem(self.addr, 0x1B, b"\x00")
        self.scale = 131.0  # LSB/(deg/s) para ±250

        self.yaw = 0.0
        self.bias_gz = 0.0
        self._last = time.ticks_ms()
        self._calibrate()

    def _read_i16(self, reg):
        hi = self.i2c.readfrom_mem(self.addr, reg, 1)[0]
        lo = self.i2c.readfrom_mem(self.addr, reg + 1, 1)[0]
        val = (hi << 8) | lo
        if val & 0x8000:
            val = -((65535 - val) + 1)
        return val

    def _read_gz_dps(self):
        gz = self._read_i16(0x47)  # GYRO_ZOUT_H
        return gz / self.scale

    def _calibrate(self, samples=200):
        acc = 0.0
        for _ in range(samples):
            acc += self._read_gz_dps()
            time.sleep_ms(5)
        self.bias_gz = acc / samples

    def update(self):
        now = time.ticks_ms()
        dt = time.ticks_diff(now, self._last) / 1000.0
        self._last = now

        gz = self._read_gz_dps() - self.bias_gz
        self.yaw += gz * dt

        # wrap opcional
        if self.yaw > 180:
            self.yaw -= 360
        elif self.yaw < -180:
            self.yaw += 360

        return round(self.yaw, 2)
