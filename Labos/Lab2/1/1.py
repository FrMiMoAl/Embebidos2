from machine import Pin
import time

led1 = Pin(18, Pin.OUT)
led2 = Pin(19, Pin.OUT)

leds = [led1, led2]
button = Pin(14, Pin.IN, Pin.PULL_UP)

state = 0

while True:
    if button.value() == 0:   
        state += 1
        if state > 3:         
            state = 0
        time.sleep(0.3)       

    if state == 0:
        for i in range (2):
            leds[i].on()
            time.sleep(0.3)
            leds[i].off()  
            
    elif state == 1:
        leds[1].on()
        leds[0].on()
        time.sleep(0.3)
        leds[1].off()
        leds[0].off()
        time.sleep(0.3) 
    elif state == 2:
        leds[1].on()
        leds[0].on()
    elif state == 3:
        leds[1].off()
        leds[0].off()
