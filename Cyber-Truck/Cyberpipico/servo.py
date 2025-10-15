from machine import Pin, PWM

FREQ   = 50      
MIN_US = 500     
MAX_US = 2500    

def pwm_from_pin(pin, freq=FREQ):
    pwm = PWM(Pin(pin))
    pwm.freq(freq)
    return pwm

def angle_to_duty(angle, min_us=MIN_US, max_us=MAX_US, freq=FREQ):
    angle = max(0, min(180, angle))
    pulse = min_us + (max_us - min_us) * (angle / 180.0)
    period_us = 1_000_000 // freq
    return int(pulse * 65535 // period_us)

def servo_write(pwm, angle, min_us=MIN_US, max_us=MAX_US, freq=FREQ):
    pwm.duty_u16(angle_to_duty(angle, min_us, max_us, freq))

def servo_deinit(pwm):
    pwm.deinit()

