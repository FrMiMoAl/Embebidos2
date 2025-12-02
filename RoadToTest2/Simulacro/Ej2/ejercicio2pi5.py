import serial
import time

class MarkerDetectionSystem:
    def __init__(self, port="/dev/ttyAMA0", baudrate=115200):
        # Abrir UART hacia la Pico
        self.ser = serial.Serial(port, baudrate, timeout=1)

        # Conteo de marcadores
        self.counts = {
            "red": 0,
            "blue": 0,
            "black": 0
        }

    def ask_minutes(self):
        while True:
            try:
                minutes = int(input("Ingrese cuántos MINUTOS quiere ejecutar el sistema: "))
                if minutes > 0:
                    return minutes
                else:
                    print("Por favor ingrese un número mayor que 0.")
            except ValueError:
                print("Entrada inválida. Use solo números enteros.")

    def ask_markers_for_minute(self, minute_idx):
        print(f"\n--- Minuto {minute_idx + 1} ---")
        print("Ingrese cuántos marcadores se detectaron en este minuto:")

        while True:
            try:
                r = int(input("  Rojos : "))
                a = int(input("  Azules: "))
                n = int(input("  Negros: "))
                break
            except ValueError:
                print("Entrada inválida. Use solo números enteros. Intente de nuevo.")

        self.counts["red"] += r
        self.counts["blue"] += a
        self.counts["black"] += n

    def decide_winner(self):
        # Devuelve el color con mayor conteo
        return max(self.counts, key=self.counts.get)

    def send_color_to_pico(self, color):
        # Mapear color -> código UART
        if color == "red":
            code = b'R'
        elif color == "blue":
            code = b'A'      # A de Azul
        else:  # "black"
            code = b'N'      # N de Negro

        print(f"\nEnviando por UART el código {code} para el color {color.upper()}...")
        self.ser.write(code)
        # pequeño delay por seguridad
        time.sleep(0.1)

    def run(self):
        minutes = self.ask_minutes()

        for i in range(minutes):
            self.ask_markers_for_minute(i)
            # Opcional: simular paso del tiempo
            # time.sleep(60)

        # Mostrar resultados
        print("\n===== RESULTADOS FINALES =====")
        print("Total rojos :", self.counts["red"])
        print("Total azules:", self.counts["blue"])
        print("Total negros:", self.counts["black"])

        winner = self.decide_winner()
        print(f"\nEl color más detectado fue: {winner.upper()}")

        # Enviar resultado a la Pico
        self.send_color_to_pico(winner)

        print("Listo. Puedes ver el LED encendido en la Pico.")

        # Cerrar UART
        self.ser.close()


if __name__ == "__main__":
    system = MarkerDetectionSystem()
    system.run()
