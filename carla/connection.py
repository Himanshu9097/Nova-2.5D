import carla


class CarlaConnection:

    def __init__(self, host="localhost", port=2000, timeout=10.0):
        self.host = host
        self.port = port
        self.timeout = timeout

        self.client = None
        self.world = None

    def connect(self):
        print(f"[CARLA] Connecting to {self.host}:{self.port}")

        self.client = carla.Client(self.host, self.port)
        self.client.set_timeout(self.timeout)

        self.world = self.client.get_world()

        print("[CARLA] Connected successfully")
        print(f"[CARLA] Map: {self.world.get_map().name}")

        return self.world

    def get_world(self):
        if self.world is None:
            raise RuntimeError("CARLA is not connected.")

        return self.world

    def get_client(self):
        if self.client is None:
            raise RuntimeError("CARLA is not connected.")

        return self.client