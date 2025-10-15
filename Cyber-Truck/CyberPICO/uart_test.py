"""
Test Simple de UART para Raspberry Pi Pico W
Usa este archivo para verificar que UART funciona correctamente
"""

from machine import Pin, UART
import utime

print("\n" + "="*50)
print("UART TEST - Raspberry Pi Pico W")
print("="*50 + "\n")

# Inicializar UART
try:
    uart = UART(0, baudrate=115200, tx=Pin(0), rx=Pin(1))
    uart.init(bits=8, parity=None, stop=1)
    print("✓ UART initialized on GPIO 0 (TX) and GPIO 1 (RX)")
    print(f"  Baudrate: 115200")
    print(f"  Config: 8N1\n")
except Exception as e:
    print(f"✗ UART initialization failed: {e}")
    import sys
    sys.exit()

# Enviar mensaje de inicio
try:
    uart.write("PICO_READY\n")
    print("→ Sent: PICO_READY\n")
except Exception as e:
    print(f"✗ Write failed: {e}\n")

print("Listening for commands...")
print("Send 'PING' to test communication")
print("Send 'HELLO' for a greeting")
print("Send 'STOP' to exit")
print("-" * 50 + "\n")

buffer = ""
running = True
counter = 0

while running:
    try:
        # Verificar si hay datos disponibles
        if uart.any():
            bytes_available = uart.any()
            print(f"\n[DEBUG] {bytes_available} bytes available")
            
            # Leer datos
            data = uart.read()
            
            if data:
                print(f"[DEBUG] Raw data: {data}")
                print(f"[DEBUG] Data length: {len(data)}")
                
                # Decodificar (método compatible con MicroPython)
                try:
                    text = data.decode('utf-8')
                    print(f"[DEBUG] Decoded (UTF-8): '{text}'")
                except Exception as e:
                    print(f"[DEBUG] UTF-8 decode failed: {e}")
                    # Fallback: convertir byte por byte
                    text = ''
                    for byte in data:
                        if 32 <= byte <= 126 or byte in [10, 13]:
                            text += chr(byte)
                    print(f"[DEBUG] Decoded (fallback): '{text}'")
                
                buffer += text
                print(f"[DEBUG] Buffer now: '{buffer}'")
                
                # Procesar líneas completas
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    line = line.strip('\r\n ')
                    
                    if line:
                        print(f"← Received: '{line}'")
                        
                        # Procesar comandos
                        if line == "PING":
                            uart.write("PONG\n")
                            print("→ Sent: PONG\n")
                        
                        elif line == "HELLO":
                            uart.write("HELLO_FROM_PICO\n")
                            print("→ Sent: HELLO_FROM_PICO\n")
                        
                        elif line == "STOP":
                            uart.write("STOPPING\n")
                            print("→ Sent: STOPPING")
                            print("\nExiting...\n")
                            running = False
                            break
                        
                        elif line.startswith("ECHO:"):
                            response = line
                            uart.write(f"{response}\n")
                            print(f"→ Sent: {response}\n")
                        
                        else:
                            response = f"UNKNOWN:{line}"
                            uart.write(f"{response}\n")
                            print(f"→ Sent: {response}\n")
                    else:
                        print("[DEBUG] Empty line after strip")
        
        # Heartbeat cada 5 segundos
        counter += 1
        if counter >= 100:  # 100 * 50ms = 5 segundos
            uart.write("HEARTBEAT\n")
            print("→ Heartbeat")
            counter = 0
        
        utime.sleep_ms(50)
        
    except KeyboardInterrupt:
        print("\n\n✗ Interrupted by user")
        running = False
    except Exception as e:
        print(f"✗ Error: {e}")
        utime.sleep_ms(100)

print("\n" + "="*50)
print("UART TEST COMPLETED")
print("="*50 + "\n")