#include "projector.hpp"
#include <cmath>

namespace nova {
namespace mapping {

CellKey Projector::project_to_cell(float x, float y, float resolution, uint8_t level) {
    int64_t ix = static_cast<int64_t>(std::floor(x / resolution));
    int64_t iy = static_cast<int64_t>(std::floor(y / resolution));
    return CellKey{level, ix, iy};
}

} // namespace mapping
} // namespace nova
