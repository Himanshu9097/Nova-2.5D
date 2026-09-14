cmake_minimum_required(VERSION 3.10)
project(Nova-2.5D-Mapping)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

include_directories(mapping)

set(MAPPING_SOURCES
    mapping/projection/projector.cpp
    mapping/adaptive_grid/resolution_policy.cpp
    mapping/adaptive_grid/importance_engine.cpp
    mapping/adaptive_grid/refinement.cpp
    mapping/adaptive_grid/coarsening.cpp
    mapping/uncertainty/uncertainty.cpp
    mapping/adaptive_grid/adaptive_grid_engine.cpp
    mapping/dummy/dummy_frame_generator.cpp
)

add_library(mapping_lib STATIC ${MAPPING_SOURCES})

add_executable(dummy_test mapping/dummy/dummy_test.cpp)
target_link_libraries(dummy_test mapping_lib)

add_executable(simulation_runner mapping/simulation_runner.cpp)
target_link_libraries(simulation_runner mapping_lib)
