import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Activity, HardDrive, Cpu, Zap, Car, Eye } from 'lucide-react';
import './index.css';

function App() {
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
    accuracy: 0
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

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-8 font-sans">
      
      {/* Header */}
      <header className="mb-10 flex justify-between items-center border-b border-slate-800 pb-6">
        <div>
          <h1 className="text-4xl font-black tracking-tight bg-gradient-to-r from-blue-400 to-emerald-400 bg-clip-text text-transparent">
            NOVA-2.5D COMMAND CENTER
          </h1>
          <p className="text-slate-400 mt-2 font-medium">Smart India Hackathon 2026 • Live CARLA Telemetry</p>
        </div>
        <div className={`px-6 py-2 rounded-full font-bold flex items-center gap-3 border ${stats.status === "Active Mapping" ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/50" : "bg-red-500/10 text-red-400 border-red-500/50"}`}>
          <div className={`w-3 h-3 rounded-full ${stats.status === "Active Mapping" ? "bg-emerald-400 animate-pulse" : "bg-red-400"}`}></div>
          {stats.status}
        </div>
      </header>

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
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
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
        </div>
      </div>

    </div>
  );
}

export default App;
