#include "refinement.hpp"
#include "../projection/projector.hpp"
#include "../cells/cell_statistics.hpp"
#include <cmath>

namespace nova {
namespace mapping {

void RefinementEngine::apply_dynamic_tracks(AdaptiveMap& map, const std::vector<ObjectTrack>& tracks, const ResolutionPolicy& policy) {
    for (const auto& track : tracks) {
        if (track.state == TrackState::LOST) continue;

        // Determine bounding box in XY plane
        float min_x = track.x - track.length / 2.0f;
        float max_x = track.x + track.length / 2.0f;
        float min_y = track.y - track.width / 2.0f;
        float max_y = track.y + track.width / 2.0f;

        // Apply track probability to all affected cells in the map
        for (auto& pair : map.cells) {
            Cell& cell = pair.second;
            if (cell.center_x >= min_x && cell.center_x <= max_x &&
                cell.center_y >= min_y && cell.center_y <= max_y) {
                cell.dynamic_probability = std::max(cell.dynamic_probability, track.dynamic_probability);
                cell.velocity_x = track.vx;
                cell.velocity_y = track.vy;
            }
        }
    }
}

bool RefinementEngine::evaluate_and_refine(AdaptiveMap& map, const CellKey& cell_key, const ResolutionPolicy& policy, const ImportanceConfig& importance_config) {
    auto it = map.cells.find(cell_key);
    if (it == map.cells.end()) return false;

    Cell& cell = it->second;
    float importance = ImportanceEngine::calculate_importance(cell, importance_config);

    // Threshold for refinement
    if (importance > 0.5f && cell.key.level > 0) {
        // Refine to a higher resolution (lower level index)
        uint8_t target_level = cell.key.level - 1;
        split_cell(map, cell_key, target_level, policy);
        return true;
    }
    return false;
}

void RefinementEngine::split_cell(AdaptiveMap& map, const CellKey& parent_key, uint8_t target_level, const ResolutionPolicy& policy) {
    auto it = map.cells.find(parent_key);
    if (it == map.cells.end()) return;
    
    Cell parent = it->second;
    map.cells.erase(it);

    float target_res = policy.get_resolution(target_level);
    
    // Create 4 children for 2x2 split (assuming 2x resolution difference approximately)
    // To be perfectly robust for non-power-of-2 scales, we should project from the bounding box of the parent.
    float half_res = parent.resolution / 2.0f;
    float min_x = parent.center_x - half_res;
    float max_x = parent.center_x + half_res;
    float min_y = parent.center_y - half_res;
    float max_y = parent.center_y + half_res;

    // We can query points inside this bounding box at the target resolution
    int64_t start_ix = static_cast<int64_t>(std::floor(min_x / target_res));
    int64_t end_ix = static_cast<int64_t>(std::floor(max_x / target_res));
    int64_t start_iy = static_cast<int64_t>(std::floor(min_y / target_res));
    int64_t end_iy = static_cast<int64_t>(std::floor(max_y / target_res));

    for (int64_t ix = start_ix; ix <= end_ix; ++ix) {
        for (int64_t iy = start_iy; iy <= end_iy; ++iy) {
            CellKey child_key{target_level, ix, iy};
            Cell child_cell;
            CellStatistics::initialize_cell(child_cell, child_key, target_res);
            
            // Inherit statistics from parent
            child_cell.elevation_mean = parent.elevation_mean;
            child_cell.elevation_min = parent.elevation_min;
            child_cell.elevation_max = parent.elevation_max;
            child_cell.elevation_variance = parent.elevation_variance;
            child_cell.occupancy_probability = parent.occupancy_probability;
            child_cell.occupancy_log_odds = parent.occupancy_log_odds;
            child_cell.semantics = parent.semantics;
            child_cell.top_class = parent.top_class;
            child_cell.semantic_confidence = parent.semantic_confidence;
            child_cell.dynamic_probability = parent.dynamic_probability;
            child_cell.velocity_x = parent.velocity_x;
            child_cell.velocity_y = parent.velocity_y;
            
            map.cells[child_key] = child_cell;
        }
    }
}

} // namespace mapping
} // namespace nova
