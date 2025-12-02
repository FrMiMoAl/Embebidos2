from machine import Pin
import time

led1 = Pin(18, Pin.OUT)
led2 = Pin(19, Pin.OUT)
led3 = Pin(20, Pin.OUT)
led4 = Pin(21, Pin.OUT)

leds = [led1, led2, led3, led4]

button1 = Pin(14, Pin.IN, Pin.PULL_UP)  
button2 = Pin(13, Pin.IN, Pin.PULL_UP)  

cont = 0       
tiempo = 1    

while True:
    if button1.value() == 0: 
        tiempo = 1  
        cont += 1
        if cont >= len(leds):
            cont = 0
        time.sleep(0.3)   
    
    
    if button2.value() == 0: 
        tiempo += 1
        if tiempo > 10:
            tiempo = 1
        print("Velocidad =", tiempo, "s")
        time.sleep(0.3)   
    
    for i in range(4):
        if i == cont:
            leds[i].on()
            time.sleep(tiempo)
            leds[i].off()
            time.sleep(tiempo)
                
        else:
            leds[i].off()   
