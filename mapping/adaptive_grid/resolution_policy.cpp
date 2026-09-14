#include "resolution_policy.hpp"

namespace nova {
namespace mapping {

ResolutionPolicy::ResolutionPolicy(const std::vector<ResolutionLevel>& levels) 
    : levels_(levels) {}

uint8_t ResolutionPolicy::choose_level_by_distance(float distance) const {
    for (const auto& level : levels_) {
        if (distance >= level.min_range && distance < level.max_range) {
            return level.level;
        }
    }
    if (!levels_.empty()) {
        return levels_.back().level; // default to coarsest if beyond max_range
    }
    return 0;
}

float ResolutionPolicy::get_resolution(uint8_t level) const {
    for (const auto& l : levels_) {
        if (l.level == level) {
            return l.resolution;
        }
    }
    return 0.05f; // fallback to 5cm
}

} // namespace mapping
} // namespace nova
