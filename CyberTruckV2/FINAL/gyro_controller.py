# gyro_controller.py - VERSIÓN CORREGIDA
from machine import Pin, I2C
import utime

class GyroController:
    def __init__(self, scl=17, sda=16):  # Cambiados a pines que no conflictúan con UART
        self.addr = 0x68
        try:
            self.i2c = I2C(0, scl=Pin(scl), sda=Pin(sda), freq=400000)
            utime.sleep_ms(100)  # Esperar estabilización
            
            # Verificar conexión
            devices = self.i2c.scan()
            if self.addr not in devices:
                raise Exception(f"MPU6050 no encontrado. Dispositivos: {[hex(d) for d in devices]}")
            
            print("✅ MPU6050 detectado en", hex(self.addr))
            
            # Reset del MPU6050
            self.i2c.writeto_mem(self.addr, 0x6B, b'\x80')
            utime.sleep_ms(100)
            
            # Wake up MPU6050
            self.i2c.writeto_mem(self.addr, 0x6B, b'\x00')
            utime.sleep_ms(100)
            
            # Configurar giroscopio (escala ±250°/s)
            self.i2c.writeto_mem(self.addr, 0x1B, b'\x00')
            utime.sleep_ms(50)
            
            # Configurar acelerómetro
            self.i2c.writeto_mem(self.addr, 0x1C, b'\x00')
            utime.sleep_ms(50)
            
        except Exception as e:
            print("❌ Error inicializando MPU6050:", e)
            print("Verifica las conexiones:")
            print(f"  - SDA -> GP{sda}")
            print(f"  - SCL -> GP{scl}")
            print("  - VCC -> 3.3V")
            print("  - GND -> GND")
            raise
        
        self.yaw = 0.0
        self.last_time = utime.ticks_ms()
        self.bias = 0.0
        self.calibrate()

    def read_word(self, reg):
        """Lee un valor de 16 bits con manejo de errores"""
        try:
            high = self.i2c.readfrom_mem(self.addr, reg, 1)[0]
            low = self.i2c.readfrom_mem(self.addr, reg + 1, 1)[0]
            value = (high << 8) | low
            if value >= 0x8000:
                value = -((65535 - value) + 1)
            return value
        except Exception as e:
            print(f"Error leyendo registro {hex(reg)}: {e}")
            return 0

    def calibrate(self, samples=500):
        """Calibra el giroscopio - MANTÉN EL ROBOT QUIETO"""
        print("⚠️  Calibrando giroscopio...")
        print("    ¡NO MUEVAS EL ROBOT!")
        utime.sleep_ms(500)
        
        total = 0
        valid_samples = 0
        
        for i in range(samples):
            gz = self.read_word(0x43) / 131.0
            # Filtrar lecturas extremas
            if abs(gz) < 50:  # Valor razonable para robot quieto
                total += gz
                valid_samples += 1
            
            if i % 100 == 0:
                print(f"    Calibrando... {i}/{samples}")
            
            utime.sleep_ms(2)
        
        if valid_samples > 0:
            self.bias = total / valid_samples
            print(f"✅ Calibración OK. Offset Z = {self.bias:.3f}°/s")
        else:
            print("⚠️  Calibración con problemas, usando offset = 0")
            self.bias = 0.0

    def update(self):
        """Actualiza el ángulo yaw"""
        gyro_z = (self.read_word(0x47) / 131.0) - self.bias
        now = utime.ticks_ms()
        dt = utime.ticks_diff(now, self.last_time) / 1000.0
        self.last_time = now
        
        # Integrar velocidad angular
        self.yaw += gyro_z * dt
        
        # Mantener en rango 0-360
        self.yaw = self.yaw % 360
        if self.yaw < 0:
            self.yaw += 360
        
        return self.yaw

    def get_gyro_z(self):
        """Retorna velocidad angular actual en °/s"""
        return (self.read_word(0x47) / 131.0) - self.bias

    def reset(self):
        """Reinicia el ángulo a 0"""
        self.yaw = 0.0
        self.last_time = utime.ticks_ms()
        print("🔄 Yaw reiniciado a 0°")