import os
import sys
import numpy as np

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.prior_map import PriorMapEngine

def test_prior_map():
    map_path = os.path.join(PROJECT_ROOT, 'data', 'maps', 'Town10HD_Opt_prior_2.5d.npz')
    engine = PriorMapEngine(map_path)
    assert engine.is_loaded(), "PriorMapEngine failed to load map"
    assert engine.get_total_cells() > 0, "No cells loaded in prior map"
    print(f"PASS: PriorMapEngine loaded {engine.get_total_cells():,} cells from {engine.map_name}")
    
    # Test local window
    window = engine.query_local_window(0.0, 0.0, radius=50.0)
    print(f"PASS: Local window returned {len(window['elevation_z']):,} cells")
    
    # Test ground truth metrics
    test_xy = engine.points_xy[:100]
    test_z = engine.elevation_z[:100]
    m_exact = engine.compute_ground_truth_metrics(test_xy, test_z)
    assert m_exact['rmse_cm'] == 0.0, f"Expected 0.0 rmse, got {m_exact['rmse_cm']}"
    assert m_exact['accuracy'] == 100.0, f"Expected 100.0 accuracy, got {m_exact['accuracy']}"
    print(f"PASS: Exact points -> RMSE: {m_exact['rmse_cm']} cm, Accuracy: {m_exact['accuracy']}%")
    
    # Test with 3 cm offset
    m_3cm = engine.compute_ground_truth_metrics(test_xy, test_z + 0.03)
    assert abs(m_3cm['rmse_cm'] - 3.0) < 0.1, f"Expected ~3.0 cm, got {m_3cm['rmse_cm']}"
    assert m_3cm['accuracy'] == 100.0, f"Expected 100.0% within 5cm tolerance, got {m_3cm['accuracy']}%"
    print(f"PASS: 3cm offset -> RMSE: {m_3cm['rmse_cm']} cm, Accuracy: {m_3cm['accuracy']}%")

    # Test dynamic vs static classification
    test_points = np.array([
        [0.0, 0.0, 0.0],
        [0.0, 0.0, 1.5]
    ], dtype=np.float32)
    test_tags = np.array([7, 4], dtype=np.uint32) # Road, Pedestrian
    is_dyn, is_stat = engine.classify_dynamic_vs_static(test_points, test_tags)
    assert not is_dyn[0] and is_stat[0], "Road should be static"
    assert is_dyn[1] and not is_stat[1], "Pedestrian should be dynamic"
    print("PASS: Dynamic vs Static classification verified")
    print("ALL TESTS PASSED SUCCESSFULLY!")

if __name__ == '__main__':
    test_prior_map()
