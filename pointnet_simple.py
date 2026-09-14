"""
Simplified PointNet inference for SemanticKITTI
Adapted from KASCedric/PointNet for SIH project
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from pathlib import Path
import time

class TNet(nn.Module):
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


def load_pointnet_model(model_path, n_classes=34, bn=False, device='cpu'):
    """Load PointNet model from checkpoint"""
    model = PointNetSemSeg(n_classes=n_classes, bn=bn).to(device)
    checkpoint = torch.load(model_path, map_location=device)
    model.load_state_dict(checkpoint)
    model.eval()
    return model


def run_pointnet_inference(model, points, device='cpu'):
    """
    Run PointNet inference on point cloud
    Args:
        model: PointNet model
        points: numpy array (N, 3) or (N, 4) for xyz or xyz+i
        device: 'cpu' or 'cuda'
    Returns:
        predictions: numpy array (N,) of class indices
        confidences: numpy array (N,) of confidence scores
    """
    # Take only xyz if points have intensity
    if points.shape[1] > 3:
        points = points[:, :3]

    # Normalize points
    points = (points - points.mean(axis=0)) / (points.std(axis=0) + 1e-8)

    # Convert to tensor
    points_tensor = torch.from_numpy(points.T).float().unsqueeze(0).to(device)  # (1, 3, N)

    # Run inference
    with torch.no_grad():
        logits, _ = model(points_tensor)  # (1, n_classes, N)
        probabilities = torch.exp(logits)  # LogSoftmax output
        predictions = torch.argmax(logits, dim=1)  # (1, N)
        confidences = torch.max(probabilities, dim=1)[0]  # (1, N)

    # Convert to numpy
    predictions = predictions.cpu().numpy().reshape(-1)
    confidences = confidences.cpu().numpy().reshape(-1)

    return predictions, confidences


def main():
    print("="*60)
    print("POINTNET INFERENCE TEST")
    print("="*60)

    # Check device
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Device: {device}")
    if torch.cuda.is_available():
        print(f"GPU: {torch.cuda.get_device_name(0)}")
        print(f"CUDA version: {torch.version.cuda}")

    # Load model
    model_path = "models\\sample-model.pth"
    print(f"\nLoading model from {model_path}...")
    start_time = time.time()
    model = load_pointnet_model(model_path, n_classes=34, bn=False, device=device)
    load_time = time.time() - start_time
    print(f"Model loaded in {load_time:.2f}s")
    print(f"Model device: {next(model.parameters()).device}")

    # Load sample data
    print("\nLoading sample point cloud...")
    from src import load_point_cloud
    points = load_point_cloud("data/sample/sample_semantickitti.bin")
    print(f"Loaded {len(points)} points")

    # Run inference
    print("\nRunning inference...")
    inference_start = time.time()
    predictions, confidences = run_pointnet_inference(model, points, device)
    inference_time = time.time() - inference_start

    print(f"\nInference completed in {inference_time:.2f}s")
    print(f"Points per second: {len(predictions) / inference_time:.1f}")
    print(f"Mean confidence: {np.mean(confidences):.3f}")

    # Show sample predictions
    print(f"\nSample predictions:")
    for i in range(min(5, len(predictions))):
        print(f"  Point {i}: class {predictions[i]}, confidence {confidences[i]:.3f}")

    # Class distribution
    from collections import Counter
    class_counts = Counter(predictions)
    print(f"\nClass distribution (top 10):")
    for class_idx, count in class_counts.most_common(10):
        print(f"  Class {class_idx}: {count} points")

    print("\n" + "="*60)
    print("POINTNET INFERENCE SUCCESSFUL!")
    print("="*60)


if __name__ == "__main__":
    main()
