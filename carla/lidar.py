import carla


class LidarManager:

    def __init__(self, world, vehicle):
        self.world = world
        self.vehicle = vehicle
        self.lidar = None

    def spawn_lidar(self, callback):

        blueprint_library = self.world.get_blueprint_library()

        lidar_bp = blueprint_library.find(
            "sensor.lidar.ray_cast"
        )

        # LiDAR configuration
        lidar_bp.set_attribute("channels", "32")
        lidar_bp.set_attribute(
            "points_per_second",
            "56000"
        )
        lidar_bp.set_attribute(
            "rotation_frequency",
            "10"
        )
        lidar_bp.set_attribute(
            "range",
            "50"
        )
        lidar_bp.set_attribute(
            "upper_fov",
            "10"
        )
        lidar_bp.set_attribute(
            "lower_fov",
            "-30"
        )

        transform = carla.Transform(
            carla.Location(
                x=0.0,
                y=0.0,
                z=2.5
            )
        )

        self.lidar = self.world.spawn_actor(
            lidar_bp,
            transform,
            attach_to=self.vehicle
        )

        self.lidar.listen(callback)

        print("[LiDAR] Sensor started")

        return self.lidar

    def stop(self):

        if self.lidar is not None:

            self.lidar.stop()
            self.lidar.destroy()

            print("[LiDAR] Sensor stopped")