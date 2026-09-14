"""
IO Utilities Module for Point Cloud Data

This module handles loading and saving point cloud data in various formats
(.bin, .pcd, .ply) and exporting semantic segmentation results.
"""

import numpy as np
import pandas as pd
import json
from pathlib import Path
from typing import Union, Optional, Dict, List
import struct


def load_bin_file(file_path: Union[str, Path]) -> np.ndarray:
    """
    Load point cloud from .bin file (SemanticKITTI format).
    
    SemanticKITTI .bin format: float32 values for x, y, z, intensity
    
    Args:
        file_path: Path to .bin file
        
    Returns:
        Point cloud as numpy array (N x 4)
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    points = np.fromfile(file_path, dtype=np.float32)
    
    # Reshape to (N, 4) - SemanticKITTI format
    if points.size % 4 != 0:
        raise ValueError(f"Invalid .bin file: number of values ({points.size}) is not divisible by 4")
    
    points = points.reshape(-1, 4)
    
    return points


def save_bin_file(points: np.ndarray, file_path: Union[str, Path]) -> None:
    """
    Save point cloud to .bin file (SemanticKITTI format).
    
    Args:
        points: Point cloud array (N x 4)
        file_path: Path to save .bin file
    """
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Ensure 4 channels
    if points.shape[1] != 4:
        raise ValueError(f"Points must have 4 channels, got {points.shape[1]}")
    
    points.astype(np.float32).tofile(file_path)


def load_pcd_file(file_path: Union[str, Path]) -> np.ndarray:
    """
    Load point cloud from .pcd file.
    
    Args:
        file_path: Path to .pcd file
        
    Returns:
        Point cloud as numpy array (N x 4)
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    try:
        import open3d as o3d
        pcd = o3d.io.read_point_cloud(str(file_path))
        points = np.asarray(pcd.points)
        
        # Try to get intensity if available
        colors = np.asarray(pcd.colors)
        if colors.shape[0] == points.shape[0]:
            # Convert RGB to intensity (grayscale)
            intensity = np.mean(colors, axis=1)
            points = np.column_stack([points, intensity])
        else:
            # Add default intensity
            points = np.column_stack([points, np.ones(points.shape[0]) * 0.5])
        
        return points
        
    except ImportError:
        # Fallback: try to parse ASCII PCD format
        return load_pcd_ascii(file_path)


def load_pcd_ascii(file_path: Path) -> np.ndarray:
    """
    Load ASCII .pcd file (fallback when Open3D is not available).
    
    Args:
        file_path: Path to .pcd file
        
    Returns:
        Point cloud as numpy array (N x 4)
    """
    points = []
    
    with open(file_path, 'r') as f:
        data_started = False
        for line in f:
            line = line.strip()
            
            if line.startswith('DATA'):
                data_started = True
                continue
            
            if data_started and line:
                values = line.split()
                if len(values) >= 3:
                    x, y, z = float(values[0]), float(values[1]), float(values[2])
                    intensity = float(values[3]) if len(values) > 3 else 0.5
                    points.append([x, y, z, intensity])
    
    if not points:
        raise ValueError(f"No point data found in {file_path}")
    
    return np.array(points, dtype=np.float32)


def save_pcd_file(points: np.ndarray, file_path: Union[str, Path]) -> None:
    """
    Save point cloud to .pcd file.
    
    Args:
        points: Point cloud array (N x 4)
        file_path: Path to save .pcd file
    """
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        import open3d as o3d
        
        pcd = o3d.geometry.PointCloud()
        pcd.points = o3d.utility.Vector3dVector(points[:, :3])
        
        # Add intensity as color
        if points.shape[1] >= 4:
            intensity = points[:, 3]
            # Convert intensity to grayscale RGB
            colors = np.column_stack([intensity, intensity, intensity])
            pcd.colors = o3d.utility.Vector3dVector(colors)
        
        o3d.io.write_point_cloud(str(file_path), pcd)
        
    except ImportError:
        # Fallback: save as ASCII PCD
        save_pcd_ascii(points, file_path)


