from flask import Flask, Response, request, jsonify
from flask_cors import CORS
import time
import json
import threading

app = Flask(__name__)
CORS(app)

# Global state to hold the latest stats from CARLA
current_stats = {
    "frame": 0,
    "raw_points": 0,
    "raw_memory_kb": 0,
    "nova_cells": 0,
    "nova_memory_kb": 0,
    "speed_kmh": 0,
    "pedestrians_tracked": 0,
    "vehicles_tracked": 0,
    "status": "Waiting for CARLA..."
}

# Queue for commands from dashboard to Python Simulation
pending_spawns = []

def event_stream():
    """Server-Sent Events stream for the React frontend"""
    last_frame = -1
    while True:
        # Only send updates if the frame has changed to avoid flooding
        if current_stats["frame"] != last_frame:
            yield f"data: {json.dumps(current_stats)}\n\n"
            last_frame = current_stats["frame"]
        time.sleep(0.1)

@app.route('/stream')
def stream():
    return Response(event_stream(), mimetype="text/event-stream")

@app.route('/update', methods=['POST'])
def update():
    """Endpoint for the CARLA live script to post updates"""
    global current_stats
    data = request.json
    if data:
        current_stats.update(data)
    return jsonify({"success": True})

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

if __name__ == '__main__':
    print("Starting Nova-2.5D Real-Time Dashboard Server on port 5000...")
    app.run(host='0.0.0.0', port=5000, threaded=True)
