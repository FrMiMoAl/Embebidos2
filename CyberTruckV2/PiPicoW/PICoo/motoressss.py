from machine import Pin, PWM
import time
import sys
import select

# ==============================
# TU CODIGO DE 4 MOTORES (NO CAMBIADO)
# ==============================
in1 = Pin(2, Pin.OUT)
in2 = Pin(3, Pin.OUT)
ena = PWM(Pin(4))
ena.freq(1000)

in11 = Pin(6, Pin.OUT)
in22 = Pin(7, Pin.OUT)
ena1 = PWM(Pin(8))
ena1.freq(1000)

in111 = Pin(12, Pin.OUT)
in222 = Pin(11, Pin.OUT)
ena2 = PWM(Pin(10))
ena2.freq(1000)

in1111 = Pin(13, Pin.OUT)
in2222 = Pin(14, Pin.OUT)
ena3 = PWM(Pin(15))
ena3.freq(1000)

# Giro hacia adelante
in1.value(1)
in2.value(0)
ena.duty_u16(40000)  # velocidad motor trasero izquierdo

in11.value(1)
in22.value(0)
ena1.duty_u16(40000)  #motor trasero derecho

in111.value(1)
in222.value(0)
ena2.duty_u16(40000) # motor delantero izquierdo

in1111.value(1)
in2222.value(0)
ena3.duty_u16(40000) # motor delantero derecho

