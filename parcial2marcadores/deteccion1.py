from ultralytics import YOLO

def main():
    # Carga un modelo base chiquito (CNN pre-entrenada)
    model = YOLO("yolov8n.pt")  # n = nano, rápido y ligero

    # Entrenamiento
    model.train(
        data="data.yaml",   # nombre del yaml exportado por Roboflow
        epochs=70,          # puedes subir si tienes tiempo
        imgsz=512,          # coincide con tu resize
        batch=16,           # ajusta según tu RAM
        patience=10,        # early stopping
        project="runs_marker",   # carpeta donde guarda resultados
        name="yolov8n_markers"   # nombre del experimento
    )

    # Evalúa en el conjunto de validación/test
    metrics = model.val()
    print(metrics)

if __name__ == "__main__":
    main()