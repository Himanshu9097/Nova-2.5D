import json
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Map of level -> resolution size (matches C++ ResolutionPolicy)
LEVEL_SIZES = {
    0: 0.05,
    1: 0.10,
    2: 0.25,
    3: 0.50
}

# Standard CARLA Semantic Colors (R, G, B) normalized to 0-1
CLASS_COLORS = {
    7: (0.5, 0.5, 0.5), # Road (Gray)
    4: (1.0, 0.0, 0.0), # Pedestrian (Red)
    10: (0.0, 0.0, 1.0) # Vehicle (Blue)
}

def plot_grid(json_path):
    try:
        with open(json_path, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: {json_path} not found. Did you run the C++ simulation_runner?")
        return

    cells = data.get("cells", [])
    
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_aspect('equal')
    
    # Track bounds for plotting
    min_x, max_x = float('inf'), float('-inf')
    min_y, max_y = float('inf'), float('-inf')
    
    for cell in cells:
        cx = cell["center_x"]
        cy = cell["center_y"]
        lvl = cell["level"]
        class_id = cell["class_id"]
        
        size = LEVEL_SIZES.get(lvl, 0.5)
        color = CLASS_COLORS.get(class_id, (0.2, 0.8, 0.2)) # Default green
        
        # Calculate bottom-left corner from center
        x = cx - (size / 2.0)
        y = cy - (size / 2.0)
        
        min_x = min(min_x, x)
        max_x = max(max_x, x + size)
        min_y = min(min_y, y)
        max_y = max(max_y, y + size)
        
        # Draw the cell
        rect = patches.Rectangle((x, y), size, size, linewidth=0.5, edgecolor='black', facecolor=color)
        ax.add_patch(rect)
        
    ax.set_xlim(min_x - 1, max_x + 1)
    ax.set_ylim(min_y - 1, max_y + 1)
    ax.set_title("Nova-2.5D: Adaptive Hierarchical Grid Map", fontsize=14)
    ax.set_xlabel("X (meters)")
    ax.set_ylabel("Y (meters)")
    
    # Legend
    legend_elements = [
        patches.Patch(facecolor=(0.5, 0.5, 0.5), edgecolor='black', label='Road (Coarse/Fine)'),
        patches.Patch(facecolor=(1.0, 0.0, 0.0), edgecolor='black', label='Pedestrian (Refined)'),
        patches.Patch(facecolor=(0.0, 0.0, 1.0), edgecolor='black', label='Vehicle (Refined)')
    ]
    ax.legend(handles=legend_elements, loc='upper right')
    
    plt.savefig('adaptive_grid_map.png', dpi=300)
    print("Saved adaptive_grid_map.png")

if __name__ == '__main__':
    # Make sure this points to the JSON exported by the C++ engine
    plot_grid('map_export.json')
