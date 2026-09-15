"""
Semantic Segmentation Inference Module

This module handles loading pretrained models and running semantic segmentation
inference on LiDAR point clouds using either torch-pointcloud's RandLA-Net
or PointNet models.
"""

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, List, Optional, Tuple, Union
from pathlib import Path
import time
import warnings

from .preprocessing import (
    validate_point_cloud,
    preprocess_for_model,
    ensure_4_channel,
    calculate_point_cloud_statistics
)
from .semantic_labels import (
    get_label_to_names,
    map_labels_to_names,
    get_semantic_importance,
    DEFAULT_SEMANTIC_IMPORTANCE,
    TORCH_POINTCLOUD_RANDLANET_LABELS
)
from .importance import ImportanceCalculator


# PointNet Model Implementation
class TNet(nn.Module):
    """Spatial Transform Network for PointNet"""
    def __init__(self, k, bn=False):
        super(TNet, self).__init__()
        self.k = k
        self.bn = bn

        self.shared_mlp = nn.Sequential(
            nn.Conv1d(k, 64, 1),
            nn.BatchNorm1d(64) if bn else nn.Identity(),
            nn.ReLU(),
            nn.Conv1d(64, 128, 1),
            nn.BatchNorm1d(128) if bn else nn.Identity(),
            nn.ReLU(),
            nn.Conv1d(128, 1024, 1),
            nn.BatchNorm1d(1024) if bn else nn.Identity(),
            nn.ReLU(),
        )

        self.mlp = nn.Sequential(
            nn.Linear(1024, 512),
            nn.BatchNorm1d(512) if bn else nn.Identity(),
            nn.ReLU(),
            nn.Linear(512, 256),
            nn.BatchNorm1d(256) if bn else nn.Identity(),
            nn.ReLU(),
            nn.Linear(256, k**2),
        )

    def forward(self, x):
        batch_size, n_channels, n_points = x.size()
        shared_mlp_output = self.shared_mlp(x)
        max_pooling = nn.MaxPool1d(n_points)(shared_mlp_output)
        max_pooling_flat = nn.Flatten(1)(max_pooling)
        mlp_output = self.mlp(max_pooling_flat)
        identity = torch.eye(self.k).repeat(batch_size, 1, 1)
        if mlp_output.is_cuda:
            identity = identity.cuda()
        transform_matrix = mlp_output.view(-1, self.k, self.k) + identity
        return transform_matrix


class PointNetLocalFeatures(nn.Module):
    """Local point features extractor for PointNet"""
    def __init__(self, bn=False):
        super(PointNetLocalFeatures, self).__init__()
        self.bn = bn

        self.t_net_3d = TNet(k=3, bn=bn)
        self.t_net_64d = TNet(k=64, bn=bn)

        self.shared_mlp = nn.Sequential(
            nn.Conv1d(3, 64, 1),
            nn.BatchNorm1d(64) if bn else nn.Identity(),
            nn.ReLU(),
            nn.Conv1d(64, 64, 1),
            nn.BatchNorm1d(64) if bn else nn.Identity(),
            nn.ReLU(),
        )

    def forward(self, x):
        t_net_3d_matrix = self.t_net_3d(x)
        input_transform = torch.bmm(t_net_3d_matrix, x)
        shared_mlp_output = self.shared_mlp(input_transform)
        t_net_64d_matrix = self.t_net_64d(shared_mlp_output)
        feat_transform = torch.bmm(t_net_64d_matrix, shared_mlp_output)
        return feat_transform, t_net_64d_matrix


class PointNetGlobalFeatures(nn.Module):
    """Global point features extractor for PointNet"""
    def __init__(self, bn=False):
        super(PointNetGlobalFeatures, self).__init__()
        self.bn = bn

        self.shared_mlp = nn.Sequential(
            nn.Conv1d(64, 64, 1),
            nn.BatchNorm1d(64) if bn else nn.Identity(),
            nn.ReLU(),
            nn.Conv1d(64, 128, 1),
            nn.BatchNorm1d(128) if bn else nn.Identity(),
            nn.ReLU(),
            nn.Conv1d(128, 1024, 1),
            nn.BatchNorm1d(1024) if bn else nn.Identity(),
            nn.ReLU(),
        )

    def forward(self, x):
        shared_mlp_output = self.shared_mlp(x)
        max_pooling = nn.MaxPool1d(x.size(2))(shared_mlp_output)
        max_pooling_flat = nn.Flatten(1)(max_pooling)
        return max_pooling_flat


