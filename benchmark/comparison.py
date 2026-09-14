def calculate_cell_reduction(uniform_cells, adaptive_cells):

    if uniform_cells == 0:
        return 0

    reduction = (
        (uniform_cells - adaptive_cells)
        / uniform_cells
    ) * 100

    return reduction


if __name__ == "__main__":

    # Temporary values
    uniform_cells = 3322
    adaptive_cells = 2000

    reduction = calculate_cell_reduction(
        uniform_cells,
        adaptive_cells
    )

    print("========== GRID COMPARISON ==========")

    print("Uniform cells :", uniform_cells)
    print("Adaptive cells:", adaptive_cells)

    print(
        f"Cell reduction: {reduction:.2f}%"
    )