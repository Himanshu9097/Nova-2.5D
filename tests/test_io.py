"""
Unit tests for IO utilities module
"""

import pytest
import numpy as np
import sys
import json
import pandas as pd
from pathlib import Path
import tempfile

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.io_utils import (
    load_bin_file,
    save_bin_file,
    load_pcd_file,
    save_pcd_file,
    load_ply_file,
    save_ply_file,
    load_point_cloud,
    save_point_cloud,
    export_semantic_results_to_csv,
    export_semantic_results_to_json,
    load_semantic_results_from_json,
    create_sample_point_cloud,
    get_supported_formats,
    is_supported_format
)


class TestBinFileOperations:
    """Test .bin file operations"""
    
    def test_save_and_load_bin(self):
        """Test saving and loading .bin file"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test data
            points = np.random.rand(100, 4).astype(np.float32)
            file_path = Path(tmpdir) / "test.bin"
            
            # Save
            save_bin_file(points, file_path)
            assert file_path.exists()
            
            # Load
            loaded = load_bin_file(file_path)
            
            np.testing.assert_array_almost_equal(points, loaded)
    
    def test_load_nonexistent_bin(self):
        """Test loading nonexistent .bin file"""
        with pytest.raises(FileNotFoundError):
            load_bin_file("nonexistent.bin")
    
    def test_invalid_bin_format(self):
        """Test loading invalid .bin file"""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "invalid.bin"
            
            # Create invalid file (wrong number of values)
            invalid_data = np.random.rand(10).astype(np.float32)  # Not divisible by 4
            invalid_data.tofile(file_path)
            
            with pytest.raises(ValueError):
                load_bin_file(file_path)


class TestPCDFileOperations:
    """Test .pcd file operations"""
    
    def test_save_and_load_pcd(self):
        """Test saving and loading .pcd file"""
        with tempfile.TemporaryDirectory() as tmpdir:
            points = np.random.rand(100, 4).astype(np.float32)
            file_path = Path(tmpdir) / "test.pcd"
            
            # Save
            save_pcd_file(points, file_path)
            assert file_path.exists()
            
            # Load
            loaded = load_pcd_file(file_path)
            
            # Check shape (may have different point count due to sampling)
            assert loaded.shape[1] == 4
            assert loaded.shape[0] > 0


class TestPlyFileOperations:
    """Test .ply file operations"""
    
    def test_save_and_load_ply(self):
        """Test saving and loading .ply file"""
        with tempfile.TemporaryDirectory() as tmpdir:
            points = np.random.rand(100, 4).astype(np.float32)
            file_path = Path(tmpdir) / "test.ply"
            
            # Save
            save_ply_file(points, file_path)
            assert file_path.exists()
            
            # Load
            loaded = load_ply_file(file_path)
            
            # Check shape
            assert loaded.shape[1] == 4
            assert loaded.shape[0] > 0


class TestLoadPointCloud:
    """Test generic point cloud loading"""
    
    def test_load_bin_auto_detect(self):
        """Test auto-detection of .bin format"""
        with tempfile.TemporaryDirectory() as tmpdir:
            points = np.random.rand(100, 4).astype(np.float32)
            file_path = Path(tmpdir) / "test.bin"
            save_bin_file(points, file_path)
            
            loaded = load_point_cloud(file_path)
            np.testing.assert_array_almost_equal(points, loaded)
    
    def test_load_unsupported_format(self):
        """Test loading unsupported format"""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test.xyz"
            file_path.write_text("fake data")
            
            with pytest.raises(ValueError):
                load_point_cloud(file_path)


class TestSavePointCloud:
    """Test generic point cloud saving"""
    
    def test_save_bin_auto_detect(self):
        """Test auto-detection for saving .bin"""
        with tempfile.TemporaryDirectory() as tmpdir:
            points = np.random.rand(100, 4).astype(np.float32)
            file_path = Path(tmpdir) / "test.bin"
            
            save_point_cloud(points, file_path)
            assert file_path.exists()
            
            loaded = load_bin_file(file_path)
            np.testing.assert_array_almost_equal(points, loaded)


class TestExportSemanticResults:
    """Test semantic results export"""
    
    def test_export_to_csv(self):
        """Test exporting results to CSV"""
        with tempfile.TemporaryDirectory() as tmpdir:
            results = [
                {'x': 1.0, 'y': 2.0, 'z': 3.0, 'intensity': 0.5, 
                 'semantic_class': 'car', 'semantic_label': 13, 
                 'confidence': 0.9, 'semantic_importance': 1.0},
                {'x': 4.0, 'y': 5.0, 'z': 6.0, 'intensity': 0.7,
                 'semantic_class': 'road', 'semantic_label': 0,
                 'confidence': 0.8, 'semantic_importance': 0.3}
            ]
            
            file_path = Path(tmpdir) / "results.csv"
            export_semantic_results_to_csv(results, file_path)
            
            assert file_path.exists()
            
            # Load and verify
            df = pd.read_csv(file_path)
            assert len(df) == 2
            assert 'semantic_class' in df.columns
            assert 'confidence' in df.columns
    
    def test_export_to_json(self):
        """Test exporting results to JSON"""
        with tempfile.TemporaryDirectory() as tmpdir:
            results = [
                {'x': 1.0, 'y': 2.0, 'z': 3.0, 'intensity': 0.5,
                 'semantic_class': 'car', 'semantic_label': 13,
                 'confidence': 0.9, 'semantic_importance': 1.0}
            ]
            
            file_path = Path(tmpdir) / "results.json"
            export_semantic_results_to_json(results, file_path)
            
            assert file_path.exists()
            
            # Load and verify
            loaded = load_semantic_results_from_json(file_path)
            assert len(loaded) == 1
            assert loaded[0]['semantic_class'] == 'car'
    
    def test_load_json_results(self):
        """Test loading JSON results"""
        with tempfile.TemporaryDirectory() as tmpdir:
            results = [
                {'x': 1.0, 'y': 2.0, 'z': 3.0, 'intensity': 0.5,
                 'semantic_class': 'car', 'semantic_label': 13,
                 'confidence': 0.9, 'semantic_importance': 1.0}
            ]
            
            file_path = Path(tmpdir) / "results.json"
            export_semantic_results_to_json(results, file_path)
            
            loaded = load_semantic_results_from_json(file_path)
            assert loaded == results
    
    def test_load_nonexistent_json(self):
        """Test loading nonexistent JSON file"""
        with pytest.raises(FileNotFoundError):
            load_semantic_results_from_json("nonexistent.json")


class TestCreateSamplePointCloud:
    """Test sample point cloud creation"""
    
    def test_create_sample(self):
        """Test creating sample point cloud"""
        points = create_sample_point_cloud(num_points=1000, seed=42)
        
        assert points.shape == (1000, 4)
        assert points.dtype == np.float32
    
    def test_create_sample_reproducibility(self):
        """Test that sample creation is reproducible with seed"""
        points1 = create_sample_point_cloud(num_points=100, seed=42)
        points2 = create_sample_point_cloud(num_points=100, seed=42)
        
        np.testing.assert_array_equal(points1, points2)
    
    def test_create_sample_different_seeds(self):
        """Test that different seeds produce different results"""
        points1 = create_sample_point_cloud(num_points=100, seed=42)
        points2 = create_sample_point_cloud(num_points=100, seed=43)
        
        assert not np.array_equal(points1, points2)


class TestFormatUtilities:
    """Test format utility functions"""
    
    def test_get_supported_formats(self):
        """Test getting supported formats"""
        formats = get_supported_formats()
        
        assert '.bin' in formats
        assert '.pcd' in formats
        assert '.ply' in formats
    
    def test_is_supported_format(self):
        """Test format checking"""
        assert is_supported_format("test.bin")
        assert is_supported_format("test.pcd")
        assert is_supported_format("test.ply")
        assert not is_supported_format("test.xyz")
        assert not is_supported_format("test.txt")


class TestInvalidChannelHandling:
    """Test handling of invalid channel counts"""
    
    def test_save_invalid_channels(self):
        """Test saving with wrong number of channels"""
        with tempfile.TemporaryDirectory() as tmpdir:
            points = np.random.rand(100, 3).astype(np.float32)  # Only 3 channels
            file_path = Path(tmpdir) / "test.bin"
            
            with pytest.raises(ValueError):
                save_bin_file(points, file_path)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
