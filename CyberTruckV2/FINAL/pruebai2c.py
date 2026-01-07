# test_mpu.py
from machine import Pin, I2C
import time

i2c = I2C(0, scl=Pin(17), sda=Pin(16), freq=400000)
time.sleep(0.1)

print("Escaneando I2C...")
devices = i2c.scan()
print("Dispositivos encontrados:", [hex(d) for d in devices])

if 0x68 in devices:
    print("✅ MPU6050 detectado!")
else:
    print("❌ MPU6050 NO detectado")
    print("Verifica:")
    print("  1. Conexiones SDA/SCL")
    print("  2. Alimentación 3.3V")
    print("  3. Resistencias pull-up (algunas placas las tienen)")