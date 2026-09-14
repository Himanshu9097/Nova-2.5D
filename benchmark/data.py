import numpy as np


def generate_dummy_scene():
    """
    Generate a simple synthetic LiDAR scene containing:
    - Road
    - Vehicle
    - Pedestrian
    - Wall
    - Random noise

    Point format:
    [x, y, z, intensity, semantic_class]

    Classes:
    0 = road
    1 = vehicle
    2 = pedestrian
    3 = wall
    4 = noise
    """

    rng = np.random.default_rng(42)

    # -------------------------
    # 1. ROAD
    # -------------------------
    road_count = 5000

    road_x = rng.uniform(-30, 30, road_count)
    road_y = rng.uniform(-10, 10, road_count)
    road_z = rng.normal(0, 0.02, road_count)
    road_intensity = rng.uniform(0.3, 0.8, road_count)

    road = np.column_stack([
        road_x,
        road_y,
        road_z,
        road_intensity,
        np.zeros(road_count)
    ])

    # -------------------------
    # 2. VEHICLE
    # -------------------------
    vehicle_count = 2000

    vehicle_x = rng.uniform(8, 12, vehicle_count)
    vehicle_y = rng.uniform(-2, 2, vehicle_count)
    vehicle_z = rng.uniform(0, 2, vehicle_count)
    vehicle_intensity = rng.uniform(0.5, 1.0, vehicle_count)

    vehicle = np.column_stack([
        vehicle_x,
        vehicle_y,
        vehicle_z,
        vehicle_intensity,
        np.ones(vehicle_count)
    ])

    # -------------------------
    # 3. PEDESTRIAN
    # -------------------------
    pedestrian_count = 1000

    pedestrian_x = rng.uniform(-5, -4, pedestrian_count)
    pedestrian_y = rng.uniform(3, 4, pedestrian_count)
    pedestrian_z = rng.uniform(0, 1.8, pedestrian_count)
    pedestrian_intensity = rng.uniform(0.4, 0.9, pedestrian_count)

    pedestrian = np.column_stack([
        pedestrian_x,
        pedestrian_y,
        pedestrian_z,
        pedestrian_intensity,
        np.full(pedestrian_count, 2)
    ])

    # -------------------------
    # 4. WALL
    # -------------------------
    wall_count = 1500

    wall_x = rng.uniform(15, 25, wall_count)
    wall_y = rng.uniform(7, 7.2, wall_count)
    wall_z = rng.uniform(0, 4, wall_count)
    wall_intensity = rng.uniform(0.2, 0.7, wall_count)

    wall = np.column_stack([
        wall_x,
        wall_y,
        wall_z,
        wall_intensity,
        np.full(wall_count, 3)
    ])

    # -------------------------
    # 5. NOISE
    # -------------------------
    noise_count = 500

    noise_x = rng.uniform(-30, 30, noise_count)
    noise_y = rng.uniform(-10, 10, noise_count)
    noise_z = rng.uniform(-2, 5, noise_count)
    noise_intensity = rng.uniform(0, 0.3, noise_count)

    noise = np.column_stack([
        noise_x,
        noise_y,
        noise_z,
        noise_intensity,
        np.full(noise_count, 4)
    ])

    # -------------------------
    # COMBINE EVERYTHING
    # -------------------------

    point_cloud = np.vstack([
        road,
        vehicle,
        pedestrian,
        wall,
        noise
    ])

    return point_cloud


if __name__ == "__main__":

    points = generate_dummy_scene()

    print("Dummy LiDAR scene generated!")
    print("Total points:", len(points))
    print("Point cloud shape:", points.shape)

    print("\nFirst 10 points:")
    print(points[:10])

    print("\nSemantic class counts:")

    classes, counts = np.unique(
        points[:, 4],
        return_counts=True
    )

    class_names = {
        0: "Road",
        1: "Vehicle",
        2: "Pedestrian",
        3: "Wall",
        4: "Noise"
    }

    for cls, count in zip(classes, counts):
        print(
            f"{class_names[int(cls)]}: {count}"
        )