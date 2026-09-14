#pragma once
#include "../cells/cell.hpp"
#include <functional>
#include <cstddef>

namespace nova {
namespace mapping {

struct CellKeyHash {
    std::size_t operator()(const CellKey& key) const {
        std::size_t h1 = std::hash<int64_t>{}(key.ix);
        std::size_t h2 = std::hash<int64_t>{}(key.iy);
        std::size_t h3 = std::hash<uint8_t>{}(key.level);
        return h1 ^ (h2 << 1) ^ (h3 << 2);
    }
};

} // namespace mapping
} // namespace nova
