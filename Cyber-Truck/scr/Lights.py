# =============================================
#
#               Module LIGHTS
#
# =============================================


# Clase para manejo de luces

from machine import Pin, PWM
import time

# --- Setup pins ---
headlights = PWM(Pin(0))
blinker_left = Pin(1, Pin.OUT)
blinker_right = Pin(2, Pin.OUT)
brake_lights = PWM(Pin(3))

# PWM freq
headlights.freq(1000)  # 1 kHz
brake_lights.freq(1000) # 1 kHz

# --- Helper function for PWM duty 0-100% ---
def pwm_duty(pwm, percent):
    duty = int(65535 * (percent / 100))
    pwm.duty_u16(duty)

# --- Headlight modes ---
def headlights_off():
    pwm_duty(headlights, 0)

def low_beam():
    pwm_duty(headlights, 50)

def high_beam():
    pwm_duty(headlights, 100)

def fog_beam():
    pwm_duty(headlights, 25)

# --- Brake lights ---
def brake_off():
    pwm_duty(brake_lights, 25)  # Always ON dim

def brake_on():
    pwm_duty(brake_lights, 75)  # Braking

# --- Blinkers ---
def blink(pin, times=5, interval=0.5):
    for _ in range(times):
        pin.value(1)
        time.sleep(interval)
        pin.value(0)
        time.sleep(interval)

def hazard(times=5, interval=0.5):
    for _ in range(times):
        blinker_left.value(1)
        blinker_right.value(1)
        time.sleep(interval)
        blinker_left.value(0)
        blinker_right.value(0)
        time.sleep(interval)
