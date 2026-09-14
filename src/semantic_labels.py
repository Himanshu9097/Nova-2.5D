"""
Semantic Labels Module for LiDAR Point Cloud Segmentation

This module defines the semantic classes for SemanticKITTI dataset and provides
utilities for working with semantic labels, including default importance values.
"""

from typing import Dict, List, Optional
import numpy as np


# SemanticKITTI label definitions (19 classes + ignored)
SEMANTICKITTI_LABELS = {
    0: "road",
    1: "sidewalk", 
    2: "building",
    3: "wall",
    4: "fence",
    5: "pole",
    6: "traffic light",
    7: "traffic sign",
    8: "vegetation",
    9: "terrain",
    10: "sky",
    11: "person",
    12: "rider",
    13: "car",
    14: "truck",
    15: "bus",
    16: "train",
    17: "motorcycle",
    18: "bicycle"
}

# torch-pointcloud RandLA-Net SemanticKITTI labels (19 classes)
TORCH_POINTCLOUD_RANDLANET_LABELS = {
    0: "car",
    1: "bicycle",
    2: "motorcycle",
    3: "truck",
    4: "other-vehicle",
    5: "person",
    6: "bicyclist",
    7: "motorcyclist",
    8: "road",
    9: "parking",
    10: "sidewalk",
    11: "other-ground",
    12: "building",
    13: "fence",
    14: "vegetation",
    15: "trunk",
    16: "terrain",
    17: "pole",
    18: "traffic-sign"
}

# Learnable/ignored label
LEARNABLE_IGNORE_INDEX = 0


# Default semantic importance values for adaptive resolution
# Higher values indicate regions needing higher resolution
DEFAULT_SEMANTIC_IMPORTANCE = {
    # Dynamic objects (highest importance)
    "car": 1.0,
    "bicycle": 1.0,
    "motorcycle": 1.0,
    "truck": 1.0,
    "other-vehicle": 1.0,
    "person": 1.0,
    "bicyclist": 1.0,
    "motorcyclist": 1.0,
    
    # Traffic infrastructure (high importance)
    "traffic-sign": 0.9,
    "pole": 0.8,
    
    # Static infrastructure (medium importance)
    "building": 0.5,
    "fence": 0.4,
    "trunk": 0.4,
    
    # Ground surfaces (low-medium importance)
    "road": 0.3,
    "parking": 0.4,
    "sidewalk": 0.4,
    "other-ground": 0.3,
    "terrain": 0.3,
    
    # Natural elements (low importance)
    "vegetation": 0.4,
    
    # Unknown classes
    "unknown": 0.1,
    "uncertain": 0.1,
    
    # Legacy class names for compatibility
    "wall": 0.4,
    "traffic light": 0.9,
    "sky": 0.1,
    "rider": 1.0,
    "bus": 1.0,
    "train": 0.9
}


# Color mapping for visualization (RGB)
CLASS_COLORS = {
    # Dynamic objects
    "car": [0, 0, 142],
    "bicycle": [119, 11, 32],
    "motorcycle": [0, 0, 230],
    "truck": [0, 0, 70],
    "other-vehicle": [0, 60, 100],
    "person": [220, 20, 60],
    "bicyclist": [255, 0, 0],
    "motorcyclist": [200, 0, 0],
    
    # Traffic infrastructure
    "traffic-sign": [220, 220, 0],
    "pole": [153, 153, 153],
    
    # Static infrastructure
    "building": [70, 70, 70],
    "fence": [190, 153, 153],
    "trunk": [110, 110, 110],
    
    # Ground surfaces
    "road": [128, 64, 128],
    "parking": [150, 100, 100],
    "sidewalk": [244, 35, 232],
    "other-ground": [152, 251, 152],
    "terrain": [152, 251, 152],
    
    # Natural elements
    "vegetation": [107, 142, 35],
    
    # Unknown classes
    "unknown": [50, 50, 50],
    "uncertain": [100, 100, 100],
    
    # Legacy class names for compatibility
    "wall": [102, 102, 156],
    "traffic light": [250, 170, 30],
    "sky": [70, 130, 180],
    "rider": [255, 0, 0],
    "bus": [0, 60, 100],
    "train": [0, 80, 100]
}


def get_label_to_names(label_set: str = "semantickitti") -> Dict[int, str]:
    """
    Get the mapping from label indices to semantic class names.
    
    Args:
        label_set: Which label set to use ("semantickitti" or "torch_pointcloud")
        
    Returns:
        Dictionary mapping label indices to class names
    """
    if label_set == "torch_pointcloud":
        return TORCH_POINTCLOUD_RANDLANET_LABELS.copy()
    return SEMANTICKITTI_LABELS.copy()


