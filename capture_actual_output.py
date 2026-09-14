# Capture actual Semantic AI output for Dynamic Object Tracking team
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import torch
import numpy as np
import json
from src import semantic_inference, load_point_cloud

print("="*70)
print("CAPTURING ACTUAL SEMANTIC AI OUTPUT")
print("="*70)

print(f"\nPyTorch version: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"GPU: {torch.cuda.get_device_name(0)}")

# Load sample data
print("\nLoading sample LiDAR data...")
points = load_point_cloud("data/sample/sample_semantickitti.bin")
print(f"Loaded {len(points)} points")
print(f"Input shape: {points.shape}")
print(f"Input data type: {points.dtype}")
print(f"Input range - X: [{points[:, 0].min():.3f}, {points[:, 0].max():.3f}]")
print(f"Input range - Y: [{points[:, 1].min():.3f}, {points[:, 1].max():.3f}]")
print(f"Input range - Z: [{points[:, 2].min():.3f}, {points[:, 2].max():.3f}]")
print(f"Input range - Intensity: [{points[:, 3].min():.3f}, {points[:, 3].max():.3f}]")

# Run real inference
print("\nRunning REAL inference...")
model_path = Path("models/sample-model.pth")
if not model_path.exists():
    model_path = Path("C:/Users/HP/OneDrive/Pictures/Desktop/SIH/models/sample-model.pth")

results = semantic_inference(
    points,
    model_name="pointnet_kasc",
    model_path=str(model_path),
    device='cuda' if torch.cuda.is_available() else 'cpu',
    label_set="semantickitti"
)

print(f"\nInference completed successfully")
print(f"Model: {results['model_info']['model_name']}")
print(f"Device: {results['model_info']['device']}")
print(f"Label set: {results['model_info']['label_set']}")
print(f"Number of classes: {results['model_info']['num_classes']}")

print(f"\nResults structure keys: {list(results.keys())}")

print(f"\nTiming:")
print(f"  Preprocessing: {results['timing']['preprocessing_time']:.4f}s")
print(f"  Inference: {results['timing']['inference_time']:.4f}s")
print(f"  Total: {results['timing']['total_time']:.4f}s")
print(f"  Throughput: {results['timing']['points_per_second']:.0f} pts/s")

print(f"\nPoint statistics:")
print(f"  Total points: {results['num_points']}")
print(f"  Mean confidence: {np.mean(results['confidences']):.4f}")
print(f"  Std confidence: {np.std(results['confidences']):.4f}")
print(f"  Mean importance: {np.mean(results['importance_scores']):.4f}")

print(f"\n" + "="*70)
print("ACTUAL OUTPUT STRUCTURE")
print("="*70)

# Show structure of one point
if len(results['points']) > 0:
    first_point = results['points'][0]
    print(f"\nFirst point keys: {list(first_point.keys())}")
    print(f"\nFirst point values:")
    for key, value in first_point.items():
        print(f"  {key}: {value}")

print(f"\n" + "="*70)
print("FIRST 10 POINTS - ACTUAL OUTPUT")
print("="*70)

for i in range(min(10, len(results['points']))):
    point = results['points'][i]
    print(f"\nPoint {i}:")
    print(f"  x: {point['x']:.6f}")
    print(f"  y: {point['y']:.6f}")
    print(f"  z: {point['z']:.6f}")
    print(f"  intensity: {point['intensity']:.6f}")
    print(f"  semantic_class: {point['semantic_class']}")
    print(f"  semantic_label: {point['semantic_label']}")
    print(f"  confidence: {point['confidence']:.6f}")
    print(f"  semantic_importance: {point['semantic_importance']:.6f}")

print(f"\n" + "="*70)
print("CLASS DISTRIBUTION")
print("="*70)

from collections import Counter
class_dist = Counter([p['semantic_class'] for p in results['points']])
for class_name, count in class_dist.most_common(20):
    print(f"  {class_name}: {count} points ({count/len(results['points'])*100:.1f}%)")

print(f"\n" + "="*70)
print("COORDINATE SYSTEM ANALYSIS")
print("="*70)

print(f"\nOutput coordinate ranges:")
x_coords = [p['x'] for p in results['points']]
y_coords = [p['y'] for p in results['points']]
z_coords = [p['z'] for p in results['points']]
print(f"  X: [{min(x_coords):.3f}, {max(x_coords):.3f}] meters")
print(f"  Y: [{min(y_coords):.3f}, {max(y_coords):.3f}] meters")
print(f"  Z: [{min(z_coords):.3f}, {max(z_coords):.3f}] meters")

print(f"\n" + "="*70)
print("TEMPORAL INFORMATION CHECK")
print("="*70)

print(f"\nChecking for temporal fields in output...")
has_frame_id = any('frame_id' in str(p) for p in results['points'])
has_timestamp = any('timestamp' in str(p) for p in results['points'])
print(f"  frame_id available: {has_frame_id}")
print(f"  timestamp available: {has_timestamp}")

print(f"\nChecking results dictionary for temporal fields...")
print(f"  'frame_id' in results: {'frame_id' in results}")
print(f"  'timestamp' in results: {'timestamp' in results}")

print(f"\n" + "="*70)
print("OBJECT/CLUSTERING CHECK")
print("="*70)

print(f"\nChecking for object/cluster fields...")
has_object_id = any('object_id' in str(p) for p in results['points'])
has_cluster_id = any('cluster' in str(p) for p in results['points'])
has_centroid = any('centroid' in str(p) for p in results['points'])
print(f"  object_id available: {has_object_id}")
print(f"  cluster_id available: {has_cluster_id}")
print(f"  centroid available: {has_centroid}")

print(f"\n" + "="*70)
print("OUTPUT LEVEL")
print("="*70)

print(f"\nCurrent output is: POINT-LEVEL")
print(f"  - Each point has individual semantic classification")
print(f"  - No object grouping or clustering performed")
print(f"  - No centroid calculation performed")
print(f"  - Downstream modules (Kashika) must perform object extraction")

print(f"\n" + "="*70)
print("SAVE SAMPLE OUTPUT TO FILE")
print("="*70)

# Save first 100 points as sample (convert numpy types to native Python types)
sample_output = {
    'total_points': int(len(results['points'])),
    'sample_points': [
        {
            'x': float(p['x']),
            'y': float(p['y']),
            'z': float(p['z']),
            'intensity': float(p['intensity']),
            'semantic_class': str(p['semantic_class']),
            'semantic_label': int(p['semantic_label']),
            'confidence': float(p['confidence']),
            'semantic_importance': float(p['semantic_importance'])
        }
        for p in results['points'][:100]
    ],
    'model_info': results['model_info'],
    'timing': results['timing']
}

with open('actual_semantic_output_sample.json', 'w') as f:
    json.dump(sample_output, f, indent=2)

print(f"\nSaved first 100 points to: actual_semantic_output_sample.json")

print(f"\n" + "="*70)
print("VERIFICATION COMPLETE")
print("="*70)
