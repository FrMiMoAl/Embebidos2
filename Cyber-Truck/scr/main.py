import sys
import os
import time
from pathlib import Path
import threading

# Ensure local vendored packages in ./libs are importable (pyserial, pyPS4Controller, etc.)
ROOT = os.path.dirname(__file__)
LIBS_DIR = os.path.join(ROOT, "libs")
if os.path.isdir(LIBS_DIR) and LIBS_DIR not in sys.path:
    sys.path.insert(0, LIBS_DIR)

try:
    import serial
except Exception as e:
    print("\u26a0\ufe0f Warning: could not import 'serial' (pyserial).",
          "If you don't have pyserial installed system-wide,",
          "ensure the ./libs folder contains pyserial or install it with pip.")
    raise

from controller import MyController

PORT = "/dev/serial0"
BAUD = 115200
FILE = Path("/home/raspberry/Documents/puerto/control.txt")

# --- FUNCIONES DE UTILIDAD ---

def clamp_speed(v):
    try:
        v = float(v)
    except:
        return 80  # default
    v = int(round(v))
    if v < 0: v = 0
    if v > 100: v = 100
    return v

def send_speed(ser, speed):
    speed = clamp_speed(speed)
    msg = f"S={speed}\n".encode("utf-8")
    ser.write(msg)
    ser.flush()
    # print(">> SPEED:", speed) # Comentado para reducir ruido en el loop continuo

VALID_SEL = {"A", "B", "X", "Y", "N"}
def send_sel(ser, sel):
    """Envía selección A/B/X/Y/N (una letra y \n)."""
    sel = (sel or "N").strip()[:1].upper()
    if sel not in VALID_SEL:
        sel = "N"
    ser.write(f"{sel}\n".encode("utf-8"))
    ser.flush()
    # print(">> SEL:", sel) # Comentado para reducir ruido en el loop continuo

def enviarInfo(ser, velocidad, instruccion):
    send_speed(ser, velocidad)
    time.sleep(0.02)
    send_sel(ser, instruccion)

def serial_reader_thread(ser):
    while True:
        try:
            data = ser.readline()
            if data:
                print("<<", data.decode(errors="ignore").strip())
        except Exception as e:
            print("Serial read error:", e)
            time.sleep(0.2)

def read_speed_from_file():
    # Usaremos esta velocidad como la máxima base permitida (0-100)
    if FILE.exists():
        return clamp_speed(FILE.read_text().strip())
    return 80

# --- LÓGICA DE CONTROL CONTINUO (LX y LY) ---

DEADZONE = 5000 # Umbral para considerar que el joystick se ha movido (ej. 5000/32767 ≈ 15%)
MAX_JOY_VAL = 32767.0
MAX_VELOCIDAD_BASE = read_speed_from_file() # Velocidad máxima del archivo

def calcular_velocidad(valor_y):
    """
    Convierte el valor analógico del eje Y (-32767..32767) 
    a velocidad (0..MAX_VELOCIDAD_BASE) por magnitud.
    """
    mag_y = abs(valor_y)
    
    # Aplicar zona muerta
    if mag_y < DEADZONE:
        return 0
        
    # Normalizar la velocidad de la zona muerta al máximo
    velocidad_relativa = (mag_y - DEADZONE) / (MAX_JOY_VAL - DEADZONE)
    
    # Multiplicar por la velocidad máxima base
    velocidad = int(round(MAX_VELOCIDAD_BASE * velocidad_relativa))
    
    return clamp_speed(velocidad)