class PointNetSemSeg(nn.Module):
    """PointNet Semantic Segmentation Network"""
    def __init__(self, n_classes=34, bn=False):
        super(PointNetSemSeg, self).__init__()
        self.n_classes = n_classes
        self.bn = bn

        self.local_feats_net = PointNetLocalFeatures(bn=bn)
        self.global_feats_net = PointNetGlobalFeatures(bn=bn)

        self.shared_mlp = nn.Sequential(
            nn.Conv1d(1088, 512, 1),
            nn.BatchNorm1d(512) if bn else nn.Identity(),
            nn.ReLU(),
            nn.Conv1d(512, 256, 1),
            nn.BatchNorm1d(256) if bn else nn.Identity(),
            nn.ReLU(),
            nn.Conv1d(256, 128, 1),
            nn.BatchNorm1d(128) if bn else nn.Identity(),
            nn.ReLU(),
            nn.Conv1d(128, 128, 1),
            nn.BatchNorm1d(128) if bn else nn.Identity(),
            nn.ReLU(),
            nn.Conv1d(128, n_classes, 1),
            nn.BatchNorm1d(n_classes) if bn else nn.Identity(),
            nn.LogSoftmax(dim=1),
        )

    def forward(self, x):
        batch_size, n_channels, n_points = x.size()
        local_features, t_net_64d_matrix = self.local_feats_net(x)
        global_features = self.global_feats_net(local_features)
        global_features = global_features.unsqueeze(dim=2)
        global_features = global_features.repeat(1, 1, n_points)
        all_features = torch.cat([local_features, global_features], dim=1)
        mlp_output = self.shared_mlp(all_features)
        return mlp_output, t_net_64d_matrix


