#pragma once
#include "../cells/cell.hpp"
#include <cstdint>

namespace nova {
namespace mapping {

class UncertaintyEngine {
public:
    static void update_uncertainty(Cell& cell, int64_t current_time_ns);
};

} // namespace mapping
} // namespace nova
