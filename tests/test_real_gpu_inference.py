"""
Verification tests for real GPU inference without mocking
These tests verify actual GPU capabilities and real model inference
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
import torch
import numpy as np
from src import semantic_inference, load_point_cloud


class TestGPUEnvironment:
    """Test GPU environment and CUDA availability"""
    
    def test_python_version(self):
        """Verify Python version is correct"""
        import sys
        assert sys.version_info.major == 3
        assert sys.version_info.minor >= 11
        print(f"Python version: {sys.version}")
    
    def test_cuda_available(self):
        """Verify CUDA is available"""
        assert torch.cuda.is_available(), "CUDA not available - GPU inference impossible"
        print("CUDA available: True")
    
    def test_gpu_detection(self):
        """Verify RTX 2050 is detected"""
        assert torch.cuda.is_available(), "CUDA not available"
        gpu_name = torch.cuda.get_device_name(0)
        print(f"GPU detected: {gpu_name}")
        assert "RTX" in gpu_name or "GeForce" in gpu_name, f"Expected RTX 2050, got {gpu_name}"
    
    def test_cuda_tensor_computation(self):
        """Verify actual CUDA tensor computation works"""
        assert torch.cuda.is_available(), "CUDA not available"
        
        # Create CUDA tensors
        x = torch.randn(4096, 4096, device="cuda")
        y = x @ x
        torch.cuda.synchronize()
        
        assert y.device.type == "cuda", "Result not on CUDA device"
        assert y.shape == (4096, 4096), "Incorrect result shape"
        print("CUDA tensor computation: PASSED")
    
    def test_pytorch_cuda_version(self):
        """Verify PyTorch CUDA version"""
        assert torch.cuda.is_available(), "CUDA not available"
        cuda_version = torch.version.cuda
        print(f"PyTorch CUDA version: {cuda_version}")
        assert cuda_version is not None, "CUDA version is None"
        assert len(cuda_version.split('.')) >= 2, "Invalid CUDA version format"


class TestPointNetModel:
    """Test PointNet model loading and structure"""
    
    def test_model_checkpoint_exists(self):
        """Verify PointNet model checkpoint exists"""
        model_path = Path("models/sample-model.pth")
        if not model_path.exists():
            model_path = Path("C:/Users/HP/OneDrive/Pictures/Desktop/SIH/models/sample-model.pth")
        assert model_path.exists(), f"Model checkpoint not found: {model_path}"
        print(f"Model checkpoint exists: {model_path}")
    
    def test_model_loading(self):
        """Verify PointNet model can be loaded"""
        from src.inference import PointNetSemSeg
        
        model_path = Path("models/sample-model.pth")
        if not model_path.exists():
            model_path = Path("C:/Users/HP/OneDrive/Pictures/Desktop/SIH/models/sample-model.pth")
        
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        model = PointNetSemSeg(n_classes=34, bn=False).to(device)
        
        checkpoint = torch.load(model_path, map_location=device)
        model.load_state_dict(checkpoint)
        model.eval()
        
        print(f"PointNet model loaded successfully on {device}")
        assert next(model.parameters()).device.type == device.replace('cuda', 'cuda')
    
    def test_model_forward_pass(self):
        """Verify PointNet model forward pass works"""
        from src.inference import PointNetSemSeg
        
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        model = PointNetSemSeg(n_classes=34, bn=False).to(device)
        model.eval()
        
        # Create dummy input
        dummy_input = torch.randn(1, 3, 1000).to(device)
        
        with torch.no_grad():
            output, _ = model(dummy_input)
        
        assert output.shape[0] == 1, "Wrong batch dimension"
        assert output.shape[1] == 34, "Wrong number of classes"
        assert output.shape[2] == 1000, "Wrong number of points"
        print(f"Model forward pass: {output.shape}")


class TestRealInference:
    """Test real model inference without mocking"""
    
    def test_sample_data_loading(self):
        """Verify sample point cloud can be loaded"""
        points = load_point_cloud("data/sample/sample_semantickitti.bin")
        assert points.shape[0] > 0, "No points loaded"
        assert points.shape[1] >= 3, "Insufficient point dimensions"
        print(f"Sample data loaded: {points.shape}")
    
    def test_real_inference_execution(self):
        """Verify real model inference executes without synthetic fallback"""
        points = load_point_cloud("data/sample/sample_semantickitti.bin")
        
        model_path = Path("models/sample-model.pth")
        if not model_path.exists():
            model_path = Path("C:/Users/HP/OneDrive/Pictures/Desktop/SIH/models/sample-model.pth")
        
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        
        results = semantic_inference(
            points,
            model_name="pointnet_kasc",
            model_path=str(model_path),
            device=device,
            label_set="semantickitti"
        )
        
        # Verify results are real, not synthetic
        assert not results.get('synthetic', False), "Results are synthetic, not real"
        assert results['model_info']['model_name'] == "pointnet_kasc", "Wrong model used"
        assert results['model_info']['device'] == device, "Wrong device used"
        
        print(f"Real inference executed on {device}")
    
    def test_gpu_inference_usage(self):
        """Verify GPU is actually used for inference when available"""
        if not torch.cuda.is_available():
            pytest.skip("CUDA not available")
        
        points = load_point_cloud("data/sample/sample_semantickitti.bin")
        
        model_path = Path("models/sample-model.pth")
        if not model_path.exists():
            model_path = Path("C:/Users/HP/OneDrive/Pictures/Desktop/SIH/models/sample-model.pth")
        
        results = semantic_inference(
            points,
            model_name="pointnet_kasc",
            model_path=str(model_path),
            device='cuda',
            label_set="semantickitti"
        )
        
        assert results['model_info']['device'] == 'cuda', "Inference not on CUDA"
        print("GPU inference verified")
    
    def test_predictions_structure(self):
        """Verify predictions have correct structure"""
        points = load_point_cloud("data/sample/sample_semantickitti.bin")
        
        model_path = Path("models/sample-model.pth")
        if not model_path.exists():
            model_path = Path("C:/Users/HP/OneDrive/Pictures/Desktop/SIH/models/sample-model.pth")
        
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        
        results = semantic_inference(
            points,
            model_name="pointnet_kasc",
            model_path=str(model_path),
            device=device,
            label_set="semantickitti"
        )
        
        # Verify output structure
        assert 'points' in results, "Missing 'points' key"
        assert 'predictions' in results, "Missing 'predictions' key"
        assert 'confidences' in results, "Missing 'confidences' key"
        assert 'importance_scores' in results, "Missing 'importance_scores' key"
        assert 'timing' in results, "Missing 'timing' key"
        assert 'model_info' in results, "Missing 'model_info' key"
        
        # Verify point structure
        first_point = results['points'][0]
        assert 'x' in first_point, "Missing 'x' in point"
        assert 'y' in first_point, "Missing 'y' in point"
        assert 'z' in first_point, "Missing 'z' in point"
        assert 'semantic_class' in first_point, "Missing 'semantic_class' in point"
        assert 'confidence' in first_point, "Missing 'confidence' in point"
        assert 'semantic_importance' in first_point, "Missing 'semantic_importance' in point"
        
        print("Output structure verified")
    
    def test_confidence_calculation(self):
        """Verify confidence scores are from real model softmax"""
        points = load_point_cloud("data/sample/sample_semantickitti.bin")
        
        model_path = Path("models/sample-model.pth")
        if not model_path.exists():
            model_path = Path("C:/Users/HP/OneDrive/Pictures/Desktop/SIH/models/sample-model.pth")
        
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        
        results = semantic_inference(
            points,
            model_name="pointnet_kasc",
            model_path=str(model_path),
            device=device,
            label_set="semantickitti"
        )
        
        confidences = results['confidences']
        
        # Verify confidence range
        assert np.all(confidences >= 0.0), "Confidence below 0"
        assert np.all(confidences <= 1.0), "Confidence above 1"
        
        # Verify confidence is not uniform (real model output)
        assert np.std(confidences) > 0.01, "Confidence appears uniform (synthetic?)"
        
        print(f"Confidence statistics: mean={np.mean(confidences):.3f}, std={np.std(confidences):.3f}")
    
    def test_semantic_importance_calculation(self):
        """Verify semantic importance is calculated from real predictions"""
        points = load_point_cloud("data/sample/sample_semantickitti.bin")
        
        model_path = Path("models/sample-model.pth")
        if not model_path.exists():
            model_path = Path("C:/Users/HP/OneDrive/Pictures/Desktop/SIH/models/sample-model.pth")
        
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        
        results = semantic_inference(
            points,
            model_name="pointnet_kasc",
            model_path=str(model_path),
            device=device,
            label_set="semantickitti"
        )
        
        importance_scores = results['importance_scores']
        
        # Verify importance range
        assert np.all(importance_scores >= 0.0), "Importance below 0"
        assert np.all(importance_scores <= 1.0), "Importance above 1"
        
        # Verify importance varies by class
        assert np.std(importance_scores) > 0.01, "Importance appears uniform"
        
        print(f"Importance statistics: mean={np.mean(importance_scores):.3f}, std={np.std(importance_scores):.3f}")


class TestPerformanceMetrics:
    """Test performance measurement and reporting"""
    
    def test_timing_metrics(self):
        """Verify timing metrics are measured"""
        points = load_point_cloud("data/sample/sample_semantickitti.bin")
        
        model_path = Path("models/sample-model.pth")
        if not model_path.exists():
            model_path = Path("C:/Users/HP/OneDrive/Pictures/Desktop/SIH/models/sample-model.pth")
        
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        
        results = semantic_inference(
            points,
            model_name="pointnet_kasc",
            model_path=str(model_path),
            device=device,
            label_set="semantickitti"
        )
        
        timing = results['timing']
        
        assert 'preprocessing_time' in timing, "Missing preprocessing time"
        assert 'inference_time' in timing, "Missing inference time"
        assert 'total_time' in timing, "Missing total time"
        assert 'points_per_second' in timing, "Missing points per second"
        
        # Verify timing is reasonable
        assert timing['inference_time'] > 0, "Inference time is zero"
        assert timing['points_per_second'] > 0, "Points per second is zero"
        
        print(f"Timing: inference={timing['inference_time']:.3f}s, throughput={timing['points_per_second']:.0f} pts/s")
    
    def test_gpu_performance(self):
        """Verify GPU performance is measured"""
        if not torch.cuda.is_available():
            pytest.skip("CUDA not available")
        
        points = load_point_cloud("data/sample/sample_semantickitti.bin")
        
        model_path = Path("models/sample-model.pth")
        if not model_path.exists():
            model_path = Path("C:/Users/HP/OneDrive/Pictures/Desktop/SIH/models/sample-model.pth")
        
        results = semantic_inference(
            points,
            model_name="pointnet_kasc",
            model_path=str(model_path),
            device='cuda',
            label_set="semantickitti"
        )
        
        # GPU should be faster than 10k points/second
        assert results['timing']['points_per_second'] > 10000, "GPU performance too low"
        
        print(f"GPU performance: {results['timing']['points_per_second']:.0f} pts/s")


class TestOutputCompatibility:
    """Test output compatibility with integration requirements"""
    
    def test_required_output_fields(self):
        """Verify required output fields are present"""
        points = load_point_cloud("data/sample/sample_semantickitti.bin")
        
        model_path = Path("models/sample-model.pth")
        if not model_path.exists():
            model_path = Path("C:/Users/HP/OneDrive/Pictures/Desktop/SIH/models/sample-model.pth")
        
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        
        results = semantic_inference(
            points,
            model_name="pointnet_kasc",
            model_path=str(model_path),
            device=device,
            label_set="semantickitti"
        )
        
        # Verify SIH integration requirements
        for point in results['points']:
            assert 'semantic_class' in point, "Missing semantic_class"
            assert 'confidence' in point, "Missing confidence"
            assert 'semantic_importance' in point, "Missing semantic_importance"
        
        print("SIH output compatibility verified")


if __name__ == "__main__":
    # Run tests manually for verification
    print("="*60)
    print("RUNNING GPU INFERENCE VERIFICATION TESTS")
    print("="*60)
    
    test_env = TestGPUEnvironment()
    test_env.test_python_version()
    test_env.test_cuda_available()
    test_env.test_gpu_detection()
    test_env.test_cuda_tensor_computation()
    test_env.test_pytorch_cuda_version()
    
    test_model = TestPointNetModel()
    test_model.test_model_checkpoint_exists()
    test_model.test_model_loading()
    test_model.test_model_forward_pass()
    
    test_inference = TestRealInference()
    test_inference.test_sample_data_loading()
    test_inference.test_real_inference_execution()
    test_inference.test_gpu_inference_usage()
    test_inference.test_predictions_structure()
    test_inference.test_confidence_calculation()
    test_inference.test_semantic_importance_calculation()
    
    test_perf = TestPerformanceMetrics()
    test_perf.test_timing_metrics()
    test_perf.test_gpu_performance()
    
    test_compat = TestOutputCompatibility()
    test_compat.test_required_output_fields()
    
    print("\n" + "="*60)
    print("ALL VERIFICATION TESTS PASSED")
    print("="*60)
