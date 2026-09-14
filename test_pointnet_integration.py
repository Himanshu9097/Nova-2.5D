"""
Test PointNet integration with existing inference module
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import torch
import numpy as np
import time

print("="*60)
print("TESTING POINTNET INTEGRATION WITH EXISTING MODULE")
print("="*60)

print(f"\nPyTorch version: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(f"CUDA version: {torch.version.cuda}")

# Import from our module
from src import semantic_inference
from src import load_point_cloud

# Load sample data
print("\nLoading sample LiDAR data...")
points = load_point_cloud("data/sample/sample_semantickitti.bin")
print(f"Loaded {len(points)} points")

# Run PointNet inference
print("\nRunning PointNet inference...")
start_time = time.time()

results = semantic_inference(
    points,
    model_name="pointnet_kasc",
    model_path="models/sample-model.pth",
    device='cuda' if torch.cuda.is_available() else 'cpu',
    label_set="semantickitti"
)

total_time = time.time() - start_time

print(f"\nInference completed in {total_time:.2f}s")
print(f"Preprocessing time: {results['timing']['preprocessing_time']:.3f}s")
print(f"Inference time: {results['timing']['inference_time']:.3f}s")
print(f"Points per second: {results['timing']['points_per_second']:.1f}")
print(f"Mean confidence: {np.mean(results['confidences']):.3f}")

# Show sample predictions
print(f"\nSample predictions:")
for i in range(min(5, len(results['points']))):
    point = results['points'][i]
    print(f"  Point {i}: {point['semantic_class']} (confidence: {point['confidence']:.3f}, importance: {point['semantic_importance']:.3f})")

# Class distribution
from collections import Counter
class_counts = Counter([p['semantic_class'] for p in results['points']])
print(f"\nClass distribution (top 10):")
for class_name, count in class_counts.most_common(10):
    print(f"  {class_name}: {count}")

# Model info
print(f"\nModel info:")
print(f"  Model: {results['model_info']['model_name']}")
print(f"  Device: {results['model_info']['device']}")
print(f"  Classes: {results['model_info']['num_classes']}")

print("\n" + "="*60)
print("POINTNET INTEGRATION SUCCESSFUL!")
print("="*60)
