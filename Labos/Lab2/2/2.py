from machine import Pin
import time

led1 = Pin(18, Pin.OUT)
led2 = Pin(19, Pin.OUT)
led3 = Pin(20, Pin.OUT)
led4 = Pin(21, Pin.OUT)

leds = [led1, led2,led3, led4]
button1 = Pin(14, Pin.IN, Pin.PULL_UP)
button2 = Pin(13, Pin.IN, Pin.PULL_UP)
cont = 0
def DecimalBinario(n): 
    return bin(n).replace("0b", "") 

def DecimalHex(n): 
    return hex(n).replace("0x", "")
while True:
    if (button1.value() == 0) and (cont < 15):   
        cont += 1
        binary_number = DecimalBinario(cont)
        hex_number = DecimalHex(cont)
        print(cont,binary_number,hex_number)
        time.sleep(0.3)       

    if (button2.value() == 0) and (cont >0): 
        cont -= 1
        binary_number = DecimalBinario(cont)
        hex_number = DecimalHex(cont)
        print(cont,binary_number,hex_number)
        time.sleep(0.3)  
    for i in range (4):
        bit = (cont >> i) & 1
        if  (bit ==1):
                leds[i].on()
                
        else:
                leds[i].off()
        