"""
Semantic Perception Module for LiDAR Point Clouds

This module provides semantic segmentation capabilities for LiDAR point clouds
using pretrained models, with support for confidence estimation and semantic
importance calculation for adaptive resolution mapping.
"""

from .inference import (
    SemanticSegmentationModel,
    semantic_inference,
    batch_inference,
    create_synthetic_predictions
)

from .preprocessing import (
    validate_point_cloud,
    normalize_point_cloud,
    filter_point_cloud,
    downsample_point_cloud,
    preprocess_for_model,
    calculate_point_cloud_statistics
)

from .semantic_labels import (
    get_label_to_names,
    get_name_to_label,
    get_semantic_importance,
    get_class_color,
    map_labels_to_names,
    map_names_to_labels,
    calculate_importance_scores,
    get_high_importance_classes,
    get_dynamic_classes,
    get_static_classes,
    get_num_classes,
    DEFAULT_SEMANTIC_IMPORTANCE
)

from .importance import (
    ImportanceCalculator,
    calculate_semantic_importance,
    combine_importance_factors,
    adaptive_sampling
)

from .io_utils import (
    load_point_cloud,
    save_point_cloud,
    load_bin_file,
    save_bin_file,
    load_pcd_file,
    save_pcd_file,
    load_ply_file,
    save_ply_file,
    export_semantic_results_to_csv,
    export_semantic_results_to_json,
    load_semantic_results_from_json,
    create_sample_point_cloud,
    get_supported_formats,
    is_supported_format
)

from .visualization import (
    visualize_point_cloud_3d,
    visualize_semantic_point_cloud,
    visualize_importance_heatmap,
    visualize_confidence_distribution,
    visualize_class_distribution,
    create_class_legend,
    visualize_comparison,
    visualize_with_open3d,
    create_summary_statistics,
    visualize_metrics_dashboard
)

__version__ = "1.0.0"
__author__ = "Vivek - SIH 2026 Team"

__all__ = [
    # Inference
    'SemanticSegmentationModel',
    'semantic_inference',
    'batch_inference',
    'create_synthetic_predictions',
    
    # Preprocessing
    'validate_point_cloud',
    'normalize_point_cloud',
    'filter_point_cloud',
    'downsample_point_cloud',
    'preprocess_for_model',
    'calculate_point_cloud_statistics',
    
    # Semantic Labels
    'get_label_to_names',
    'get_name_to_label',
    'get_semantic_importance',
    'get_class_color',
    'map_labels_to_names',
    'map_names_to_labels',
    'calculate_importance_scores',
    'get_high_importance_classes',
    'get_dynamic_classes',
    'get_static_classes',
    'get_num_classes',
    'DEFAULT_SEMANTIC_IMPORTANCE',
    
    # Importance
    'ImportanceCalculator',
    'calculate_semantic_importance',
    'combine_importance_factors',
    'adaptive_sampling',
    
    # IO Utilities
    'load_point_cloud',
    'save_point_cloud',
    'load_bin_file',
    'save_bin_file',
    'load_pcd_file',
    'save_pcd_file',
    'load_ply_file',
    'save_ply_file',
    'export_semantic_results_to_csv',
    'export_semantic_results_to_json',
    'load_semantic_results_from_json',
    'create_sample_point_cloud',
    'get_supported_formats',
    'is_supported_format',
    
    # Visualization
    'visualize_point_cloud_3d',
    'visualize_semantic_point_cloud',
    'visualize_importance_heatmap',
    'visualize_confidence_distribution',
    'visualize_class_distribution',
    'create_class_legend',
    'visualize_comparison',
    'visualize_with_open3d',
    'create_summary_statistics',
    'visualize_metrics_dashboard',
]
