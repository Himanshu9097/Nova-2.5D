import numpy as np


def create_uniform_grid(point_cloud, resolution=0.5):
    """
    Convert LiDAR point cloud into a uniform 2.5D grid.

    Parameters
    ----------
    point_cloud : numpy.ndarray
        Columns:
        x, y, z, intensity, semantic_class

    resolution : float
        Grid cell size in meters.

    Returns
    -------
    grid : dict
        Dictionary containing grid-cell information.
    """

    grid = {}

    for point in point_cloud:

        x, y, z, intensity, semantic_class = point

        # Determine grid cell
        cell_x = int(np.floor(x / resolution))
        cell_y = int(np.floor(y / resolution))

        cell_id = (cell_x, cell_y)

        # Create cell if it doesn't exist
        if cell_id not in grid:

            grid[cell_id] = {
                "points": [],
                "max_height": z,
                "semantic_classes": []
            }

        # Store point
        grid[cell_id]["points"].append(point)

        # Update maximum elevation
        grid[cell_id]["max_height"] = max(
            grid[cell_id]["max_height"],
            z
        )

        # Store semantic class
        grid[cell_id]["semantic_classes"].append(
            int(semantic_class)
        )

    return grid


if __name__ == "__main__":

    from data import generate_dummy_scene

    # Generate dummy LiDAR
    point_cloud = generate_dummy_scene()

    # Create uniform grid
    grid = create_uniform_grid(
        point_cloud,
        resolution=0.5
    )

    print("Uniform Grid created!")

    print("Input points:", len(point_cloud))

    print("Grid cells:", len(grid))

    # Show first few cells
    print("\nFirst 5 cells:")

    for i, (cell_id, cell_data) in enumerate(grid.items()):

        print(
            cell_id,
            "points:",
            len(cell_data["points"]),
            "height:",
            round(cell_data["max_height"], 3)
        )

        if i == 4:
            break