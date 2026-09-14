#pragma once
#include "../cells/cell.hpp"

namespace nova {
namespace mapping {

class Projector {
public:
    static CellKey project_to_cell(float x, float y, float resolution, uint8_t level);
};

} // namespace mapping
} // namespace nova
