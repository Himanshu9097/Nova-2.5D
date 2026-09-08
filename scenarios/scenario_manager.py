import sys
import time

# Allow imports from project root
sys.path.append(".")

from carla.connection import CarlaConnection
from carla.vehicle import VehicleManager
from carla.lidar import LidarManager

from sensors.lidar_recorder import LidarRecorder
from ground_truth.ground_truth_logger import GroundTruthLogger

from scenarios.pedestrian_crossing import PedestrianScenario


def main():

    print("\n==============================")
    print("      NOVA-2.5D SIMULATION")
    print("==============================\n")

    vehicle = None
    pedestrian = None
    lidar_manager = None

    try:

        # --------------------------------
        # 1. Connect to CARLA
        # --------------------------------

        connection = CarlaConnection()

        world = connection.connect()

        # --------------------------------
        # 2. Spawn Ego Vehicle
        # --------------------------------

        print("\n[1] Spawning ego vehicle...")

        vehicle_manager = VehicleManager(world)

        vehicle = vehicle_manager.spawn_vehicle()

        vehicle_manager.set_autopilot(True)

        # --------------------------------
        # 3. Spawn Pedestrian
        # --------------------------------

        print("\n[2] Spawning pedestrian...")

        pedestrian_scenario = PedestrianScenario(world)

        pedestrian = (
            pedestrian_scenario.spawn_pedestrian()
        )

        if pedestrian is not None:
            pedestrian_scenario.start_walking()

        # --------------------------------
        # 4. Create LiDAR Recorder
        # --------------------------------

        print("\n[3] Starting LiDAR recorder...")

        lidar_recorder = LidarRecorder(
            output_dir="data/raw"
        )

        # --------------------------------
        # 5. Spawn LiDAR
        # --------------------------------

        print("\n[4] Starting LiDAR...")

        lidar_manager = LidarManager(
            world,
            vehicle
        )

        lidar_manager.spawn_lidar(
            lidar_recorder.callback
        )

        # --------------------------------
        # 6. Ground Truth Logger
        # --------------------------------

        print("\n[5] Starting ground truth logger...")

        ground_truth = GroundTruthLogger(
            world,
            output_dir="data/ground_truth"
        )

        # --------------------------------
        # 7. Run Simulation
        # --------------------------------

        print("\n==============================")
        print("       SIMULATION STARTED")
        print("==============================\n")

        for frame in range(300):

            # Wait for next CARLA frame
            world.wait_for_tick()

            # Record object positions
            ground_truth.collect_frame(frame)

            # Small delay
            time.sleep(0.01)

        print("\n[SIMULATION] Completed 300 frames.")

    except KeyboardInterrupt:

        print("\n[SIMULATION] Interrupted by user.")

    except Exception as e:

        print(f"\n[ERROR] {e}")

    finally:

        print("\n==============================")
        print("       CLEANING UP")
        print("==============================\n")

        # --------------------------------
        # Save Ground Truth
        # --------------------------------

        try:
            ground_truth.save()
        except Exception:
            pass

        # --------------------------------
        # Stop LiDAR
        # --------------------------------

        try:

            if lidar_manager is not None:
                lidar_manager.stop()

        except Exception as e:

            print(
                f"[LiDAR] Cleanup error: {e}"
            )

        # --------------------------------
        # Destroy Pedestrian
        # --------------------------------

        try:

            if pedestrian is not None:

                pedestrian_scenario.destroy()

        except Exception as e:

            print(
                f"[PEDESTRIAN] Cleanup error: {e}"
            )

        # --------------------------------
        # Destroy Vehicle
        # --------------------------------

        try:

            if vehicle is not None:

                vehicle.destroy()

                print(
                    "[VEHICLE] Destroyed"
                )

        except Exception as e:

            print(
                f"[VEHICLE] Cleanup error: {e}"
            )

        print(
            "\n[NOVA-2.5D] Simulation finished."
        )


if __name__ == "__main__":
    main()
