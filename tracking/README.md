# Dynamic Object Tracking

This package provides CARLA-independent dynamic object tracking for the
Nova-2.5D pipeline.

It performs:

1. Semantic point-to-object clustering
2. 3D constant-velocity Kalman filtering
3. Class-aware nearest-distance data association
4. Multi-object track lifecycle management
5. Velocity-based dynamic probability estimation

## Public entry point

The simplest handoff interface is:

```python
from tracking import SemanticTrackingPipeline

pipeline = SemanticTrackingPipeline()

outputs = pipeline.process_frame(
    results,
    frame_id=frame_id,
    timestamp=timestamp,
)
```

The same `pipeline` instance must be reused for consecutive frames so track
IDs and filter state persist.

`frame_id` and `timestamp` are supplied by the caller. The tracking package
does not generate them.

## Expected input

`results` must follow Vivek's verified Semantic AI output structure:

```python
{
    "points": [
        {
            "x": 15.0,
            "y": -4.0,
            "z": 0.5,
            "intensity": 0.7,
            "semantic_class": 10,
            "semantic_label": "Vehicle",
            "confidence": 0.95,
            "semantic_importance": 0.8,
        },
    ],
}
```

The point coordinates remain in raw LiDAR/sensor coordinates. The adapter
groups points by `semantic_class`, applies lightweight spatial clustering,
and converts valid clusters into object-level `Detection` values.

Clustering can be configured when constructing the pipeline:

```python
from tracking import ClusteringConfig, SemanticTrackingPipeline

pipeline = SemanticTrackingPipeline(
    clustering_config=ClusteringConfig(
        eps=1.0,
        min_points=3,
        confidence_threshold=0.5,
    ),
)
```

## Output

`process_frame()` returns a list of `TrackOutput` values. Each output contains:

```text
track_id
class_id
x, y, z
vx, vy, vz
dynamic_probability
state
```

Example:

```python
TrackOutput(
    track_id=1,
    class_id=10,
    x=15.2,
    y=-4.1,
    z=0.5,
    vx=1.2,
    vy=0.0,
    vz=0.0,
    dynamic_probability=0.94,
    state=1,
)
```

## Track states

```text
0 = Tentative
1 = Confirmed
2 = Lost
```

A new track starts as Tentative. It becomes Confirmed after the configured
number of successful detections. A track becomes Lost after exceeding the
configured missed-frame limit.

## Dynamic probability

`dynamic_probability` is an initial motion-based estimate derived from the
Kalman filter's estimated speed:

- Near-zero speed produces a low probability.
- Clearly moving objects produce a high probability.
- Intermediate speeds are mapped smoothly between the two.

This value is not a semantic-model confidence and is not a final behavioral
classification.

## Integration boundary

This package intentionally does **not** include:

- CARLA connection or actor management
- Live CARLA LiDAR acquisition
- Vivek's Semantic AI implementation
- C++ mapping integration
- Dashboard or visualization integration

The team lead should provide live LiDAR/Semantic AI results, along with the
corresponding frame ID and timestamp, at the `process_frame()` boundary.
