# NOVA-2.5D

NOVA-2.5D is an early-stage CARLA data-generation scaffold for autonomous-driving experiments. It creates a simple pedestrian-crossing scenario, records LiDAR point clouds from an autopilot vehicle, and saves actor ground truth for each simulation frame.

## Current Pipeline

The main entrypoint is `scenarios/scenario_manager.py`. It currently:

1. Connects to a CARLA server at `localhost:2000`.
2. Spawns a Tesla Model 3 at the first available map spawn point.
3. Enables vehicle autopilot.
4. Spawns a randomly selected pedestrian at a hardcoded location.
5. Moves the pedestrian toward a hardcoded destination using CARLA's AI walker controller.
6. Attaches a ray-cast LiDAR to the vehicle.
7. Records LiDAR and actor ground truth for 300 CARLA ticks.
8. Cleans up the vehicle, pedestrian, and sensor after the run.

## LiDAR Configuration

The LiDAR is configured in `carla/lidar.py` with:

- 32 channels
- 56,000 points per second
- 10 Hz rotation frequency
- 50 m range
- Vertical field of view from -30 to 10 degrees

Each LiDAR frame is written by `sensors/lidar_recorder.py` to:

```text
data/raw/<carla_frame>.bin
```

Each file contains a sequence of 32-bit floating-point values grouped as:

```text
x, y, z, intensity
```

## Ground Truth

`ground_truth/ground_truth_logger.py` records every vehicle and pedestrian visible in the CARLA world. Each object includes:

- Actor ID and CARLA type
- Position
- Rotation
- Velocity
- Bounding-box extents

The result is written to:

```text
data/ground_truth/ground_truth.json
```

## Requirements

- CARLA simulator running and reachable at `localhost:2000`
- Python environment with the CARLA Python API installed
- `numpy`

There is currently no dependency file or installation script in the repository.

## Running

From the project root:

```bash
python scenarios/scenario_manager.py
```

## Current Status

The Python files pass syntax compilation, but the simulation does not currently start because this repository has a local package named `carla`. That package shadows the external CARLA Python API when `import carla` is executed. The runtime therefore resolves to `./carla/__init__.py`, which does not provide `carla.Client`.

The project needs that naming/import conflict resolved before the scenario can connect to CARLA.

## Scope and Limitations

This is currently a scenario and sensor recorder, not a complete 2.5D perception system. It does not yet include:

- Camera or radar sensors
- Object detection, tracking, or inference
- 2D/3D-to-2.5D projection
- Configurable maps, spawn points, or scenario parameters
- Explicit synchronization between LiDAR callback frames and ground-truth records
- Automated tests or dataset validation
