"""
Raspberry Pi Pico - Main con Timers
Controla LEDs según mensajes UART usando timers
"""
from machine import Pin, Timer
from uart_comm import UARTComm

# ===== CONFIGURACIÓN =====
LED_PINS = [18, 19, 20, 21]
LED_NOMBRES = ["Rojos", "Azules", "Negros", "Borradores"]

# ===== INICIALIZACIÓN =====
uart = UARTComm(uart_id=0, baudrate=115200, tx_pin=0, rx_pin=1)

# LEDs
leds = [Pin(pin, Pin.OUT) for pin in LED_PINS]

# ===== FUNCIONES =====

def actualizar_leds(valores):
    for indice, valor in enumerate(valores):
        led_actual = leds[indice]

        if valor > 0:
            led_actual.value(1)
        else:
            led_actual.value(0)



def procesar_uart(timer):
    linea = uart.leer_linea()
    
    if linea is None:
        return  
    
    valores = uart.parsear_mensaje(linea)
    
    if valores is None:
        print(f"Formato incorrecto: {linea}")
        uart.enviar("ERROR: Formato debe ser (a,b,c,d)")
        return
    actualizar_leds(valores)
    
    print(f"Recibido: {linea}")
    for i, nombre in enumerate(LED_NOMBRES):
        if valores[i] > 0:
            estado = "ON "
        else:
            estado = "OFF"
        print(f"  {nombre:11} : {valores[i]:3}, {estado}")
    print()

    uart.enviar(f"OK: {linea}")



timer_uart = Timer()
timer_uart.init(period=10, mode=Timer.PERIODIC, callback=procesar_uart)

print(" Sistema listo - Esperando datos...\n")



try:
    while True:


        pass

except KeyboardInterrupt:
    print("\n Deteniendo sistema...")
    timer_uart.deinit()
    
    # Apagar todos los LEDs
    for led in leds:
        led.value(0)
    
    print(" Sistema apagado")