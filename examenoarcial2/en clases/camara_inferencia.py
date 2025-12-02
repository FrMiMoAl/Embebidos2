import cv2
import torch
from torchvision import transforms
from PIL import Image
import numpy as np

# FORZAR CPU EN RASPBERRY PI
device = torch.device("cpu")
print("Usando dispositivo:", device)

from train_multilabel_cnn import MultiLabelCNN, LABEL_COLUMNS, IMAGE_SIZE

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

def predecir_en_frame(frame_bgr, umbral=0.5, umbral_minimo=0.3):
    frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
    img_pil = Image.fromarray(frame_rgb)

    img_tensor = transform(img_pil).unsqueeze(0).to(device)

    with torch.no_grad():
        outputs = model(img_tensor)
        probs = torch.sigmoid(outputs)[0]

    probs = probs.cpu().numpy()

    resultados = {}
    for clase, p in zip(LABEL_COLUMNS, probs):
        if p >= umbral:
            resultados[clase] = float(p)

    hay_deteccion = False
    if resultados:
        hay_deteccion = True
    else:
        max_prob = float(np.max(probs))
        if max_prob >= umbral_minimo:
            idx_max = int(np.argmax(probs))
            resultados[LABEL_COLUMNS[idx_max]] = max_prob
            hay_deteccion = True

    return resultados, probs, hay_deteccion


def main():
    cap = cv2.VideoCapture(2)

    if not cap.isOpened():
        print("❌ No se pudo abrir la cámara.")
        return

    print("Presiona 'q' para salir, 'r' para reiniciar contadores")

    # Contadores simples
    contadores = {}
    for label in LABEL_COLUMNS:
        contadores[label] = 0
    
    # Control para evitar contar múltiples veces el mismo objeto
    ultimo_detectado = set()

    # Parámetros ajustables
    UMBRAL_DETECCION = 0.5
    UMBRAL_MINIMO = 0.3

    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ No se pudo leer el frame.")
            break

        frame_mostrar = cv2.resize(frame, (640, 480))

        resultados, probs, hay_deteccion = predecir_en_frame(
            frame_mostrar, 
            umbral=UMBRAL_DETECCION,
            umbral_minimo=UMBRAL_MINIMO
        )

        # Actualizar contadores cuando aparece algo nuevo
        detectado_ahora = set(resultados.keys())
        nuevos = detectado_ahora - ultimo_detectado
        
        for clase in nuevos:
            contadores[clase] += 1
            print(f"✅ Detectado: {clase} (Total: {contadores[clase]})")
        
        ultimo_detectado = detectado_ahora

        # Mostrar detección actual
        y0 = 25
        dy = 25

        if hay_deteccion:
            cv2.putText(frame_mostrar, "Detectado:", (10, y0),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

            for i, (clase, p) in enumerate(resultados.items(), 1):
                txt = f"{clase}: {p*100:.1f}%"
                cv2.putText(frame_mostrar, txt, (10, y0 + i*dy),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        else:
            cv2.putText(frame_mostrar, "Sin deteccion", (10, y0),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        # Mostrar contadores en la esquina superior derecha
        y_contador = 25
        for label, count in contadores.items():
            txt = f"N {label}: {count}"
            cv2.putText(frame_mostrar, txt, (450, y_contador),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)
            y_contador += 25

        cv2.imshow("Detector con Contadores", frame_mostrar)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('r'):
            # Reiniciar contadores
            for label in LABEL_COLUMNS:
                contadores[label] = 0
            ultimo_detectado = set()
            print("🔄 Contadores reiniciados")

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()