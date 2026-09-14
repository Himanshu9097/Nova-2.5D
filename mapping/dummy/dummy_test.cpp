#include "../adaptive_grid/adaptive_grid_engine.hpp"
#include "dummy_frame_generator.hpp"
#include <iostream>

using namespace nova::mapping;

int main() {
    MappingConfig config;
    config.resolution_levels = {
        {0, 0.05f, 0.0f, 10.0f},
        {1, 0.10f, 10.0f, 25.0f},
        {2, 0.25f, 25.0f, 50.0f},
        {3, 0.50f, 50.0f, 100.0f}
    };
    
    AdaptiveGridEngine engine(config);
    
    std::cout << "--- Processing Frame 1 ---" << std::endl;
    auto lidar = DummyFrameGenerator::generate_lidar_frame();
    auto semantics = DummyFrameGenerator::generate_semantics();
    auto tracks = DummyFrameGenerator::generate_tracks();
    std::vector<TerrainFeatures> terrain;
    
    engine.update(lidar, semantics, tracks, terrain);
    
    auto stats = engine.get_statistics();
    std::cout << "[MAP]\n";
    std::cout << "Input points: " << lidar.x.size() << "\n";
    std::cout << "Valid points: " << stats.total_points_processed << "\n";
    std::cout << "Active Cells: " << stats.active_cells << "\n";
    std::cout << "Level 0 cells: " << stats.cells_by_level[0] << "\n";
    std::cout << "Level 1 cells: " << stats.cells_by_level[1] << "\n";
    std::cout << "Level 2 cells: " << stats.cells_by_level[2] << "\n";
    std::cout << "Level 3 cells: " << stats.cells_by_level[3] << "\n";
    std::cout << "Refined: " << stats.refined_cells << "\n";
    std::cout << "Coarsened: " << stats.coarsened_cells << "\n";
    std::cout << "Average Uncertainty: " << stats.average_uncertainty << "\n";
    std::cout << "Map memory bytes: " << stats.map_memory_bytes << "\n";
    
    return 0;
}
