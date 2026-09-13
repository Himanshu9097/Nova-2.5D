"""
Preprocessing Module for LiDAR Point Cloud Data

This module handles loading, validation, and preprocessing of point cloud data
from various formats (.bin, .pcd, .ply) for semantic segmentation.
"""

import numpy as np
from typing import Tuple, Optional, Union
import struct
import warnings


def validate_point_cloud(points: np.ndarray) -> Tuple[bool, str]:
    """
    Validate point cloud data structure and values.
    
    Args:
        points: Numpy array of point cloud data
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(points, np.ndarray):
        return False, "Input must be a numpy array"
    
    if points.ndim != 2:
        return False, f"Points must be 2D array, got {points.ndim}D"
    
    if points.shape[0] == 0:
        return False, "Point cloud is empty"
    
    if points.shape[1] < 3:
        return False, f"Points must have at least 3 coordinates (x,y,z), got {points.shape[1]}"
    
    # Check for NaN or Inf values
    if np.any(np.isnan(points)):
        return False, "Point cloud contains NaN values"
    
    if np.any(np.isinf(points)):
        return False, "Point cloud contains infinite values"
    
    return True, ""


def normalize_point_cloud(points: np.ndarray, 
                        method: str = "none",
                        target_range: Optional[Tuple[float, float]] = None) -> np.ndarray:
    """
    Normalize point cloud coordinates.
    
    Args:
        points: Point cloud array (N x 4+)
        method: Normalization method ('none', 'mean_std', 'min_max', 'range')
        target_range: Target range for min_max normalization (min, max)
        
    Returns:
        Normalized point cloud
    """
    points_normalized = points.copy()
    
    if method == "none":
        return points_normalized
    
    xyz = points_normalized[:, :3]
    
    if method == "mean_std":
        # Z-score normalization
        mean = np.mean(xyz, axis=0)
        std = np.std(xyz, axis=0)
        xyz = (xyz - mean) / (std + 1e-8)
        
    elif method == "min_max":
        # Min-max normalization
        if target_range is None:
            target_range = (0.0, 1.0)
        
        min_vals = np.min(xyz, axis=0)
        max_vals = np.max(xyz, axis=0)
        
        xyz = (xyz - min_vals) / (max_vals - min_vals + 1e-8)
        xyz = xyz * (target_range[1] - target_range[0]) + target_range[0]
        
    elif method == "range":
        # Range-based normalization
        ranges = np.max(xyz, axis=0) - np.min(xyz, axis=0)
        xyz = xyz / (ranges + 1e-8)
    
    else:
        warnings.warn(f"Unknown normalization method: {method}, using 'none'")
        return points_normalized
    
    points_normalized[:, :3] = xyz
    return points_normalized


def filter_point_cloud(points: np.ndarray,
                     min_range: float = -50.0,
                     max_range: float = 50.0,
                     min_z: float = -5.0,
                     max_z: float = 5.0) -> np.ndarray:
    """
    Filter points based on spatial ranges.
    
    Args:
        points: Point cloud array (N x 4+)
        min_range: Minimum x/y range
        max_range: Maximum x/y range
        min_z: Minimum z (height) value
        max_z: Maximum z (height) value
        
    Returns:
        Filtered point cloud
    """
    x, y, z = points[:, 0], points[:, 1], points[:, 2]
    
    mask = (x >= min_range) & (x <= max_range) & \
           (y >= min_range) & (y <= max_range) & \
           (z >= min_z) & (z <= max_z)
    
    return points[mask]


def downsample_point_cloud(points: np.ndarray,
                          target_num_points: Optional[int] = None,
                          voxel_size: Optional[float] = None) -> np.ndarray:
    """
    Downsample point cloud using random sampling or voxel grid.
    
    Args:
        points: Point cloud array (N x 4+)
        target_num_points: Target number of points for random sampling
        voxel_size: Voxel size for voxel grid downsampling
        
    Returns:
        Downsampled point cloud
    """
    if target_num_points is None and voxel_size is None:
        return points
    
    if target_num_points is not None:
        # Random sampling
        num_points = points.shape[0]
        if num_points <= target_num_points:
            return points
        
        indices = np.random.choice(num_points, target_num_points, replace=False)
        return points[indices]
    
    if voxel_size is not None:
        # Voxel grid downsampling
        try:
            import open3d as o3d
            
            # Convert to Open3D point cloud
            pcd = o3d.geometry.PointCloud()
            pcd.points = o3d.utility.Vector3dVector(points[:, :3])
            
            # Voxel downsample
            pcd_down = pcd.voxel_down_sample(voxel_size=voxel_size)
            
            # Convert back to numpy
            points_down = np.asarray(pcd_down.points)
            
            # Keep intensity if available
            if points.shape[1] > 3:
                # Simple approach: keep first point intensity per voxel
                # For more sophisticated approach, could use averaging
                warnings.warn("Intensity values may be imprecise after voxel downsampling")
                
            return points_down
            
        except ImportError:
            warnings.warn("Open3D not available, using random sampling instead")
            # Fallback to random sampling
            target_points = max(10000, points.shape[0] // 10)
            return downsample_point_cloud(points, target_num_points=target_points)
    
    return points


def add_intensity_if_missing(points: np.ndarray, default_intensity: float = 0.5) -> np.ndarray:
    """
    Add intensity channel if missing from point cloud.
    
    Args:
        points: Point cloud array (N x 3 or N x 4+)
        default_intensity: Default intensity value to use
        
    Returns:
        Point cloud with intensity channel (N x 4+)
    """
    if points.shape[1] >= 4:
        return points
    
    # Add intensity column
    points_with_intensity = np.zeros((points.shape[0], 4))
    points_with_intensity[:, :3] = points
    points_with_intensity[:, 3] = default_intensity
    
    return points_with_intensity


def ensure_4_channel(points: np.ndarray) -> np.ndarray:
    """
    Ensure point cloud has exactly 4 channels (x, y, z, intensity).
    
    Args:
        points: Point cloud array (N x 3+)
        
    Returns:
        Point cloud with exactly 4 channels
    """
    if points.shape[1] == 4:
        return points
    
    if points.shape[1] < 4:
        return add_intensity_if_missing(points)
    
    # Truncate if more than 4 channels
    return points[:, :4]


def preprocess_for_model(points: np.ndarray,
                       normalize: bool = False,
                       filter_range: bool = True,
                       downsample: bool = False,
                       target_points: Optional[int] = None) -> np.ndarray:
    """
    Complete preprocessing pipeline for model input.
    
    Args:
        points: Raw point cloud array
        normalize: Whether to normalize coordinates
        filter_range: Whether to filter by spatial range
        downsample: Whether to downsample points
        target_points: Target number of points if downsampling
        
    Returns:
        Preprocessed point cloud
    """
    # Validate input
    is_valid, error_msg = validate_point_cloud(points)
    if not is_valid:
        raise ValueError(f"Invalid point cloud: {error_msg}")
    
    # Ensure 4 channels
    points = ensure_4_channel(points)
    
    # Filter by range
    if filter_range:
        points = filter_point_cloud(points)
    
    # Normalize
    if normalize:
        points = normalize_point_cloud(points, method="mean_std")
    
    # Downsample
    if downsample and target_points is not None:
        points = downsample_point_cloud(points, target_num_points=target_points)
    
    return points


def split_train_val_test(points: np.ndarray,
                        train_ratio: float = 0.7,
                        val_ratio: float = 0.15,
                        test_ratio: float = 0.15,
                        random_seed: Optional[int] = None) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Split point cloud into train/validation/test sets.
    
    Args:
        points: Point cloud array
        train_ratio: Ratio for training set
        val_ratio: Ratio for validation set
        test_ratio: Ratio for test set
        random_seed: Random seed for reproducibility
        
    Returns:
        Tuple of (train_points, val_points, test_points)
    """
    if random_seed is not None:
        np.random.seed(random_seed)
    
    num_points = points.shape[0]
    indices = np.random.permutation(num_points)
    
    train_end = int(num_points * train_ratio)
    val_end = train_end + int(num_points * val_ratio)
    
    train_points = points[indices[:train_end]]
    val_points = points[indices[train_end:val_end]]
    test_points = points[indices[val_end:]]
    
    return train_points, val_points, test_points


def calculate_point_cloud_statistics(points: np.ndarray) -> dict:
    """
    Calculate statistics about the point cloud.
    
    Args:
        points: Point cloud array
        
    Returns:
        Dictionary with statistics
    """
    stats = {
        'num_points': points.shape[0],
        'num_features': points.shape[1],
        'x_range': (np.min(points[:, 0]), np.max(points[:, 0])),
        'y_range': (np.min(points[:, 1]), np.max(points[:, 1])),
        'z_range': (np.min(points[:, 2]), np.max(points[:, 2])),
        'x_mean': np.mean(points[:, 0]),
        'y_mean': np.mean(points[:, 1]),
        'z_mean': np.mean(points[:, 2]),
        'x_std': np.std(points[:, 0]),
        'y_std': np.std(points[:, 1]),
        'z_std': np.std(points[:, 2]),
    }
    
    if points.shape[1] >= 4:
        stats['intensity_range'] = (np.min(points[:, 3]), np.max(points[:, 3]))
        stats['intensity_mean'] = np.mean(points[:, 3])
        stats['intensity_std'] = np.std(points[:, 3])
    
    return stats
