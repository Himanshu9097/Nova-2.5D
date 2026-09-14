"""
Semantic Importance Calculation Module

This module calculates semantic importance values for adaptive resolution mapping.
Higher importance values indicate regions that need higher resolution processing.
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from .semantic_labels import (
    get_semantic_importance,
    get_dynamic_classes,
    get_static_classes,
    DEFAULT_SEMANTIC_IMPORTANCE,
    validate_importance_config
)


class ImportanceCalculator:
    """
    Calculate semantic importance for adaptive resolution mapping.
    """
    
    def __init__(self, importance_config: Optional[Dict[str, float]] = None):
        """
        Initialize importance calculator.
        
        Args:
            importance_config: Custom importance configuration (class -> importance)
        """
        if importance_config is not None:
            if not validate_importance_config(importance_config):
                raise ValueError("Invalid importance configuration")
            self.importance_config = importance_config
        else:
            self.importance_config = DEFAULT_SEMANTIC_IMPORTANCE.copy()
    
    def calculate_importance(self, 
                            class_names: List[str],
                            confidences: Optional[np.ndarray] = None,
                            distance_weights: Optional[np.ndarray] = None) -> np.ndarray:
        """
        Calculate semantic importance scores for points.
        
        Args:
            class_names: List of semantic class names for each point
            confidences: Optional confidence scores for each prediction
            distance_weights: Optional distance-based weights (closer = higher importance)
            
        Returns:
            Array of importance scores (0.0 to 1.0)
        """
        # Base importance from semantic class
        base_importance = np.array([
            get_semantic_importance(name, self.importance_config) 
            for name in class_names
        ])
        
        # Adjust by confidence if provided
        if confidences is not None:
            # Higher confidence -> higher importance
            confidence_adjustment = confidences * 0.3  # 30% weight
            base_importance = base_importance * (0.7 + confidence_adjustment)
        
        # Adjust by distance if provided
        if distance_weights is not None:
            # Normalize distance weights to 0-1 range
            if distance_weights.max() > distance_weights.min():
                normalized_distance = (
                    (distance_weights - distance_weights.min()) / 
                    (distance_weights.max() - distance_weights.min())
                )
                # Closer points (higher distance weight) get higher importance
                distance_adjustment = normalized_distance * 0.2  # 20% weight
                base_importance = base_importance * (0.8 + distance_adjustment)
        
        # Clip to valid range
        base_importance = np.clip(base_importance, 0.0, 1.0)
        
        return base_importance
    
    def calculate_importance_for_dynamic_objects(self, 
                                                class_names: List[str],
                                                confidences: Optional[np.ndarray] = None) -> np.ndarray:
        """
        Calculate importance with emphasis on dynamic objects.
        
        Args:
            class_names: List of semantic class names
            confidences: Optional confidence scores
            
        Returns:
            Array of importance scores with dynamic object emphasis
        """
        dynamic_classes = get_dynamic_classes()
        
        # Boost importance for dynamic objects
        base_importance = self.calculate_importance(class_names, confidences)
        
        for i, class_name in enumerate(class_names):
            if class_name.lower() in [dc.lower() for dc in dynamic_classes]:
                # Boost dynamic objects by 20%
                base_importance[i] = min(1.0, base_importance[i] * 1.2)
        
        return base_importance
    
    def get_importance_thresholds(self, 
                                 num_levels: int = 3) -> List[float]:
        """
        Get importance thresholds for multi-level resolution.
        
        Args:
            num_levels: Number of resolution levels
            
        Returns:
            List of threshold values (ascending)
        """
        thresholds = np.linspace(0.0, 1.0, num_levels + 1)[1:]
        return thresholds.tolist()
    
    def assign_resolution_levels(self, 
                                importance_scores: np.ndarray,
                                num_levels: int = 3) -> np.ndarray:
        """
        Assign resolution levels based on importance scores.
        
        Args:
            importance_scores: Array of importance scores
            num_levels: Number of resolution levels (0 = lowest, num_levels-1 = highest)
            
        Returns:
            Array of resolution level indices
        """
        thresholds = self.get_importance_thresholds(num_levels)
        levels = np.zeros_like(importance_scores, dtype=int)
        
        for i, threshold in enumerate(thresholds):
            levels[importance_scores >= threshold] = i + 1
        
        return levels
    
    def get_high_importance_regions(self,
                                   importance_scores: np.ndarray,
                                   threshold: float = 0.7) -> np.ndarray:
        """
        Identify high-importance regions.
        
        Args:
            importance_scores: Array of importance scores
            threshold: Importance threshold
            
        Returns:
            Boolean mask for high-importance points
        """
        return importance_scores >= threshold
    
    def calculate_importance_statistics(self, 
                                       importance_scores: np.ndarray) -> Dict:
        """
        Calculate statistics about importance distribution.
        
        Args:
            importance_scores: Array of importance scores
            
        Returns:
            Dictionary with statistics
        """
        return {
            'mean_importance': float(np.mean(importance_scores)),
            'std_importance': float(np.std(importance_scores)),
            'min_importance': float(np.min(importance_scores)),
            'max_importance': float(np.max(importance_scores)),
            'median_importance': float(np.median(importance_scores)),
            'high_importance_ratio': float(np.mean(importance_scores >= 0.7)),
            'low_importance_ratio': float(np.mean(importance_scores <= 0.3))
        }


def calculate_semantic_importance(class_names: List[str],
                                 importance_config: Optional[Dict[str, float]] = None) -> np.ndarray:
    """
    Simple function to calculate semantic importance from class names.
    
    Args:
        class_names: List of semantic class names
        importance_config: Optional custom importance configuration
        
    Returns:
        Array of importance scores
    """
    calculator = ImportanceCalculator(importance_config)
    return calculator.calculate_importance(class_names)


def combine_importance_factors(base_importance: np.ndarray,
                              confidence: np.ndarray,
                              distance: Optional[np.ndarray] = None,
                              weights: Dict[str, float] = None) -> np.ndarray:
    """
    Combine multiple importance factors.
    
    Args:
        base_importance: Base semantic importance
        confidence: Confidence scores
        distance: Optional distance-based importance
        weights: Weights for each factor (default: base=0.5, confidence=0.3, distance=0.2)
        
    Returns:
        Combined importance scores
    """
    if weights is None:
        weights = {'base': 0.5, 'confidence': 0.3, 'distance': 0.2}
    
    # Normalize weights
    total_weight = sum(weights.values())
    normalized_weights = {k: v / total_weight for k, v in weights.items()}
    
    # Calculate combined importance
    combined = (
        base_importance * normalized_weights['base'] +
        confidence * normalized_weights['confidence']
    )
    
    if distance is not None:
        combined += distance * normalized_weights['distance']
    
    return np.clip(combined, 0.0, 1.0)


def adaptive_sampling(importance_scores: np.ndarray,
                     target_points: int,
                     points: np.ndarray) -> np.ndarray:
    """
    Perform adaptive sampling based on importance scores.
    
    Higher importance regions are sampled more densely.
    
    Args:
        importance_scores: Array of importance scores
        target_points: Target number of points
        points: Original point cloud
        
    Returns:
        Adaptively sampled point cloud
    """
    num_points = points.shape[0]
    
    if num_points <= target_points:
        return points
    
    # Calculate sampling probability proportional to importance
    sampling_prob = importance_scores / np.sum(importance_scores)
    
    # Sample points
    sampled_indices = np.random.choice(
        num_points, 
        size=target_points, 
        replace=False, 
        p=sampling_prob
    )
    
    return points[sampled_indices]


def get_importance_by_class(class_names: List[str],
                            importance_config: Optional[Dict[str, float]] = None) -> Dict[str, float]:
    """
    Get importance values grouped by class.
    
    Args:
        class_names: List of semantic class names
        importance_config: Optional custom importance configuration
        
    Returns:
        Dictionary mapping class names to mean importance
    """
    from collections import defaultdict
    
    class_scores = defaultdict(list)
    
    for name in class_names:
        score = get_semantic_importance(name, importance_config)
        class_scores[name].append(score)
    
    return {cls: np.mean(scores) for cls, scores in class_scores.items()}


def compare_importance_configurations(class_names: List[str],
                                     config1: Dict[str, float],
                                     config2: Dict[str, float]) -> Dict:
    """
    Compare two importance configurations.
    
    Args:
        class_names: List of semantic class names
        config1: First importance configuration
        config2: Second importance configuration
        
    Returns:
        Dictionary with comparison statistics
    """
    importance1 = [get_semantic_importance(name, config1) for name in class_names]
    importance2 = [get_semantic_importance(name, config2) for name in class_names]
    
    diff = np.array(importance2) - np.array(importance1)
    
    return {
        'mean_difference': float(np.mean(diff)),
        'std_difference': float(np.std(diff)),
        'max_increase': float(np.max(diff)),
        'max_decrease': float(np.min(diff)),
        'classes_with_increase': int(np.sum(diff > 0)),
        'classes_with_decrease': int(np.sum(diff < 0))
    }
