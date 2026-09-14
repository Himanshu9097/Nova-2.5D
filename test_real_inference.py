"""
Test real pretrained model inference with CPU
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import torch
import torch_pointcloud as tp
from torch_pointcloud.utils.data import collate
import numpy as np
import time

print("="*60)
print("TESTING REAL PRETRAINED MODEL INFERENCE (CPU MODE)")
print("="*60)

print(f"\nPyTorch version: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")

# Load model
print("\nLoading RandLA-Net model...")
start_time = time.time()
model, info = tp.create_model(
    "randlanet.semantickitti.tsung-han-wu",
    task="segmentation",
    pretrained=True,
    return_info=True
)
model = model.eval()
load_time = time.time() - start_time

print(f"Model loaded in {load_time:.2f}s")
print(f"Model info: {info}")

# Load sample data
print("\nLoading sample LiDAR data...")
from src import load_point_cloud
points = load_point_cloud("data/sample/sample_semantickitti.bin")
print(f"Loaded {len(points)} points")

# Prepare data
print("\nPreparing data for inference...")
num_points = len(points)
sample = {
    "pos": torch.from_numpy(points[:, :3]).float(),
    "intensity": torch.from_numpy(points[:, 3:4]).float(),
    "segment": torch.zeros(num_points, dtype=torch.long),
    "instance": torch.zeros(num_points, dtype=torch.long),
}

# Apply transforms
print("Applying model transforms...")
data = info["transform"](sample)
data = collate([data])

# Run inference
print("\nRunning inference...")
inference_start = time.time()

with torch.no_grad():
    logits = model(data.get("x"), data.get("pos"), data.get("batch"))

inference_time = time.time() - inference_start

# Get predictions
predictions = logits.argmax(dim=1).cpu().numpy()
probabilities = torch.softmax(logits, dim=1).cpu().numpy()
confidences = np.max(probabilities, axis=1)

print(f"\nInference completed in {inference_time:.2f}s")
print(f"Points processed: {len(predictions)}")
print(f"Points per second: {len(predictions) / inference_time:.1f}")
print(f"Mean confidence: {np.mean(confidences):.3f}")

# Show sample predictions
print(f"\nSample predictions:")
for i in range(min(5, len(predictions))):
    class_idx = predictions[i]
    class_name = info['weights']['classes'][class_idx]
    conf = confidences[i]
    print(f"  Point {i}: {class_name} (confidence: {conf:.3f})")

# Class distribution
from collections import Counter
class_counts = Counter(predictions)
print(f"\nClass distribution:")
for class_idx, count in class_counts.most_common(10):
    class_name = info['weights']['classes'][class_idx]
    print(f"  {class_name}: {count}")

print("\n" + "="*60)
print("REAL INFERENCE SUCCESSFUL!")
print("="*60)
