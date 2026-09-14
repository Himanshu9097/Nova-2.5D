import matplotlib.pyplot as plt

def plot_memory():
    labels = ['Raw 3D LiDAR\n(1 Million Points)', 'Nova-2.5D Adaptive Grid\n(1 Million Points)']
    
    # 1M points * 16 bytes (x,y,z,intensity) = ~16 MB
    memory_mb_raw = 16.0 
    
    # 1M points mapped to a typical road scene reduces to ~5,000 active cells
    # 5,000 cells * 144 bytes = ~0.72 MB
    memory_mb_nova = 0.72 
    
    values = [memory_mb_raw, memory_mb_nova]
    
    fig, ax = plt.subplots(figsize=(8, 6))
    bars = ax.bar(labels, values, color=['#e74c3c', '#2ecc71'])
    
    ax.set_ylabel('Memory Footprint (MB)', fontsize=12)
    ax.set_title('Nova-2.5D Memory Optimization (95% Reduction)', fontsize=14, pad=20)
    
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.2,
                f'{height:.2f} MB',
                ha='center', va='bottom', fontsize=12, fontweight='bold')
                
    plt.tight_layout()
    plt.savefig('memory_comparison.png', dpi=300)
    print("Saved memory_comparison.png")

if __name__ == '__main__':
    plot_memory()
