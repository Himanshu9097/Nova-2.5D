#pragma once

#include <cstdint>
#include <string>
#include <vector>

namespace nova {
namespace mapping {

struct Pose {
    float x;
    float y;
    float z;
    float roll;
    float pitch;
    float yaw;
};

struct LiDARFrame {
    uint64_t frame_id;
    int64_t timestamp_ns;
    std::string sensor_id;
    std::string coordinate_frame;

    std::vector<float> x;
    std::vector<float> y;
    std::vector<float> z;
    std::vector<float> intensity;

    Pose sensor_pose;
};

struct SemanticPoint {
    uint32_t point_index;
    uint16_t class_id;
    float confidence;
};

enum class TrackState {
    TENTATIVE,
    CONFIRMED,
    LOST
};

struct ObjectTrack {
    uint64_t track_id;
    uint16_t class_id;
    float confidence;

    float x;
    float y;
    float z;
    float vx;
    float vy;
    float vz;

    float length;
    float width;
    float height;
    float yaw;

    float dynamic_probability;
    int64_t first_seen_ns;
    int64_t last_update_ns;

    TrackState state;
};

struct TerrainFeatures {
    float slope;
    float roughness;
    float height_variance;
    float traversability;
    bool obstacle;
    float confidence;
};

} // namespace mapping
} // namespace nova
