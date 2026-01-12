from machine import I2C, Pin
import time

SDA = 26
SCL = 27
I2C_ID = 1

def who_am_i(i2c, addr):
    try:
        return i2c.readfrom_mem(addr, 0x75, 1)[0]  # WHO_AM_I
    except Exception as e:
        return None

for freq in (100000, 400000):
    i2c = I2C(I2C_ID, scl=Pin(SCL), sda=Pin(SDA), freq=freq)
    devs = i2c.scan()
    print("\nFREQ =", freq, "scan =", [hex(d) for d in devs])

    for addr in devs:
        w = who_am_i(i2c, addr)
        print(" addr", hex(addr), "WHO_AM_I =", w)
    time.sleep_ms(200)
