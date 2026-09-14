#include "importance_engine.hpp"
#include <cmath>
#include <algorithm>

namespace nova {
namespace mapping {

float ImportanceEngine::get_semantic_score(uint16_t class_id) {
    switch (class_id) {
        case 10: return 1.0f; // Pedestrian
        case 11: return 1.0f; // Cyclist
        case 9:  return 0.8f; // Vehicle
        case 12: return 0.7f; // OtherObstacle
        case 5:  return 0.5f; // Wall
        case 7:  return 0.5f; // Pole
        case 1:  return 0.2f; // Road
        default: return 0.1f;
    }
}

float ImportanceEngine::calculate_importance(const Cell& cell, const ImportanceConfig& config) {
    float sem_score = get_semantic_score(cell.top_class) * cell.semantic_confidence;
    float dyn_score = cell.dynamic_probability;

    // Decay importance slightly by distance, but keep it high for high intrinsic importance
    float distance = std::sqrt(cell.center_x * cell.center_x + cell.center_y * cell.center_y);
    float distance_factor = std::exp(-config.distance_decay * distance);

    float raw_score = (sem_score * config.semantic_weight + dyn_score * config.dynamic_weight);
    return std::min(1.0f, raw_score * distance_factor);
}

} // namespace mapping
} // namespace nova
