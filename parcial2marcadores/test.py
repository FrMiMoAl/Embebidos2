from ultralytics import YOLO
import cv2
import time

# ================== CONFIGURACIÓN ==================
MODEL_PATH   = "runs_marker/yolov8n_markers7/weights/best.pt"
CONF_TH      = 0.5         # Umbral de confianza
CAMERA_INDEX = 2           # Cambia esto en la RPi si usas otra cámara
WINDOW_NAME  = "markers"   # Nombre de la ventana
# ===================================================


def draw_detections(frame, boxes, class_names):
    """
    Dibuja los bounding boxes y etiquetas sobre el frame.
    """
    for box in boxes:
        # Coordenadas del bounding box
        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)

        # Clase y confianza
        cls_id = int(box.cls[0])
        conf   = float(box.conf[0])
        label  = f"{class_names[cls_id]} {conf:.2f}"

        # Dibujar rectángulo
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

        # Fondo para el texto
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

        # Texto
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


def main() -> None:
    # Cargar modelo
    print("[i] Cargando modelo...")
    model = YOLO(MODEL_PATH)

    # Abrir cámara
    cap = cv2.VideoCapture(CAMERA_INDEX)
    if not cap.isOpened():
        print("[!] No se pudo abrir la cámara")
        return

    prev_time = time.time()

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("[!] No se pudo leer frame de la cámara")
                break

            # Inferencia
            results = model(frame, conf=CONF_TH, verbose=False)
            r = results[0]

            boxes = r.boxes
            if len(boxes) == 0:
                text = "No object"
            else:
                text = ""  # no usamos texto global si ya dibujamos cajas
                draw_detections(frame, boxes, model.names)

            # Calcular FPS
            now = time.time()
            fps = 1.0 / (now - prev_time) if now > prev_time else 0.0
            prev_time = now

            # Overlay de info (No object / FPS)
            if len(boxes) == 0:
                cv2.putText(
                    frame,
                    text,
                    (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 0, 255),
                    2,
                    cv2.LINE_AA,
                )

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

            # Salir con ESC o 'q'
            key = cv2.waitKey(1) & 0xFF
            if key == 27 or key == ord("q"):
                break

            # Si la ventana se cierra manualmente
            if cv2.getWindowProperty(WINDOW_NAME, cv2.WND_PROP_VISIBLE) < 1:
                break

    except KeyboardInterrupt:
        print("\n[i] Interrumpido por el usuario (Ctrl+C)")

    finally:
        cap.release()
        cv2.destroyAllWindows()
        print("[i] Cámara liberada y ventanas cerradas.")


if __name__ == "__main__":
    main()