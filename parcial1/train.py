import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import torchvision
from torchvision.models.detection import fasterrcnn_resnet50_fpn
from torchvision.models.detection.faster_rcnn import FastRCNNPredictor
import tensorflow as tf
import cv2
import numpy as np
from pathlib import Path
import json
from tqdm import tqdm
import time

# ==================== TFRecord Dataset Loader ====================
class TFRecordDataset(Dataset):
    """Convert TFRecord to PyTorch Dataset"""
    def __init__(self, tfrecord_path, label_map_path, transforms=None):
        self.transforms = transforms
        self.data = []
        self.label_map = self._load_label_map(label_map_path)
        self._load_tfrecord(tfrecord_path)
    
    def _load_label_map(self, path):
        """Load label map from pbtxt file"""
        label_map = {}
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
            items = content.split('item {')[1:]
            for item in items:
                lines = item.strip().split('\n')
                item_id = None
                name = None
                for line in lines:
                    line = line.strip()
                    if 'id:' in line or 'id :' in line:
                        # Extract ID, removing any trailing comma or whitespace
                        id_part = line.split(':')[1].strip().rstrip(',').strip()
                        try:
                            item_id = int(id_part)
                        except ValueError:
                            continue
                    elif 'name:' in line or 'name :' in line:
                        # Extract name, removing quotes and commas
                        name = line.split(':')[1].strip().strip("'\"").rstrip(',').strip()
                if item_id and name:
                    label_map[name] = item_id
        
        print(f"Loaded label map: {label_map}")
        return label_map
    
    def _load_tfrecord(self, tfrecord_path):
        """Load data from TFRecord file"""
        dataset = tf.data.TFRecordDataset(tfrecord_path)
        
        feature_description = {
            'image/encoded': tf.io.FixedLenFeature([], tf.string),
            'image/object/bbox/xmin': tf.io.VarLenFeature(tf.float32),
            'image/object/bbox/xmax': tf.io.VarLenFeature(tf.float32),
            'image/object/bbox/ymin': tf.io.VarLenFeature(tf.float32),
            'image/object/bbox/ymax': tf.io.VarLenFeature(tf.float32),
            'image/object/class/text': tf.io.VarLenFeature(tf.string),
            'image/height': tf.io.FixedLenFeature([], tf.int64),
            'image/width': tf.io.FixedLenFeature([], tf.int64),
        }
        
        skipped = 0
        loaded = 0
        
        for raw_record in dataset:
            example = tf.io.parse_single_example(raw_record, feature_description)
            
            # Decode image
            img = tf.io.decode_jpeg(example['image/encoded']).numpy()
            height = int(example['image/height'].numpy())
            width = int(example['image/width'].numpy())
            
            # Extract boxes and labels
            xmin = tf.sparse.to_dense(example['image/object/bbox/xmin']).numpy()
            xmax = tf.sparse.to_dense(example['image/object/bbox/xmax']).numpy()
            ymin = tf.sparse.to_dense(example['image/object/bbox/ymin']).numpy()
            ymax = tf.sparse.to_dense(example['image/object/bbox/ymax']).numpy()
            classes = tf.sparse.to_dense(example['image/object/class/text']).numpy()
            
            # Skip images with no annotations
            if len(xmin) == 0:
                skipped += 1
                continue
            
            boxes = []
            labels = []
            for i in range(len(xmin)):
                # Convert normalized coordinates to absolute
                x1 = float(xmin[i]) * width
                y1 = float(ymin[i]) * height
                x2 = float(xmax[i]) * width
                y2 = float(ymax[i]) * height
                
                # Validate bounding box
                if x2 <= x1 or y2 <= y1:
                    continue
                
                boxes.append([x1, y1, x2, y2])
                
                class_name = classes[i].decode('utf-8')
                label_id = self.label_map.get(class_name, None)
                if label_id is None:
                    print(f"Warning: Unknown class '{class_name}', skipping")
                    continue
                labels.append(label_id)
            
            # Only add if we have valid boxes
            if len(boxes) > 0:
                self.data.append({
                    'image': img,
                    'boxes': np.array(boxes, dtype=np.float32),
                    'labels': np.array(labels, dtype=np.int64)
                })
                loaded += 1
            else:
                skipped += 1
        
        print(f"Loaded {loaded} samples, skipped {skipped} samples with no valid annotations")
    
    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, idx):
        item = self.data[idx]
        image = item['image']
        boxes = item['boxes']
        labels = item['labels']
        
        # Convert to tensor
        image = torch.from_numpy(image).permute(2, 0, 1).float() / 255.0
        
        target = {
            'boxes': torch.from_numpy(boxes),
            'labels': torch.from_numpy(labels)
        }
        
        if self.transforms:
            image = self.transforms(image)
        
        return image, target

