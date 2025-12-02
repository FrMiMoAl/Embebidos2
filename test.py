"""
Detección simple de marcadores y borrador con webcam
Colores: Rojo, Negro, Azul y Borrador
"""

import torch
import torchvision
from torchvision.models.detection import fasterrcnn_resnet50_fpn
from torchvision.models.detection.faster_rcnn import FastRCNNPredictor
import cv2
import json

# ==================== Cargar Modelo ====================
def cargar_modelo():
    """Carga el modelo entrenado"""
    print("Cargando modelo...")
    
    # Cargar mapa de etiquetas
    with open('label_map.json', 'r') as f:
        label_map = json.load(f)
    
    num_classes = len(label_map)
    
    # Crear modelo
    model = fasterrcnn_resnet50_fpn(pretrained=False)
    in_features = model.roi_heads.box_predictor.cls_score.in_features
    model.roi_heads.box_predictor = FastRCNNPredictor(in_features, num_classes + 1)
    
    # Cargar pesos
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model.load_state_dict(torch.load('marker_detector_final.pth', map_location=device))
    model.to(device)
    model.eval()
    
    # Crear diccionario inverso (id -> nombre)
    id_to_name = {v: k for k, v in label_map.items()}
    
    print(f"✓ Modelo cargado en {device}")
    print(f"✓ Clases: {list(label_map.keys())}")
    
    return model, id_to_name, device

# ==================== Detectar ====================
@torch.no_grad()
def detectar(model, frame, device):
    """Detecta objetos en el frame"""
    # BGR a RGB
    img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Convertir a tensor
    img_tensor = torch.from_numpy(img_rgb).permute(2, 0, 1).float() / 255.0
    img_tensor = img_tensor.to(device)
    
    # Inferencia
    predictions = model([img_tensor])[0]
    
    # Filtrar por confianza
    mask = predictions['scores'] > 0.1
    boxes = predictions['boxes'][mask].cpu().numpy()
    labels = predictions['labels'][mask].cpu().numpy()
    scores = predictions['scores'][mask].cpu().numpy()
    
    return boxes, labels, scores

# ==================== Main ====================
def main():
    print("=" * 60)
    print("Detección de Marcadores - Webcam")
    print("=" * 60)
    
    # Cargar modelo
    model, id_to_name, device = cargar_modelo()
    
    # Abrir webcam
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Error: No se pudo abrir la webcam")
        return
    
    # Configurar resolución 512x512
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 512)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 512)
    
    print("\n✓ Webcam iniciada (512x512)")
    print("Presiona 'q' para salir")
    print("Presiona 's' para guardar captura")
    print("=" * 60)
    
    # Colores para cada objeto (BGR)
    colores = {
        'marcador rojo': (0, 0, 255),      # Rojo
        'marcador negro': (50, 50, 50),    # Gris oscuro
        'marcador azul': (255, 0, 0),      # Azul
        'borrador': (0, 255, 0)            # Verde
    }
    
    contador = 0
    
    while True:
        # Capturar frame
        ret, frame = cap.read()
        if not ret:
            print("Error al capturar frame")
            break
        
        # Redimensionar a 512x512 si es necesario
        if frame.shape[0] != 512 or frame.shape[1] != 512:
            frame = cv2.resize(frame, (512, 512))
        
        # Detectar objetos
        boxes, labels, scores = detectar(model, frame, device)
        
        # Dibujar resultados
        if len(boxes) == 0:
            # No hay objetos
            cv2.putText(frame, "No object", (20, 50),
                       cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)
        else:
            # Dibujar cada detección
            for box, label, score in zip(boxes, labels, scores):
                nombre = id_to_name.get(label, 'desconocido')
                color = colores.get(nombre, (255, 255, 255))
                
                # Coordenadas del cuadro
                x1, y1, x2, y2 = int(box[0]), int(box[1]), int(box[2]), int(box[3])
                
                # Dibujar cuadro
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 3)
                
                # Preparar texto
                texto = f"{nombre}: {score:.2f}"
                
                # Fondo para el texto
                (ancho_texto, alto_texto), _ = cv2.getTextSize(
                    texto, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2
                )
                cv2.rectangle(frame,
                            (x1, y1 - alto_texto - 10),
                            (x1 + ancho_texto + 10, y1),
                            color, -1)
                
                # Texto
                cv2.putText(frame, texto, (x1 + 5, y1 - 5),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Contador de objetos detectados
        if len(boxes) > 0:
            texto_contador = f"Detectados: {len(boxes)}"
            cv2.putText(frame, texto_contador, (20, frame.shape[0] - 20),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        
        # Mostrar frame
        cv2.imshow('Deteccion de Marcadores', frame)
        
        # Manejar teclas
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            print("\nSaliendo...")
            break
        elif key == ord('s'):
            nombre_archivo = f"captura_{contador:04d}.jpg"
            cv2.imwrite(nombre_archivo, frame)
            print(f"✓ Guardado: {nombre_archivo}")
            contador += 1
    
    # Limpiar
    cap.release()
    cv2.destroyAllWindows()
    print("✓ Webcam cerrada")

if __name__ == "__main__":
    main()