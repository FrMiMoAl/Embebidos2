import tkinter as tk
from tkinter import ttk
import cv2
from abc import ABC, abstractmethod
import threading
#import pyperclip  # asegúrate de tenerlo instalado: pip install pyperclip


class video_capture_abs(ABC):
    @abstractmethod
    def display_camera(self):
        pass

    @abstractmethod
    def stop_display(self):
        pass

    @abstractmethod
    def camera_visualization(self):
        pass



class video_Capture(video_capture_abs):
    def __init__(self, camera, width=640, height=480, fps=30) -> None:
        self.camera = camera
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        self.camera.set(cv2.CAP_PROP_FPS, fps)
        self.displayed = False

    def display_camera(self):
        self.displayed = True
        self.camera_visualization()

    def stop_display(self):
        self.displayed = False
        self.camera.release()
        cv2.destroyAllWindows()

    def camera_visualization(self):
        while self.displayed:
            check, frame = self.camera.read()

            if check:
                HSV = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
                try:
                    inf = (H1.variable_principal.get(), S1.variable_principal.get(), V1.variable_principal.get())
                    sup = (H2.variable_principal.get(), S2.variable_principal.get(), V2.variable_principal.get())
                except Exception:
                    continue

                mask = cv2.inRange(HSV, inf, sup)
                result = cv2.bitwise_and(frame, frame, mask=mask)

                # Encontrar contornos
                contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
                cv2.drawContours(frame, contours, -1, (0, 255, 0), 2)

                cv2.imshow("Original + Contours", frame)
                cv2.imshow("Mask Only", mask)

            key = cv2.waitKey(1)
            if key == ord('q') or key == ord('Q'):
                self.stop_display()
                break


class ModificadorVariablesApp:
    def __init__(self, master, nombre):
        self.master = master
        self.nombre = nombre

        self.marco_principal = ttk.Frame(master)
        self.marco_principal.pack()

        ttk.Label(self.marco_principal, text=nombre).pack(side="left", padx=5)

        self.variable_principal = tk.IntVar()

        self.barra_deslizamiento = ttk.Scale(self.marco_principal, variable=self.variable_principal, from_=0, to=255,
                                             orient="horizontal", command=self.actualizar_entrada)
        self.barra_deslizamiento.pack(side="left", padx=5)

        self.entrada_texto = ttk.Entry(self.marco_principal, textvariable=self.variable_principal, width=5)
        self.entrada_texto.pack(side="left", padx=5)
        self.entrada_texto.bind("<Return>", self.actualizar_deslizamiento)

    def actualizar_entrada(self, value):
        try:
            self.variable_principal.set(int(float(value)))
        except ValueError:
            pass

    def actualizar_deslizamiento(self, event):
        try:
            value = int(self.entrada_texto.get())
            self.barra_deslizamiento.set(value)
        except ValueError:
            pass


def copiar_al_portapapeles():
    lower = (H1.variable_principal.get(), S1.variable_principal.get(), V1.variable_principal.get())
    upper = (H2.variable_principal.get(), S2.variable_principal.get(), V2.variable_principal.get())

    texto = f"lower_hsv = {lower}\nupper_hsv = {upper}"
    #pyperclip.copy(texto)


def iniciar_aplicacion():
    root = tk.Tk()
    root.title("HSV Settings")

    global H1, S1, V1, H2, S2, V2
    ttk.Label(root, text="Low Values").pack()
    H1 = ModificadorVariablesApp(root, "H Low")
    S1 = ModificadorVariablesApp(root, "S Low")
    V1 = ModificadorVariablesApp(root, "V Low")

    ttk.Label(root, text="High Values").pack()
    H2 = ModificadorVariablesApp(root, "H High")
    S2 = ModificadorVariablesApp(root, "S High")
    V2 = ModificadorVariablesApp(root, "V High")

    # Botón para copiar valores HSV
    copiar_btn = ttk.Button(root, text="Copi HSV values", command=copiar_al_portapapeles)
    copiar_btn.pack(pady=10)

    root.mainloop()


def iniciar_opencv():
    video = cv2.VideoCapture(0)
    video_object = video_Capture(video, width=640, height=480, fps=30)
    video_object.display_camera()


if __name__ == "__main__":
    thread_tkinter = threading.Thread(target=iniciar_aplicacion)
    thread_opencv = threading.Thread(target=iniciar_opencv)

    thread_tkinter.start()
    thread_opencv.start()

    thread_tkinter.join()
    thread_opencv.join()