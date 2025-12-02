import time
from ps4_controller import PS4Controller

controller = PS4Controller(deadzone=0.15)

while True:
    controller.update()

    # Left joystick
    left_x = controller.get_axis(0)
    left_y = controller.get_axis(1)

    # Buttons
    cross = controller.get_button(0)
    circle = controller.get_button(1)
    triangle = controller.get_button(2)
    square = controller.get_button(3)

          
    print(f"LX:{left_x:.2f}  LY:{left_y:.2f}  |  X:{cross}  Circle:{circle}  Square:{square}  Triangle:{triangle}")

    time.sleep(0.05)
