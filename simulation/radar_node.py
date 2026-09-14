import os
import sys
import numpy as np
import time
import requests
import math
import argparse
import traceback

parser = argparse.ArgumentParser()
parser.add_argument('--host', default='127.0.0.1', help='IP Address of the Main Laptop running CARLA')
args = parser.parse_args()
HOST = args.host
PORT = 2000

try:
    import carla
except ImportError:
    print("Error: carla module not found.")
    sys.exit(1)

try:
    import pygame
    import pygame.surfarray
except ImportError:
    print("Error: pygame module not found. Run 'pip install pygame'")
    sys.exit(1)



accumulated_raw_points = 0
autopilot_enabled = False
auto_follow_camera = True
latest_lidar_points = None
latest_lidar_tags = None
latest_lidar_frame = None
latest_lidar_raw_data = None

def main():
    actor_list = []
    client = None
    
    try:
        print(f"Connecting to CARLA Server at {HOST}:{PORT}...")
        client = carla.Client(HOST, PORT)
        client.set_timeout(10.0)
        
        world = client.get_world()
        
        print("Waiting for Main Laptop to spawn Ego Vehicle and LiDAR...")
        lidar = None
        vehicle = None
        while lidar is None:
            actors = world.get_actors()
            lidars = actors.filter('sensor.lidar.ray_cast_semantic')
            vehicles = actors.filter('vehicle.tesla.model3')
            if len(lidars) > 0 and len(vehicles) > 0:
                lidar = lidars[0]
                vehicle = vehicles[0]
            else:
                time.sleep(1)
                
        print("Connected! Listening to Live LiDAR Stream...")

        # 3. Callback (MUST ONLY DO DATA PARSING. NO ACTOR CALLS OR CARLA WILL SEGFAULT!)
        def lidar_callback(image):
            global latest_lidar_frame, latest_lidar_raw_data
            latest_lidar_frame = image.frame
            # Copy bytes so memory isn't freed by C++
            latest_lidar_raw_data = bytes(image.raw_data) 
                
        lidar.listen(lidar_callback)
        
        # --- PYGAME RADAR LOOP ---
        pygame.init()
        pygame.font.init()
        display = pygame.display.set_mode((480, 540))
        pygame.display.set_caption("Nova-2.5D Adaptive Priority Radar")
        title_font = pygame.font.SysFont("monospace", 18, bold=True)
        
        global latest_lidar_frame, latest_lidar_raw_data
        clock = pygame.time.Clock()
        
        radar_surf = pygame.Surface((480, 540), depth=32)
        
            # 1. Update Display
            display.fill((10, 15, 30))
            
            # Header
            title_surf = title_font.render("NOVA-2.5D ADAPTIVE PRIORITY RADAR", True, (16, 185, 129))
            display.blit(title_surf, (20, 15))
            
            # 2. Parse New Frame
            if latest_lidar_frame is not None and latest_lidar_frame != last_processed_frame:
                last_processed_frame = latest_lidar_frame
                raw_bytes = latest_lidar_raw_data
                
                # Parse byte array
                dtype = np.dtype([
                    ('x', np.float32), ('y', np.float32), ('z', np.float32),
                    ('cos_inc', np.float32), ('idx', np.uint32), ('tag', np.uint32)
                ])
                data = np.frombuffer(raw_bytes, dtype=dtype)
                points = np.column_stack((data['x'], data['y'], data['z']))
                tags = data['tag']
                
                # We don't even need to downsample for the pure visualizer, but we will to keep FPS high
                latest_lidar_points = points[::8]
                latest_lidar_tags = tags[::8]
            
            # Vectorized Radar Rendering
            radar_surf.fill((10, 15, 30))
            if latest_lidar_points is not None and latest_lidar_tags is not None:
                try:
                    pts = latest_lidar_points
                    tgs = latest_lidar_tags
                    
                    scale = 8.0 # Pixels per meter
                    radar_w, radar_h = 480, 540
                    center_x, center_y = 240, 450
                    
                    # Math: Project to 2D pixels (CARLA: +X is Forward, +Y is Right)
                    px = (center_x + pts[:, 1] * scale).astype(np.int32)
                    py = (center_y - pts[:, 0] * scale).astype(np.int32)
                    
                    # Filter points inside screen bounds
                    valid = (px >= 0) & (px < radar_w) & (py >= 0) & (py < radar_h)
                    px = px[valid]
                    py = py[valid]
                    pts_v = pts[valid]
                    tgs_v = tgs[valid]
                    
                    if len(px) > 0:
                        # Adaptive 2.5D Priority Logic
                        dists = np.sqrt(pts_v[:,0]**2 + pts_v[:,1]**2)
                        
                        is_dyn = (tgs_v == 4) | (tgs_v == 10) # Pedestrians & Vehicles
                        is_road = (tgs_v == 7) | (tgs_v == 6) | (tgs_v == 8) # Roads & Sidewalks
                        is_static = ~(is_dyn | is_road)
                        
                        # Culling: Nova-2.5D ignores distant static data to save memory
                        keep = np.zeros(len(px), dtype=bool)
                        keep[is_dyn] = True # High Priority (Always Render)
                        keep[is_static & (dists < 30)] = True # Medium Priority
                        keep[is_road & (dists < 15)] = True # Low Priority
                        
                        px, py = px[keep], py[keep]
                        final_tags = tgs_v[keep]
                        
                        if len(px) > 0:
                            # Colorize based on semantics
                            colors = np.zeros((len(px), 3), dtype=np.uint8)
                            
                            f_dyn = (final_tags == 4) | (final_tags == 10)
                            f_road = (final_tags == 7) | (final_tags == 6) | (final_tags == 8)
                            f_static = ~(f_dyn | f_road)
                            
                            # Dynamic = Bright Red
                            colors[f_dyn] = [255, 50, 50]
                            # Static = Yellow
                            colors[f_static] = [250, 204, 21]
                            # Road = Faint Green
                            colors[f_road] = [16, 80, 40]
                            
                            # Map array directly to surface pixels
                            pixels = pygame.surfarray.pixels3d(radar_surf)
                            pixels[px, py] = colors
                            del pixels # Unlock surface
                except Exception as e:
                    print(f"Radar Render Error: {e}")
                    traceback.print_exc()
                
            # Draw Ego Vehicle (Cyan)
            pygame.draw.circle(radar_surf, (0, 255, 255), (240, 450), 5)
            
            # Blit radar to display
            display.blit(radar_surf, (0, 45))

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                    running = False
    finally:
        print("Cleaning up actors...")
        for actor in reversed(actor_list):
            if actor.is_alive:
                actor.destroy()
        
        try:
            pygame.quit()
        except:
            pass
            
        try:
            requests.post("http://127.0.0.1:5000/update", json={"status": "Offline"})
        except:
            pass

if __name__ == '__main__':
    main()
