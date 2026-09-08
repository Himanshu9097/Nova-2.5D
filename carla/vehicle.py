import carla


class VehicleManager:

    def __init__(self, world):
        self.world = world
        self.vehicle = None

    def spawn_vehicle(self):

        blueprint_library = self.world.get_blueprint_library()

        vehicle_bp = blueprint_library.find("vehicle.tesla.model3")

        spawn_points = self.world.get_map().get_spawn_points()

        if not spawn_points:
            raise RuntimeError("No spawn points available.")

        spawn_point = spawn_points[0]

        self.vehicle = self.world.try_spawn_actor(
            vehicle_bp,
            spawn_point
        )

        if self.vehicle is None:
            raise RuntimeError("Vehicle could not be spawned.")

        print(
            f"[VEHICLE] Spawned: "
            f"{self.vehicle.type_id}"
        )

        return self.vehicle

    def set_autopilot(self, enabled=True):

        if self.vehicle is None:
            raise RuntimeError("Vehicle has not been spawned.")

        self.vehicle.set_autopilot(enabled)

        print(
            f"[VEHICLE] Autopilot: "
            f"{'ON' if enabled else 'OFF'}"
        )

    def get_vehicle(self):
        return self.vehicle