def save_pcd_ascii(points: np.ndarray, file_path: Path) -> None:
    """
    Save point cloud as ASCII .pcd file (fallback).
    
    Args:
        points: Point cloud array (N x 4)
        file_path: Path to save .pcd file
    """
    with open(file_path, 'w') as f:
        # Write PCD header
        f.write("# .PCD v0.7 - Point Cloud Data file format\n")
        f.write("VERSION 0.7\n")
        f.write("FIELDS x y z intensity\n")
        f.write("SIZE 4 4 4 4\n")
        f.write("TYPE F F F F\n")
        f.write("COUNT 1 1 1 1\n")
        f.write(f"WIDTH {points.shape[0]}\n")
        f.write("HEIGHT 1\n")
        f.write("VIEWPOINT 0 0 0 1 0 0 0\n")
        f.write(f"POINTS {points.shape[0]}\n")
        f.write("DATA ascii\n")
        
        # Write point data
        for point in points:
            f.write(f"{point[0]:.6f} {point[1]:.6f} {point[2]:.6f} {point[3]:.6f}\n")


def load_ply_file(file_path: Union[str, Path]) -> np.ndarray:
    """
    Load point cloud from .ply file.
    
    Args:
        file_path: Path to .ply file
        
    Returns:
        Point cloud as numpy array (N x 4)
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    try:
        import open3d as o3d
        pcd = o3d.io.read_point_cloud(str(file_path))
        points = np.asarray(pcd.points)
        
        # Try to get intensity from colors or other attributes
        colors = np.asarray(pcd.colors)
        if colors.shape[0] == points.shape[0]:
            intensity = np.mean(colors, axis=1)
            points = np.column_stack([points, intensity])
        else:
            points = np.column_stack([points, np.ones(points.shape[0]) * 0.5])
        
        return points
        
    except ImportError:
        # Fallback: try to parse ASCII PLY format
        return load_ply_ascii(file_path)


def load_ply_ascii(file_path: Path) -> np.ndarray:
    """
    Load ASCII .ply file (fallback when Open3D is not available).
    
    Args:
        file_path: Path to .ply file
        
    Returns:
        Point cloud as numpy array (N x 4)
    """
    points = []
    vertex_count = 0
    header_ended = False
    
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            
            if line.startswith('element vertex'):
                vertex_count = int(line.split()[2])
            
            if line == 'end_header':
                header_ended = True
                continue
            
            if header_ended and line:
                values = line.split()
                if len(values) >= 3:
                    x, y, z = float(values[0]), float(values[1]), float(values[2])
                    intensity = float(values[3]) if len(values) > 3 else 0.5
                    points.append([x, y, z, intensity])
    
    if not points:
        raise ValueError(f"No point data found in {file_path}")
    
    return np.array(points, dtype=np.float32)


def save_ply_file(points: np.ndarray, file_path: Union[str, Path]) -> None:
    """
    Save point cloud to .ply file.
    
    Args:
        points: Point cloud array (N x 4)
        file_path: Path to save .ply file
    """
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        import open3d as o3d
        
        pcd = o3d.geometry.PointCloud()
        pcd.points = o3d.utility.Vector3dVector(points[:, :3])
        
        if points.shape[1] >= 4:
            intensity = points[:, 3]
            colors = np.column_stack([intensity, intensity, intensity])
            pcd.colors = o3d.utility.Vector3dVector(colors)
        
        o3d.io.write_point_cloud(str(file_path), pcd)
        
    except ImportError:
        # Fallback: save as ASCII PLY
        save_ply_ascii(points, file_path)


def save_ply_ascii(points: np.ndarray, file_path: Path) -> None:
    """
    Save point cloud as ASCII .ply file (fallback).
    
    Args:
        points: Point cloud array (N x 4)
        file_path: Path to save .ply file
    """
    with open(file_path, 'w') as f:
        # Write PLY header
        f.write("ply\n")
        f.write("format ascii 1.0\n")
        f.write(f"element vertex {points.shape[0]}\n")
        f.write("property float x\n")
        f.write("property float y\n")
        f.write("property float z\n")
        f.write("property float intensity\n")
        f.write("end_header\n")
        
        # Write point data
        for point in points:
            f.write(f"{point[0]:.6f} {point[1]:.6f} {point[2]:.6f} {point[3]:.6f}\n")


def load_point_cloud(file_path: Union[str, Path]) -> np.ndarray:
    """
    Load point cloud from file (auto-detect format).
    
    Supported formats: .bin, .pcd, .ply
    
    Args:
        file_path: Path to point cloud file
        
    Returns:
        Point cloud as numpy array (N x 4)
    """
    file_path = Path(file_path)
    suffix = file_path.suffix.lower()
    
    if suffix == '.bin':
        return load_bin_file(file_path)
    elif suffix == '.pcd':
        return load_pcd_file(file_path)
    elif suffix == '.ply':
        return load_ply_file(file_path)
    else:
        raise ValueError(f"Unsupported file format: {suffix}. Supported: .bin, .pcd, .ply")


def save_point_cloud(points: np.ndarray, file_path: Union[str, Path]) -> None:
    """
    Save point cloud to file (auto-detect format from extension).
    
    Supported formats: .bin, .pcd, .ply
    
    Args:
        points: Point cloud array (N x 4)
        file_path: Path to save point cloud file
    """
    file_path = Path(file_path)
    suffix = file_path.suffix.lower()
    
    if suffix == '.bin':
        save_bin_file(points, file_path)
    elif suffix == '.pcd':
        save_pcd_file(points, file_path)
    elif suffix == '.ply':
        save_ply_file(points, file_path)
    else:
        raise ValueError(f"Unsupported file format: {suffix}. Supported: .bin, .pcd, .ply")


def export_semantic_results_to_csv(results: List[Dict], output_path: Union[str, Path]) -> None:
    """
    Export semantic segmentation results to CSV file.
    
    Args:
        results: List of result dictionaries with keys: x, y, z, intensity, 
                 semantic_class, semantic_label, confidence, semantic_importance
        output_path: Path to save CSV file
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    df = pd.DataFrame(results)
    df.to_csv(output_path, index=False)


