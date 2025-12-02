import pygame

class PS4Controller:
    def __init__(self, deadzone=0.1):
        """
        Initialize the PS4 controller interface.
        deadzone: minimum analog stick movement to be considered valid (0.0 - 1.0)
        """
        pygame.init()
        pygame.joystick.init()

        if pygame.joystick.get_count() == 0:
            raise RuntimeError("No controller detected! Please connect a PS4 controller.")

        self.joystick = pygame.joystick.Joystick(0)
        self.joystick.init()

        print(f"Controller connected: {self.joystick.get_name()}")

        self.deadzone = deadzone
        self.axis_data = {}
        self.button_data = {}

    def update(self):
        """ Update controller state (must be called inside a loop). """
        pygame.event.pump()

        # Read only left analog stick (LX = 0, LY = 1)
        for i in [0, 1]:
            value = self.joystick.get_axis(i)
            if abs(value) < self.deadzone:
                value = 0
            self.axis_data[i] = round(value, 3)

        # Read only main buttons (Square=2, Cross=0, Circle=1, Triangle=3)
        for i in [0, 1, 2, 3]:
            self.button_data[i] = self.joystick.get_button(i)

    def get_axis(self, index):
        """ Return axis value (LX or LY). """
        return self.axis_data.get(index, 0.0)

    def get_button(self, index):
        """ Return button pressed state (1 or 0). """
        return self.button_data.get(index, 0)