class SemanticSegmentationModel:
    """
    Semantic segmentation model wrapper supporting both RandLA-Net and PointNet.
    """
    
    def __init__(self, 
                 model_name: str = "pointnet_kasc",
                 model_path: Optional[str] = None,
                 device: Optional[str] = None,
                 confidence_threshold: float = 0.5,
                 label_set: str = "semantickitti"):
        """
        Initialize the semantic segmentation model.
        
        Args:
            model_name: Model type ("pointnet_kasc" or "randlanet")
            model_path: Path to model checkpoint (for PointNet)
            device: Device to run inference on ('cuda', 'cpu', or None for auto)
            confidence_threshold: Threshold for confident predictions
            label_set: Which label set to use ("semantickitti" or "torch_pointcloud")
        """
        self.model_name = model_name
        self.model_path = model_path
        self.confidence_threshold = confidence_threshold
        self.device = self._get_device(device)
        self.label_set = label_set
        self.model = None
        self.model_info = None
        self.label_to_names = get_label_to_names(label_set)
        
        # Initialize importance calculator
        self.importance_calculator = ImportanceCalculator()
        
        # Model loading status
        self.model_loaded = False
        
    def _get_device(self, device: Optional[str]) -> str:
        """
        Determine the device to use for inference.
        
        Args:
            device: Specified device or None for auto-detection
            
        Returns:
            Device string ('cuda' or 'cpu')
        """
        if device is not None:
            return device
        
        if torch.cuda.is_available():
            return 'cuda'
        else:
            return 'cpu'
    
    def load_model(self) -> None:
        """
        Load the pretrained model (PointNet or RandLA-Net).
        """
        if self.model_name == "pointnet_kasc":
            self._load_pointnet_model()
        elif self.model_name == "randlanet":
            self._load_randlanet_model()
        else:
            raise ValueError(f"Unknown model type: {self.model_name}")
    
    def _load_pointnet_model(self) -> None:
        """Load PointNet model from checkpoint"""
        if self.model_path is None:
            # Default path
            self.model_path = "models/sample-model.pth"
        
        if not Path(self.model_path).exists():
            raise FileNotFoundError(f"Model checkpoint not found: {self.model_path}")
        
        print(f"Loading PointNet model from {self.model_path}")
        print(f"Device: {self.device}")
        
        # PointNet uses 34 classes for SemanticKITTI
        n_classes = 34
        self.model = PointNetSemSeg(n_classes=n_classes, bn=False).to(self.device)
        
        # Load checkpoint
        checkpoint = torch.load(self.model_path, map_location=self.device)
        self.model.load_state_dict(checkpoint)
        self.model.eval()
        
        self.model_loaded = True
        self.model_info = {
            'model_type': 'PointNet',
            'n_classes': n_classes,
            'checkpoint_path': self.model_path
        }
        
        print(f"PointNet model loaded successfully!")
    
    def _load_randlanet_model(self) -> None:
        """Load RandLA-Net model using torch-pointcloud"""
        try:
            import torch_pointcloud as tp
            
            print(f"Loading RandLA-Net model")
            print(f"Device: {self.device}")
            
            # Create model with pretrained weights
            self.model, self.model_info = tp.create_model(
                "randlanet.semantickitti.tsung-han-wu",
                task="segmentation",
                pretrained=True,
                return_info=True
            )
            
            # Move model to device
            self.model = self.model.to(self.device)
            self.model.eval()
            
            self.model_loaded = True
            
            print(f"RandLA-Net model loaded successfully!")
            
        except ImportError as e:
            raise ImportError(
                "torch-pointcloud not installed. Please install it with: pip install torch-pointcloud"
            ) from e
        except Exception as e:
            raise RuntimeError(f"Failed to load RandLA-Net model: {e}") from e
    
    def predict(self, 
                points: np.ndarray,
                return_confidence: bool = True,
                return_importance: bool = True) -> Dict:
        """
        Run semantic segmentation inference on point cloud.
        
        Args:
            points: Point cloud array (N x 4)
            return_confidence: Whether to return confidence scores
            return_importance: Whether to return semantic importance
            
        Returns:
            Dictionary with prediction results
        """
        if not self.model_loaded:
            self.load_model()
        
        # Validate input
        is_valid, error_msg = validate_point_cloud(points)
        if not is_valid:
            raise ValueError(f"Invalid point cloud: {error_msg}")
        
        # Ensure 4 channels
        points = ensure_4_channel(points)
        
        # Run inference based on model type
        if self.model_name == "pointnet_kasc":
            return self._predict_pointnet(points, return_confidence, return_importance)
        elif self.model_name == "randlanet":
            return self._predict_randlanet(points, return_confidence, return_importance)
        else:
            raise ValueError(f"Unknown model type: {self.model_name}")
    
    def _predict_pointnet(self, 
                         points: np.ndarray,
                         return_confidence: bool,
                         return_importance: bool) -> Dict:
        """Run PointNet inference"""
        # Preprocess - minimal for PointNet
        start_time = time.time()
        points_processed = points.copy()
        
        # Take only xyz coordinates
        xyz = points_processed[:, :3]
        
        # Normalize points
        xyz = (xyz - xyz.mean(axis=0)) / (xyz.std(axis=0) + 1e-8)
        
        preprocessing_time = time.time() - start_time
        
        # Run inference
        inference_start = time.time()
        
        # Convert to tensor
        points_tensor = torch.from_numpy(xyz.T).float().unsqueeze(0).to(self.device)
        
        with torch.no_grad():
            logits, _ = self.model(points_tensor)
            probabilities = torch.exp(logits)  # LogSoftmax output
            predictions = torch.argmax(logits, dim=1)
            confidences = torch.max(probabilities, dim=1)[0]
        
        # Convert to numpy
        pred_labels = predictions.cpu().numpy().reshape(-1)
        confidences = confidences.cpu().numpy().reshape(-1)
        
        inference_time = time.time() - inference_start
        
        # Post-process
        if not return_confidence:
            confidences = np.ones(len(pred_labels))
        
        results = self._postprocess_predictions(
            pred_labels,
            points_processed,
            confidences,
            return_confidence,
            return_importance
        )
        
        # Add timing information
        results['timing'] = {
            'preprocessing_time': preprocessing_time,
            'inference_time': inference_time,
            'total_time': preprocessing_time + inference_time,
            'points_per_second': len(points_processed) / (inference_time + 1e-6)
        }
        
        # Add statistics
        results['statistics'] = calculate_point_cloud_statistics(points_processed)
        
        # Add model info
        results['model_info'] = {
            'model_name': self.model_name,
            'device': self.device,
            'label_set': self.label_set,
            'num_classes': len(self.label_to_names)
        }
        
        return results
    
    def _predict_randlanet(self, 
                          points: np.ndarray,
                          return_confidence: bool,
                          return_importance: bool) -> Dict:
        """Run RandLA-Net inference"""
        # Preprocess
        start_time = time.time()
        points_processed = preprocess_for_model(
            points,
            normalize=False,
            filter_range=True,
            downsample=True,
            target_points=45056  # RandLA-Net default
        )
        preprocessing_time = time.time() - start_time
        
        # Run inference
        inference_start = time.time()
        
        try:
            from torch_pointcloud.utils.data import collate
            
            # Prepare data for torch-pointcloud according to the expected format
            xyz = points_processed[:, :3]
            intensity = points_processed[:, 3:4] if points_processed.shape[1] > 3 else np.ones((len(points_processed), 1))
            
            # Create sample with the keys a dataset provides
            num_points = len(points_processed)
            sample = {
                "pos": torch.from_numpy(xyz).float(),
                "intensity": torch.from_numpy(intensity).float(),
                "segment": torch.zeros(num_points, dtype=torch.long),
                "instance": torch.zeros(num_points, dtype=torch.long),
            }
            
            # Apply the model's transform
            data = self.model_info["transform"](sample)
            
            # Collate the data (add batch dimension)
            data = collate([data])
            
            # Move to device
            for key in data:
                if isinstance(data[key], torch.Tensor):
                    data[key] = data[key].to(self.device)
            
            # Run model inference with correct arguments
            with torch.no_grad():
                logits = self.model(data.get("x"), data.get("pos"), data.get("batch"))
            
            # Get predictions from logits
            if isinstance(logits, dict):
                if 'logits' in logits:
                    logits = logits['logits']
                else:
                    logits = list(logits.values())[0]
            
            # Get predicted classes
            pred_labels = logits.argmax(dim=1).cpu().numpy()
            
            # Get confidence scores from softmax
            probabilities = torch.softmax(logits, dim=1).cpu().numpy()
            confidences = np.max(probabilities, axis=1)
            
            # Handle inverse mapping from voxelize transform
            if 'inverse' in data:
                # The transform may have voxelized the data, so we need to map back
                # For now, we'll use the predictions as-is and assume they match
                pass
            
            # Ensure we have the right number of predictions
            if len(pred_labels) != len(points_processed):
                warnings.warn(f"Prediction count mismatch: {len(pred_labels)} vs {len(points_processed)}")
                # Truncate or pad to match
                if len(pred_labels) > len(points_processed):
                    pred_labels = pred_labels[:len(points_processed)]
                    confidences = confidences[:len(points_processed)]
                else:
                    pred_labels = np.pad(pred_labels, (0, len(points_processed) - len(pred_labels)), 'constant')
                    confidences = np.pad(confidences, (0, len(points_processed) - len(confidences)), 'constant', constant_values=0.5)
            
            inference_time = time.time() - inference_start
            
        except Exception as e:
            raise RuntimeError(f"Inference failed: {e}") from e
        
        # Confidence scores are already calculated from softmax above
        if not return_confidence:
            confidences = np.ones(len(pred_labels))
        
        # Post-process predictions
        results = self._postprocess_predictions(
            pred_labels,
            points_processed,
            confidences,
            return_confidence,
            return_importance
        )
        
        # Add timing information
        results['timing'] = {
            'preprocessing_time': preprocessing_time,
            'inference_time': inference_time,
            'total_time': preprocessing_time + inference_time,
            'points_per_second': len(points_processed) / (inference_time + 1e-6)
        }
        
        # Add statistics
        results['statistics'] = calculate_point_cloud_statistics(points_processed)
        
        # Add model info
        results['model_info'] = {
            'model_name': self.model_name,
            'device': self.device,
            'label_set': self.label_set,
            'num_classes': len(self.label_to_names)
        }
        
        return results
    
    def _postprocess_predictions(self,
                                predictions: np.ndarray,
                                points: np.ndarray,
                                confidences: np.ndarray,
                                return_confidence: bool,
                                return_importance: bool) -> Dict:
        """
        Post-process model predictions into structured output.
        
        Args:
            predictions: Raw model predictions
            points: Processed point cloud
            confidences: Confidence scores
            return_confidence: Whether confidence was computed
            return_importance: Whether to compute importance
            
        Returns:
            Dictionary with processed results
        """
        # Convert labels to class names
        class_names = map_labels_to_names(predictions, self.label_to_names)
        
        # Apply confidence threshold
        if return_confidence:
            uncertain_mask = confidences < self.confidence_threshold
            class_names = [
                "uncertain" if uncertain else name 
                for uncertain, name in zip(uncertain_mask, class_names)
            ]
        
        # Calculate semantic importance
        if return_importance:
            importance_scores = self.importance_calculator.calculate_importance(
                class_names, confidences if return_confidence else None
            )
        else:
            importance_scores = np.ones(len(predictions))
        
        # Build result list
        results = []
        for i in range(len(points)):
            result = {
                'x': float(points[i, 0]),
                'y': float(points[i, 1]),
                'z': float(points[i, 2]),
                'intensity': float(points[i, 3]),
                'semantic_class': class_names[i],
                'semantic_label': int(predictions[i]),
                'confidence': float(confidences[i]) if return_confidence else 1.0,
                'semantic_importance': float(importance_scores[i])
            }
            results.append(result)
        
        return {
            'points': results,
            'predictions': predictions,
            'class_names': class_names,
            'confidences': confidences if return_confidence else np.ones(len(predictions)),
            'importance_scores': importance_scores,
            'num_points': len(points)
        }
    
    def get_model_info(self) -> Dict:
        """
        Get information about the loaded model.
        
        Returns:
            Dictionary with model information
        """
        return {
            'model_name': self.model_name,
            'device': self.device,
            'model_loaded': self.model_loaded,
            'label_set': self.label_set,
            'num_classes': len(self.label_to_names),
            'confidence_threshold': self.confidence_threshold,
            'model_info': self.model_info
        }


