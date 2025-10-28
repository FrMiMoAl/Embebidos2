# ps4_remote.py
from controller import MyController  # <- renombraste el archivo

class PS4Remote:
    def __init__(self, robot_controller, interface="/dev/input/js0"):
        self.robot = robot_controller
        self.controller = MyController(interface=interface)
        self._setup_callbacks()

    def _setup_callbacks(self):
        # Ejemplos mínimos (agrega los que uses)
        self.controller.register_callback('triangle_press', self.robot.load_speed_from_file)
        self.controller.register_callback('share_press', self.robot.stop)

    def start(self):
        # Alias simple por si lo llamas directo
        self.controller.start_listening()

# Añade un wrapper en MyController para compatibilidad:
# en controller.py (antes robot_controller.py) agrega:
#   def start_listening(self, **kwargs):
#       self.listen(**kwargs)