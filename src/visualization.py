"""
Visualization Module for LiDAR Point Clouds

This module handles 3D visualization of point clouds with semantic coloring
using Open3D and Plotly for Streamlit integration.
"""

import numpy as np
from typing import Dict, List, Optional, Union
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path

from .semantic_labels import (
    get_class_color,
    get_label_to_names,
    CLASS_COLORS
)


def visualize_point_cloud_3d(points: np.ndarray,
                             colors: Optional[np.ndarray] = None,
                             class_names: Optional[List[str]] = None,
                             title: str = "Point Cloud Visualization",
                             point_size: int = 2) -> go.Figure:
    """
    Create a 3D scatter plot of point cloud using Plotly.
    
    Args:
        points: Point cloud array (N x 3 or N x 4)
        colors: Optional color array (N x 3) for RGB colors
        class_names: Optional list of class names for semantic coloring
        title: Plot title
        point_size: Size of points in the plot
        
    Returns:
        Plotly figure object
    """
    # Extract x, y, z coordinates
    x = points[:, 0]
    y = points[:, 1]
    z = points[:, 2]
    
    # Determine colors
    if colors is not None:
        # Use provided RGB colors
        rgb_colors = colors
    elif class_names is not None:
        # Use semantic class colors
        rgb_colors = np.array([get_class_color(name) for name in class_names])
        rgb_colors = rgb_colors / 255.0  # Normalize to 0-1 range
    else:
        # Use single color (blue)
        rgb_colors = np.array([[0.0, 0.5, 1.0]] * len(points))
    
    # Create figure
    fig = go.Figure(data=[go.Scatter3d(
        x=x,
        y=y,
        z=z,
        mode='markers',
        marker=dict(
            size=point_size,
            color=rgb_colors,
            opacity=0.8
        ),
        text=[f"Point {i}" for i in range(len(points))],
        hovertemplate="<b>Point %{text}</b><br>" +
                     "X: %{x:.2f}<br>" +
                     "Y: %{y:.2f}<br>" +
                     "Z: %{z:.2f}<br>" +
                     "<extra></extra>"
    )])
    
    fig.update_layout(
        title=title,
        scene=dict(
            xaxis_title='X (m)',
            yaxis_title='Y (m)',
            zaxis_title='Z (m)',
            aspectmode='data'
        ),
        margin=dict(l=0, r=0, b=0, t=30),
        height=600
    )
    
    return fig


def visualize_semantic_point_cloud(results: List[Dict],
                                  title: str = "Semantic Point Cloud",
                                  point_size: int = 3,
                                  show_unknown: bool = True) -> go.Figure:
    """
    Visualize semantic segmentation results with color-coded classes.
    
    Args:
        results: List of result dictionaries from semantic inference
        title: Plot title
        point_size: Size of points
        show_unknown: Whether to show unknown/uncertain points
        
    Returns:
        Plotly figure object
    """
    # Extract data
    points = np.array([[r['x'], r['y'], r['z']] for r in results])
    class_names = [r['semantic_class'] for r in results]
    confidences = [r['confidence'] for r in results]
    
    # Filter unknown if needed
    if not show_unknown:
        mask = [name not in ['unknown', 'uncertain'] for name in class_names]
        points = points[mask]
        class_names = [class_names[i] for i in range(len(mask)) if mask[i]]
        confidences = [confidences[i] for i in range(len(mask)) if mask[i]]
    
    # Get colors for each class
    colors = np.array([get_class_color(name) for name in class_names])
    colors = colors / 255.0  # Normalize to 0-1
    
    # Create figure with custom hover info
    hover_text = [
        f"Class: {class_names[i]}<br>"
        f"Confidence: {confidences[i]:.2f}<br>"
        f"X: {points[i, 0]:.2f}<br>"
        f"Y: {points[i, 1]:.2f}<br>"
        f"Z: {points[i, 2]:.2f}"
        for i in range(len(points))
    ]
    
    fig = go.Figure(data=[go.Scatter3d(
        x=points[:, 0],
        y=points[:, 1],
        z=points[:, 2],
        mode='markers',
        marker=dict(
            size=point_size,
            color=colors,
            opacity=0.7,
            line=dict(width=0, color='')
        ),
        text=hover_text,
        hovertemplate="<b>%{text}</b><extra></extra>"
    )])
    
    fig.update_layout(
        title=title,
        scene=dict(
            xaxis_title='X (m)',
            yaxis_title='Y (m)',
            zaxis_title='Z (m)',
            aspectmode='data'
        ),
        margin=dict(l=0, r=0, b=0, t=30),
        height=600
    )
    
    return fig


