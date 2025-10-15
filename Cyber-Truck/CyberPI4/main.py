import time
import threading
from serial_comm import SerialComm
from model_a import VehicleControl  # Model A handles vehicle control and movement
#from model_b import DistanceSensor  # Model B can be extended for additional sensor tasks

def main():
    
    serial_device_pico = SerialComm("/dev/ttyS0", 115200)  

    vehicle_control = VehicleControl(serial_device_pico)

    vehicle_control.run()


if __name__ == "__main__":
    main()
