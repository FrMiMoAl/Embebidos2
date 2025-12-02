import torch
from torchvision import transforms
from PIL import Image
import cv2
import numpy as np


class DetectorModule:
    
    def __init__(self, model_path, label_columns, image_size=96, device="cpu"):
        self.model_path = model_path
        self.label_columns = label_columns
        self.image_size = 96
        self.device = torch.device(device)

        self.model = None
        self.load_model()

        self.transform = transforms.Compose([
            transforms.Resize((self.image_size, self.image_size)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])
        ])
        print(f"Usando image_size = {self.image_size}")

        
    def load_model(self):
        try:
            from train_multilabel_cnn import MultiLabelCNN
            
            self.model = MultiLabelCNN(num_outputs=len(self.label_columns)).to(self.device)
            self.model.load_state_dict(
                torch.load(self.model_path, map_location=self.device)
            )
            self.model.eval()
            print(f"Modelo cargado correctamente desde {self.model_path}")
            
        except Exception as e:
            print(f"Error al cargar el modelo: {e}")
            raise
    
    def detect(self, frame_bgr, umbral=0.5, umbral_minimo=0.3):
        frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(frame_rgb)
        
        img_tensor = self.transform(img_pil).unsqueeze(0).to(self.device)
        
        with torch.no_grad():
            outputs = self.model(img_tensor)
            probs = torch.sigmoid(outputs)[0]
        
        probs = probs.cpu().numpy()
        
        detecciones = {}
        for clase, p in zip(self.label_columns, probs):
            if p >= umbral:
                detecciones[clase] = float(p)
        
        hay_deteccion = False
        if detecciones:
            hay_deteccion = True
        else:
            max_prob = float(np.max(probs))
            if max_prob >= umbral_minimo:
                idx_max = int(np.argmax(probs))
                detecciones[self.label_columns[idx_max]] = max_prob
                hay_deteccion = True
        
        return detecciones, probs, hay_deteccion