def visualize_importance_heatmap(results: List[Dict],
                                  title: str = "Semantic Importance Heatmap",
                                  point_size: int = 4) -> go.Figure:
    """
    Visualize semantic importance as a color heatmap.
    
    Args:
        results: List of result dictionaries
        title: Plot title
        point_size: Size of points
        
    Returns:
        Plotly figure object
    """
    points = np.array([[r['x'], r['y'], r['z']] for r in results])
    importance = np.array([r['semantic_importance'] for r in results])
    
    # Create color scale from blue (low importance) to red (high importance)
    fig = go.Figure(data=[go.Scatter3d(
        x=points[:, 0],
        y=points[:, 1],
        z=points[:, 2],
        mode='markers',
        marker=dict(
            size=point_size,
            color=importance,
            colorscale='RdYlBu_r',  # Red-Yellow-Blue reversed (Red = high)
            opacity=0.7,
            colorbar=dict(title='Importance')
        ),
        text=[f"Importance: {imp:.2f}" for imp in importance],
        hovertemplate="<b>%{text}</b><br>" +
                     "X: %{x:.2f}<br>" +
                     "Y: %{y:.2f}<br>" +
                     "Z: %{z:.2f}<br>" +
                     "<extra></extra>"
    )])
    
    fig.update_layout(
        title=title,
        scene=dict(
            xaxis_title='X (m)',
            yaxis_title='Y (m)',
            zaxis_title='Z (m)',
            aspectmode='data'
        ),
        margin=dict(l=0, r=0, b=0, t=30),
        height=600
    )
    
    return fig


def visualize_confidence_distribution(results: List[Dict],
                                      title: str = "Confidence Distribution") -> go.Figure:
    """
    Visualize the distribution of confidence scores.
    
    Args:
        results: List of result dictionaries
        title: Plot title
        
    Returns:
        Plotly figure object
    """
    confidences = [r['confidence'] for r in results]
    class_names = [r['semantic_class'] for r in results]
    
    fig = go.Figure()
    
    # Create histogram
    fig.add_trace(go.Histogram(
        x=confidences,
        nbinsx=20,
        name='Confidence',
        marker_color='skyblue',
        opacity=0.7
    ))
    
    fig.update_layout(
        title=title,
        xaxis_title='Confidence Score',
        yaxis_title='Count',
        bargap=0.1,
        height=400
    )
    
    return fig


def visualize_class_distribution(results: List[Dict],
                                  title: str = "Class Distribution",
                                  top_n: int = 10) -> go.Figure:
    """
    Visualize the distribution of semantic classes.
    
    Args:
        results: List of result dictionaries
        title: Plot title
        top_n: Number of top classes to show
        
    Returns:
        Plotly figure object
    """
    # Count classes
    class_counts = {}
    for result in results:
        class_name = result['semantic_class']
        class_counts[class_name] = class_counts.get(class_name, 0) + 1
    
    # Sort by count
    sorted_classes = sorted(class_counts.items(), key=lambda x: x[1], reverse=True)
    
    # Take top N
    if len(sorted_classes) > top_n:
        sorted_classes = sorted_classes[:top_n]
    
    classes = [item[0] for item in sorted_classes]
    counts = [item[1] for item in sorted_classes]
    
    # Create bar chart
    fig = go.Figure(data=[go.Bar(
        x=classes,
        y=counts,
        marker_color='lightblue'
    )])
    
    fig.update_layout(
        title=title,
        xaxis_title='Semantic Class',
        yaxis_title='Number of Points',
        xaxis_tickangle=-45,
        height=400
    )
    
    return fig


def create_class_legend() -> go.Figure:
    """
    Create a legend showing semantic class colors.
    
    Returns:
        Plotly figure object with legend
    """
    label_to_names = get_label_to_names()
    
    classes = []
    colors = []
    
    for label_id, class_name in sorted(label_to_names.items()):
        classes.append(class_name)
        rgb_color = get_class_color(class_name)
        colors.append(f'rgb({rgb_color[0]}, {rgb_color[1]}, {rgb_color[2]})')
    
    fig = go.Figure(data=[go.Table(
        header=dict(
            values=['Class', 'Color'],
            fill_color='lightgray',
            align='left'
        ),
        cells=dict(
            values=[classes, [''] * len(classes)],
            fill_color=[['white'] * len(classes), colors],
            align='left',
            height=30
        )
    )])
    
    fig.update_layout(
        title='Semantic Class Legend',
        height=600
    )
    
    return fig


def visualize_comparison(results1: List[Dict],
                       results2: List[Dict],
                       title1: str = "Result 1",
                       title2: str = "Result 2") -> go.Figure:
    """
    Create side-by-side comparison of two semantic segmentation results.
    
    Args:
        results1: First result list
        results2: Second result list
        title1: Title for first plot
        title2: Title for second plot
        
    Returns:
        Plotly figure object with subplots
    """
    from plotly.subplots import make_subplots
    
    # Extract data
    points1 = np.array([[r['x'], r['y'], r['z']] for r in results1])
    class_names1 = [r['semantic_class'] for r in results1]
    colors1 = np.array([get_class_color(name) for name in class_names1]) / 255.0
    
    points2 = np.array([[r['x'], r['y'], r['z']] for r in results2])
    class_names2 = [r['semantic_class'] for r in results2]
    colors2 = np.array([get_class_color(name) for name in class_names2]) / 255.0
    
    # Create subplots
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=(title1, title2),
        specs=[[{'type': 'scatter3d'}, {'type': 'scatter3d'}]]
    )
    
    # Add first plot
    fig.add_trace(
        go.Scatter3d(
            x=points1[:, 0],
            y=points1[:, 1],
            z=points1[:, 2],
            mode='markers',
            marker=dict(size=2, color=colors1, opacity=0.7),
            name=title1
        ),
        row=1, col=1
    )
    
    # Add second plot
    fig.add_trace(
        go.Scatter3d(
            x=points2[:, 0],
            y=points2[:, 1],
            z=points2[:, 2],
            mode='markers',
            marker=dict(size=2, color=colors2, opacity=0.7),
            name=title2
        ),
        row=1, col=2
    )
    
    fig.update_layout(height=600, showlegend=False)
    
    return fig