# ==================== Model Definition ====================
def create_model(num_classes):
    """Create Faster R-CNN model with custom number of classes"""
    # Load pretrained model
    model = fasterrcnn_resnet50_fpn(pretrained=True)
    
    # Get number of input features for the classifier
    in_features = model.roi_heads.box_predictor.cls_score.in_features
    
    # Replace the pre-trained head with a new one
    # +1 for background class
    model.roi_heads.box_predictor = FastRCNNPredictor(in_features, num_classes + 1)
    
    return model

# ==================== Training Function ====================
def train_one_epoch(model, optimizer, data_loader, device, epoch):
    model.train()
    total_loss = 0
    valid_batches = 0
    
    progress_bar = tqdm(data_loader, desc=f'Epoch {epoch}')
    for images, targets in progress_bar:
        try:
            images = [img.to(device) for img in images]
            targets = [{k: v.to(device) for k, v in t.items()} for t in targets]
            
            # Skip if any target has no boxes
            skip_batch = False
            for t in targets:
                if len(t['boxes']) == 0:
                    skip_batch = True
                    break
            
            if skip_batch:
                continue
            
            # Forward pass
            loss_dict = model(images, targets)
            losses = sum(loss for loss in loss_dict.values())
            
            # Check for NaN
            if torch.isnan(losses):
                print("Warning: NaN loss detected, skipping batch")
                continue
            
            # Backward pass
            optimizer.zero_grad()
            losses.backward()
            
            # Gradient clipping
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=10.0)
            
            optimizer.step()
            
            total_loss += losses.item()
            valid_batches += 1
            progress_bar.set_postfix({'loss': losses.item()})
            
        except Exception as e:
            print(f"Error in batch: {e}")
            continue
    
    return total_loss / valid_batches if valid_batches > 0 else 0

# ==================== Evaluation Function ====================
@torch.no_grad()
def evaluate(model, data_loader, device, iou_threshold=0.5):
    model.eval()
    correct = 0
    total = 0
    
    for images, targets in tqdm(data_loader, desc='Evaluating'):
        try:
            images = [img.to(device) for img in images]
            
            predictions = model(images)
            
            for pred, target in zip(predictions, targets):
                pred_boxes = pred['boxes'].cpu().numpy()
                pred_labels = pred['labels'].cpu().numpy()
                pred_scores = pred['scores'].cpu().numpy()
                
                target_boxes = target['boxes'].cpu().numpy()
                target_labels = target['labels'].cpu().numpy()
                
                # Skip empty targets
                if len(target_boxes) == 0:
                    continue
                
                # Filter predictions by confidence threshold
                mask = pred_scores > 0.5
                pred_boxes = pred_boxes[mask]
                pred_labels = pred_labels[mask]
                
                # Calculate IoU and match predictions
                total += len(target_boxes)
                
                for t_box, t_label in zip(target_boxes, target_labels):
                    best_iou = 0
                    best_pred_label = -1
                    
                    for p_box, p_label in zip(pred_boxes, pred_labels):
                        iou = calculate_iou(t_box, p_box)
                        if iou > best_iou:
                            best_iou = iou
                            best_pred_label = p_label
                    
                    if best_iou >= iou_threshold and best_pred_label == t_label:
                        correct += 1
        except Exception as e:
            print(f"Error in evaluation: {e}")
            continue
    
    accuracy = correct / total if total > 0 else 0
    return accuracy

def calculate_iou(box1, box2):
    """Calculate Intersection over Union"""
    x1 = max(box1[0], box2[0])
    y1 = max(box1[1], box2[1])
    x2 = min(box1[2], box2[2])
    y2 = min(box1[3], box2[3])
    
    intersection = max(0, x2 - x1) * max(0, y2 - y1)
    area1 = (box1[2] - box1[0]) * (box1[3] - box1[1])
    area2 = (box2[2] - box2[0]) * (box2[3] - box2[1])
    union = area1 + area2 - intersection
    
    return intersection / union if union > 0 else 0

# ==================== Collate Function ====================
def collate_fn(batch):
    return tuple(zip(*batch))

