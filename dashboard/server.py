from flask import Flask, Response, request, jsonify
from flask_cors import CORS
import time
import json
import base64
import threading

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Global state to hold the latest stats from CARLA
current_stats = {
    "frame": 0,
    "raw_points": 0,
    "raw_memory_kb": 0,
    "nova_cells": 0,
    "nova_memory_kb": 0,
    "cells_l0": 0,
    "cells_l1": 0,
    "cells_l2": 0,
    "speed_kmh": 0,
    "pedestrians_tracked": 0,
    "vehicles_tracked": 0,
    "fps": 0.0,
    "latency_ms": 0.0,
    "accuracy": 0.0,
    "rmse_cm": 0.0,
    "ram_mb": 0.0,
    "gpu_vram_mb": 0.0,
    "prior_map_loaded": False,
    "prior_map_name": "Town10HD_Opt",
    "prior_map_cells": 0,
    "status": "Waiting for CARLA..."
}

stats_version = 0

# Queue for commands from dashboard to Python Simulation
pending_spawns = []

# Control State Buffer
latest_web_control = {
    "throttle": 0.0,
    "steer": 0.0,
    "brake": 0.0,
    "reverse": False,
    "timestamp": 0.0
}
pending_commands = []

def event_stream():
    """Server-Sent Events stream for the React frontend"""
    global stats_version
    last_version = -1
    while True:
        # Send update immediately whenever ANY field in stats changes
        if stats_version != last_version:
            yield f"data: {json.dumps(current_stats)}\n\n"
            last_version = stats_version
        time.sleep(0.05)

@app.route('/stream')
def stream():
    response = Response(event_stream(), mimetype="text/event-stream")
    response.headers['Cache-Control'] = 'no-cache, no-transform'
    response.headers['X-Accel-Buffering'] = 'no'
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response

@app.route('/update', methods=['POST'])
def update():
    """Endpoint for the CARLA live script to post updates"""
    global current_stats, stats_version
    data = request.json
    if data:
        current_stats.update(data)
        stats_version += 1
    return jsonify({"success": True})

# Video streaming buffers
latest_camera_bytes = None
latest_lidar_bytes = None

@app.route('/upload_camera', methods=['POST'])
def upload_camera():
    global latest_camera_bytes
    latest_camera_bytes = request.data
    return jsonify({"success": True})

@app.route('/upload_lidar', methods=['POST'])
def upload_lidar():
    global latest_lidar_bytes
    latest_lidar_bytes = request.data
    return jsonify({"success": True})

# Binary point cloud buffer for Canvas BEV visualization
latest_pointcloud_bytes = None
pointcloud_version = 0

@app.route('/upload_pointcloud', methods=['POST'])
def upload_pointcloud():
    global latest_pointcloud_bytes, pointcloud_version
    latest_pointcloud_bytes = request.data
    pointcloud_version += 1
    return jsonify({"success": True})

def pointcloud_event_stream():
    """SSE stream that broadcasts binary point cloud as base64"""
    global pointcloud_version
    last_ver = -1
    while True:
        if pointcloud_version != last_ver and latest_pointcloud_bytes:
            b64 = base64.b64encode(latest_pointcloud_bytes).decode('ascii')
            yield f"data: {b64}\n\n"
            last_ver = pointcloud_version
        time.sleep(0.05)

@app.route('/pointcloud_stream')
def pointcloud_stream():
    response = Response(pointcloud_event_stream(), mimetype="text/event-stream")
    response.headers['Cache-Control'] = 'no-cache, no-transform'
    response.headers['X-Accel-Buffering'] = 'no'
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response

@app.route('/camera_feed')
def camera_feed():
    def generate():
        while True:
            if latest_camera_bytes:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + latest_camera_bytes + b'\r\n')
            time.sleep(0.05)
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/lidar_feed')
def lidar_feed():
    def generate():
        while True:
            if latest_lidar_bytes:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + latest_lidar_bytes + b'\r\n')
            time.sleep(0.05)
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/spawn', methods=['GET', 'POST'])
def spawn():
    """Endpoint for triggering new objects in the simulation"""
    global pending_spawns
    if request.method == 'POST':
        # Dashboard wants to spawn something
        data = request.json
        if data:
            pending_spawns.append(data)
            return jsonify({"success": True, "message": f"Queued {data.get('type')} spawn at {data.get('distance')}m"})
        return jsonify({"success": False})
    
    elif request.method == 'GET':
        # Python script polling for new commands
        if len(pending_spawns) > 0:
            spawns_to_send = pending_spawns.copy()
            pending_spawns.clear()
            return jsonify({"spawns": spawns_to_send})
        return jsonify({"spawns": []})

@app.route('/control', methods=['POST', 'OPTIONS'])
def web_control():
    """Receive continuous control inputs from React Dashboard"""
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200
    global latest_web_control
    data = request.json
    if data:
        latest_web_control["throttle"] = float(data.get("throttle", 0.0))
        latest_web_control["steer"] = float(data.get("steer", 0.0))
        latest_web_control["brake"] = float(data.get("brake", 0.0))
        latest_web_control["reverse"] = bool(data.get("reverse", False))
        latest_web_control["timestamp"] = time.time()
        return jsonify({"success": True})
    return jsonify({"success": False})

@app.route('/control/command', methods=['POST', 'OPTIONS'])
def web_command():
    """Receive discrete vehicle commands from React Dashboard"""
    if request.method == 'OPTIONS':
        return jsonify({"success": True}), 200
    global pending_commands
    data = request.json
    if data and "command" in data:
        pending_commands.append(data["command"])
        return jsonify({"success": True})
    return jsonify({"success": False})

@app.route('/control/poll', methods=['GET'])
def control_poll():
    """Simulation requests latest control state and any pending commands"""
    global pending_commands
    cmds_to_send = pending_commands.copy()
    pending_commands.clear()
    
    return jsonify({
        "control": latest_web_control,
        "commands": cmds_to_send
    })

if __name__ == '__main__':
    print("Starting Nova-2.5D Real-Time Dashboard Server on port 5000...")
    app.run(host='0.0.0.0', port=5000, threaded=True)
