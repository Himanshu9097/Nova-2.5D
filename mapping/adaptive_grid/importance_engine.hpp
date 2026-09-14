#pragma once
#include "../cells/cell.hpp"

namespace nova {
namespace mapping {

struct ImportanceConfig {
    float semantic_weight = 1.0f;
    float dynamic_weight = 1.0f;
    float distance_decay = 0.01f;
};

class ImportanceEngine {
public:
    static float calculate_importance(const Cell& cell, const ImportanceConfig& config = ImportanceConfig());
    static float get_semantic_score(uint16_t class_id);
};

} // namespace mapping
} // namespace nova
