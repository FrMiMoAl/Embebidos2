# motor_controller.py - Control de motores omni wheels
from machine import Pin, PWM

class Motor:
    """Control individual de un motor DC con puente H"""
    def __init__(self, pwm_pin, in1_pin, in2_pin):
        self.pwm = PWM(Pin(pwm_pin))
        self.pwm.freq(1000)
        self.in1 = Pin(in1_pin, Pin.OUT)
        self.in2 = Pin(in2_pin, Pin.OUT)
    
    def set_speed(self, speed):
        """
        Establece velocidad del motor
        speed: -100 a 100 (-100=reversa máxima, 100=adelante máximo)
        """
        speed = max(min(speed, 100), -100)  # Limitar rango
        
        if speed > 0:
            self.in1.value(1)
            self.in2.value(0)
            self.pwm.duty_u16(int(abs(speed) * 655.35))
        elif speed < 0:
            self.in1.value(0)
            self.in2.value(1)
            self.pwm.duty_u16(int(abs(speed) * 655.35))
        else:
            self.in1.value(0)
            self.in2.value(0)
            self.pwm.duty_u16(0)
    
    def stop(self):
        """Detiene el motor"""
        self.set_speed(0)


class OmniDrive:
    """Control de plataforma omni de 4 ruedas"""
    def __init__(self, m_fl, m_fr, m_rl, m_rr):
        self.m_fl = m_fl  # Motor frontal izquierdo
        self.m_fr = m_fr  # Motor frontal derecho
        self.m_rl = m_rl  # Motor trasero izquierdo
        self.m_rr = m_rr  # Motor trasero derecho
    
    def drive(self, vx, vy, omega):
        """
        Control de movimiento omni
        vx: velocidad en X (-100 a 100) - adelante/atrás
        vy: velocidad en Y (-100 a 100) - izquierda/derecha
        omega: velocidad angular (-100 a 100) - rotación
        """
        # Cinemática inversa para omni wheels
        fl_speed = vx - vy - omega
        fr_speed = vx + vy + omega
        rl_speed = vx + vy - omega
        rr_speed = vx - vy + omega
        
        # Normalizar si algún valor excede 100
        max_speed = max(abs(fl_speed), abs(fr_speed), abs(rl_speed), abs(rr_speed))
        if max_speed > 100:
            factor = 100.0 / max_speed
            fl_speed *= factor
            fr_speed *= factor
            rl_speed *= factor
            rr_speed *= factor
        
        # Aplicar velocidades
        self.m_fl.set_speed(fl_speed)
        self.m_fr.set_speed(fr_speed)
        self.m_rl.set_speed(rl_speed)
        self.m_rr.set_speed(rr_speed)
    
    def stop(self):
        """Detiene todos los motores"""
        self.m_fl.stop()
        self.m_fr.stop()
        self.m_rl.stop()
        self.m_rr.stop()
    
    def test(self):
        """Test rápido de todos los motores"""
        print("Test de motores omni:")
        
        print("  → Adelante")
        self.drive(50, 0, 0)
        
        print("  → Derecha")
        self.drive(0, 50, 0)
        
        print("  → Giro horario")
        self.drive(0, 0, 50)
        
        print("  → Atrás")
        self.drive(-50, 0, 0)
        
        self.stop()
        print("✅ Test completado")