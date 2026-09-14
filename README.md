# Nova-2.5D: Adaptive Variable Resolution 2.5D Lidar Mapping

This repository contains the high-performance **Adaptive Variable-Resolution 2.5D LiDAR Mapping Engine** built for Smart India Hackathon 2026.

## Overview
Nova-2.5D is designed to solve the critical memory and performance bottlenecks of processing raw 3D LiDAR data in autonomous vehicles. Instead of maintaining a dense 3D voxel grid, it projects points onto an intelligent **2.5D elevation map** that dynamically adjusts its resolution based on:
1. **Distance** (High resolution near the ego vehicle, coarse resolution far away).
2. **Semantic Importance** (Distant pedestrians trigger high-resolution splits).
3. **Dynamic Motion** (Actively tracked moving objects preserve detail and uncertainty).

## Architecture
The system is built as a highly optimized C++ core, with Python bridges for Deep Learning Integration and Simulation:

*   **`mapping/` (C++ Core):** Uses sparse `std::unordered_map` with Welford's algorithm to compute incremental statistics (elevation, occupancy, semantics) with minimal memory footprint.
*   **`perception/` (Python AI Bridge):** Outlines the data ingestion for external AI models.
    *   `semantic/`: Built to ingest data from sparse convolution networks like **PointNet**, **SPVNAS** or **Cylinder3D**. (Integrated Real GPU Inference using PointNet).
    *   `tracking/`: Multi-Object Kalman Tracking architecture.
*   **`simulation/` (CARLA Bridge):** Contains tools to parse Semantic LiDAR arrays from the CARLA Simulator and generate ground-truth JSON files for engine validation.

## Building the C++ Engine
Ensure you have CMake installed and configured (e.g., Visual Studio Build Tools).
```powershell
mkdir build
cd build
cmake ..
cmake --build .
```

## Running the Simulation
1. **Generate CARLA Ground-Truth:**
```powershell
python simulation/carla_bridge.py
```
2. **Run the Mapping Engine:**
```powershell
.\build\Debug\simulation_runner.exe carla_frame_0000.json
```

powershell -ExecutionPolicy Bypass -File .\launch_sih_demo.ps1
