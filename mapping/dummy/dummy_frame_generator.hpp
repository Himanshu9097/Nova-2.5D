#pragma once
#include "../core/types.hpp"
#include <vector>

namespace nova {
namespace mapping {

struct DummyFrameGenerator {
    static LiDARFrame generate_lidar_frame();
    static std::vector<SemanticPoint> generate_semantics();
    static std::vector<ObjectTrack> generate_tracks();
};

} // namespace mapping
} // namespace nova
