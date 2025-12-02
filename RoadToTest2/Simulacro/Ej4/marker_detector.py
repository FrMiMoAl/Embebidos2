# marker_detector.py
from ultralytics import YOLO
import cv2


class MarkerDetector:
    def __init__(self, model_path: str, conf_th: float = 0.5):
        print(f"[i] Cargando modelo YOLO desde: {model_path}")
        self.model = YOLO(model_path)
        self.conf_th = conf_th

    def _draw_detections(self, frame, boxes):
        """
        Dibuja bounding boxes y etiquetas sobre el frame.
        """
        for box in boxes:
            # Coordenadas del bounding box
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)

            # Clase y confianza
            cls_id = int(box.cls[0])
            conf   = float(box.conf[0])
            label  = f"{self.model.names[cls_id]} {conf:.2f}"

            # Rectángulo
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

            # Fondo del texto
            (tw, th), baseline = cv2.getTextSize(
                label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1
            )
            y_text = max(y1 - th - baseline, 0)
            cv2.rectangle(
                frame,
                (x1, y_text),
                (x1 + tw, y_text + th + baseline),
                (0, 255, 0),
                -1,
            )

            # Texto encima del rectángulo
            cv2.putText(
                frame,
                label,
                (x1, y_text + th),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 0, 0),
                1,
                cv2.LINE_AA,
            )

    def process_frame(self, frame):
        """
        Recibe un frame, corre YOLO, dibuja todo y devuelve:
        - frame_annotated
        - num_detecciones
        """
        results = self.model(frame, conf=self.conf_th, verbose=False)
        r = results[0]
        boxes = r.boxes

        if len(boxes) > 0:
            self._draw_detections(frame, boxes)

        return frame, len(boxes)