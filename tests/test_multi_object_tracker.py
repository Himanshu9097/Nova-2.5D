"""Synthetic tests for multi-object nearest-distance association."""

import unittest

from tracking.multi_object_tracker import MultiObjectTracker
from tracking.schemas import Detection
from tracking.track import TrackState


class TestMultiObjectTracker(unittest.TestCase):
    """Validate association, creation, prediction, and class gating."""

    @staticmethod
    def detection(class_id, position, frame_id):
        return Detection(
            class_id=class_id,
            x=position[0],
            y=position[1],
            z=position[2],
            confidence=0.95,
            frame_id=frame_id,
            timestamp=float(frame_id),
        )

    def test_two_moving_vehicles_keep_ids_and_velocity_signs(self):
        tracker = MultiObjectTracker(
            association_distance=2.0,
            confirmation_hits=1,
        )
        frames = [
            [(10, 5, 0), (20, 5, 0)],
            [(11, 5, 0), (19, 5, 0)],
            [(12, 5, 0), (18, 5, 0)],
        ]

        initial_outputs = []
        outputs = []
        for frame_id, positions in enumerate(frames):
            outputs = tracker.update([
                self.detection(10, position, frame_id)
                for position in positions
            ], dt=1.0)
            if frame_id == 0:
                initial_outputs = outputs

        self.assertEqual(len(outputs), 2)
        track_a_id = min(initial_outputs, key=lambda output: abs(output.x - 10.0)).track_id
        track_b_id = min(initial_outputs, key=lambda output: abs(output.x - 20.0)).track_id
        final_by_id = {output.track_id: output for output in outputs}
        self.assertNotEqual(track_a_id, track_b_id)
        self.assertGreater(final_by_id[track_a_id].vx, 0.0)
        self.assertLess(final_by_id[track_b_id].vx, 0.0)

    def test_new_object_gets_new_track_id(self):
        tracker = MultiObjectTracker(confirmation_hits=1)
        first_outputs = tracker.update([
            self.detection(10, (10, 0, 0), 0),
        ])
        existing_id = first_outputs[0].track_id

        outputs = tracker.update([
            self.detection(10, (10, 0, 0), 1),
            self.detection(10, (20, 0, 0), 1),
        ])
        self.assertEqual(len(outputs), 2)
        self.assertIn(existing_id, {output.track_id for output in outputs})
        self.assertEqual(len({output.track_id for output in outputs}), 2)

    def test_missing_object_is_predicted_then_marked_lost(self):
        tracker = MultiObjectTracker(
            association_distance=2.0,
            confirmation_hits=1,
            max_missed_frames=2,
        )
        tracker.update([self.detection(10, (0, 0, 0), 0)])
        tracker.update([self.detection(10, (1, 0, 0), 1)])
        track_id = tracker.tracks[0].track_id

        outputs = tracker.update([], dt=1.0)
        track = next(track for track in tracker.tracks if track.track_id == track_id)
        self.assertEqual(track.missed_frames, 1)
        self.assertNotEqual(track.state, TrackState.LOST)
        self.assertGreater(next(output for output in outputs if output.track_id == track_id).x, 1.0)

        outputs = tracker.update([], dt=1.0)
        track = next(track for track in tracker.tracks if track.track_id == track_id)
        self.assertEqual(track.state, TrackState.LOST)
        self.assertEqual(
            next(output for output in outputs if output.track_id == track_id).state,
            TrackState.LOST,
        )

    def test_different_classes_near_each_other_keep_separate_tracks(self):
        tracker = MultiObjectTracker(
            association_distance=1.0,
            confirmation_hits=1,
        )
        outputs = tracker.update([
            self.detection(10, (5, 5, 0), 0),
            self.detection(4, (5.2, 5, 0), 0),
        ])
        self.assertEqual(len(outputs), 2)
        self.assertEqual({output.class_id for output in outputs}, {4, 10})

        outputs = tracker.update([
            self.detection(10, (5.2, 5, 0), 1),
            self.detection(4, (5, 5, 0), 1),
        ])
        self.assertEqual(len(outputs), 2)
        self.assertEqual(
            {output.class_id: output.track_id for output in outputs},
            {10: outputs[0].track_id if outputs[0].class_id == 10 else outputs[1].track_id,
             4: outputs[0].track_id if outputs[0].class_id == 4 else outputs[1].track_id},
        )


if __name__ == "__main__":
    unittest.main()
