import os
import json
import carla


class GroundTruthLogger:

    def __init__(self, world, output_dir="data/ground_truth"):

        self.world = world
        self.output_dir = output_dir

        os.makedirs(
            self.output_dir,
            exist_ok=True
        )

        self.frame_data = []

    def collect_frame(self, frame_number):

        actors = self.world.get_actors()

        objects = []

        for actor in actors:

            if not (
                actor.type_id.startswith("vehicle")
                or actor.type_id.startswith("walker")
            ):
                continue

            transform = actor.get_transform()
            velocity = actor.get_velocity()
            bounding_box = actor.bounding_box

            object_data = {

                "id": actor.id,

                "type": actor.type_id,

                "location": {
                    "x": transform.location.x,
                    "y": transform.location.y,
                    "z": transform.location.z
                },

                "rotation": {
                    "pitch": transform.rotation.pitch,
                    "yaw": transform.rotation.yaw,
                    "roll": transform.rotation.roll
                },

                "velocity": {
                    "x": velocity.x,
                    "y": velocity.y,
                    "z": velocity.z
                },

                "bounding_box": {
                    "extent_x": bounding_box.extent.x,
                    "extent_y": bounding_box.extent.y,
                    "extent_z": bounding_box.extent.z
                }
            }

            objects.append(object_data)

        frame_data = {

            "frame": frame_number,

            "timestamp": self.world.get_snapshot().timestamp.elapsed_seconds,

            "objects": objects

        }

        self.frame_data.append(frame_data)

    def save(self, filename="ground_truth.json"):

        path = os.path.join(
            self.output_dir,
            filename
        )

        with open(path, "w") as file:

            json.dump(
                self.frame_data,
                file,
                indent=4
            )

        print(
            f"[GROUND TRUTH] Saved: {path}"
        )