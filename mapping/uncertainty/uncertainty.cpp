#include "uncertainty.hpp"
#include <cmath>
#include <algorithm>

namespace nova {
namespace mapping {

void UncertaintyEngine::update_uncertainty(Cell& cell, int64_t current_time_ns) {
    float distance = std::sqrt(cell.center_x * cell.center_x + cell.center_y * cell.center_y);
    
    // Farther points have higher base uncertainty
    float dist_uncertainty = std::min(1.0f, distance / 100.0f);
    
    // More observations reduce uncertainty
    float obs_uncertainty = 1.0f / (1.0f + cell.observation_count * 0.1f);
    
    // Low semantic confidence increases uncertainty
    float sem_uncertainty = 1.0f - cell.semantic_confidence;
    
    // Time since last observation increases uncertainty
    float time_uncertainty = 0.0f;
    if (cell.last_update_ns > 0 && current_time_ns > cell.last_update_ns) {
        float dt_sec = (current_time_ns - cell.last_update_ns) * 1e-9f;
        time_uncertainty = std::min(1.0f, dt_sec / 10.0f); // 10s to full uncertainty
    }
    
    cell.uncertainty = (dist_uncertainty * 0.3f) + (obs_uncertainty * 0.3f) + (sem_uncertainty * 0.2f) + (time_uncertainty * 0.2f);
    cell.uncertainty = std::min(1.0f, std::max(0.0f, cell.uncertainty));
}

} // namespace mapping
} // namespace nova
