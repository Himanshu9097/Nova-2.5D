#pragma once
#include "../cells/cell.hpp"
#include "cell_hash.hpp"
#include <unordered_map>
#include <cstdint>

namespace nova {
namespace mapping {

struct AdaptiveMap {
    uint64_t frame_id;
    int64_t timestamp_ns;
    std::unordered_map<CellKey, Cell, CellKeyHash> cells;
};

} // namespace mapping
} // namespace nova