def get_name_to_label() -> Dict[str, int]:
    """
    Get the mapping from semantic class names to label indices.
    
    Returns:
        Dictionary mapping class names to label indices
    """
    return {v: k for k, v in SEMANTICKITTI_LABELS.items()}


def get_semantic_importance(class_name: str, importance_config: Optional[Dict[str, float]] = None) -> float:
    """
    Get the semantic importance value for a given class.
    
    Args:
        class_name: Semantic class name
        importance_config: Optional custom importance configuration
        
    Returns:
        Importance value (0.0 to 1.0)
    """
    if importance_config is None:
        importance_config = DEFAULT_SEMANTIC_IMPORTANCE
    
    # Return configured importance or default for unknown classes
    return importance_config.get(class_name.lower(), importance_config.get("unknown", 0.1))


def get_class_color(class_name: str) -> List[int]:
    """
    Get the RGB color for visualization of a semantic class.
    
    Args:
        class_name: Semantic class name
        
    Returns:
        RGB color as list of integers [R, G, B]
    """
    return CLASS_COLORS.get(class_name.lower(), CLASS_COLORS["unknown"])


def map_labels_to_names(labels: np.ndarray, label_mapping: Optional[Dict[int, str]] = None) -> List[str]:
    """
    Convert label indices to semantic class names.
    
    Args:
        labels: Array of label indices
        label_mapping: Optional custom label mapping
        
    Returns:
        List of semantic class names
    """
    if label_mapping is None:
        label_mapping = get_label_to_names()
    return [label_mapping.get(int(label), "unknown") for label in labels]


def map_names_to_labels(class_names: List[str]) -> np.ndarray:
    """
    Convert semantic class names to label indices.
    
    Args:
        class_names: List of semantic class names
        
    Returns:
        Array of label indices
    """
    name_to_label = get_name_to_label()
    return np.array([name_to_label.get(name.lower(), 0) for name in class_names])


def calculate_importance_scores(class_names: List[str], 
                               importance_config: Optional[Dict[str, float]] = None) -> np.ndarray:
    """
    Calculate semantic importance scores for a list of class names.
    
    Args:
        class_names: List of semantic class names
        importance_config: Optional custom importance configuration
        
    Returns:
        Array of importance scores
    """
    return np.array([get_semantic_importance(name, importance_config) for name in class_names])


def get_high_importance_classes(threshold: float = 0.8) -> List[str]:
    """
    Get classes with importance above a threshold.
    
    Args:
        threshold: Importance threshold (default 0.8)
        
    Returns:
        List of high-importance class names
    """
    return [cls for cls, imp in DEFAULT_SEMANTIC_IMPORTANCE.items() if imp >= threshold]


def get_dynamic_classes(label_set: str = "semantickitti") -> List[str]:
    """
    Get classes that represent dynamic objects (moving entities).
    
    Args:
        label_set: Which label set to use ("semantickitti" or "torch_pointcloud")
        
    Returns:
        List of dynamic class names
    """
    if label_set == "torch_pointcloud":
        return ["person", "bicyclist", "motorcyclist", "car", "bicycle", "motorcycle", "truck", "other-vehicle"]
    return ["person", "rider", "car", "truck", "bus", "train", "motorcycle", "bicycle"]


def get_static_classes() -> List[str]:
    """
    Get classes that represent static objects (infrastructure).
    
    Returns:
        List of static class names
    """
    return ["road", "sidewalk", "building", "wall", "fence", "pole", 
            "traffic light", "traffic sign", "vegetation", "terrain"]


def get_num_classes() -> int:
    """
    Get the total number of semantic classes.
    
    Returns:
        Number of semantic classes
    """
    return len(SEMANTICKITTI_LABELS)


def validate_importance_config(importance_config: Dict[str, float]) -> bool:
    """
    Validate a custom importance configuration.
    
    Args:
        importance_config: Dictionary mapping class names to importance values
        
    Returns:
        True if configuration is valid, False otherwise
    """
    for class_name, value in importance_config.items():
        if not isinstance(value, (int, float)):
            return False
        if value < 0.0 or value > 1.0:
            return False
    
    return True


def get_class_statistics(class_names: List[str]) -> Dict[str, int]:
    """
    Get statistics about class distribution.
    
    Args:
        class_names: List of semantic class names
        
    Returns:
        Dictionary with class counts
    """
    stats = {}
    for name in class_names:
        stats[name] = stats.get(name, 0) + 1
    return stats