def calcular_instruccion(valor_x, valor_y):
    """
    Calcula la instrucción (X/Y/A/B/N) basada en X y Y.
    
    - Y < 0: Adelante (X)
    - Y > 0: Atrás (Y)
    - X < 0: Gira Izquierda (A o B, dependiendo de la convención de tu robot)
    - X > 0: Gira Derecha (A o B, dependiendo de la convención de tu robot)
    - Cerca de 0: Parada (N)
    """
    
    # Si la velocidad es 0, la instrucción debe ser N
    if abs(valor_y) < DEADZONE and abs(valor_x) < DEADZONE:
        return "N"
        
    # Priorizar la dirección principal (Y)
    if valor_y < -DEADZONE:
        # Movimiento Adelante
        # Podrías implementar giro más complejo aquí (ej. control diferencial)
        return "X" # Ambos adelante
    elif valor_y > DEADZONE:
        # Movimiento Atrás
        return "Y" # Ambos atrás
    elif abs(valor_x) > DEADZONE:
        # Movimiento lateral (giro puro)
        if valor_x < 0:
            # Giro a la izquierda (solo motor A) - Convención asumida para giro.
            return "A" 
        else:
            # Giro a la derecha (solo motor B) - Convención asumida para giro.
            return "B" 
            
    return "N"

# --- MAIN CONTROLLER LOGIC ---

def cb_move_left_joystick(x, y):
    """
    Callback llamado continuamente por pyPS4Controller con los valores (lx, ly).
    """
    # Los valores son típicamente enteros de -32767 a 32767
    
    # 1. Calcular Velocidad (basado en Y)
    velocidad = calcular_velocidad(y)
    
    # 2. Calcular Instrucción (basado en X e Y)
    instruccion = calcular_instruccion(x, y)
    
    # 3. Enviar Comando
    if velocidad > 0 or instruccion != "N":
        # Solo enviar si hay movimiento o una instrucción específica (para giros puros)
        enviarInfo(controller.ser, velocidad, instruccion)
        print(f"JOY ({x},{y}) → V:{velocidad} I:{instruccion}", end='\r')
    elif instruccion == "N" and velocidad == 0:
        # Esto asegura que la parada se envíe una vez al volver al centro
        if not hasattr(controller, '_stopped') or not controller._stopped:
            enviarInfo(controller.ser, 0, "N")
            controller._stopped = True
            print("🛑 Joystick centrado. Motores detenidos.   ")
    
# --- OTROS CALLBACKS (R2) ---

def cb_r2_press(value):
    velocidad_max = 100
    # Al presionar R2, sobrescribir la dirección a X (adelante) con velocidad max
    enviarInfo(controller.ser, velocidad_max, "X") 
    print(f"\n🚀 R2 presionado → velocidad {velocidad_max}%")
    controller._stopped = False # Reset flag de parada

def cb_r2_release():
    # Al soltar R2, detener (0 velocidad y N instrucción)
    enviarInfo(controller.ser, 0, "N") 
    print("🛑 R2 liberado. Deteniendo motores.")
    controller._stopped = True # Establecer flag de parada

# --- FUNCIÓN PRINCIPAL ---

def main():
    global MAX_VELOCIDAD_BASE # Asegurar que la función use el valor global inicializado
    
    ser = serial.Serial(PORT, BAUD, timeout=0.2)
    # Adjuntar el objeto serial al controlador para usarlo en los callbacks
    controller = MyController(interface="/dev/input/js0", connecting_using_ds4drv=False)
    controller.ser = ser
    controller._stopped = False # Flag para rastrear el estado de detención

    threading.Thread(target=serial_reader_thread, args=(ser,), daemon=True).start()

    # Parada inicial para asegurar que los motores no se muevan al arrancar
    enviarInfo(ser, 0, "N")
    print("✅ Estado inicial: Motores detenidos. Esperando entrada del mando...")

    # --- Registro de Callbacks ---

    # Callback para movimiento continuo del joystick izquierdo (L3)
    controller.register_callback('on_move_left_joystick', cb_move_left_joystick)

    # Callbacks para R2
    controller.register_callback('r2_press', cb_r2_press)
    controller.register_callback('r2_release', cb_r2_release)

    print("🎮 Escuchando mando PS4…")
    try:
        controller.start_listening()  # bloqueante
    except KeyboardInterrupt:
        print("\nSaliendo…")
    finally:
        # Aseguramos parada al salir
        print("🔌 Enviando señal de parada final...")
        enviarInfo(ser, 0, "N")
        ser.close()
        print("Proceso finalizado.")

if __name__ == "__main__":
    main()