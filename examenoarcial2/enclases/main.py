import cv2
from settings import Config
from camera_module import CameraModule
from detector_module import DetectorModule
from counter_module import CounterModule
from uart_module import UARTModule


class SistemaDeteccion:
    def __init__(self):
        self.config = Config()

        self.camera = CameraModule(
            camera_index=self.config.CAMERA_INDEX,
            width=self.config.CAMERA_WIDTH,
            height=self.config.CAMERA_HEIGHT
        )

        self.detector = DetectorModule(
            model_path=self.config.MODEL_PATH,
            label_columns=self.config.LABEL_COLUMNS,
            image_size=self.config.IMAGE_SIZE,
            device=self.config.DEVICE
        )

        self.counter = CounterModule(
            label_columns=self.config.LABEL_COLUMNS
        )

        self.uart = UARTModule(
            port=self.config.UART_PORT,
            baudrate=self.config.UART_BAUDRATE,
            timeout=self.config.UART_TIMEOUT
        )

        self.running = False

    def on_uart_receive(self, data):
        data = data.strip().upper()

        if data == "RESET":
            self.counter.reset()
            self.uart.send("OK:RESET")

        elif data == "GET_COUNTS":
            counts_str = self.counter.get_formatted_counts()
            self.uart.send(f"COUNTS:{counts_str}")

        elif data == "PING":
            self.uart.send("PONG")

        else:
            print(f"Comando desconocido: {data}")
            self.uart.send("ERROR:UNKNOWN_CMD")

    def draw_interface(self, frame, detecciones, hay_deteccion):
        y0 = 25
        dy = 25

        if hay_deteccion:
            cv2.putText(
                frame,
                "Detectado:",
                (10, y0),
                self.config.FONT,
                0.7,
                (0, 255, 255),
                2
            )

            for i, (clase, prob) in enumerate(detecciones.items(), 1):
                txt = f"{clase}: {prob*100:.1f}%"
                cv2.putText(
                    frame,
                    txt,
                    (10, y0 + i * dy),
                    self.config.FONT,
                    self.config.FONT_SCALE,
                    (0, 255, 0),
                    self.config.FONT_THICKNESS
                )
        else:
            cv2.putText(
                frame,
                "Sin deteccion",
                (10, y0),
                self.config.FONT,
                0.7,
                (0, 0, 255),
                2
            )

        contadores = self.counter.get_counts()
        y_contador = 25

        for label, count in contadores.items():
            txt = f"N{label}: {count}"
            cv2.putText(
                frame,
                txt,
                (450, y_contador),
                self.config.FONT,
                0.5,
                (255, 255, 0),
                2
            )
            y_contador += 25

        cv2.putText(
            frame,
            "Q:Salir | R:Reset | S:Enviar",
            (10, frame.shape[0] - 10),
            self.config.FONT,
            0.4,
            (200, 200, 200),
            1
        )

        return frame

    def start(self, use_uart=True):
        print("INICIANDO")

        if not self.camera.open():
            return

        uart_enabled = False
        if use_uart:
            if self.uart.connect():
                uart_enabled = True
            else:
                print("Continuando sin UART...")

        print("\nSistema listo")
        print("Controles:")
        print("  Q - Salir")
        print("  R - Reiniciar contadores")
        if uart_enabled:
            print("  S - Enviar contadores por UART")

        self.running = True

        try:
            while self.running:
                ret, frame = self.camera.read_frame()
                if not ret:
                    print("Error al leer frame")
                    break

                detecciones, probs, hay_deteccion = self.detector.detect(
                    frame,
                    umbral=self.config.UMBRAL_DETECCION,
                    umbral_minimo=self.config.UMBRAL_MINIMO
                )

                self.counter.update(detecciones)

                if uart_enabled:
                    data = self.uart.receive_line()
                    if data is not None:
                        self.on_uart_receive(data)

                frame = self.draw_interface(frame, detecciones, hay_deteccion)

                cv2.imshow("Sistema de Deteccion", frame)

                key = cv2.waitKey(1) & 0xFF

                if key == ord('q'):
                    self.running = False
                    print("\nSaliendo...")

                elif key == ord('r'):
                    self.counter.reset()

                elif key == ord('s') and uart_enabled:
                    counts_str = self.counter.get_formatted_counts()
                    self.uart.send(f"COUNTS:{counts_str}")

        except KeyboardInterrupt:
            print("\nInterrupcion por teclado")

        finally:
            self.stop()

    def stop(self):
        print("\nDeteniendo sistema...")
        self.camera.close()
        self.uart.disconnect()
        cv2.destroyAllWindows()
        print("Sistema detenido correctamente")


if __name__ == "__main__":
    sistema = SistemaDeteccion()
    sistema.start(use_uart=True)
