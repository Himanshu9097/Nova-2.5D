"""Synthetic tests for semantic point-to-object detection conversion."""

import unittest

from tracking.detection_adapter import (
    ClusteringConfig,
    semantic_points_to_detections,
    semantic_results_to_detections,
)
from tracking.multi_object_tracker import MultiObjectTracker
from tracking.semantic_tracking import SemanticTrackingPipeline


class TestDetectionAdapter(unittest.TestCase):
    """Validate class-aware clustering, noise rejection, and confidence."""

    @staticmethod
    def point(x, y, z, class_id, confidence=0.9):
        return {
            "x": x,
            "y": y,
            "z": z,
            "intensity": 0.5,
            "semantic_class": class_id,
            "semantic_label": "vehicle" if class_id == 10 else "pedestrian",
            "confidence": confidence,
            "semantic_importance": 1.0,
        }

    def test_nearby_vehicle_points_form_one_detection(self):
        points = [
            self.point(10.0, 5.0, 0.0, 10),
            self.point(10.2, 5.0, 0.1, 10),
            self.point(9.8, 5.1, 0.0, 10),
        ]
        detections = semantic_points_to_detections(
            points, frame_id=7, timestamp=12.5,
            config=ClusteringConfig(eps=0.5, min_points=3),
        )
        self.assertEqual(len(detections), 1)
        self.assertEqual(detections[0].class_id, 10)
        self.assertAlmostEqual(detections[0].x, 10.0, places=6)
        self.assertAlmostEqual(detections[0].y, 5.033333, places=5)
        self.assertEqual(detections[0].frame_id, 7)
        self.assertEqual(detections[0].timestamp, 12.5)

    def test_separated_vehicle_groups_form_two_detections(self):
        points = [
            self.point(0.0, 0.0, 0.0, 10),
            self.point(0.1, 0.0, 0.0, 10),
            self.point(0.0, 0.1, 0.0, 10),
            self.point(5.0, 0.0, 0.0, 10),
            self.point(5.1, 0.0, 0.0, 10),
            self.point(5.0, 0.1, 0.0, 10),
        ]
        detections = semantic_points_to_detections(
            points, frame_id=1, timestamp=1.0,
            config=ClusteringConfig(eps=0.3, min_points=3),
        )
        self.assertEqual(len(detections), 2)
        self.assertEqual(sorted(round(detection.x, 1) for detection in detections), [0.0, 5.0])

    def test_nearby_classes_are_clustered_separately(self):
        points = [
            self.point(2.0, 2.0, 0.0, 10),
            self.point(2.1, 2.0, 0.0, 10),
            self.point(2.0, 2.1, 0.0, 10),
            self.point(2.05, 2.05, 0.0, 4),
            self.point(2.15, 2.05, 0.0, 4),
            self.point(2.05, 2.15, 0.0, 4),
        ]
        detections = semantic_points_to_detections(
            points, frame_id=1, timestamp=1.0,
            config=ClusteringConfig(eps=0.3, min_points=3),
        )
        self.assertEqual(len(detections), 2)
        self.assertEqual({detection.class_id for detection in detections}, {4, 10})

    def test_isolated_noise_does_not_create_detection(self):
        points = [
            self.point(0.0, 0.0, 0.0, 10),
            self.point(10.0, 10.0, 0.0, 10),
        ]
        detections = semantic_points_to_detections(
            points, frame_id=1, timestamp=1.0,
            config=ClusteringConfig(eps=0.5, min_points=2),
        )
        self.assertEqual(detections, [])

    def test_cluster_confidence_is_mean_of_point_confidences(self):
        points = [
            self.point(1.0, 1.0, 1.0, 10, 0.6),
            self.point(1.1, 1.0, 1.0, 10, 0.8),
            self.point(1.0, 1.1, 1.0, 10, 1.0),
        ]
        detections = semantic_points_to_detections(
            points, frame_id=1, timestamp=1.0,
            config=ClusteringConfig(eps=0.3, min_points=3),
        )
        self.assertEqual(len(detections), 1)
        self.assertAlmostEqual(detections[0].confidence, 0.8)

    def test_low_confidence_points_are_filtered(self):
        points = [
            self.point(1.0, 1.0, 1.0, 10, 0.4),
            self.point(1.1, 1.0, 1.0, 10, 0.4),
            self.point(1.0, 1.1, 1.0, 10, 0.4),
        ]
        self.assertEqual(
            semantic_points_to_detections(
                points, frame_id=1, timestamp=1.0,
                config=ClusteringConfig(confidence_threshold=0.5),
            ),
            [],
        )

    def test_verified_semantic_results_structure_is_adapted(self):
        results = {
            "points": [
                {
                    "x": 15.0,
                    "y": -4.0,
                    "z": 0.5,
                    "intensity": 0.7,
                    "semantic_class": 10,
                    "semantic_label": "Vehicle",
                    "confidence": 0.9,
                    "semantic_importance": 0.8,
                },
                {
                    "x": 15.2,
                    "y": -4.0,
                    "z": 0.5,
                    "intensity": 0.6,
                    "semantic_class": 10,
                    "semantic_label": "Vehicle",
                    "confidence": 0.8,
                    "semantic_importance": 0.9,
                },
                {
                    "x": 15.0,
                    "y": -4.2,
                    "z": 0.5,
                    "intensity": 0.65,
                    "semantic_class": 10,
                    "semantic_label": "Vehicle",
                    "confidence": 1.0,
                    "semantic_importance": 0.85,
                },
            ],
        }

        detections = semantic_results_to_detections(
            results,
            frame_id=42,
            timestamp=123.5,
            config=ClusteringConfig(eps=0.5, min_points=3),
        )

        self.assertEqual(len(detections), 1)
        detection = detections[0]
        self.assertEqual(detection.class_id, 10)
        self.assertAlmostEqual(detection.x, 15.066666, places=5)
        self.assertAlmostEqual(detection.y, -4.066666, places=5)
        self.assertAlmostEqual(detection.z, 0.5)
        self.assertAlmostEqual(detection.confidence, 0.9)
        self.assertEqual(detection.frame_id, 42)
        self.assertEqual(detection.timestamp, 123.5)

    def test_semantic_frames_feed_one_persistent_tracker(self):
        pipeline = SemanticTrackingPipeline(
            tracker=MultiObjectTracker(
                association_distance=2.0,
                confirmation_hits=1,
            ),
            clustering_config=ClusteringConfig(eps=0.5, min_points=3),
        )

        def semantic_frame(x):
            return {
                "points": [
                    self.point(x, 0.0, 0.0, 10, 0.9),
                    self.point(x + 0.1, 0.0, 0.0, 10, 0.9),
                    self.point(x, 0.1, 0.0, 10, 0.9),
                ],
            }

        first_outputs = pipeline.process_frame(
            semantic_frame(10.0),
            frame_id=100,
            timestamp=10.0,
            dt=1.0,
        )
        first_detection = pipeline.last_detections[0]
        second_outputs = pipeline.process_frame(
            semantic_frame(11.0),
            frame_id=101,
            timestamp=11.0,
            dt=1.0,
        )
        second_detection = pipeline.last_detections[0]

        self.assertEqual(len(first_outputs), 1)
        self.assertEqual(len(second_outputs), 1)
        self.assertEqual(first_outputs[0].track_id, second_outputs[0].track_id)
        self.assertGreater(second_outputs[0].vx, 0.0)
        self.assertGreater(
            second_outputs[0].dynamic_probability,
            first_outputs[0].dynamic_probability,
        )
        self.assertEqual(first_detection.frame_id, 100)
        self.assertEqual(first_detection.timestamp, 10.0)
        self.assertEqual(second_detection.frame_id, 101)
        self.assertEqual(second_detection.timestamp, 11.0)


if __name__ == "__main__":
    unittest.main()
