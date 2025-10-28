# ps4_controller.py
import time
import pygame

class PS4Controller:
    def __init__(self, deadzone=0.1, wait_for_controller=True, retry_sec=1.0):
        """
        deadzone: 0.0..1.0
        wait_for_controller: si True, espera hasta que haya un mando
        retry_sec: cada cuántos segundos reintenta
        """
        pygame.init()
        pygame.joystick.init()

        self.deadzone = deadzone
        self.axis_data = {0: 0.0, 1: 0.0}
        self.button_data = {0: 0, 1: 0, 2: 0, 3: 0}
        self.joystick = None
        self.retry_sec = retry_sec

        if wait_for_controller:
            print("🔌 Buscando control PS4… Conéctalo y/o enciéndelo (Ctrl+C para salir).")
            while True:
                try:
                    if pygame.joystick.get_count() > 0:
                        self.joystick = pygame.joystick.Joystick(0)
                        self.joystick.init()
                        print(f"✅ Controller connected: {self.joystick.get_name()}")
                        break
                    time.sleep(self.retry_sec)
                except KeyboardInterrupt:
                    raise SystemExit
        else:
            # Modo no bloqueante: intenta 1 vez y continúa (dummy si no hay mando)
            if pygame.joystick.get_count() > 0:
                self.joystick = pygame.joystick.Joystick(0)
                self.joystick.init()
                print(f"✅ Controller connected: {self.joystick.get_name()}")
            else:
                print("⚠️ No controller detected. Running in dummy mode (axes=0, buttons=0).")

    def _try_reconnect(self):
        """Si el mando se desconecta, intenta reconectar sin romper el programa."""
        if self.joystick is None and pygame.joystick.get_count() > 0:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()
            print(f"🔁 Reconnected: {self.joystick.get_name()}")

    def update(self):
        """Actualizar estado (llamar en un loop)."""
        pygame.event.pump()
        self._try_reconnect()

        if self.joystick is None:
            # dummy: deja todo en cero
            self.axis_data[0] = 0.0
            self.axis_data[1] = 0.0
            self.button_data[0] = 0
            self.button_data[1] = 0
            self.button_data[2] = 0
            self.button_data[3] = 0
            return

        # Ejes: LX=0, LY=1
        for i in (0, 1):
            v = self.joystick.get_axis(i)
            if abs(v) < self.deadzone:
                v = 0.0
            self.axis_data[i] = round(v, 3)

        # Botones: Cross=0, Circle=1, Square=2, Triangle=3
        for i in (0, 1, 2, 3):
            self.button_data[i] = self.joystick.get_button(i)

    def get_axis(self, index):
        return self.axis_data.get(index, 0.0)

    def get_button(self, index):
        return self.button_data.get(index, 0)
