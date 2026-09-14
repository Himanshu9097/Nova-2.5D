#include "adaptive_grid_engine.hpp"
#include "../projection/projector.hpp"
#include "../cells/cell_statistics.hpp"
#include "refinement.hpp"
#include "coarsening.hpp"
#include "../uncertainty/uncertainty.hpp"
#include <vector>

namespace nova {
namespace mapping {

AdaptiveGridEngine::AdaptiveGridEngine(const MappingConfig& config)
    : config_(config), resolution_policy_(config.resolution_levels) {
    map_.frame_id = 0;
    map_.timestamp_ns = 0;
    stats_ = MappingStatistics();
}

void AdaptiveGridEngine::update(
    const LiDARFrame& lidar,
    const std::vector<SemanticPoint>& semantics,
    const std::vector<ObjectTrack>& tracks,
    const std::vector<TerrainFeatures>& terrain
) {
    map_.frame_id = lidar.frame_id;
    map_.timestamp_ns = lidar.timestamp_ns;

    size_t num_points = lidar.x.size();
    stats_.total_points_processed += num_points;
    
    // Phase 5 - Distance-based Adaptive Resolution
    for (size_t i = 0; i < num_points; ++i) {
        float px = lidar.x[i];
        float py = lidar.y[i];
        float pz = lidar.z[i];

        float distance = std::sqrt(px * px + py * py);
        
        uint8_t level = resolution_policy_.choose_level_by_distance(distance);
        float resolution = resolution_policy_.get_resolution(level);

        // 3D -> 2.5D Projection
        CellKey key = Projector::project_to_cell(px, py, resolution, level);

        auto it = map_.cells.find(key);
        if (it == map_.cells.end()) {
            Cell new_cell;
            CellStatistics::initialize_cell(new_cell, key, resolution);
            it = map_.cells.insert({key, new_cell}).first;
        }

        Cell& cell = it->second;
        CellStatistics::update_elevation(cell, pz);
    }
    
    // Process Semantics
    for (const auto& sem_pt : semantics) {
        if (sem_pt.point_index < lidar.x.size()) {
            float px = lidar.x[sem_pt.point_index];
            float py = lidar.y[sem_pt.point_index];
            float distance = std::sqrt(px * px + py * py);
            uint8_t level = resolution_policy_.choose_level_by_distance(distance);
            float resolution = resolution_policy_.get_resolution(level);
            
            CellKey key = Projector::project_to_cell(px, py, resolution, level);
            auto it = map_.cells.find(key);
            if (it != map_.cells.end()) {
                CellStatistics::update_semantics(it->second, sem_pt.class_id, sem_pt.confidence);
            }
        }
    }

    // Process Dynamic Tracks
    RefinementEngine::apply_dynamic_tracks(map_, tracks, resolution_policy_);

    // Phase 7 & 8: Evaluate for semantic/dynamic refinement
    // We collect keys first to avoid invalidating iterators when cells split
    std::vector<CellKey> keys_to_evaluate;
    for (const auto& pair : map_.cells) {
        keys_to_evaluate.push_back(pair.first);
    }

    for (const auto& key : keys_to_evaluate) {
        if (RefinementEngine::evaluate_and_refine(map_, key, resolution_policy_, config_.importance_config)) {
            stats_.refined_cells++;
        }
    }

    // Phase 9: Update Uncertainty
    for (auto& pair : map_.cells) {
        UncertaintyEngine::update_uncertainty(pair.second, map_.timestamp_ns);
    }

    // Phase 10: Evaluate and Coarsen
    stats_.coarsened_cells += CoarseningEngine::evaluate_and_coarsen(map_, resolution_policy_, map_.timestamp_ns);
}

MappingStatistics AdaptiveGridEngine::get_statistics() const {
    MappingStatistics current_stats = stats_;
    current_stats.active_cells = map_.cells.size();
    current_stats.map_memory_bytes = map_.cells.size() * sizeof(Cell);
    
    float total_uncertainty = 0.0f;
    for (const auto& pair : map_.cells) {
        if (pair.second.key.level < 8) {
            current_stats.cells_by_level[pair.second.key.level]++;
        }
        total_uncertainty += pair.second.uncertainty;
    }
    
    if (current_stats.active_cells > 0) {
        current_stats.average_uncertainty = total_uncertainty / current_stats.active_cells;
    }
    
    return current_stats;
}

AdaptiveMap AdaptiveGridEngine::get_map() const {
    return map_;
}

void AdaptiveGridEngine::clear() {
    map_.cells.clear();
    stats_ = MappingStatistics();
}

} // namespace mapping
} // namespace nova
