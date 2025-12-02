# archivo: resupply_system.py  (Raspberry Pi 5)
import serial
import time

class ReSupplySystem:
    def __init__(self, port="/dev/ttyAMA0", baudrate=115200):
        # UART hacia la Pico
        self.ser = serial.Serial(port, baudrate, timeout=1)

    def detectar_elementos(self):
        """
        AQUÍ irá el modelo de visión más adelante.
        Debe devolver True si hay marcadores o tablero,
        False si NO hay nada.

        De momento lo simulamos con input del usuario.
        """
        resp = input("\n¿Hay marcadores o tablero en la imagen? (s/n): ").strip().lower()
        if resp == "s":
            return True
        return False

    def enviar_comando_motor(self):
        """
        Envía un comando simple a la Pico para activar el motor.
        """
        print("Enviando comando 'M' para activar motor de reabastecimiento...")
        self.ser.write(b'M')
        time.sleep(0.1)  # pequeño delay

    def run(self):
        print("=== Sistema de Re-abastecimiento de Marcadores ===")
        print("Presiona Ctrl+C para salir.\n")

        try:
            while True:
                hay_algo = self.detectar_elementos()

                if not hay_algo:
                    print("No hay marcadores NI tablero -> activar sistema de reabastecimiento.")
                    self.enviar_comando_motor()
                else:
                    print("Sí hay elementos, no se activa el motor.")

                # simula tiempo entre chequeos (por ejemplo cada 2 s)
                time.sleep(2)

        except KeyboardInterrupt:
            print("\nPrograma terminado por el usuario.")
            self.ser.close()


if __name__ == "__main__":
    sistema = ReSupplySystem()
    sistema.run()
