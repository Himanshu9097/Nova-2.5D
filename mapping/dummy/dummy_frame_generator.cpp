#include "dummy_frame_generator.hpp"

namespace nova {
namespace mapping {

LiDARFrame DummyFrameGenerator::generate_lidar_frame() {
    LiDARFrame frame;
    frame.frame_id = 100;
    frame.timestamp_ns = 1000000000;
    
    // Scenario 1: Flat road close by
    for (int x = 0; x < 20; ++x) {
        for (int y = -3; y <= 3; ++y) {
            frame.x.push_back(static_cast<float>(x));
            frame.y.push_back(static_cast<float>(y));
            frame.z.push_back(0.0f);
            frame.intensity.push_back(0.8f);
        }
    }
    
    // Scenario 2: Pedestrian at 60m
    frame.x.push_back(60.0f);
    frame.y.push_back(2.0f);
    frame.z.push_back(1.0f); 
    frame.intensity.push_back(0.5f);
    
    // Scenario 3: Pothole
    frame.x.push_back(10.0f);
    frame.y.push_back(0.0f);
    frame.z.push_back(-0.15f);
    frame.intensity.push_back(0.2f);

    return frame;
}

std::vector<SemanticPoint> DummyFrameGenerator::generate_semantics() {
    std::vector<SemanticPoint> semantics;
    // Map road points
    for (uint32_t i = 0; i < 20 * 7; ++i) {
        semantics.push_back({i, 1, 0.95f}); // Road
    }
    // Pedestrian point
    semantics.push_back({20 * 7, 10, 0.98f}); // Pedestrian
    // Pothole point (Road)
    semantics.push_back({20 * 7 + 1, 1, 0.8f}); // Road
    
    return semantics;
}

std::vector<ObjectTrack> DummyFrameGenerator::generate_tracks() {
    std::vector<ObjectTrack> tracks;
    
    ObjectTrack ped_track;
    ped_track.track_id = 1;
    ped_track.class_id = 10;
    ped_track.confidence = 0.98f;
    ped_track.x = 60.0f;
    ped_track.y = 2.0f;
    ped_track.z = 1.0f;
    ped_track.length = 0.5f;
    ped_track.width = 0.5f;
    ped_track.height = 1.8f;
    ped_track.vx = -1.0f;
    ped_track.vy = 0.0f;
    ped_track.vz = 0.0f;
    ped_track.dynamic_probability = 0.95f;
    ped_track.state = TrackState::CONFIRMED;
    
    tracks.push_back(ped_track);
    return tracks;
}

} // namespace mapping
} // namespace nova
