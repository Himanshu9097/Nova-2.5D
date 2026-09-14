#pragma once
#include "../cells/cell.hpp"
#include "../projection/projector.hpp"
#include "../adaptive_grid/resolution_policy.hpp"

namespace nova {
namespace mapping {

class ParentChildMapper {
public:
    static CellKey get_parent(const Cell& child, uint8_t parent_level, const ResolutionPolicy& policy) {
        float parent_res = policy.get_resolution(parent_level);
        return Projector::project_to_cell(child.center_x, child.center_y, parent_res, parent_level);
    }
    
    // We do not enforce a strict 2x2 split since resolutions are not exactly powers of two.
    // Instead, spatial lookups map points back down to finer resolution levels using the Projector directly.
};

} // namespace mapping
} // namespace nova
