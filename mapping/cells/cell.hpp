#pragma once

#include <cstdint>
#include "semantic_distribution.hpp"

namespace nova {
namespace mapping {

struct CellKey {
    uint8_t level;
    int64_t ix;
    int64_t iy;

    bool operator==(const CellKey& other) const {
        return level == other.level &&
               ix == other.ix &&
               iy == other.iy;
    }
};

struct Cell {
    CellKey key;
    float resolution;
    float center_x;
    float center_y;

    // Elevation
    float elevation_mean;
    float elevation_min;
    float elevation_max;
    float elevation_variance;

    // Occupancy
    float occupancy_probability;
    float occupancy_log_odds;

    // Semantic
    SemanticDistribution semantics;
    uint16_t top_class;
    float semantic_confidence;

    // Static / Dynamic
    float static_probability;
    float dynamic_probability;

    // Motion
    float velocity_x;
    float velocity_y;

    // Quality
    uint32_t observation_count;
    int64_t last_update_ns;
    float uncertainty;
};

} // namespace mapping
} // namespace nova