def export_semantic_results_to_json(results: List[Dict], output_path: Union[str, Path]) -> None:
    """
    Export semantic segmentation results to JSON file.
    
    Args:
        results: List of result dictionaries
        output_path: Path to save JSON file
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)


def load_semantic_results_from_json(input_path: Union[str, Path]) -> List[Dict]:
    """
    Load semantic segmentation results from JSON file.
    
    Args:
        input_path: Path to JSON file
        
    Returns:
        List of result dictionaries
    """
    input_path = Path(input_path)
    
    if not input_path.exists():
        raise FileNotFoundError(f"File not found: {input_path}")
    
    with open(input_path, 'r') as f:
        results = json.load(f)
    
    return results


def create_sample_point_cloud(num_points: int = 1000, 
                             seed: Optional[int] = None) -> np.ndarray:
    """
    Create a synthetic point cloud for testing.
    
    Args:
        num_points: Number of points to generate
        seed: Random seed for reproducibility
        
    Returns:
        Synthetic point cloud (N x 4)
    """
    if seed is not None:
        np.random.seed(seed)
    
    # Generate random points in a 50x50x5 meter volume
    points = np.random.rand(num_points, 4)
    points[:, 0] = points[:, 0] * 100 - 50  # x: -50 to 50
    points[:, 1] = points[:, 1] * 100 - 50  # y: -50 to 50
    points[:, 2] = points[:, 2] * 10 - 5   # z: -5 to 5
    points[:, 3] = points[:, 3]  # intensity: 0 to 1
    
    return points.astype(np.float32)


def get_supported_formats() -> List[str]:
    """
    Get list of supported point cloud file formats.
    
    Returns:
        List of supported file extensions
    """
    return ['.bin', '.pcd', '.ply']


def is_supported_format(file_path: Union[str, Path]) -> bool:
    """
    Check if file format is supported.
    
    Args:
        file_path: Path to file
        
    Returns:
        True if format is supported, False otherwise
    """
    file_path = Path(file_path)
    return file_path.suffix.lower() in get_supported_formats()
