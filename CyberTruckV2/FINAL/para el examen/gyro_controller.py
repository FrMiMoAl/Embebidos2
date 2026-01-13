# gyro_controller.py
import time
from machine import I2C, Pin

class GyroController:
    """
    MPU-6050 roll aproximado integrando gyro X.
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

        self.roll = 0.0
        self.bias_gx = 0.0
        self._last = time.ticks_ms()
        self._calibrate()

    def _read_i16(self, reg):
        hi = self.i2c.readfrom_mem(self.addr, reg, 1)[0]
        lo = self.i2c.readfrom_mem(self.addr, reg + 1, 1)[0]
        val = (hi << 8) | lo
        if val & 0x8000:
            val = -((65535 - val) + 1)
        return val

    def _read_gx_dps(self):
        gx = self._read_i16(0x43)  # GYRO_XOUT_H
        return gx / self.scale

    def _calibrate(self, samples=200):
        acc = 0.0
        for _ in range(samples):
            acc += self._read_gx_dps()
            time.sleep_ms(5)
        self.bias_gx = acc / samples

    def update(self):
        now = time.ticks_ms()
        dt = time.ticks_diff(now, self._last) / 1000.0
        self._last = now

        gx = self._read_gx_dps() - self.bias_gx
        self.roll += gx * dt

        # wrap opcional
        if self.roll > 180:
            self.roll -= 360
        elif self.roll < -180:
            self.roll += 360

        return round(self.roll, 2)