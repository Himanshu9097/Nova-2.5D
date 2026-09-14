#pragma once

#include "../core/types.hpp"
#include "../storage/sparse_map.hpp"
#include "../adaptive_grid/resolution_policy.hpp"
#include "../adaptive_grid/importance_engine.hpp"

namespace nova {
namespace mapping {

struct MappingConfig {
    std::vector<ResolutionLevel> resolution_levels;
    float default_resolution = 0.05f;
    uint8_t default_level = 0;
    ImportanceConfig importance_config;
};

struct MappingStatistics {
    uint64_t total_points_processed = 0;
    uint64_t active_cells = 0;
    uint64_t cells_by_level[8] = {0};
    uint64_t refined_cells = 0;
    uint64_t coarsened_cells = 0;
    float processing_time_ms = 0.0f;
    float map_memory_bytes = 0.0f;
    float average_uncertainty = 0.0f;
};

class AdaptiveGridEngine {
public:
    explicit AdaptiveGridEngine(const MappingConfig& config);

    void update(
        const LiDARFrame& lidar,
        const std::vector<SemanticPoint>& semantics,
        const std::vector<ObjectTrack>& tracks,
        const std::vector<TerrainFeatures>& terrain
    );

    AdaptiveMap get_map() const;
    MappingStatistics get_statistics() const;
    void clear();

private:
    MappingConfig config_;
    AdaptiveMap map_;
    ResolutionPolicy resolution_policy_;
    MappingStatistics stats_;
};

} // namespace mapping
} // namespace nova