_MODEL_CACHE = {}

def get_cached_semantic_model(model_name: str = "pointnet_kasc",
                               model_path: Optional[str] = None,
                               device: Optional[str] = None,
                               confidence_threshold: float = 0.5,
                               label_set: str = "semantickitti") -> SemanticSegmentationModel:
    global _MODEL_CACHE
    key = (model_name, model_path, device, label_set)
    if key not in _MODEL_CACHE:
        _MODEL_CACHE[key] = SemanticSegmentationModel(
            model_name=model_name,
            model_path=model_path,
            device=device,
            confidence_threshold=confidence_threshold,
            label_set=label_set
        )
    return _MODEL_CACHE[key]


def semantic_inference(points: np.ndarray,
                      model_name: str = "pointnet_kasc",
                      model_path: Optional[str] = None,
                      confidence_threshold: float = 0.5,
                      device: Optional[str] = None,
                      label_set: str = "semantickitti") -> Dict:
    """
    Convenience function for semantic segmentation inference (cached for real-time speed).
    """
    model = get_cached_semantic_model(
        model_name=model_name,
        model_path=model_path,
        device=device,
        confidence_threshold=confidence_threshold,
        label_set=label_set
    )
    return model.predict(points)


def batch_inference(point_clouds: List[np.ndarray],
                   model_name: str = "pointnet_kasc",
                   model_path: Optional[str] = None,
                   device: Optional[str] = None) -> List[Dict]:
    """
    Run semantic segmentation on multiple point clouds.
    
    Args:
        point_clouds: List of point cloud arrays
        model_name: Model type
        model_path: Path to model checkpoint (for PointNet)
        device: Device to use
        
    Returns:
        List of result dictionaries
    """
    model = SemanticSegmentationModel(
        model_name=model_name,
        model_path=model_path,
        device=device
    )
    
    results = []
    for points in point_clouds:
        result = model.predict(points)
        results.append(result)
    
    return results