# ==================== Main Training Script ====================
def main():
    # Configuration
    BATCH_SIZE = 4
    NUM_EPOCHS = 50
    LEARNING_RATE = 0.005
    NUM_CLASSES = 4  # borrador, marcador azul, marcador negro, marcador rojo
    TARGET_ACCURACY = 0.88
    
    # Check GPU availability
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")
    if torch.cuda.is_available():
        print(f"GPU: {torch.cuda.get_device_name(0)}")
    
    # Paths - UPDATED
    train_tfrecord = "dataset/train/objects.tfrecord"
    train_labelmap = "dataset/train/objects_label_map.pbtxt"
    valid_tfrecord = "dataset/valid/objects.tfrecord"
    valid_labelmap = "dataset/valid/objects_label_map.pbtxt"
    test_tfrecord = "dataset/test/objects.tfrecord"
    test_labelmap = "dataset/test/objects_label_map.pbtxt"
    
    # Create datasets
    print("Loading datasets...")
    train_dataset = TFRecordDataset(train_tfrecord, train_labelmap)
    valid_dataset = TFRecordDataset(valid_tfrecord, valid_labelmap)
    test_dataset = TFRecordDataset(test_tfrecord, test_labelmap)
    
    # Create data loaders
    train_loader = DataLoader(
        train_dataset, 
        batch_size=BATCH_SIZE, 
        shuffle=True, 
        collate_fn=collate_fn,
        num_workers=0  # Windows compatibility
    )
    valid_loader = DataLoader(
        valid_dataset, 
        batch_size=BATCH_SIZE, 
        shuffle=False, 
        collate_fn=collate_fn,
        num_workers=0
    )
    test_loader = DataLoader(
        test_dataset, 
        batch_size=BATCH_SIZE, 
        shuffle=False, 
        collate_fn=collate_fn,
        num_workers=0
    )
    
    print(f"Train samples: {len(train_dataset)}")
    print(f"Valid samples: {len(valid_dataset)}")
    print(f"Test samples: {len(test_dataset)}")
    
    if len(train_dataset) == 0:
        print("ERROR: No training data loaded!")
        return
    
    # Create model
    print("\nCreating model...")
    model = create_model(NUM_CLASSES)
    model.to(device)
    
    # Optimizer and scheduler
    params = [p for p in model.parameters() if p.requires_grad]
    optimizer = optim.SGD(params, lr=LEARNING_RATE, momentum=0.9, weight_decay=0.0005)
    lr_scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=10, gamma=0.1)
    
    # Training loop
    print("\nStarting training...")
    best_accuracy = 0
    
    for epoch in range(1, NUM_EPOCHS + 1):
        print(f"\n{'='*50}")
        print(f"Epoch {epoch}/{NUM_EPOCHS}")
        print(f"{'='*50}")
        
        # Train
        train_loss = train_one_epoch(model, optimizer, train_loader, device, epoch)
        print(f"Training Loss: {train_loss:.4f}")
        
        # Validate
        valid_accuracy = evaluate(model, valid_loader, device)
        print(f"Validation Accuracy: {valid_accuracy*100:.2f}%")
        
        # Learning rate scheduler step
        lr_scheduler.step()
        
        # Save best model
        if valid_accuracy > best_accuracy:
            best_accuracy = valid_accuracy
            torch.save({
                'epoch': epoch,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'accuracy': valid_accuracy,
            }, 'best_model.pth')
            print(f"✓ Saved best model (accuracy: {valid_accuracy*100:.2f}%)")
        
        # Save checkpoint every 5 epochs
        if epoch % 5 == 0:
            torch.save({
                'epoch': epoch,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'accuracy': valid_accuracy,
            }, f'checkpoint_epoch_{epoch}.pth')
        
        # Check if target accuracy reached
        if valid_accuracy >= TARGET_ACCURACY:
            print(f"\n🎉 Target accuracy of {TARGET_ACCURACY*100}% reached!")
            break
    
    # Final evaluation on test set
    print("\n" + "="*50)
    print("Final Evaluation on Test Set")
    print("="*50)
    
    # Load best model
    checkpoint = torch.load('best_model.pth')
    model.load_state_dict(checkpoint['model_state_dict'])
    
    test_accuracy = evaluate(model, test_loader, device)
    print(f"Test Accuracy: {test_accuracy*100:.2f}%")
    
    if test_accuracy >= TARGET_ACCURACY:
        print(f"✓ Model meets the 88% accuracy requirement!")
    else:
        print(f"✗ Model accuracy ({test_accuracy*100:.2f}%) is below 88% requirement.")
        print(f"  Consider training for more epochs or adjusting hyperparameters.")
    
    # Save final model for deployment
    torch.save(model.state_dict(), 'marker_detector_final.pth')
    print("\nModel saved as 'marker_detector_final.pth'")
    
    # Save label map for inference
    with open('label_map.json', 'w') as f:
        json.dump(train_dataset.label_map, f)
    print("Label map saved as 'label_map.json'")

if __name__ == "__main__":
    main()