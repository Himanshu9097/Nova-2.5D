#pragma once
#include "../hierarchy/resolution_level.hpp"
#include <vector>

namespace nova {
namespace mapping {

class ResolutionPolicy {
public:
    ResolutionPolicy() = default;
    explicit ResolutionPolicy(const std::vector<ResolutionLevel>& levels);

    uint8_t choose_level_by_distance(float distance) const;
    float get_resolution(uint8_t level) const;
    const std::vector<ResolutionLevel>& get_levels() const { return levels_; }

private:
    std::vector<ResolutionLevel> levels_;
};

} // namespace mapping
} // namespace nova
