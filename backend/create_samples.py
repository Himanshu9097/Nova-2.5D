import numpy as np
import os

os.makedirs("backend/sample_datasets", exist_ok=True)
rng = np.random.default_rng(123)

# 1. Urban Intersection Sample (3,000 points)
# Road (0): 1500, Vehicles (1): 800, Pedestrians (2): 400, Buildings (3): 300
road_x = rng.uniform(-20, 20, 1500)
road_y = rng.uniform(-8, 8, 1500)
road_z = rng.normal(0, 0.02, 1500)
road_i = rng.uniform(0.3, 0.7, 1500)
road_c = np.zeros(1500)

veh_x = rng.uniform(5, 12, 800)
veh_y = rng.uniform(-2.5, 2.5, 800)
veh_z = rng.uniform(0, 1.8, 800)
veh_i = rng.uniform(0.6, 1.0, 800)
veh_c = np.ones(800)

ped_x = rng.uniform(-6, -3, 400)
ped_y = rng.uniform(2, 5, 400)
ped_z = rng.uniform(0, 1.7, 400)
ped_i = rng.uniform(0.4, 0.8, 400)
ped_c = np.full(400, 2)

wall_x = rng.uniform(10, 18, 300)
wall_y = rng.uniform(7, 7.5, 300)
wall_z = rng.uniform(0, 3.5, 300)
wall_i = rng.uniform(0.2, 0.5, 300)
wall_c = np.full(300, 3)

pts = np.vstack([
    np.column_stack([road_x, road_y, road_z, road_i, road_c]),
    np.column_stack([veh_x, veh_y, veh_z, veh_i, veh_c]),
    np.column_stack([ped_x, ped_y, ped_z, ped_i, ped_c]),
    np.column_stack([wall_x, wall_y, wall_z, wall_i, wall_c])
])

np.savetxt(
    "backend/sample_datasets/sample_urban_intersection.csv", 
    pts, 
    delimiter=",", 
    header="x,y,z,intensity,semantic_class", 
    comments="", 
    fmt="%.3f,%.3f,%.3f,%.3f,%d"
)

# 2. Unlabeled Highway Corridor Sample (1,500 points, space-separated, no semantic_class)
h_x = rng.uniform(-40, 40, 1500)
h_y = rng.uniform(-6, 6, 1500)
h_z = rng.uniform(-0.1, 1.5, 1500)
h_i = rng.uniform(0.2, 0.9, 1500)

unlabeled_pts = np.column_stack([h_x, h_y, h_z, h_i])
np.savetxt(
    "backend/sample_datasets/sample_unlabeled_highway.txt", 
    unlabeled_pts, 
    delimiter=" ", 
    header="x y z intensity", 
    comments="", 
    fmt="%.3f %.3f %.3f %.3f"
)

print("Sample datasets generated successfully!")
