"""
Unit tests for importance calculation module
"""

import pytest
import numpy as np
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.importance import (
    ImportanceCalculator,
    calculate_semantic_importance,
    combine_importance_factors,
    adaptive_sampling,
    get_importance_by_class
)

from src.semantic_labels import (
    DEFAULT_SEMANTIC_IMPORTANCE,
    get_dynamic_classes
)


class TestImportanceCalculator:
    """Test ImportanceCalculator class"""
    
    def test_initialization_default(self):
        """Test initialization with default config"""
        calc = ImportanceCalculator()
        assert calc.importance_config == DEFAULT_SEMANTIC_IMPORTANCE
    
    def test_initialization_custom(self):
        """Test initialization with custom config"""
        custom_config = {"car": 0.9, "road": 0.3}
        calc = ImportanceCalculator(custom_config)
        assert calc.importance_config == custom_config
    
    def test_invalid_config_raises_error(self):
        """Test that invalid config raises error"""
        invalid_config = {"car": 1.5}  # > 1.0
        
        with pytest.raises(ValueError):
            ImportanceCalculator(invalid_config)
    
    def test_calculate_importance(self):
        """Test importance calculation"""
        calc = ImportanceCalculator()
        class_names = ["car", "road", "person"]
        
        importance = calc.calculate_importance(class_names)
        
        assert len(importance) == 3
        assert importance[0] > importance[1]  # car > road
        assert importance[2] > importance[1]  # person > road
        assert np.all(importance >= 0) and np.all(importance <= 1)
    
    def test_calculate_importance_with_confidence(self):
        """Test importance calculation with confidence"""
        calc = ImportanceCalculator()
        class_names = ["car", "road"]
        confidences = np.array([0.9, 0.6])
        
        importance = calc.calculate_importance(class_names, confidences=confidences)
        
        # Higher confidence should give higher importance
        assert importance[0] > importance[1]
    
    def test_dynamic_object_emphasis(self):
        """Test dynamic object emphasis"""
        calc = ImportanceCalculator()
        class_names = ["car", "road", "person"]
        
        importance = calc.calculate_importance_for_dynamic_objects(class_names)
        
        # Dynamic objects should have boosted importance
        dynamic_classes = get_dynamic_classes()
        for i, name in enumerate(class_names):
            if name.lower() in [dc.lower() for dc in dynamic_classes]:
                assert importance[i] >= DEFAULT_SEMANTIC_IMPORTANCE.get(name, 0.5)
    
    def test_get_importance_thresholds(self):
        """Test importance threshold generation"""
        calc = ImportanceCalculator()
        thresholds = calc.get_importance_thresholds(num_levels=3)
        
        assert len(thresholds) == 3
        assert thresholds == sorted(thresholds)  # Should be ascending
        assert thresholds[0] > 0
        assert thresholds[-1] <= 1
    
    def test_assign_resolution_levels(self):
        """Test resolution level assignment"""
        calc = ImportanceCalculator()
        importance_scores = np.array([0.2, 0.5, 0.8, 0.9])
        
        levels = calc.assign_resolution_levels(importance_scores, num_levels=3)
        
        assert len(levels) == 4
        assert np.all(levels >= 0) and np.all(levels < 3)
        # Higher importance should get higher level
        assert levels[-1] >= levels[0]
    
    def test_get_high_importance_regions(self):
        """Test high importance region identification"""
        calc = ImportanceCalculator()
        importance_scores = np.array([0.2, 0.5, 0.8, 0.9])
        
        mask = calc.get_high_importance_regions(importance_scores, threshold=0.7)
        
        assert len(mask) == 4
        assert np.sum(mask) == 2  # 2 points above threshold
        assert mask[2] and mask[3]  # Last two should be True
        assert not mask[0] and not mask[1]  # First two should be False
    
    def test_importance_statistics(self):
        """Test importance statistics calculation"""
        calc = ImportanceCalculator()
        importance_scores = np.array([0.2, 0.5, 0.8, 0.9])
        
        stats = calc.calculate_importance_statistics(importance_scores)
        
        assert 'mean_importance' in stats
        assert 'std_importance' in stats
        assert 'min_importance' in stats
        assert 'max_importance' in stats
        assert stats['mean_importance'] == pytest.approx(0.6, rel=0.1)


class TestCalculateSemanticImportance:
    """Test simple importance calculation function"""
    
    def test_simple_calculation(self):
        """Test simple importance calculation"""
        class_names = ["car", "road", "person"]
        importance = calculate_semantic_importance(class_names)
        
        assert len(importance) == 3
        assert np.all(importance >= 0) and np.all(importance <= 1)


class TestCombineImportanceFactors:
    """Test importance factor combination"""
    
    def test_combine_base_and_confidence(self):
        """Test combining base importance and confidence"""
        base = np.array([0.5, 0.7, 0.3])
        confidence = np.array([0.9, 0.6, 0.8])
        
        combined = combine_importance_factors(base, confidence)
        
        assert len(combined) == 3
        assert np.all(combined >= 0) and np.all(combined <= 1)
    
    def test_combine_with_distance(self):
        """Test combining with distance factor"""
        base = np.array([0.5, 0.7])
        confidence = np.array([0.9, 0.6])
        distance = np.array([0.8, 0.3])
        
        combined = combine_importance_factors(base, confidence, distance)
        
        assert len(combined) == 2
        assert np.all(combined >= 0) and np.all(combined <= 1)
    
    def test_custom_weights(self):
        """Test custom weights for combination"""
        base = np.array([0.5, 0.7])
        confidence = np.array([0.9, 0.6])
        
        weights = {'base': 0.8, 'confidence': 0.2}
        combined = combine_importance_factors(base, confidence, weights=weights)
        
        # Should be closer to base due to higher weight
        assert np.allclose(combined, base * 0.8 + confidence * 0.2)


class TestAdaptiveSampling:
    """Test adaptive sampling based on importance"""
    
    def test_adaptive_sampling(self):
        """Test adaptive sampling"""
        points = np.random.rand(1000, 4).astype(np.float32)
        importance = np.array([0.5] * 500 + [0.9] * 500)  # Higher importance for second half
        
        sampled = adaptive_sampling(importance, target_points=100, points=points)
        
        assert sampled.shape[0] == 100
        assert sampled.shape[1] == 4
    
    def test_no_sampling_needed(self):
        """Test when no sampling is needed"""
        points = np.random.rand(50, 4).astype(np.float32)
        importance = np.random.rand(50)
        
        sampled = adaptive_sampling(importance, target_points=100, points=points)
        
        # Should return original if already under target
        assert sampled.shape[0] == 50


class TestGetImportanceByClass:
    """Test importance grouping by class"""
    
    def test_importance_by_class(self):
        """Test getting importance by class"""
        class_names = ["car", "road", "car", "person", "road"]
        
        importance_dict = get_importance_by_class(class_names)
        
        assert "car" in importance_dict
        assert "road" in importance_dict
        assert "person" in importance_dict
        assert all(0 <= v <= 1 for v in importance_dict.values())


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
