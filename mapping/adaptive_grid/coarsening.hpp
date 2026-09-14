#pragma once
#include "../storage/sparse_map.hpp"
#include "../core/types.hpp"
#include "resolution_policy.hpp"
#include <vector>

namespace nova {
namespace mapping {

class CoarseningEngine {
public:
    // Tries to merge fine cells into a coarser cell if it doesn't cause information loss
    static uint64_t evaluate_and_coarsen(AdaptiveMap& map, const ResolutionPolicy& policy, int64_t current_time_ns);

private:
    static bool can_coarsen(const Cell& parent, const std::vector<Cell>& children);
};

} // namespace mapping
} // namespace nova
