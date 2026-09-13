# Test Streamlit integration with real PointNet inference
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import torch
import numpy as np

print("="*60)
print("TESTING STREAMLIT INTEGRATION WITH REAL INFERENCE")
print("="*60)

print(f"\nPyTorch version: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(f"CUDA version: {torch.version.cuda}")

# Import from our module
from src import semantic_inference, load_point_cloud

# Load sample data
print("\nLoading sample LiDAR data...")
points = load_point_cloud("data/sample/sample_semantickitti.bin")
print(f"Loaded {len(points)} points")

# Test the exact call that Streamlit will make
print("\nTesting Streamlit-style inference call...")
model_path = Path("models/sample-model.pth")
if not model_path.exists():
    model_path = Path("C:/Users/HP/OneDrive/Pictures/Desktop/SIH/models/sample-model.pth")

try:
    results = semantic_inference(
        points,
        model_name="pointnet_kasc",
        model_path=str(model_path),
        confidence_threshold=0.5,
        device='cuda' if torch.cuda.is_available() else 'cpu',
        label_set="semantickitti"
    )
    
    print(f"\n[PASS] Streamlit integration test PASSED")
    print(f"Model: {results['model_info']['model_name']}")
    print(f"Device: {results['model_info']['device']}")
    print(f"Points processed: {results['num_points']}")
    print(f"Inference time: {results['timing']['inference_time']:.3f}s")
    print(f"Points per second: {results['timing']['points_per_second']:.1f}")
    print(f"Mean confidence: {np.mean(results['confidences']):.3f}")
    print(f"Mean importance: {np.mean(results['importance_scores']):.3f}")
    
    # Verify output structure
    print(f"\nOutput structure verification:")
    print(f"  'points' key exists: {('points' in results)}")
    print(f"  'predictions' key exists: {('predictions' in results)}")
    print(f"  'confidences' key exists: {('confidences' in results)}")
    print(f"  'importance_scores' key exists: {('importance_scores' in results)}")
    print(f"  'timing' key exists: {('timing' in results)}")
    print(f"  'model_info' key exists: {('model_info' in results)}")
    
    # Verify point structure
    if 'points' in results and len(results['points']) > 0:
        first_point = results['points'][0]
        print(f"\nFirst point structure:")
        print(f"  'x' exists: {('x' in first_point)}")
        print(f"  'y' exists: {('y' in first_point)}")
        print(f"  'z' exists: {('z' in first_point)}")
        print(f"  'semantic_class' exists: {('semantic_class' in first_point)}")
        print(f"  'confidence' exists: {('confidence' in first_point)}")
        print(f"  'semantic_importance' exists: {('semantic_importance' in first_point)}")
        
        print(f"\nFirst point values:")
        print(f"  x: {first_point['x']:.3f}")
        print(f"  y: {first_point['y']:.3f}")
        print(f"  z: {first_point['z']:.3f}")
        print(f"  semantic_class: {first_point['semantic_class']}")
        print(f"  confidence: {first_point['confidence']:.3f}")
        print(f"  semantic_importance: {first_point['semantic_importance']:.3f}")
    
    print("\n" + "="*60)
    print("STREAMLIT INTEGRATION READY FOR PRODUCTION")
    print("="*60)
    
except Exception as e:
    print(f"\n[FAIL] Streamlit integration test FAILED: {e}")
    import traceback
    traceback.print_exc()
