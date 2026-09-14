#include "adaptive_grid/adaptive_grid_engine.hpp"
#include "core/json.hpp"
#include <iostream>
#include <fstream>
#include <string>
#include <vector>

using json = nlohmann::json;
using namespace nova::mapping;

int main(int argc, char** argv) {
    std::cout << "--- Nova-2.5D C++ Simulation Runner ---\n";
    
    if (argc < 2) {
        std::cerr << "Usage: simulation_runner <path_to_json_file>\n";
        return 1;
    }
    
    std::string json_file_path = argv[1];
    std::ifstream f(json_file_path);
    if (!f.is_open()) {
        std::cerr << "Error: Could not open file " << json_file_path << "\n";
        return 1;
    }
    
    json data = json::parse(f);
    
    std::cout << "Loaded CARLA Frame ID: " << data["frame_id"] << "\n";
    
    // Parse into C++ types
    LiDARFrame lidar_frame;
    lidar_frame.frame_id = data["frame_id"];
    lidar_frame.timestamp_ns = data["timestamp_ns"];
    
    std::vector<SemanticPoint> semantics;
    if (data.contains("semantics") && data["semantics"].is_array()) {
        for (const auto& sem : data["semantics"]) {
            SemanticPoint sp;
            sp.point_index = sem["point_index"];
            sp.class_id = sem["class_id"];
            sp.confidence = sem["confidence"];
            semantics.push_back(sp);
        }
    }
    
    if (data.contains("points") && data["points"].is_array()) {
        for (const auto& pt : data["points"]) {
            lidar_frame.x.push_back(pt[0]);
            lidar_frame.y.push_back(pt[1]);
            lidar_frame.z.push_back(pt[2]);
            lidar_frame.intensity.push_back(0.5f);
        }
    }
    
    // Fix up the tracked pedestrian point coordinates based on the track
    std::vector<ObjectTrack> tracks;
    for (const auto& trk : data["tracks"]) {
        ObjectTrack ot;
        ot.track_id = trk["track_id"];
        ot.class_id = trk["class_id"];
        ot.confidence = trk["confidence"];
        ot.x = trk["x"];
        ot.y = trk["y"];
        ot.z = trk["z"];
        ot.vx = trk["vx"];
        ot.vy = trk["vy"];
        ot.vz = trk["vz"];
        ot.length = trk["length"];
        ot.width = trk["width"];
        ot.height = trk["height"];
        ot.yaw = trk["yaw"];
        ot.dynamic_probability = trk["dynamic_probability"];
        ot.first_seen_ns = trk["first_seen_ns"];
        ot.last_update_ns = trk["last_update_ns"];
        ot.state = static_cast<TrackState>(trk["state"].get<int>());
        tracks.push_back(ot);
        
        // Sync raw point with tracking point for demonstration
        if (!lidar_frame.x.empty()) {
            lidar_frame.x.back() = ot.x;
            lidar_frame.y.back() = ot.y;
            lidar_frame.z.back() = ot.z;
        }
    }
    
    // Run the engine
    MappingConfig config;
    config.resolution_levels = {
        {0, 0.05f, 0.0f, 10.0f},
        {1, 0.10f, 10.0f, 25.0f},
        {2, 0.25f, 25.0f, 50.0f},
        {3, 0.50f, 50.0f, 100.0f}
    };
    
    AdaptiveGridEngine engine(config);
    std::vector<TerrainFeatures> terrain;
    
    std::cout << "Executing Adaptive Grid Engine Update...\n";
    engine.update(lidar_frame, semantics, tracks, terrain);
    
    auto stats = engine.get_statistics();
    std::cout << "[MAP STATISTICS]\n";
    std::cout << "Valid points: " << stats.total_points_processed << "\n";
    std::cout << "Active Cells: " << stats.active_cells << "\n";
    std::cout << "Level 0 (5cm): " << stats.cells_by_level[0] << "\n";
    std::cout << "Level 3 (50cm): " << stats.cells_by_level[3] << "\n";
    std::cout << "Refined Cells: " << stats.refined_cells << "\n";
    std::cout << "Coarsened Cells: " << stats.coarsened_cells << "\n";
    std::cout << "Map memory bytes: " << stats.map_memory_bytes << "\n";
    
    // Dump map for visualization
    json export_data;
    export_data["cells"] = json::array();
    
    AdaptiveMap final_map = engine.get_map();
    for (const auto& pair : final_map.cells) {
        const Cell& cell = pair.second;
        json cell_json = {
            {"level", cell.key.level},
            {"center_x", cell.center_x},
            {"center_y", cell.center_y},
            {"elevation", cell.elevation_mean},
            {"class_id", cell.top_class},
            {"uncertainty", cell.uncertainty}
        };
        export_data["cells"].push_back(cell_json);
    }
    
    std::ofstream out_f("map_export.json");
    out_f << export_data.dump(2);
    out_f.close();
    std::cout << "Exported map grid to map_export.json for visualization.\n";
    
    return 0;
}
