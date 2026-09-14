# Nova-2.5D Project Context & Execution Guide
*Smart India Hackathon 2026 - Problem Statement 26053*

## 1. Project Overview
Nova-2.5D is an **Adaptive Variable-Resolution 2.5D LiDAR Mapping Engine**. It solves the critical memory and compute bottlenecks of traditional 3D voxel grids used in autonomous vehicles by intelligently mapping environments using distance, semantic importance, and dynamic uncertainty.

### Core Innovations (The "Adaptive" Edge)
Instead of processing all LiDAR points equally, the engine employs a strict 20-meter cutoff rule for static objects:
- **Static Objects (Roads, Buildings, Walls):** Filtered out beyond 20 meters. This dramatically saves memory and compute power.
- **Dynamic Objects (Pedestrians, Vehicles):** Retained and tracked regardless of distance (e.g., a pedestrian 50m away is still processed).
- **Kalman Filtering:** Raw LiDAR data can be noisy, and objects might briefly be occluded behind trees. The Kalman filter tracks their trajectory, predicting where they will be to ensure smooth, jitter-free dashboard tracking.

---

## 2. Distributed Hardware Architecture (The 2-Laptop Setup)
To guarantee a lag-free experience, the computation is distributed across two laptops.

### Laptop 1: Asus (The Simulator Server)
This laptop acts purely as the physics engine. 3D rendering has been disabled in the CARLA script to save GPU memory, meaning it just runs the physical simulation and broadcasts the data over the local Wi-Fi network.

### Laptop 2: Victus (The Brains & Dashboard)
This laptop does the heavy lifting:
1. **PyTorch AI Inference (PointNet):** Replaces simulated ground-truth data with real neural network semantic labels.
2. **C++ Mapping Engine:** Computes the 2.5D elevation map and grid cells.
3. **React Web Dashboard:** Displays the real-time telemetry, memory reduction metrics, and the interactive UI.

---

## 3. How to Run the Pitch Demo

### Step 1: Asus Laptop (CARLA Server)
1. Ensure both laptops are connected to the same Wi-Fi network.
2. Find the IP Address of the Asus laptop (e.g., `192.168.1.14`).
3. Open PowerShell and launch CARLA in ultra-low overhead mode:
```powershell
E:\SIH\CARLA_0.9.16\CarlaUE4.exe -quality-level=Low -windowed -ResX=320 -ResY=240 -NoVSync -dx11
```
*(No further action is needed on the Asus).*

### Step 2: Victus Laptop (Backend Servers)
Open a PowerShell terminal in the `Nova-2.5D` directory and pull the latest code:
```powershell
git pull
```

**Start the Flask API Server:**
*(This bridges the React Dashboard and the Python Simulation)*
```powershell
.\.venv\Scripts\Activate.ps1
python dashboard\server.py
```

### Step 3: Victus Laptop (Frontend Dashboard)
Open a new PowerShell terminal, navigate to the React app, and start it:
```powershell
cd dashboard\client
npm run dev
```
*(Open `http://localhost:5173` in your browser. You will see the "NOVA-2.5D COMMAND CENTER".)*

### Step 4: Victus Laptop (Live Simulation Engine)
Open a final PowerShell terminal and start the bridge script. Replace the `--carla-host` IP with your Asus IP. The `--use-ai` flag activates the real PyTorch PointNet model!
```powershell
.\.venv\Scripts\Activate.ps1
python simulation\live_demo.py --carla-host 192.168.1.14 --dashboard-host 127.0.0.1 --use-ai
```

---

## 4. Presenting to the Judges

### The "Algorithm Comparison" View
In the React Web Dashboard, click the **Algorithm Comparison** toggle at the top right. This reveals a 3-panel interactive infographic mirroring your presentation slides:
1. **Traditional Uniform:** Shows how fixed 10cm grids waste compute everywhere.
2. **Distance-Based:** Shows how objects far away are dropped completely.
3. **Nova-2.5D:** Shows the hybrid approach: Finer where it matters, coarser where it doesn't.

### The "Interactive Live Spawn" Demo
To prove your adaptive engine actually works, use the **Interactive Adaptive Test** panel at the bottom of the Comparison dashboard:
1. **The Negative Test (Static Wall):** Select "Concrete Wall", set distance to `50m`, and hit "EXECUTE LIVE SPAWN". The dashboard memory and cell counts will barely move because the Python bridge dynamically **culled** the wall before it reached the C++ engine (since it is >20m away and static).
2. **The Positive Test (Dynamic Pedestrian):** Select "Pedestrian", set distance to `50m`, and hit "EXECUTE LIVE SPAWN". The dashboard will instantly show "Tracked Target!" pulsing in the 3rd panel, and the `Currently Tracking` count will update. This proves your engine successfully bypassed the distance filter for a high-priority semantic object!

### Controller / Keyboard Driving
While presenting, you can drive the car around Town03:
- **W, A, S, D:** Accelerate, Steer, Brake
- **P:** Toggle Autopilot (The script connects to the Asus Traffic Manager to auto-drive)
- **F:** Toggle Auto-Follow Spectator Camera (Locks the camera behind the car)
- **C:** Snap Camera behind the car instantly

### The Pygame Window
The Python script also opens a Pygame window showing the RAW LiDAR feed:
- **Red/Blue Points:** Pedestrians and Vehicles (Highest Priority)
- **Bright Yellow/Green:** Close objects (<20m) (Medium Priority)
- **Faded Dark Colors:** Distant objects (>20m) that have been intentionally dropped from the compute pipeline.
