#pragma once

#include <cstdint>
#include <vector>

namespace nova {
namespace mapping {

struct SemanticProbability {
    uint16_t class_id;
    float probability;
};

struct SemanticDistribution {
    std::vector<SemanticProbability> probabilities;
};

} // namespace mapping
} // namespace nova
