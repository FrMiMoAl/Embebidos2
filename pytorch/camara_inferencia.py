import cv2
import torch
from torchvision import transforms
from PIL import Image
import numpy as np

# Importamos definiciones del script de entrenamiento (no entrena porque está dentro de main())
from train_multilabel_cnn import MultiLabelCNN, LABEL_COLUMNS, IMAGE_SIZE, device


# ============================
# 1. Cargar modelo entrenado
# ============================

model = MultiLabelCNN(num_outputs=len(LABEL_COLUMNS)).to(device)
model.load_state_dict(torch.load("mejor_modelo_multilabel.pth", map_location=device))
model.eval()
print("✅ Modelo cargado correctamente en", device)

# Transformación igual que en validación
transform = transforms.Compose([
    transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.5, 0.5, 0.5],
                         std=[0.5, 0.5, 0.5])
])


# ============================
# 2. Función de inferencia en un frame
# ============================

def predecir_en_frame(frame_bgr, umbral=0.5):
    """
    Recibe un frame en BGR (como viene de OpenCV),
    devuelve diccionario {clase: probabilidad} para las que superan el umbral.
    """
    # BGR -> RGB
    frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
    img_pil = Image.fromarray(frame_rgb)

    # Transformar
    img_tensor = transform(img_pil).unsqueeze(0).to(device)  # [1,3,H,W]

    with torch.no_grad():
        outputs = model(img_tensor)          # [1, 4]
        probs = torch.sigmoid(outputs)[0]    # [4]

    probs = probs.cpu().numpy()

    resultados = {}
    for clase, p in zip(LABEL_COLUMNS, probs):
        if p >= umbral:
            resultados[clase] = float(p)

    # Si ninguna supera el umbral, mostramos la más alta igualmente
    if not resultados:
        idx_max = int(np.argmax(probs))
        resultados[LABEL_COLUMNS[idx_max]] = float(probs[idx_max])

    return resultados, probs


# ============================
# 3. Loop principal de cámara
# ============================

def main():
    # 0 suele ser la webcam integrada; si no funciona prueba 1, 2, etc.
    cap = cv2.VideoCapture(1)

    if not cap.isOpened():
        print("❌ No se pudo abrir la cámara.")
        return

    print("Presiona 'q' para salir.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ No se pudo leer frame de la cámara.")
            break

        # Opcional: redimensionar el frame mostrado (no afecta a la predicción)
        frame_mostrar = cv2.resize(frame, (640, 480))

        # Hacer predicción
        resultados, probs = predecir_en_frame(frame_mostrar, umbral=0.5)

        # Dibujar texto en la imagen
        y0 = 25
        dy = 25

        # Línea principal
        texto_principal = "Detectado:"
        cv2.putText(frame_mostrar, texto_principal, (10, y0),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

        # Cada clase detectada
        for i, (clase, p) in enumerate(resultados.items(), start=1):
            txt = f"{clase}: {p*100:.1f}%"
            cv2.putText(frame_mostrar, txt, (10, y0 + i*dy),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        # Mostrar ventana
        cv2.imshow("Camara - Modelo Multilabel", frame_mostrar)

        # Salir con 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
