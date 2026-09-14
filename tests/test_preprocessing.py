"""
Unit tests for preprocessing module
"""

import pytest
import numpy as np
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.preprocessing import (
    validate_point_cloud,
    normalize_point_cloud,
    filter_point_cloud,
    downsample_point_cloud,
    add_intensity_if_missing,
    ensure_4_channel,
    preprocess_for_model,
    calculate_point_cloud_statistics
)


class TestValidatePointCloud:
    """Test point cloud validation"""
    
    def test_valid_point_cloud(self):
        """Test validation of valid point cloud"""
        points = np.random.rand(100, 4).astype(np.float32)
        is_valid, error = validate_point_cloud(points)
        assert is_valid
        assert error == ""
    
    def test_invalid_dimensions(self):
        """Test validation fails for wrong dimensions"""
        points = np.random.rand(100, 2).astype(np.float32)
        is_valid, error = validate_point_cloud(points)
        assert not is_valid
        assert "at least 3 coordinates" in error
    
    def test_empty_point_cloud(self):
        """Test validation fails for empty point cloud"""
        points = np.array([]).reshape(0, 4)
        is_valid, error = validate_point_cloud(points)
        assert not is_valid
        assert "empty" in error.lower()
    
    def test_nan_values(self):
        """Test validation fails for NaN values"""
        points = np.random.rand(100, 4).astype(np.float32)
        points[0, 0] = np.nan
        is_valid, error = validate_point_cloud(points)
        assert not is_valid
        assert "NaN" in error
    
    def test_inf_values(self):
        """Test validation fails for infinite values"""
        points = np.random.rand(100, 4).astype(np.float32)
        points[0, 0] = np.inf
        is_valid, error = validate_point_cloud(points)
        assert not is_valid
        assert "infinite" in error.lower()


class TestNormalizePointCloud:
    """Test point cloud normalization"""
    
    def test_no_normalization(self):
        """Test no normalization returns unchanged"""
        points = np.random.rand(100, 4).astype(np.float32)
        normalized = normalize_point_cloud(points, method="none")
        np.testing.assert_array_almost_equal(points, normalized)
    
    def test_mean_std_normalization(self):
        """Test mean-std normalization"""
        points = np.random.rand(100, 4).astype(np.float32)
        normalized = normalize_point_cloud(points, method="mean_std")
        
        # Check that XYZ are normalized (approximately zero mean, unit std)
        xyz = normalized[:, :3]
        assert np.allclose(np.mean(xyz, axis=0), 0, atol=1e-6)
        assert np.allclose(np.std(xyz, axis=0), 1, atol=1e-6)
    
    def test_min_max_normalization(self):
        """Test min-max normalization"""
        points = np.random.rand(100, 4).astype(np.float32)
        normalized = normalize_point_cloud(points, method="min_max", target_range=(0, 1))
        
        # Check that XYZ are in [0, 1] range
        xyz = normalized[:, :3]
        assert np.all(xyz >= 0) and np.all(xyz <= 1)


class TestFilterPointCloud:
    """Test point cloud filtering"""
    
    def test_range_filtering(self):
        """Test spatial range filtering"""
        points = np.array([
            [10, 10, 0, 0.5],  # Inside range
            [100, 100, 0, 0.5],  # Outside range
            [-10, -10, 0, 0.5],  # Inside range
            [0, 0, 10, 0.5],  # Outside Z range
        ], dtype=np.float32)
        
        filtered = filter_point_cloud(points, min_range=-20, max_range=20, min_z=-5, max_z=5)
        
        # Should keep only points within range
        assert filtered.shape[0] == 2  # 2 points inside range
        assert np.all(filtered[:, 0] >= -20) and np.all(filtered[:, 0] <= 20)


class TestDownsamplePointCloud:
    """Test point cloud downsampling"""
    
    def test_random_sampling(self):
        """Test random sampling downsampling"""
        points = np.random.rand(1000, 4).astype(np.float32)
        downsampled = downsample_point_cloud(points, target_num_points=100)
        
        assert downsampled.shape[0] == 100
        assert downsampled.shape[1] == 4
    
    def test_no_downsampling_needed(self):
        """Test when no downsampling is needed"""
        points = np.random.rand(50, 4).astype(np.float32)
        downsampled = downsample_point_cloud(points, target_num_points=100)
        
        # Should return original if already under target
        assert downsampled.shape[0] == 50


class TestAddIntensity:
    """Test intensity channel handling"""
    
    def test_add_intensity_to_3d(self):
        """Test adding intensity to 3D points"""
        points = np.random.rand(100, 3).astype(np.float32)
        with_intensity = add_intensity_if_missing(points, default_intensity=0.7)
        
        assert with_intensity.shape == (100, 4)
        assert np.all(with_intensity[:, 3] == 0.7)
    
    def test_keep_existing_intensity(self):
        """Test keeping existing intensity"""
        points = np.random.rand(100, 4).astype(np.float32)
        with_intensity = add_intensity_if_missing(points)
        
        assert with_intensity.shape == (100, 4)
        np.testing.assert_array_equal(points, with_intensity)


class TestEnsure4Channel:
    """Test 4-channel enforcement"""
    
    def test_3d_to_4d(self):
        """Test converting 3D to 4D"""
        points = np.random.rand(100, 3).astype(np.float32)
        result = ensure_4_channel(points)
        
        assert result.shape == (100, 4)
    
    def test_4d_unchanged(self):
        """Test 4D remains unchanged"""
        points = np.random.rand(100, 4).astype(np.float32)
        result = ensure_4_channel(points)
        
        assert result.shape == (100, 4)
        np.testing.assert_array_equal(points, result)
    
    def test_5d_truncated(self):
        """Test 5D truncated to 4D"""
        points = np.random.rand(100, 5).astype(np.float32)
        result = ensure_4_channel(points)
        
        assert result.shape == (100, 4)
        np.testing.assert_array_equal(points[:, :4], result)


class TestPreprocessForModel:
    """Test complete preprocessing pipeline"""
    
    def test_preprocessing_pipeline(self):
        """Test complete preprocessing pipeline"""
        points = np.random.rand(1000, 4).astype(np.float32)
        processed = preprocess_for_model(
            points,
            normalize=True,
            filter_range=True,
            downsample=True,
            target_points=500
        )
        
        assert processed.shape[1] == 4
        assert processed.shape[0] <= 500  # Downsampled
    
    def test_invalid_input_raises_error(self):
        """Test that invalid input raises error"""
        points = np.array([]).reshape(0, 4)
        
        with pytest.raises(ValueError):
            preprocess_for_model(points)


class TestCalculateStatistics:
    """Test statistics calculation"""
    
    def test_statistics_calculation(self):
        """Test statistics calculation"""
        points = np.random.rand(100, 4).astype(np.float32)
        stats = calculate_point_cloud_statistics(points)
        
        assert 'num_points' in stats
        assert stats['num_points'] == 100
        assert 'x_range' in stats
        assert 'y_range' in stats
        assert 'z_range' in stats
        assert 'x_mean' in stats
        assert 'intensity_mean' in stats


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
