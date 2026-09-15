import sys
import argparse

try:
    import carla
except ImportError:
    print("Error: CARLA Python module not found.")
    sys.exit(1)

parser = argparse.ArgumentParser(description="Restore CARLA 3D viewport rendering")
parser.add_argument('--carla-host', default='127.0.0.1', help='IP Address of the machine running CARLA')
parser.add_argument('--port', type=int, default=2000, help='CARLA server port')
args = parser.parse_args()

try:
    print(f"Connecting to CARLA at {args.carla_host}:{args.port}...")
    client = carla.Client(args.carla_host, args.port)
    client.set_timeout(10.0)
    world = client.get_world()
    settings = world.get_settings()
    settings.no_rendering_mode = False
    world.apply_settings(settings)
    print("\nâœ… SUCCESS: CARLA 3D Viewport Rendering is now ENABLED! The black screen is gone.")
except Exception as e:
    print(f"\nâ Œ Error connecting to CARLA: {e}")
