#pragma once
#include <cstdint>

namespace nova {
namespace mapping {

struct ResolutionLevel {
    uint8_t level;
    float resolution;
    float min_range;
    float max_range;
};

} // namespace mapping
} // namespace nova
