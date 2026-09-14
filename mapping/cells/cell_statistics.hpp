#pragma once
#include "cell.hpp"
#include <algorithm>

namespace nova {
namespace mapping {

class CellStatistics {
public:
    static void initialize_cell(Cell& cell, const CellKey& key, float resolution) {
        cell.key = key;
        cell.resolution = resolution;
        cell.center_x = (key.ix + 0.5f) * resolution;
        cell.center_y = (key.iy + 0.5f) * resolution;

        cell.elevation_mean = 0.0f;
        cell.elevation_min = 1e9f;
        cell.elevation_max = -1e9f;
        cell.elevation_variance = 0.0f;

        cell.occupancy_probability = 0.0f;
        cell.occupancy_log_odds = 0.0f;
        
        cell.semantics.probabilities.clear();
        cell.top_class = 0;
        cell.semantic_confidence = 0.0f;

        cell.static_probability = 0.5f;
        cell.dynamic_probability = 0.0f;
        cell.velocity_x = 0.0f;
        cell.velocity_y = 0.0f;

        cell.observation_count = 0;
        cell.last_update_ns = 0;
        cell.uncertainty = 1.0f;
    }

    static void update_elevation(Cell& cell, float z) {
        cell.observation_count++;
        
        if (cell.observation_count == 1) {
            cell.elevation_min = z;
            cell.elevation_max = z;
            cell.elevation_mean = z;
            cell.elevation_variance = 0.0f;
        } else {
            cell.elevation_min = std::min(cell.elevation_min, z);
            cell.elevation_max = std::max(cell.elevation_max, z);

            float delta = z - cell.elevation_mean;
            cell.elevation_mean += delta / cell.observation_count;
            float delta2 = z - cell.elevation_mean;
            
            // Welford's online algorithm for variance
            cell.elevation_variance = ((cell.observation_count - 1) * cell.elevation_variance + delta * delta2) / cell.observation_count;
        }
    }

    static void update_occupancy(Cell& cell, bool is_occupied, float prob_hit = 0.7f, float prob_miss = 0.4f) {
        // Simple log odds update
        auto log_odds = [](float p) { return std::log(p / (1.0f - p)); };
        auto prob_from_log_odds = [](float lo) { return 1.0f - (1.0f / (1.0f + std::exp(lo))); };

        float update_lo = is_occupied ? log_odds(prob_hit) : log_odds(prob_miss);
        cell.occupancy_log_odds += update_lo;
        
        // Clamp log odds
        cell.occupancy_log_odds = std::max(-10.0f, std::min(10.0f, cell.occupancy_log_odds));
        cell.occupancy_probability = prob_from_log_odds(cell.occupancy_log_odds);
    }

    static void update_semantics(Cell& cell, uint16_t class_id, float confidence) {
        bool found = false;
        for (auto& prob : cell.semantics.probabilities) {
            if (prob.class_id == class_id) {
                // simple rolling average of probability for now
                prob.probability = (prob.probability * cell.observation_count + confidence) / (cell.observation_count + 1);
                found = true;
                break;
            }
        }
        
        if (!found) {
            cell.semantics.probabilities.push_back({class_id, confidence / (cell.observation_count + 1)});
        }
        
        // Normalize
        float sum = 0.0f;
        for (const auto& prob : cell.semantics.probabilities) {
            sum += prob.probability;
        }
        
        float max_prob = -1.0f;
        for (auto& prob : cell.semantics.probabilities) {
            if (sum > 0.0f) {
                prob.probability /= sum;
            }
            if (prob.probability > max_prob) {
                max_prob = prob.probability;
                cell.top_class = prob.class_id;
                cell.semantic_confidence = max_prob;
            }
        }
    }
};

} // namespace mapping
} // namespace nova
