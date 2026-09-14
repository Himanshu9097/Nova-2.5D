#include "coarsening.hpp"
#include "../hierarchy/parent_child.hpp"
#include "../cells/cell_statistics.hpp"
#include <unordered_map>
#include <vector>
#include <cmath>

namespace nova {
namespace mapping {

uint64_t CoarseningEngine::evaluate_and_coarsen(AdaptiveMap& map, const ResolutionPolicy& policy, int64_t current_time_ns) {
    std::unordered_map<CellKey, std::vector<CellKey>, CellKeyHash> parent_to_children;

    // 1. Group active fine cells by their prospective parent
    for (const auto& pair : map.cells) {
        const Cell& cell = pair.second;
        
        float distance = std::sqrt(cell.center_x * cell.center_x + cell.center_y * cell.center_y);
        uint8_t base_level = policy.choose_level_by_distance(distance);
        
        // If cell is finer than base_level, it's a candidate for coarsening
        if (cell.key.level < base_level) {
            uint8_t parent_level = cell.key.level + 1;
            CellKey parent_key = ParentChildMapper::get_parent(cell, parent_level, policy);
            parent_to_children[parent_key].push_back(cell.key);
        }
    }

    // 2. Evaluate each parent group
    uint64_t coarsened = 0;
    for (const auto& pair : parent_to_children) {
        const CellKey& parent_key = pair.first;
        const std::vector<CellKey>& child_keys = pair.second;

        std::vector<Cell> children;
        for (const auto& ck : child_keys) {
            children.push_back(map.cells.at(ck));
        }

        Cell parent_cell;
        float parent_res = policy.get_resolution(parent_key.level);
        CellStatistics::initialize_cell(parent_cell, parent_key, parent_res);

        // Aggregate statistics
        float min_z = 1e9f, max_z = -1e9f;
        float sum_z = 0.0f;
        float sum_dyn = 0.0f;
        uint32_t total_obs = 0;
        float max_uncertainty = 0.0f;
        
        // Naive semantics aggregation for evaluation
        std::unordered_map<uint16_t, float> class_scores;

        for (const auto& child : children) {
            min_z = std::min(min_z, child.elevation_min);
            max_z = std::max(max_z, child.elevation_max);
            sum_z += child.elevation_mean * child.observation_count;
            total_obs += child.observation_count;
            sum_dyn = std::max(sum_dyn, child.dynamic_probability);
            max_uncertainty = std::max(max_uncertainty, child.uncertainty);
            class_scores[child.top_class] += child.semantic_confidence;
        }

        if (total_obs > 0) {
            parent_cell.elevation_min = min_z;
            parent_cell.elevation_max = max_z;
            parent_cell.elevation_mean = sum_z / total_obs;
            parent_cell.observation_count = total_obs;
        }

        parent_cell.dynamic_probability = sum_dyn;
        parent_cell.uncertainty = max_uncertainty;
        
        float max_score = -1.0f;
        uint16_t best_class = 0;
        for (const auto& sc : class_scores) {
            if (sc.second > max_score) {
                max_score = sc.second;
                best_class = sc.first;
            }
        }
        parent_cell.top_class = best_class;

        // 3. Information-preserving Merge Gate
        if (can_coarsen(parent_cell, children)) {
            // Re-assign semantics properly to parent
            for (const auto& child : children) {
                for (const auto& prob : child.semantics.probabilities) {
                    CellStatistics::update_semantics(parent_cell, prob.class_id, prob.probability);
                }
            }

            for (const auto& ck : child_keys) {
                map.cells.erase(ck);
            }
            map.cells[parent_key] = parent_cell;
            coarsened += child_keys.size();
        }
    }
    return coarsened;
}

bool CoarseningEngine::can_coarsen(const Cell& parent, const std::vector<Cell>& children) {
    if (children.empty()) return false;

    // Elevation variance check
    if (parent.elevation_max - parent.elevation_min > 0.2f) { // Vertical threshold
        return false;
    }

    // Semantic divergence check
    uint16_t dominant_class = children[0].top_class;
    for (const auto& child : children) {
        if (child.top_class != dominant_class) {
            return false;
        }
    }

    // Dynamic activity check
    if (parent.dynamic_probability > 0.3f) {
        return false;
    }

    // Uncertainty check
    if (parent.uncertainty > 0.6f) {
        return false;
    }

    return true;
}

} // namespace mapping
} // namespace nova
