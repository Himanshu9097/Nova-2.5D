#pragma once
#include "../storage/sparse_map.hpp"
#include "../core/types.hpp"
#include "resolution_policy.hpp"
#include "importance_engine.hpp"
#include <vector>

namespace nova {
namespace mapping {

class RefinementEngine {
public:
    // Mark cells in map with dynamic probability based on tracks
    static void apply_dynamic_tracks(AdaptiveMap& map, const std::vector<ObjectTrack>& tracks, const ResolutionPolicy& policy);
    
    // Check if cell needs refinement based on importance and split it if necessary
    static bool evaluate_and_refine(AdaptiveMap& map, const CellKey& cell_key, const ResolutionPolicy& policy, const ImportanceConfig& importance_config);

private:
    static void split_cell(AdaptiveMap& map, const CellKey& parent_key, uint8_t target_level, const ResolutionPolicy& policy);
};

} // namespace mapping
} // namespace nova