def create_synthetic_predictions(points: np.ndarray,
                                num_classes: int = 19,
                                label_set: str = "torch_pointcloud") -> Dict:
    """
    Create synthetic predictions for testing (no model required).
    
    Args:
        points: Point cloud array
        num_classes: Number of semantic classes
        label_set: Which label set to use
        
    Returns:
        Dictionary with synthetic results
    """
    num_points = points.shape[0]
    
    # Generate random predictions
    predictions = np.random.randint(0, num_classes, size=num_points)
    
    # Use correct label mapping
    label_to_names = get_label_to_names(label_set)
    class_names = [label_to_names.get(int(label), "unknown") for label in predictions]
    
    # Generate confidence scores
    confidences = np.random.uniform(0.6, 0.99, size=num_points)
    
    # Calculate importance
    importance_scores = np.array([
        get_semantic_importance(name) for name in class_names
    ])
    
    # Build results
    results = []
    for i in range(num_points):
        result = {
            'x': float(points[i, 0]),
            'y': float(points[i, 1]),
            'z': float(points[i, 2]),
            'intensity': float(points[i, 3]) if points.shape[1] > 3 else 0.5,
            'semantic_class': class_names[i],
            'semantic_label': int(predictions[i]),
            'confidence': float(confidences[i]),
            'semantic_importance': float(importance_scores[i])
        }
        results.append(result)
    
    return {
        'points': results,
        'predictions': predictions,
        'class_names': class_names,
        'confidences': confidences,
        'importance_scores': importance_scores,
        'num_points': num_points,
        'timing': {
            'preprocessing_time': 0.0,
            'inference_time': 0.0,
            'total_time': 0.0,
            'points_per_second': 0.0
        },
        'statistics': calculate_point_cloud_statistics(points),
        'synthetic': True,
        'model_info': {
            'model_name': 'synthetic',
            'device': 'none',
            'label_set': label_set,
            'num_classes': num_classes
        }
    }
