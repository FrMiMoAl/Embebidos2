from machine import Pin
import time, network

led = Pin("LED", Pin.OUT)

ssid = "MiRed"
psk  = "MiClave"

w = network.WLAN(network.STA_IF)
w.active(True)
w.connect(ssid, psk)

t0 = time.time()
while not w.isconnected() and time.time() - t0 < 15:
    led.toggle(); time.sleep(0.2)

print("IP:", w.ifconfig())

while True:
    led.toggle()
    time.sleep(0.5)
