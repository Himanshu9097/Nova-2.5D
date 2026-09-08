import carla
import random


class PedestrianScenario:

    def __init__(self, world):

        self.world = world
        self.walker = None
        self.controller = None

    def spawn_pedestrian(self):

        blueprint_library = (
            self.world.get_blueprint_library()
        )

        walker_bps = blueprint_library.filter(
            "walker.pedestrian.*"
        )

        walker_bp = random.choice(
            walker_bps
        )

        spawn_location = carla.Location(
            x=20,
            y=5,
            z=1
        )

        transform = carla.Transform(
            spawn_location
        )

        self.walker = self.world.try_spawn_actor(
            walker_bp,
            transform
        )

        if self.walker is None:

            print(
                "[PEDESTRIAN] Spawn failed"
            )

            return None

        print(
            f"[PEDESTRIAN] Spawned: "
            f"{self.walker.id}"
        )

        return self.walker

    def start_walking(self):

        if self.walker is None:

            raise RuntimeError(
                "Pedestrian not spawned."
            )

        controller_bp = (
            self.world
            .get_blueprint_library()
            .find(
                "controller.ai.walker"
            )
        )

        self.controller = (
            self.world.spawn_actor(
                controller_bp,
                carla.Transform(),
                attach_to=self.walker
            )
        )

        self.controller.start()

        destination = carla.Location(
            x=20,
            y=30,
            z=1
        )

        self.controller.go_to_location(
            destination
        )

        self.controller.set_max_speed(
            1.5
        )

        print(
            "[PEDESTRIAN] Started walking"
        )

    def destroy(self):

        if self.controller:

            self.controller.stop()
            self.controller.destroy()

        if self.walker:

            self.walker.destroy()

        print(
            "[PEDESTRIAN] Destroyed"
        )