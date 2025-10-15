# robot_controller.py
class RobotController:
    def __init__(self, serial_comm, config_file):
        self.comm = serial_comm
        self.config_file = config_file
        self.current_speed = 120

    def load_speed_from_file(self):
        try:
            with open(self.config_file, "r") as f:
                val = f.read().strip()
            spd = max(0, min(255, int(val)))
            self.current_speed = spd
            print(f"⚙️ Velocidad cargada: {self.current_speed}")
        except Exception as e:
            print(f"⚠️ No se pudo leer {self.config_file}: {e}")

    def stop(self):
        try:
            self.comm.send_instruction(0, "N")
        except Exception as e:
            print(f"⚠️ stop(): {e}")