def visualize_with_open3d(points: np.ndarray,
                         colors: Optional[np.ndarray] = None,
                         class_names: Optional[List[str]] = None) -> None:
    """
    Visualize point cloud using Open3D (interactive window).
    
    Args:
        points: Point cloud array (N x 3 or N x 4)
        colors: Optional RGB colors (N x 3)
        class_names: Optional class names for semantic coloring
    """
    try:
        import open3d as o3d
        
        # Create point cloud
        pcd = o3d.geometry.PointCloud()
        pcd.points = o3d.utility.Vector3dVector(points[:, :3])
        
        # Set colors
        if colors is not None:
            pcd.colors = o3d.utility.Vector3dVector(colors)
        elif class_names is not None:
            rgb_colors = np.array([get_class_color(name) for name in class_names])
            pcd.colors = o3d.utility.Vector3dVector(rgb_colors / 255.0)
        else:
            # Default blue color
            pcd.colors = o3d.utility.Vector3dVector(
                np.array([[0.0, 0.5, 1.0]] * len(points))
            )
        
        # Visualize
        o3d.visualization.draw_geometries([pcd])
        
    except ImportError:
        raise ImportError("Open3D not installed. Install with: pip install open3d")


def create_summary_statistics(results: List[Dict]) -> Dict:
    """
    Calculate summary statistics for visualization.
    
    Args:
        results: List of result dictionaries
        
    Returns:
        Dictionary with summary statistics
    """
    class_names = [r['semantic_class'] for r in results]
    confidences = [r['confidence'] for r in results]
    importance = [r['semantic_importance'] for r in results]
    
    # Count classes
    class_counts = {}
    for name in class_names:
        class_counts[name] = class_counts.get(name, 0) + 1
    
    return {
        'total_points': len(results),
        'num_classes': len(class_counts),
        'class_counts': class_counts,
        'mean_confidence': np.mean(confidences),
        'std_confidence': np.std(confidences),
        'mean_importance': np.mean(importance),
        'std_importance': np.std(importance),
        'high_confidence_ratio': np.mean(np.array(confidences) > 0.8),
        'high_importance_ratio': np.mean(np.array(importance) > 0.7)
    }


def visualize_metrics_dashboard(results: List[Dict],
                                timing: Dict) -> go.Figure:
    """
    Create a dashboard with key metrics.
    
    Args:
        results: List of result dictionaries
        timing: Timing information from inference
        
    Returns:
        Plotly figure object with dashboard
    """
    stats = create_summary_statistics(results)
    
    # Create dashboard with subplots
    from plotly.subplots import make_subplots
    
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Class Distribution', 'Confidence Distribution',
                       'Processing Time', 'Key Metrics'),
        specs=[[{'type': 'bar'}, {'type': 'histogram'}],
               [{'type': 'indicator'}, {'type': 'table'}]]
    )
    
    # Class distribution
    sorted_classes = sorted(stats['class_counts'].items(), key=lambda x: x[1], reverse=True)[:10]
    fig.add_trace(
        go.Bar(x=[c[0] for c in sorted_classes], y=[c[1] for c in sorted_classes]),
        row=1, col=1
    )
    
    # Confidence distribution
    confidences = [r['confidence'] for r in results]
    fig.add_trace(
        go.Histogram(x=confidences, nbinsx=20),
        row=1, col=2
    )
    
    # Processing time indicator
    total_time = timing.get('total_time', 0)
    fig.add_trace(
        go.Indicator(
            mode="number",
            value=total_time,
            title={'text': "Total Time (s)"},
            number={'font': {'size': 50}}
        ),
        row=2, col=1
    )
    
    # Key metrics table
    fig.add_trace(
        go.Table(
            header=dict(values=['Metric', 'Value']),
            cells=dict(values=[
                ['Total Points', 'Classes', 'Mean Confidence', 'Mean Importance'],
                [stats['total_points'], stats['num_classes'], 
                 f"{stats['mean_confidence']:.3f}", f"{stats['mean_importance']:.3f}"]
            ])
        ),
        row=2, col=2
    )
    
    fig.update_layout(height=800, showlegend=False)
    
    return fig
