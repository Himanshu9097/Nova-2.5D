import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Activity, HardDrive, Cpu, Zap, Car, Eye, Map, Sliders } from 'lucide-react';
import './index.css';

function App() {
  const [activeView, setActiveView] = useState('telemetry'); // 'telemetry' or 'comparison'
  const [spawnType, setSpawnType] = useState('pedestrian');
  const [spawnDist, setSpawnDist] = useState(20);
  const [spawnStatus, setSpawnStatus] = useState('');

  const [stats, setStats] = useState({
    frame: 0,
    raw_points: 0,
    raw_memory_kb: 0,
    nova_cells: 0,
    nova_memory_kb: 0,
    speed_kmh: 0,
    status: "Offline",
    fps: 0,
    latency_ms: 0,
    accuracy: 0,
    rmse_cm: 0,
    pedestrians_tracked: 0,
    vehicles_tracked: 0
  });

  const [history, setHistory] = useState([]);

  useEffect(() => {
    // Connect to Python Flask SSE dynamically based on the IP address used in the URL
    const eventSource = new EventSource(`http://${window.location.hostname}:5000/stream`);
    
    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setStats(prev => ({ ...prev, ...data }));
      
      setHistory(prev => {
        const newHistory = [...prev, { 
          time: data.frame, 
          rawMemory: data.raw_memory_kb, 
          novaMemory: data.nova_memory_kb 
        }];
        if (newHistory.length > 50) newHistory.shift();
        return newHistory;
      });
    };

    return () => eventSource.close();
  }, []);

  const calculateReduction = () => {
    if (stats.raw_memory_kb === 0) return 0;
    return (((stats.raw_memory_kb - stats.nova_memory_kb) / stats.raw_memory_kb) * 100).toFixed(1);
  };

  const formatMemory = (kb) => {
    if (kb < 1024) return { value: kb.toFixed(2), unit: 'KB' };
    const mb = kb / 1024;
    if (mb < 1024) return { value: mb.toFixed(2), unit: 'MB' };
    const gb = mb / 1024;
    return { value: gb.toFixed(2), unit: 'GB' };
  };

  const rawMem = formatMemory(stats.raw_memory_kb);
  const novaMem = formatMemory(stats.nova_memory_kb);

  const handleSpawn = async () => {
    try {
      const res = await fetch(`http://${window.location.hostname}:5000/spawn`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ type: spawnType, distance: spawnDist })
      });
      if(res.ok) {
        setSpawnStatus(`Spawned ${spawnType} at ${spawnDist}m!`);
        setTimeout(() => setSpawnStatus(''), 3000);
      }
    } catch (e) {
      setSpawnStatus("Connection error");
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-8 font-sans">
      
      {/* Header */}
      <header className="mb-10 flex flex-col md:flex-row justify-between items-center border-b border-slate-800 pb-6 gap-6">
        <div>
          <h1 className="text-4xl font-black tracking-tight bg-gradient-to-r from-blue-400 to-emerald-400 bg-clip-text text-transparent">
            NOVA-2.5D COMMAND CENTER
          </h1>
          <p className="text-slate-400 mt-2 font-medium">Smart India Hackathon 2026 • Live CARLA Telemetry</p>
        </div>
        
        {/* Navigation */}
        <div className="flex items-center gap-4 bg-slate-900/80 p-2 rounded-2xl border border-slate-800">
          <button 
            onClick={() => setActiveView('telemetry')}
            className={`px-6 py-3 rounded-xl font-bold flex items-center gap-2 transition-all ${activeView === 'telemetry' ? 'bg-blue-500/20 text-blue-400 border border-blue-500/30 shadow-[0_0_15px_rgba(59,130,246,0.2)]' : 'text-slate-400 hover:text-white'}`}
          >
            <Activity size={18} /> Telemetry
          </button>
          <button 
            onClick={() => setActiveView('comparison')}
            className={`px-6 py-3 rounded-xl font-bold flex items-center gap-2 transition-all ${activeView === 'comparison' ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 shadow-[0_0_15px_rgba(16,185,129,0.2)]' : 'text-slate-400 hover:text-white'}`}
          >
            <Map size={18} /> Algorithm Comparison
          </button>
        </div>

        <div className={`px-6 py-2 rounded-full font-bold flex items-center gap-3 border ${stats.status === "Active Mapping" ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/50" : "bg-red-500/10 text-red-400 border-red-500/50"}`}>
          <div className={`w-3 h-3 rounded-full ${stats.status === "Active Mapping" ? "bg-emerald-400 animate-pulse" : "bg-red-400"}`}></div>
          {stats.status}
        </div>
      </header>

      {activeView === 'telemetry' ? (
        <>
          {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        
        {/* Left Panel: Raw 3D */}
        <div className="glass-panel p-8 rounded-3xl relative overflow-hidden group">
          <div className="absolute top-0 right-0 w-64 h-64 bg-red-500/10 rounded-full blur-3xl -mr-20 -mt-20 transition-all group-hover:bg-red-500/20"></div>
          <div className="flex items-center gap-4 mb-8">
            <div className="p-4 bg-red-500/20 rounded-2xl text-red-400">
              <HardDrive size={32} />
            </div>
            <div>
              <h2 className="text-2xl font-bold text-red-100">Standard 3D LiDAR Pipeline</h2>
              <p className="text-red-400/80">Massive Computation Overhead</p>
            </div>
          </div>
          
          <div className="space-y-6">
            <div className="bg-slate-900/50 p-6 rounded-2xl border border-red-500/20">
              <p className="text-slate-400 mb-1 text-sm font-semibold uppercase tracking-wider">Processed Points / Frame</p>
              <p className="text-5xl font-mono font-light text-white">{stats.raw_points.toLocaleString()}</p>
            </div>
            <div className="bg-slate-900/50 p-6 rounded-2xl border border-red-500/20">
              <p className="text-slate-400 mb-1 text-sm font-semibold uppercase tracking-wider">Map RAM Allocation</p>
              <p className="text-5xl font-mono font-light text-red-400">{rawMem.value} <span className="text-2xl">{rawMem.unit}</span></p>
            </div>
          </div>
        </div>

        {/* Right Panel: Nova 2.5D */}
        <div className="glass-panel p-8 rounded-3xl relative overflow-hidden group border border-emerald-500/30 shadow-[0_0_50px_rgba(16,185,129,0.1)]">
          <div className="absolute top-0 right-0 w-64 h-64 bg-emerald-500/10 rounded-full blur-3xl -mr-20 -mt-20 transition-all group-hover:bg-emerald-500/20"></div>
          <div className="flex items-center gap-4 mb-8">
            <div className="p-4 bg-emerald-500/20 rounded-2xl text-emerald-400">
              <Cpu size={32} />
            </div>
            <div>
              <h2 className="text-2xl font-bold text-emerald-100">Nova-2.5D Adaptive Pipeline</h2>
              <p className="text-emerald-400/80">Intelligent Variable Resolution</p>
            </div>
          </div>
          
          <div className="space-y-6">
            <div className="bg-slate-900/50 p-6 rounded-2xl border border-emerald-500/20 flex justify-between items-center">
              <div>
                <p className="text-slate-400 mb-1 text-sm font-semibold uppercase tracking-wider">Active Grid Cells</p>
                <p className="text-5xl font-mono font-light text-white">{stats.nova_cells.toLocaleString()}</p>
              </div>
              <div className="text-right">
                <p className="text-slate-400 mb-1 text-sm font-semibold uppercase tracking-wider">Reduction</p>
                <p className="text-3xl font-mono text-emerald-400 font-bold">-{calculateReduction()}%</p>
              </div>
            </div>
            <div className="bg-slate-900/50 p-6 rounded-2xl border border-emerald-500/20">
              <p className="text-slate-400 mb-1 text-sm font-semibold uppercase tracking-wider">Map RAM Allocation</p>
              <p className="text-5xl font-mono font-light text-emerald-400">{novaMem.value} <span className="text-2xl">{novaMem.unit}</span></p>
            </div>
          </div>
        </div>

      </div>

      {/* Graph and Vehicle Stats */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Chart */}
        <div className="lg:col-span-2 glass-panel p-8 rounded-3xl">
          <div className="flex items-center gap-3 mb-8">
            <Activity className="text-blue-400" />
            <h3 className="text-xl font-bold">Real-Time Memory Consumption</h3>
          </div>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={history}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
                <XAxis dataKey="time" stroke="#475569" tickFormatter={(t) => `#${t}`} />
                <YAxis stroke="#475569" />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b', borderRadius: '12px' }}
                  itemStyle={{ fontFamily: 'monospace' }}
                />
                <Line type="monotone" dataKey="rawMemory" name="Standard 3D (KB)" stroke="#ef4444" strokeWidth={3} dot={false} />
                <Line type="monotone" dataKey="novaMemory" name="Nova-2.5D (KB)" stroke="#10b981" strokeWidth={3} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Telemetry */}
        <div className="glass-panel p-8 rounded-3xl flex flex-col justify-between">
          <div>
            <div className="flex items-center gap-3 mb-8">
              <Car className="text-blue-400" />
              <h3 className="text-xl font-bold">Ego Vehicle Telemetry</h3>
            </div>
            
            <div className="space-y-4">
              <div className="flex justify-between items-center p-4 bg-slate-900/50 rounded-xl">
                <span className="text-slate-400 font-medium">Speed</span>
                <span className="text-2xl font-mono text-white">{stats.speed_kmh} <span className="text-sm text-slate-500">km/h</span></span>
              </div>
              <div className="flex justify-between items-center p-4 bg-slate-900/50 rounded-xl">
                <span className="text-slate-400 font-medium">Tracking</span>
                <span className="text-xl font-medium text-emerald-400 flex items-center gap-2">
                  <Eye size={18} /> Active
                </span>
              </div>
            </div>
          </div>
          
          <div className="mt-8 p-6 bg-gradient-to-br from-blue-600/20 to-purple-600/20 border border-blue-500/30 rounded-2xl">
            <div className="flex items-center gap-3 mb-2">
              <Zap className="text-blue-400" />
              <h4 className="font-bold text-blue-100">System Ready</h4>
            </div>
            <p className="text-sm text-blue-200/70">Semantic Importance and Dynamic Tracking logic are fully active in the C++ core.</p>
          </div>
        </div>

      </div>

      {/* System Performance Matrix */}
      <div className="mt-8 glass-panel p-8 rounded-3xl border border-blue-500/20">
        <h3 className="text-xl font-bold mb-6 text-slate-200">System Performance Matrix</h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="bg-slate-900/50 p-6 rounded-2xl border border-slate-800">
            <p className="text-slate-400 mb-1 text-sm font-semibold uppercase tracking-wider">Pipeline FPS</p>
            <p className="text-4xl font-mono text-white">{stats.fps.toFixed(1)} <span className="text-xl text-slate-500">Hz</span></p>
          </div>
          <div className="bg-slate-900/50 p-6 rounded-2xl border border-slate-800">
            <p className="text-slate-400 mb-1 text-sm font-semibold uppercase tracking-wider">End-to-End Latency</p>
            <p className="text-4xl font-mono text-white">{stats.latency_ms.toFixed(1)} <span className="text-xl text-slate-500">ms</span></p>
          </div>
          <div className="bg-slate-900/50 p-6 rounded-2xl border border-emerald-500/20 shadow-[0_0_15px_rgba(16,185,129,0.05)]">
            <p className="text-emerald-400/80 mb-1 text-sm font-semibold uppercase tracking-wider">Map Accuracy</p>
            <p className="text-4xl font-mono text-emerald-400">{stats.accuracy.toFixed(1)} <span className="text-xl">%</span></p>
          </div>
          <div className="bg-slate-900/50 p-6 rounded-2xl border border-orange-500/20 shadow-[0_0_15px_rgba(249,115,22,0.05)]">
            <p className="text-orange-400/80 mb-1 text-sm font-semibold uppercase tracking-wider">Elevation Error</p>
            <p className="text-4xl font-mono text-orange-400">{(stats.rmse_cm || 0).toFixed(1)} <span className="text-xl">cm</span></p>
          </div>
        </div>
      </div>
      </>) : (
        <div className="space-y-6 animate-in fade-in duration-500">
          
          <div className="text-center mb-8">
            <h2 className="text-4xl font-black text-white mb-2">Why <span className="text-emerald-400">Nova-2.5D</span> is Different?</h2>
            <p className="text-xl text-emerald-400/80 font-medium tracking-wide">Map intelligently, not uniformly.</p>
          </div>

          {/* Top Panel: Real World vs Raw Point Cloud */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {/* Real World View placeholder */}
            <div className="glass-panel rounded-2xl overflow-hidden border border-slate-700 bg-slate-900/50 h-80 relative flex items-center justify-center group">
              <div className="absolute top-0 left-0 right-0 p-3 bg-gradient-to-b from-slate-950/80 to-transparent z-10">
                <span className="bg-slate-800/80 text-white text-xs font-bold px-3 py-1 rounded">Real World View (CARLA Simulation)</span>
              </div>
              <div className="text-slate-600 flex flex-col items-center gap-2">
                <Eye size={48} className="opacity-50" />
                <p className="font-medium text-sm">[Insert CARLA Screenshot Here]</p>
              </div>
            </div>

            {/* Raw LiDAR View placeholder */}
            <div className="glass-panel rounded-2xl overflow-hidden border border-slate-700 bg-slate-950 h-80 relative flex items-center justify-center group">
              <div className="absolute top-0 left-0 right-0 p-3 bg-gradient-to-b from-slate-950/80 to-transparent z-10 flex justify-between items-start">
                <span className="bg-slate-800/80 text-white text-xs font-bold px-3 py-1 rounded">Raw LiDAR Point Cloud (Bird's Eye View)</span>
                <div className="bg-slate-800/80 p-2 rounded text-[10px] text-slate-300 font-medium space-y-1">
                  <div className="flex items-center gap-2"><span className="w-2 h-2 rounded-full bg-blue-400"></span> Road</div>
                  <div className="flex items-center gap-2"><span className="w-2 h-2 rounded-full bg-red-400"></span> Vehicle</div>
                  <div className="flex items-center gap-2"><span className="w-2 h-2 rounded-full bg-green-400"></span> Pedestrian</div>
                  <div className="flex items-center gap-2"><span className="w-2 h-2 rounded-full bg-purple-400"></span> Building</div>
                </div>
              </div>
              <div className="text-slate-700 flex flex-col items-center gap-2">
                <Activity size={48} className="opacity-50" />
                <p className="font-medium text-sm">[Insert Point Cloud Image Here]</p>
              </div>
            </div>
          </div>

          {/* Infographic 3-Panel Grids */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
            
            {/* Panel 1 */}
            <div className="glass-panel p-5 rounded-2xl border border-slate-700 flex flex-col justify-between">
              <div>
                <h3 className="text-lg font-bold text-white mb-1">1. Traditional Uniform Mapping</h3>
                <p className="text-slate-400 text-xs mb-4">(Same resolution everywhere)</p>
                
                <div className="aspect-video bg-[#1a202c] rounded-lg border border-slate-600 mb-4 flex items-end p-2 relative overflow-hidden group">
                  <div className="absolute inset-0 grid grid-cols-12 grid-rows-8 gap-px opacity-40">
                    {Array.from({length: 96}).map((_, i) => <div key={i} className="bg-slate-400"></div>)}
                  </div>
                  <div className="relative z-10 bg-slate-900/90 border border-slate-700 p-2 rounded text-[10px] text-slate-300 ml-auto shadow-lg backdrop-blur-sm">
                    <p className="font-bold mb-1">Grid Size: 10 cm (uniform)</p>
                    <p>Total Cells: 1,000,000</p>
                    <p>Memory Usage: ~500 MB</p>
                  </div>
                </div>
              </div>
              
              <div className="flex items-start gap-3 bg-red-500/10 p-3 rounded-lg border border-red-500/20">
                <div className="bg-red-500 text-white rounded-full w-5 h-5 flex items-center justify-center font-bold text-xs shrink-0 mt-0.5">X</div>
                <p className="text-xs text-red-200">Wastes memory and computation on less important areas.</p>
              </div>
            </div>

            {/* Panel 2 */}
            <div className="glass-panel p-5 rounded-2xl border border-slate-700 flex flex-col justify-between">
              <div>
                <h3 className="text-lg font-bold text-white mb-1">2. Distance-based Mapping</h3>
                <p className="text-slate-400 text-xs mb-4">(Resolution changes only with distance)</p>
                
                <div className="aspect-video bg-[#1a202c] rounded-lg border border-slate-600 mb-4 flex items-end p-2 relative overflow-hidden group">
                  <div className="absolute inset-0 flex items-center justify-center opacity-40">
                    {/* Fake concentric distance rings */}
                    <div className="w-[120%] h-[120%] border-[20px] border-slate-600 rounded-full"></div>
                    <div className="absolute w-[80%] h-[80%] border-[20px] border-slate-500 rounded-full"></div>
                    <div className="absolute w-[40%] h-[40%] border-[20px] border-slate-400 rounded-full"></div>
                  </div>
                  <div className="relative z-10 bg-slate-900/90 border border-slate-700 p-2 rounded text-[10px] text-slate-300 ml-auto shadow-lg backdrop-blur-sm">
                    <p className="font-bold text-blue-300">Near (0-10 m): 5 cm</p>
                    <p className="font-bold text-blue-400">Mid (10-25 m): 10 cm</p>
                    <p className="font-bold text-blue-500 mb-1">Far (25-50 m): 25 cm</p>
                    <p>Total Cells: 400,000</p>
                    <p>Memory Usage: ~200 MB</p>
                  </div>
                </div>
              </div>

              <div className="flex items-start gap-3 bg-red-500/10 p-3 rounded-lg border border-red-500/20">
                <div className="bg-red-500 text-white rounded-full w-5 h-5 flex items-center justify-center font-bold text-xs shrink-0 mt-0.5">X</div>
                <p className="text-xs text-red-200">Considers only distance, ignores what the object actually is.</p>
              </div>
            </div>

            {/* Panel 3 */}
            <div className="glass-panel p-5 rounded-2xl border border-emerald-500/40 bg-emerald-950/20 flex flex-col justify-between shadow-[0_0_20px_rgba(16,185,129,0.1)]">
              <div>
                <h3 className="text-lg font-bold text-emerald-400 mb-1">3. Nova-2.5D (Ours)</h3>
                <p className="text-emerald-300/70 text-xs mb-4">(Distance + Semantic + Dynamic + Uncertainty)</p>
                
                <div className="aspect-video bg-[#0f172a] rounded-lg border border-emerald-500/30 mb-4 flex items-end p-2 relative overflow-hidden group">
                  <div className="absolute inset-0 grid grid-cols-12 grid-rows-8 gap-px opacity-30">
                     {/* Adaptive grid simulation */}
                     {Array.from({length: 96}).map((_, i) => {
                       const isTarget = i === 44 || i === 45 || i === 56 || i === 57;
                       return <div key={i} className={isTarget ? "bg-emerald-400" : "bg-slate-600"}></div>
                     })}
                  </div>
                  <div className="relative z-10 bg-slate-900/90 border border-emerald-500/50 p-2 rounded text-[10px] text-emerald-200 ml-auto shadow-lg backdrop-blur-sm">
                    <p className="font-bold mb-1">Pedestrian (dynamic): 5 cm</p>
                    <p className="text-slate-300">Vehicle: 10 cm</p>
                    <p className="text-slate-300">Road (static): 25 cm</p>
                    <p className="text-slate-300 mb-1">Building (far): 50 cm</p>
                    <p className="font-medium text-emerald-400">Total Cells: 120,000</p>
                    <p className="font-medium text-emerald-400">Memory Usage: ~60 MB</p>
                  </div>
                </div>
              </div>

              <div className="flex items-start gap-3 bg-emerald-500/10 p-3 rounded-lg border border-emerald-500/30">
                <div className="bg-emerald-500 text-white rounded-full w-5 h-5 flex items-center justify-center font-bold text-xs shrink-0 mt-0.5">✓</div>
                <p className="text-xs text-emerald-200 font-medium">Finer where it matters,<br/>Coarser where it doesn't.</p>
              </div>
            </div>

          </div>

          {/* Interactive Spawn Control Panel */}
          <div className="mt-8 glass-panel p-8 rounded-3xl border border-blue-500/30 bg-gradient-to-br from-slate-900 to-slate-900/50">
            <div className="flex items-center gap-3 mb-6">
              <Sliders className="text-blue-400" size={28} />
              <div>
                <h3 className="text-2xl font-bold text-white">Interactive Adaptive Test</h3>
                <p className="text-slate-400 text-sm">Spawn objects live in CARLA to test the 20m adaptive compute cutoff.</p>
              </div>
            </div>

            <div className="flex flex-col md:flex-row gap-6 items-end">
              
              <div className="flex-1 w-full">
                <label className="block text-sm font-bold text-slate-400 uppercase tracking-wider mb-2">Object Type</label>
                <select 
                  value={spawnType} 
                  onChange={(e) => setSpawnType(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-700 text-white rounded-xl px-4 py-3 focus:outline-none focus:border-blue-500 font-medium"
                >
                  <option value="pedestrian">Pedestrian (Dynamic - High Priority)</option>
                  <option value="vehicle">Vehicle (Dynamic - High Priority)</option>
                  <option value="wall">Concrete Wall (Static - Low Priority)</option>
                </select>
              </div>

              <div className="flex-1 w-full">
                <label className="block text-sm font-bold text-slate-400 uppercase tracking-wider mb-2">Spawn Distance (Meters)</label>
                <div className="flex items-center gap-4">
                  <input 
                    type="range" 
                    min="10" max="100" step="10" 
                    value={spawnDist} 
                    onChange={(e) => setSpawnDist(e.target.value)}
                    className="w-full accent-blue-500"
                  />
                  <span className="bg-slate-950 border border-slate-700 px-4 py-2 rounded-lg font-mono text-blue-400 font-bold w-20 text-center">
                    {spawnDist}m
                  </span>
                </div>
              </div>

              <button 
                onClick={handleSpawn}
                className="w-full md:w-auto px-10 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-bold rounded-xl transition-all shadow-[0_0_20px_rgba(59,130,246,0.3)] hover:shadow-[0_0_30px_rgba(59,130,246,0.5)] transform hover:-translate-y-1 active:translate-y-0"
              >
                EXECUTE LIVE SPAWN
              </button>
            </div>

            {spawnStatus && (
              <div className="mt-6 p-4 bg-emerald-500/20 border border-emerald-500/50 rounded-xl text-emerald-400 font-mono flex items-center justify-center animate-in zoom-in duration-300">
                &gt; {spawnStatus}
              </div>
            )}
            
            <div className="mt-8 pt-6 border-t border-slate-800 grid grid-cols-1 md:grid-cols-2 gap-4">
               <div className="bg-slate-950/50 p-4 rounded-xl border border-slate-800">
                 <p className="text-slate-400 text-sm mb-1 uppercase font-bold">Currently Tracking</p>
                 <p className="text-xl font-medium text-white">{stats.pedestrians_tracked} Pedestrians, {stats.vehicles_tracked} Vehicles</p>
               </div>
               <div className="bg-slate-950/50 p-4 rounded-xl border border-slate-800">
                 <p className="text-slate-400 text-sm mb-1 uppercase font-bold">Rule Demonstration</p>
                 <p className="text-sm text-slate-300">Spawn a <span className="text-blue-400 font-bold">Wall</span> at 50m: Memory won't change (culled).<br/>Spawn a <span className="text-red-400 font-bold">Pedestrian</span> at 50m: Engine dynamically allocates a high-res subgrid to track them!</p>
               </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
