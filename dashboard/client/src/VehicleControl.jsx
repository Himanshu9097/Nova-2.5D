import React, { useState, useEffect, useRef } from 'react';
import { Play, Settings, AlertTriangle, Crosshair, MapPin, RefreshCw } from 'lucide-react';

const VehicleControl = () => {
  const [controlState, setControlState] = useState({
    throttle: 0.0,
    steer: 0.0,
    brake: 0.0,
    reverse: false
  });
  
  const [eStop, setEStop] = useState(false);
  const [autopilot, setAutopilot] = useState(false);
  
  const keysRef = useRef({
    w: false,
    a: false,
    s: false,
    d: false,
    space: false,
    ArrowUp: false,
    ArrowDown: false,
    ArrowLeft: false,
    ArrowRight: false
  });

  const btnRef = useRef({
    throttle: false,
    brake: false,
    steerLeft: false,
    steerRight: false
  });

  // Handle continuous keypresses
  useEffect(() => {
    const handleKeyDown = (e) => {
      const key = e.key.length === 1 ? e.key.toLowerCase() : e.key;
      if (keysRef.current[key] !== undefined) {
        keysRef.current[key] = true;
        // Prevent scrolling when using WASD/Arrows
        if (['w', 'a', 's', 'd', 'ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight', ' '].includes(e.key)) {
          e.preventDefault();
        }
      }
      
      // Discrete commands
      if (key === 'p') {
        sendCommand('toggle_autopilot');
        setAutopilot(prev => !prev);
      }
      if (key === 'c') sendCommand('camera_snap');
      if (key === 'f') sendCommand('camera_follow');
    };

    const handleKeyUp = (e) => {
      const key = e.key.length === 1 ? e.key.toLowerCase() : e.key;
      if (keysRef.current[key] !== undefined) {
        keysRef.current[key] = false;
      }
    };

    window.addEventListener('keydown', handleKeyDown, { passive: false });
    window.addEventListener('keyup', handleKeyUp);
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
      window.removeEventListener('keyup', handleKeyUp);
    };
  }, []);

  // Polling loop to send continuous control state
  useEffect(() => {
    const sendControlState = async () => {
      const keys = keysRef.current;
      const btns = btnRef.current;
      
      let out_t = (keys.w || keys.ArrowUp || btns.throttle) ? 1.0 : 0.0;
      let out_b = (keys.s || keys.ArrowDown || btns.brake) ? 1.0 : 0.0;
      let out_s = 0.0;
      let out_r = false;
      
      if (out_b > 0) {
        out_r = true; // Signal reverse intent
      }

      if (keys.space || keys[' ']) {
        out_b = 1.0;
        out_t = 0.0;
      }

      if (keys.a || keys.ArrowLeft || btns.steerLeft) {
        out_s = -0.75;
      } else if (keys.d || keys.ArrowRight || btns.steerRight) {
        out_s = 0.75;
      }

      const newState = { throttle: out_t, steer: out_s, brake: out_b, reverse: out_r };
      
      // Only send if state is active (to allow Pygame fallback)
      if (out_t > 0 || Math.abs(out_s) > 0 || out_b > 0) {
        setControlState(newState);
        try {
          await fetch(`http://${window.location.hostname}:5000/control`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(newState)
          });
        } catch (e) {
          // Ignore network errs on rapid fire
        }
      } else if (controlState.throttle > 0 || Math.abs(controlState.steer) > 0 || controlState.brake > 0) {
        // Send a single zeroed state to stop
        setControlState(newState);
        try {
          await fetch(`http://${window.location.hostname}:5000/control`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(newState)
          });
        } catch (e) {}
      }
    };

    const intervalId = setInterval(sendControlState, 50); // 20 Hz
    return () => clearInterval(intervalId);
  }, [controlState]);

  const sendCommand = async (cmd) => {
    try {
      await fetch(`http://${window.location.hostname}:5000/control/command`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ command: cmd })
      });
    } catch (e) {
      console.error(e);
    }
  };

  const toggleEStop = () => {
    if (eStop) {
      sendCommand('release_stop');
      setEStop(false);
    } else {
      sendCommand('e_stop');
      setEStop(true);
      setAutopilot(false);
    }
  };
  
  const handleToggleAutopilot = () => {
    sendCommand('toggle_autopilot');
    setAutopilot(!autopilot);
  };

  return (
    <div className="glass-panel p-6 rounded-3xl mt-8">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <Settings className="text-blue-400" />
          <h3 className="text-xl font-bold">Nova Command Center</h3>
        </div>
        <div className="flex items-center gap-2 text-xs font-mono bg-slate-900 px-3 py-1.5 rounded-full border border-slate-700">
          <span className={`w-2 h-2 rounded-full ${eStop ? 'bg-red-500 animate-ping' : 'bg-green-500'}`}></span>
          {eStop ? 'SYSTEM HALTED' : 'SYSTEM READY'}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* Driving Controls */}
        <div className="space-y-6">
          <h4 className="text-sm text-slate-400 font-semibold mb-2">TELEOPERATION (WASD / ARROWS)</h4>
          
          <div className="flex flex-col items-center gap-2">
            <button 
              className="w-16 h-16 bg-slate-800 rounded-xl border border-slate-700 flex items-center justify-center font-bold shadow-lg active:bg-blue-600 active:border-blue-400 transition-colors"
              onPointerDown={() => btnRef.current.throttle = true}
              onPointerUp={() => btnRef.current.throttle = false}
              onPointerLeave={() => btnRef.current.throttle = false}
            >W</button>
            <div className="flex gap-2">
              <button 
                className="w-16 h-16 bg-slate-800 rounded-xl border border-slate-700 flex items-center justify-center font-bold shadow-lg active:bg-blue-600 active:border-blue-400 transition-colors"
                onPointerDown={() => btnRef.current.steerLeft = true}
                onPointerUp={() => btnRef.current.steerLeft = false}
                onPointerLeave={() => btnRef.current.steerLeft = false}
              >A</button>
              <button 
                className="w-16 h-16 bg-slate-800 rounded-xl border border-slate-700 flex items-center justify-center font-bold shadow-lg active:bg-blue-600 active:border-blue-400 transition-colors"
                onPointerDown={() => btnRef.current.brake = true}
                onPointerUp={() => btnRef.current.brake = false}
                onPointerLeave={() => btnRef.current.brake = false}
              >S</button>
              <button 
                className="w-16 h-16 bg-slate-800 rounded-xl border border-slate-700 flex items-center justify-center font-bold shadow-lg active:bg-blue-600 active:border-blue-400 transition-colors"
                onPointerDown={() => btnRef.current.steerRight = true}
                onPointerUp={() => btnRef.current.steerRight = false}
                onPointerLeave={() => btnRef.current.steerRight = false}
              >D</button>
            </div>
          </div>
          
          {/* Active Inputs Readout */}
          <div className="flex justify-between bg-slate-900/50 p-3 rounded-lg border border-slate-800 text-xs font-mono">
            <div>THR: {(controlState.throttle * 100).toFixed(0)}%</div>
            <div>STR: {controlState.steer.toFixed(2)}</div>
            <div>BRK: {(controlState.brake * 100).toFixed(0)}%</div>
          </div>
        </div>

        {/* System Commands */}
        <div className="space-y-3">
          <h4 className="text-sm text-slate-400 font-semibold mb-2">SYSTEM COMMANDS</h4>
          
          <button 
            onClick={handleToggleAutopilot}
            className={`w-full py-3 rounded-xl font-bold flex items-center justify-center gap-2 border transition-all ${
              autopilot 
                ? 'bg-blue-600/20 text-blue-400 border-blue-500/50 shadow-[0_0_15px_rgba(59,130,246,0.3)]' 
                : 'bg-slate-800 text-slate-300 border-slate-700 hover:bg-slate-700'
            }`}
          >
            <Play size={18} /> {autopilot ? 'AUTOPILOT ENGAGED' : 'ENGAGE AUTOPILOT'}
          </button>

          <div className="grid grid-cols-2 gap-3">
            <button 
              onClick={() => sendCommand('camera_follow')}
              className="py-3 bg-slate-800 rounded-xl border border-slate-700 hover:bg-slate-700 flex items-center justify-center gap-2 text-sm font-semibold"
            >
              <Crosshair size={16} /> Follow Cam
            </button>
            
            <button 
              onClick={() => sendCommand('camera_snap')}
              className="py-3 bg-slate-800 rounded-xl border border-slate-700 hover:bg-slate-700 flex items-center justify-center gap-2 text-sm font-semibold"
            >
              <MapPin size={16} /> Snap Cam
            </button>
          </div>

          <div className="grid grid-cols-2 gap-3 pt-2">
            <button 
              onClick={toggleEStop}
              className={`py-3 rounded-xl border font-bold flex items-center justify-center gap-2 text-sm transition-all ${
                eStop 
                  ? 'bg-red-600 text-white border-red-500 shadow-[0_0_20px_rgba(220,38,38,0.5)] animate-pulse' 
                  : 'bg-red-950/30 text-red-500 border-red-900/50 hover:bg-red-900/50'
              }`}
            >
              <AlertTriangle size={16} /> {eStop ? 'RELEASE STOP' : 'E-STOP'}
            </button>
            
            <button 
              onClick={() => { sendCommand('reset_vehicle'); setAutopilot(false); setEStop(false); }}
              className="py-3 bg-slate-800 text-amber-500 rounded-xl border border-slate-700 hover:bg-slate-700 flex items-center justify-center gap-2 text-sm font-semibold"
            >
              <RefreshCw size={16} /> Reset Vehicle
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default VehicleControl;
