import os
import csv
import time
from PIL import Image

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms


# ============================
# 1. CONFIGURACIÓN BÁSICA
# ============================
ROOT_DIR   = "embebidos.v14i.multiclass"  # carpeta de Roboflow
BATCH_SIZE = 32
NUM_EPOCHS = 20
LR         = 0.0005
IMAGE_SIZE = 96

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("Usando dispositivo:", device)


# ============================
# 2. DATASET MULTI-LABEL
# ============================

# nombres EXACTOS de las columnas del CSV
COL_BORRADOR = "borrador"
COL_AZUL     = "marcador azul"
COL_NEGRO    = "marcador negro"
COL_ROJO     = "marcador rojo"

LABEL_COLUMNS = [COL_ROJO, COL_NEGRO, COL_AZUL, COL_BORRADOR]


class MarkersDataset(Dataset):
    def __init__(self, root_dir, split="train", transform=None):
        self.images_dir = os.path.join(root_dir, split)
        csv_path = os.path.join(self.images_dir, "_classes.csv")
        self.transform = transform
        self.samples = []  # (ruta_imagen, tensor_labels)

        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"No se encontró CSV: {csv_path}")

        with open(csv_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                filename = row["filename"]
                img_path = os.path.join(self.images_dir, filename)
                if not os.path.exists(img_path):
                    # Si alguna imagen falta, se salta
                    continue

                labels = [int(row[col]) for col in LABEL_COLUMNS]
                labels = torch.tensor(labels, dtype=torch.float32)  # [4]
                self.samples.append((img_path, labels))

        if len(self.samples) == 0:
            raise RuntimeError(f"No se cargaron muestras para split '{split}'")

        print(f"Split {split}: {len(self.samples)} imágenes")

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        img_path, labels = self.samples[idx]
        image = Image.open(img_path).convert("RGB")
        if self.transform:
            image = self.transform(image)
        return image, labels


# ============================
# 3. TRANSFORMS
# ============================

train_transforms = transforms.Compose([
    transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
    transforms.RandomHorizontalFlip(),
    transforms.RandomRotation(10),
    transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.5, 0.5, 0.5],
                         std=[0.5, 0.5, 0.5])
])

val_transforms = transforms.Compose([
    transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.5, 0.5, 0.5],
                         std=[0.5, 0.5, 0.5])
])

train_dataset = MarkersDataset(ROOT_DIR, "train", transform=train_transforms)
val_dataset   = MarkersDataset(ROOT_DIR, "valid", transform=val_transforms)

train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE,
                          shuffle=True, num_workers=0)
val_loader   = DataLoader(val_dataset, batch_size=BATCH_SIZE,
                          shuffle=False, num_workers=0)


# ============================
# 4. MODELO CNN MULTI-LABEL
# ============================

class MultiLabelCNN(nn.Module):
    def __init__(self, num_outputs=4):
        super().__init__()
        self.conv1 = nn.Conv2d(3, 32, kernel_size=3, padding=1)
        self.bn1   = nn.BatchNorm2d(32)

        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
        self.bn2   = nn.BatchNorm2d(64)

        self.conv3 = nn.Conv2d(64, 128, kernel_size=3, padding=1)
        self.bn3   = nn.BatchNorm2d(128)

        self.pool     = nn.MaxPool2d(2, 2)
        self.dropout  = nn.Dropout(0.5)

        # IMAGE_SIZE = 96 -> después de 3 pools: 96 -> 48 -> 24 -> 12
        self.fc1 = nn.Linear(128 * 12 * 12, 256)
        self.fc2 = nn.Linear(256, num_outputs)  # 4 salidas

    def forward(self, x):
        x = self.pool(torch.relu(self.bn1(self.conv1(x))))
        x = self.pool(torch.relu(self.bn2(self.conv2(x))))
        x = self.pool(torch.relu(self.bn3(self.conv3(x))))

        x = x.view(x.size(0), -1)
        x = self.dropout(torch.relu(self.fc1(x)))
        x = self.fc2(x)  # sin activación aquí (la aplica el loss)
        return x


model = MultiLabelCNN(num_outputs=len(LABEL_COLUMNS)).to(device)
print(model)


# ============================
# 5. LOSS Y OPTIMIZADOR
# ============================

criterion = nn.BCEWithLogitsLoss()  # multi-label
optimizer = optim.Adam(model.parameters(), lr=LR)


# ============================
# 6. FUNCIONES DE ENTRENAMIENTO
# ============================

def calc_accuracy(outputs, labels):
    """
    Accuracy multi-label: comparamos cada etiqueta (0/1) por separado.
    """
    probs = torch.sigmoid(outputs)
    preds = (probs >= 0.5).float()
    correct = (preds == labels).float().sum().item()
    total = labels.numel()
    return correct / total


def train_one_epoch(epoch):
    model.train()
    running_loss = 0.0
    correct_labels = 0
    total_labels = 0

    start_time = time.time()

    for inputs, labels in train_loader:
        inputs = inputs.to(device)
        labels = labels.to(device)

        optimizer.zero_grad()

        outputs = model(inputs)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        running_loss += loss.item() * inputs.size(0)
        acc = calc_accuracy(outputs.detach(), labels)
        correct_labels += acc * labels.numel()
        total_labels += labels.numel()

    epoch_loss = running_loss / len(train_dataset)
    epoch_acc = correct_labels / total_labels

    print(f"Epoch [{epoch+1}] - "
          f"Train Loss: {epoch_loss:.4f}  "
          f"Train Acc (labels): {epoch_acc*100:.2f}%  "
          f"Tiempo: {time.time()-start_time:.1f}s")


def validate():
    model.eval()
    running_loss = 0.0
    correct_labels = 0
    total_labels = 0

    with torch.no_grad():
        for inputs, labels in val_loader:
            inputs = inputs.to(device)
            labels = labels.to(device)

            outputs = model(inputs)
            loss = criterion(outputs, labels)

            running_loss += loss.item() * inputs.size(0)
            acc = calc_accuracy(outputs, labels)
            correct_labels += acc * labels.numel()
            total_labels += labels.numel()

    epoch_loss = running_loss / len(val_dataset)
    epoch_acc = correct_labels / total_labels

    print(f"Valid Loss: {epoch_loss:.4f}  "
          f"Valid Acc (labels): {epoch_acc*100:.2f}%")

    return epoch_acc


# ============================
# 7. BUCLE PRINCIPAL
# ============================

def main():
    best_acc = 0.0

    for epoch in range(NUM_EPOCHS):
        train_one_epoch(epoch)
        val_acc = validate()

        if val_acc > best_acc:
            best_acc = val_acc
            torch.save(model.state_dict(), "mejor_modelo_multilabel.pth")
            print(f"✅ Nuevo mejor modelo guardado con acc etiquetas: {best_acc*100:.2f}%")

    print("Entrenamiento finalizado.")
    print(f"Mejor accuracy en validación (por etiqueta): {best_acc*100:.2f}%")
    print("Modelo guardado como 'mejor_modelo_multilabel.pth'")


if __name__ == "__main__":
    main()