#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time
import threading

from ps4_controller import PS4Controller
from serial_comm import SerialComm

from model_a import ModelA
from model_b import ModelB
from model_c import ModelC

SERIAL_PORT = "/dev/serial0"
SERIAL_BAUD = 115200
SERVO_CENTER = 50

class Supervisor:

    def __init__(self, wait_for_controller=True):
        # UART
        self.ser = SerialComm(port=SERIAL_PORT, baudrate=SERIAL_BAUD)

        self.ps4 = PS4Controller(deadzone=0.15, wait_for_controller=wait_for_controller)

        self.active = None
        self.active_name = "STOP"
        self.last_btn = {0:0, 1:0, 2:0, 3:0}

    def _stop_active(self):
        if self.active and self.active.is_alive():
            self.active.stop()
            self.active.join(timeout=1.0)
        self.active = None
        self.active_name = "STOP"

    def _start_model(self, name: str):
        self._stop_active()

        if name == "A":
            self.active = ModelA(self.ser)
        elif name == "B":
            self.active = ModelB(self.ser)
        elif name == "C":
            self.active = ModelC(self.ser, self.ps4)
        else:
            self.active = None  # STOP

        self.active_name = name

        if self.active:
            print(f">>> CAMBIO A MODEL {name}")
            self.active.start()
        else:
            print(">>> STOP / MENÚ")
            # STOP seguro: motores 0 y servo centrado
            self.ser.send(f"0,0,{SERVO_CENTER}")

    def loop(self, start_mode="C"):
        print("\n=== Controles de modo (PS4) ===")
        if start_mode in ("A", "B", "C"): 
            self._start_model(start_mode)
        else:
            self._start_model("STOP")

        try:
            while True:
                self.ps4.update()

                for idx in (0, 1, 2, 3):  
                    cur = self.ps4.get_button(idx)
                    if cur == 1 and self.last_btn[idx] == 0:
                        if idx == 3:   
                            self._start_model("A")
                        elif idx == 1: 
                            self._start_model("B")
                        elif idx == 0: 
                            self._start_model("C")
                        elif idx == 2:  
                            self._start_model("STOP")
                    self.last_btn[idx] = cur

                time.sleep(0.02)  

        except KeyboardInterrupt:
            print("\n[Supervisor] Saliendo...")
        finally:
            self._stop_active()
            self.ser.close()


if __name__ == "__main__":
    Supervisor(wait_for_controller=True).loop(start_mode="C")