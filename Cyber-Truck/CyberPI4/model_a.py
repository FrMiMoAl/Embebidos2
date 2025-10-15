# model_a.py (Raspberry Pi 4)
import time
from serial_comm import SerialComm

class VehicleControl:
    def __init__(self, serial_device):
        self.serial_device = serial_device

    def send_command(self, pwm1, pwm2, servo_angle):
        # Sends the movement command to the Pi Pico (e.g., move forward, rotate, etc.)
        command = f"{pwm1},{pwm2},{servo_angle}"
        self.serial_device.send(command)

    def receive_distance(self):
        # Receives distance data from Pi Pico over UART
        distance = self.serial_device.receive()
        try:
            return float(distance)
        except ValueError:
            return None  # Return None if the distance is not valid

    def move_forward(self):
        # Command to move forward
        self.send_command(50, 50, 50)
        
    def stop_movement(self):
        # Command to stop movement
        self.send_command(0, 0, 50)  # pwm1, pwm2 = 0 (stop) and servo angle = 50

    def rotate_180(self):
        # Command to rotate 180 degrees
        self.send_command(0, 0, 30) 
        time.sleep(1)
        self.send_command(-50, -50, 30)  
        time.sleep(3)  # Allow time to rotate
        self.stop_movement()
        
        self.send_command(0, 0, 70)
        time.sleep(1)
        self.send_command(50, 50, 70)
        time.sleep(3)  # Allow time for the turn to complete
        self.stop_movement()

    def rotate_left(self, degrees):
        # Command to rotate left by a certain number of degrees
        current_angle = 50
        target_angle = current_angle - degrees
        if target_angle < 30:
            target_angle = 30
        self.send_command(0, 0, target_angle)
        time.sleep(1)

    def rotate_right(self, degrees):
        # Command to rotate right by a certain number of degrees
        current_angle = 50
        target_angle = current_angle + degrees
        if target_angle > 70:
            target_angle = 70
        self.send_command(0, 0, target_angle)
        time.sleep(1)

    def run(self):
        try:
            while True:
                distance = self.receive_distance()
                if distance is not None:
                    print(f"Received distance: {distance} cm")

                    if distance < 30:  # If an object is detected within 10 cm
                        print("Object detected, rotating 180°")
                        self.rotate_180()
                    else:
                        print("No object detected, moving forward")
                        self.move_forward()

                    time.sleep(0.1)
        except KeyboardInterrupt:
            print("Program terminated")
