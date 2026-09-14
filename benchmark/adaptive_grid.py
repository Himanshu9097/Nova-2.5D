import numpy as np


def get_resolution(x, y, semantic_class):
    """
    Decide grid resolution based on distance and semantic importance.

    Smaller resolution = higher detail.
    """

    distance = np.sqrt(x**2 + y**2)

    # Important objects get high resolution
    if semantic_class in [1, 2]:
        # Vehicle or pedestrian
        return 0.25

    # Close region
    if distance < 10:
        return 0.25

    # Medium distance
    elif distance < 25:
        return 0.5

    # Far region
    else:
        return 1.0


def create_adaptive_grid(point_cloud):
    """
    Create an adaptive 2.5D grid.

    Point format:
    x, y, z, intensity, semantic_class
    """

    grid = {}

    for point in point_cloud:

        x, y, z, intensity, semantic_class = point

        semantic_class = int(semantic_class)

        resolution = get_resolution(
            x,
            y,
            semantic_class
        )

        cell_x = int(np.floor(x / resolution))
        cell_y = int(np.floor(y / resolution))

        cell_id = (
            cell_x,
            cell_y,
            resolution
        )

        if cell_id not in grid:

            grid[cell_id] = {
                "points": [],
                "resolution": resolution,
                "max_height": z,
                "semantic_classes": []
            }

        grid[cell_id]["points"].append(point)

        grid[cell_id]["max_height"] = max(
            grid[cell_id]["max_height"],
            z
        )

        grid[cell_id]["semantic_classes"].append(
            semantic_class
        )

    return grid


if __name__ == "__main__":

    from data import generate_dummy_scene

    point_cloud = generate_dummy_scene()

    grid = create_adaptive_grid(point_cloud)

    print("Adaptive Grid created!")

    print("Input points:", len(point_cloud))

    print("Adaptive grid cells:", len(grid))

    print("\nResolution distribution:")

    resolutions = {}

    for cell in grid.values():

        resolution = cell["resolution"]

        resolutions[resolution] = (
            resolutions.get(resolution, 0) + 1
        )

    for resolution, count in sorted(resolutions.items()):

        print(
            f"{resolution} m : {count} cells"
        )