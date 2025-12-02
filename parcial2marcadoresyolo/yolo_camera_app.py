# yolo_camera_app.py
import cv2
import time

from camera_module import video_Capture
from marker_detector import MarkerDetector

MODEL_PATH   = "runs_marker/yolov8n_markers8/weights/best.pt"
CONF_TH      = 0.5
CAMERA_INDEX = 0
WINDOW_NAME  = "markers"


class YoloVideoCapture(video_Capture):
    """
    Extiende tu video_Capture para meter el detector en el loop.
    """
    def __init__(self, camera, detector: MarkerDetector) -> None:
        super().__init__(camera)
        self.detector = detector

    def camera_visualization(self):
        prev_time = time.time()

        while self.displayed:
            check, frame = self.camera.read()
            if not check:
                print("[!] No se pudo leer frame de la cámara")
                break

            # Procesar frame con YOLO
            frame, n_dets = self.detector.process_frame(frame)

            # Calcular FPS
            now = time.time()
            fps = 1.0 / (now - prev_time) if now > prev_time else 0.0
            prev_time = now

            # Mensaje si no detecta nada
            if n_dets == 0:
                cv2.putText(
                    frame,
                    "No object",
                    (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 0, 255),
                    2,
                    cv2.LINE_AA,
                )

            # FPS
            cv2.putText(
                frame,
                f"FPS: {fps:.1f}",
                (20, 80),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2,
                cv2.LINE_AA,
            )

            # Mostrar
            cv2.imshow(WINDOW_NAME, frame)

            key = cv2.waitKey(1) & 0xFF
            if key == 27 or key == ord("q"):
                self.stop_display()

            # Si el usuario cierra la ventana con la X
            if cv2.getWindowProperty(WINDOW_NAME, cv2.WND_PROP_VISIBLE) < 1:
                self.stop_display()

        # Al salir
        self.camera.release()
        cv2.destroyAllWindows()


def main():
    cam = cv2.VideoCapture(CAMERA_INDEX)
    if not cam.isOpened():
        print("[!] No se pudo abrir la cámara")
        return

    detector = MarkerDetector(MODEL_PATH, conf_th=CONF_TH)
    yolo_cam = YoloVideoCapture(cam, detector)
    yolo_cam.display_camera()


if __name__ == "__main__":
    main()