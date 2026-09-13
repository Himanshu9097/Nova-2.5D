"""Synthetic unit tests for the CARLA-independent tracking primitives."""

import unittest

from tracking.dynamic_probability import DynamicProbabilityConfig, dynamic_probability
from tracking.schemas import Detection
from tracking.track import Track, TrackState


class TestTracking(unittest.TestCase):
    """Tests for stationary, moving, and lifecycle behavior."""

    def make_detection(self, class_id, position, frame_id):
        return Detection(
            class_id=class_id,
            x=position[0],
            y=position[1],
            z=position[2],
            confidence=0.95,
            frame_id=frame_id,
            timestamp=float(frame_id),
        )

    def test_stationary_object_has_low_dynamic_probability(self):
        track = Track(self.make_detection(10, (10, 5, 0), 0))
        for frame_id in range(1, 4):
            track.predict(1.0)
            track.update(self.make_detection(10, (10, 5, 0), frame_id))

        self.assertAlmostEqual(track.filter.velocity[0], 0.0, delta=0.15)
        self.assertAlmostEqual(track.filter.velocity[1], 0.0, delta=0.15)
        self.assertLess(track.to_output().dynamic_probability, 0.2)

    def test_moving_vehicle_estimates_positive_velocity(self):
        track = Track(self.make_detection(10, (10, 5, 0), 0))
        for frame_id, x in enumerate((11, 12, 13), start=1):
            track.predict(1.0)
            track.update(self.make_detection(10, (x, 5, 0), frame_id))

        output = track.to_output()
        self.assertGreater(output.vx, 0.5)
        self.assertAlmostEqual(output.vx, 1.0, delta=0.35)
        self.assertGreater(output.dynamic_probability, 0.8)

    def test_moving_pedestrian_estimates_nonzero_velocity(self):
        track = Track(self.make_detection(4, (0, 0, 0), 0))
        for frame_id, y in enumerate((1.0, 2.0, 3.0), start=1):
            track.predict(1.0)
            track.update(self.make_detection(4, (0, y, 0), frame_id))

        output = track.to_output()
        self.assertGreater(output.vy, 0.2)
        self.assertGreater(output.dynamic_probability, 0.5)

    def test_track_lifecycle_and_missed_frames(self):
        first = self.make_detection(10, (1, 1, 0), 0)
        track = Track(first, confirmation_hits=3, max_missed_frames=2)
        self.assertEqual(track.state, TrackState.TENTATIVE)

        for frame_id in (1, 2):
            track.predict(1.0)
            track.update(self.make_detection(10, (1, 1, 0), frame_id))
        self.assertEqual(track.state, TrackState.CONFIRMED)

        track.mark_missed()
        self.assertEqual(track.missed_frames, 1)
        self.assertEqual(track.state, TrackState.CONFIRMED)
        track.mark_missed()
        self.assertEqual(track.missed_frames, 2)
        self.assertEqual(track.state, TrackState.LOST)

    def test_probability_thresholds_are_configurable(self):
        config = DynamicProbabilityConfig(stationary_speed=0.1, moving_speed=0.5)
        self.assertEqual(dynamic_probability((0.05, 0.0, 0.0), config), 0.0)
        self.assertEqual(dynamic_probability((0.5, 0.0, 0.0), config), 1.0)


if __name__ == "__main__":
    unittest.main()
