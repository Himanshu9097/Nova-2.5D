import React, { useRef, useEffect, useState, useCallback } from 'react';

/**
 * RadarBEV — Real-time Bird's-Eye-View LiDAR Point Cloud Canvas Renderer
 * 
 * Consumes REAL binary point cloud data from the Nova-2.5D pipeline via SSE.
 * Binary format: [uint32 N][float16 x × N][float16 y × N][uint8 tag × N]
 * 
 * Coordinate system (CARLA sensor-local):
 *   +X = Forward, +Y = Right, +Z = Up
 * 
 * Screen mapping:
 *   screen_x = center_x + point_y * scale  (Y right → screen right)
 *   screen_y = ego_y    - point_x * scale  (X forward → screen up)
 */

// CARLA Semantic LiDAR color palette (matches reference image)
const SEMANTIC_COLORS = {
  0:  { r: 100, g: 116, b: 139, label: 'Other' },       // Unlabeled → gray
  1:  { r: 168, g:  85, b: 247, label: 'Building' },     // Purple
  2:  { r: 100, g: 116, b: 139, label: 'Other' },        // Fence
  3:  { r: 148, g: 163, b: 184, label: 'Other' },        // Other
  4:  { r:  34, g: 197, b:  94, label: 'Pedestrian' },   // Green
  5:  { r: 250, g: 204, b:  21, label: 'Pole' },         // Yellow
  6:  { r: 200, g: 220, b: 255, label: 'Road' },         // Road lines → light cyan
  7:  { r:   0, g: 168, b: 255, label: 'Road' },         // Road → cyan
  8:  { r:  56, g: 189, b: 248, label: 'Road' },         // Sidewalk → sky blue
  9:  { r:  22, g: 163, b:  74, label: 'Other' },        // Vegetation
  10: { r: 239, g:  68, b:  68, label: 'Vehicle' },      // Red
  12: { r: 245, g: 158, b:  11, label: 'Pole' },         // Traffic sign → orange
  18: { r: 250, g: 204, b:  21, label: 'Pole' },         // Traffic light → gold
};

const LEGEND_ITEMS = [
  { label: 'Road',       color: '#00a8ff' },
  { label: 'Vehicle',    color: '#ef4444' },
  { label: 'Pedestrian', color: '#22c55e' },
  { label: 'Building',   color: '#a855f7' },
  { label: 'Pole',       color: '#facc15' },
  { label: 'Other',      color: '#94a3b8' },
];

const SENSOR_RANGE = 50.0; // meters (configured in live_demo.py)
const RANGE_RINGS = [10, 20, 30, 40, 50]; // meters

function getSemanticColor(tag) {
  return SEMANTIC_COLORS[tag] || SEMANTIC_COLORS[0];
}

// Decode float16 (IEEE 754 half-precision) from two bytes
function decodeFloat16(byte0, byte1) {
  const bits = byte0 | (byte1 << 8);
  const sign = (bits >> 15) & 1;
  let exp = (bits >> 10) & 0x1f;
  let frac = bits & 0x3ff;

  if (exp === 0) {
    // Subnormal
    if (frac === 0) return sign ? -0.0 : 0.0;
    return (sign ? -1 : 1) * Math.pow(2, -14) * (frac / 1024);
  }
  if (exp === 31) {
    return frac === 0 ? (sign ? -Infinity : Infinity) : NaN;
  }
  return (sign ? -1 : 1) * Math.pow(2, exp - 15) * (1 + frac / 1024);
}

export default function RadarBEV({ stats }) {
  const canvasRef = useRef(null);
  const containerRef = useRef(null);
  const pointsRef = useRef(null); // { xs: Float32Array, ys: Float32Array, tags: Uint8Array, count: number }
  const frameCountRef = useRef(0);
  const lastFrameTimeRef = useRef(performance.now());
  const [updateHz, setUpdateHz] = useState(0);
  const [detectionCount, setDetectionCount] = useState(0);
  const animFrameRef = useRef(null);

  // Connect to binary point cloud SSE stream
  useEffect(() => {
    const url = `http://${window.location.hostname}:5000/pointcloud_stream`;
    const es = new EventSource(url);

    es.onmessage = (event) => {
      try {
        // Decode base64 → binary
        const binaryStr = atob(event.data);
        const bytes = new Uint8Array(binaryStr.length);
        for (let i = 0; i < binaryStr.length; i++) {
          bytes[i] = binaryStr.charCodeAt(i);
        }

        // Parse header: uint32 little-endian point count
        if (bytes.length < 4) return;
        const n = bytes[0] | (bytes[1] << 8) | (bytes[2] << 16) | (bytes[3] << 24);
        
        // Validate: need 4 + n*2 (x) + n*2 (y) + n*1 (tag) bytes
        const expectedLen = 4 + n * 5;
        if (bytes.length < expectedLen || n === 0) return;

        // Decode float16 arrays
        const xOffset = 4;
        const yOffset = 4 + n * 2;
        const tOffset = 4 + n * 4;

        const xs = new Float32Array(n);
        const ys = new Float32Array(n);
        const tags = new Uint8Array(n);

        for (let i = 0; i < n; i++) {
          xs[i] = decodeFloat16(bytes[xOffset + i * 2], bytes[xOffset + i * 2 + 1]);
          ys[i] = decodeFloat16(bytes[yOffset + i * 2], bytes[yOffset + i * 2 + 1]);
          tags[i] = bytes[tOffset + i];
        }

        pointsRef.current = { xs, ys, tags, count: n };
        setDetectionCount(n);

        // Measure real update rate
        frameCountRef.current++;
        const now = performance.now();
        const elapsed = now - lastFrameTimeRef.current;
        if (elapsed >= 1000) {
          setUpdateHz(Math.round(frameCountRef.current * 1000 / elapsed));
          frameCountRef.current = 0;
          lastFrameTimeRef.current = now;
        }
      } catch (e) {
        // Silently skip malformed frames
      }
    };

    return () => es.close();
  }, []);

  // Canvas rendering loop
  const render = useCallback(() => {
    const canvas = canvasRef.current;
    const container = containerRef.current;
    if (!canvas || !container) {
      animFrameRef.current = requestAnimationFrame(render);
      return;
    }

    // Responsive sizing
    const rect = container.getBoundingClientRect();
    const dpr = window.devicePixelRatio || 1;
    const w = rect.width;
    const h = rect.height;
    canvas.width = w * dpr;
    canvas.height = h * dpr;
    canvas.style.width = w + 'px';
    canvas.style.height = h + 'px';

    const ctx = canvas.getContext('2d');
    ctx.scale(dpr, dpr);

    // Background - almost black with subtle navy tint
    ctx.fillStyle = '#040810';
    ctx.fillRect(0, 0, w, h);

    // Subtle radial gradient from ego position
    const egoX = w / 2;
    const egoY = h * 0.78; // Ego at 78% down (bottom-center area)
    
    const grad = ctx.createRadialGradient(egoX, egoY, 0, egoX, egoY, Math.min(w, h) * 0.9);
    grad.addColorStop(0, 'rgba(0, 80, 160, 0.06)');
    grad.addColorStop(0.5, 'rgba(0, 40, 80, 0.03)');
    grad.addColorStop(1, 'rgba(0, 0, 0, 0)');
    ctx.fillStyle = grad;
    ctx.fillRect(0, 0, w, h);

    // Scale: fit 50m forward (above ego) and ~15m behind, ~35m sides
    const maxForwardMeters = SENSOR_RANGE;
    const pixelsPerMeter = Math.min(
      (egoY - 40) / maxForwardMeters,   // forward space
      (w / 2 - 20) / (SENSOR_RANGE * 0.7) // side space
    );

    // --- RANGE RINGS ---
    ctx.lineWidth = 1;
    ctx.font = '10px Inter, system-ui, sans-serif';
    for (const ringM of RANGE_RINGS) {
      const ringPx = ringM * pixelsPerMeter;
      ctx.beginPath();
      ctx.arc(egoX, egoY, ringPx, 0, Math.PI * 2);
      ctx.strokeStyle = 'rgba(0, 180, 255, 0.12)';
      ctx.stroke();

      // Subtle glow ring
      ctx.beginPath();
      ctx.arc(egoX, egoY, ringPx, 0, Math.PI * 2);
      ctx.strokeStyle = 'rgba(0, 180, 255, 0.04)';
      ctx.lineWidth = 3;
      ctx.stroke();
      ctx.lineWidth = 1;

      // Distance label
      ctx.fillStyle = 'rgba(0, 180, 255, 0.35)';
      ctx.fillText(`${ringM}m`, egoX + ringPx * 0.71 + 4, egoY - ringPx * 0.71 - 4);
    }

    // --- AXIS LINES ---
    ctx.strokeStyle = 'rgba(0, 180, 255, 0.06)';
    ctx.lineWidth = 1;
    // Forward line
    ctx.beginPath();
    ctx.moveTo(egoX, egoY);
    ctx.lineTo(egoX, 10);
    ctx.stroke();
    // Left/Right line
    ctx.beginPath();
    ctx.moveTo(20, egoY);
    ctx.lineTo(w - 20, egoY);
    ctx.stroke();

    // --- RENDER POINT CLOUD ---
    const pts = pointsRef.current;
    if (pts && pts.count > 0) {
      const { xs, ys, tags, count } = pts;

      // Pre-sort by distance (far points first → near points on top)
      const indices = new Uint32Array(count);
      const distsSq = new Float32Array(count);
      for (let i = 0; i < count; i++) {
        indices[i] = i;
        distsSq[i] = xs[i] * xs[i] + ys[i] * ys[i];
      }
      // Sort descending by distance (far first)
      indices.sort((a, b) => distsSq[b] - distsSq[a]);

      // Batch render by semantic class for efficiency
      ctx.globalCompositeOperation = 'lighter'; // Additive blending for glow

      for (let idx = 0; idx < count; idx++) {
        const i = indices[idx];
        const x = xs[i];
        const y = ys[i];
        const tag = tags[i];
        const dist = Math.sqrt(distsSq[i]);

        // Screen coordinates: Y→right, X→up (CARLA convention)
        const sx = egoX + y * pixelsPerMeter;
        const sy = egoY - x * pixelsPerMeter;

        // Clip to canvas
        if (sx < -5 || sx > w + 5 || sy < -5 || sy > h + 5) continue;

        const color = getSemanticColor(tag);

        // Dynamic objects (ped=4, vehicle=10) get larger, brighter points
        const isDynamic = tag === 4 || tag === 10;
        
        // Point radius: near = larger, far = smaller. Dynamic = extra large.
        let radius = isDynamic ? 3.0 : 1.5;
        if (dist < 10) radius += 0.8;
        else if (dist > 35) radius -= 0.3;

        // Distance-based opacity: near = brighter, far = dimmer
        const alpha = isDynamic ? 0.95 : Math.max(0.25, 1.0 - dist / (SENSOR_RANGE * 1.2));

        // Glow effect for dynamic threats
        if (isDynamic) {
          ctx.shadowColor = `rgb(${color.r}, ${color.g}, ${color.b})`;
          ctx.shadowBlur = 8;
        } else {
          ctx.shadowColor = `rgba(${color.r}, ${color.g}, ${color.b}, 0.3)`;
          ctx.shadowBlur = 2;
        }

        ctx.fillStyle = `rgba(${color.r}, ${color.g}, ${color.b}, ${alpha})`;
        ctx.beginPath();
        ctx.arc(sx, sy, radius, 0, Math.PI * 2);
        ctx.fill();
      }

      // Reset composite and shadow
      ctx.globalCompositeOperation = 'source-over';
      ctx.shadowBlur = 0;
    }

    // --- EGO VEHICLE ---
    ctx.save();
    ctx.translate(egoX, egoY);
    
    // Car body silhouette (top-down view)
    const carW = 12, carL = 24;
    
    // Subtle glow beneath car
    const carGlow = ctx.createRadialGradient(0, 0, 0, 0, 0, 30);
    carGlow.addColorStop(0, 'rgba(0, 200, 255, 0.15)');
    carGlow.addColorStop(1, 'rgba(0, 0, 0, 0)');
    ctx.fillStyle = carGlow;
    ctx.fillRect(-30, -30, 60, 60);
    
    // Car body
    ctx.fillStyle = '#0a1628';
    ctx.strokeStyle = 'rgba(0, 220, 255, 0.7)';
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.roundRect(-carW / 2, -carL / 2, carW, carL, 3);
    ctx.fill();
    ctx.stroke();

    // Windshield indicator (front)
    ctx.fillStyle = 'rgba(0, 220, 255, 0.3)';
    ctx.fillRect(-carW / 2 + 2, -carL / 2 + 2, carW - 4, 5);

    // Heading arrow
    ctx.strokeStyle = 'rgba(0, 255, 255, 0.6)';
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.moveTo(0, -carL / 2 - 2);
    ctx.lineTo(0, -carL / 2 - 12);
    ctx.stroke();
    // Arrow tip
    ctx.beginPath();
    ctx.moveTo(-3, -carL / 2 - 9);
    ctx.lineTo(0, -carL / 2 - 14);
    ctx.lineTo(3, -carL / 2 - 9);
    ctx.strokeStyle = 'rgba(0, 255, 255, 0.6)';
    ctx.stroke();

    ctx.restore();

    // --- LEGEND (top-right) ---
    const legendX = w - 140;
    const legendY = 16;
    ctx.fillStyle = 'rgba(4, 8, 16, 0.85)';
    ctx.strokeStyle = 'rgba(100, 116, 139, 0.3)';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.roundRect(legendX - 12, legendY - 6, 145, LEGEND_ITEMS.length * 20 + 14, 8);
    ctx.fill();
    ctx.stroke();

    ctx.font = '11px Inter, system-ui, sans-serif';
    LEGEND_ITEMS.forEach((item, i) => {
      const ly = legendY + 8 + i * 20;
      
      // Glowing dot
      ctx.shadowColor = item.color;
      ctx.shadowBlur = 6;
      ctx.fillStyle = item.color;
      ctx.beginPath();
      ctx.arc(legendX, ly, 4, 0, Math.PI * 2);
      ctx.fill();
      ctx.shadowBlur = 0;

      // Label
      ctx.fillStyle = 'rgba(203, 213, 225, 0.9)';
      ctx.fillText(item.label, legendX + 12, ly + 4);
    });

    // --- HUD (top-left) ---
    const hudX = 14;
    const hudY = 14;
    ctx.fillStyle = 'rgba(4, 8, 16, 0.8)';
    ctx.strokeStyle = 'rgba(0, 180, 255, 0.2)';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.roundRect(hudX, hudY, 170, 96, 8);
    ctx.fill();
    ctx.stroke();

    ctx.font = 'bold 11px Inter, system-ui, sans-serif';
    ctx.fillStyle = 'rgba(0, 200, 255, 0.9)';
    ctx.fillText('LIDAR POINT CLOUD (BEV)', hudX + 10, hudY + 18);

    ctx.font = '10px JetBrains Mono, monospace';
    ctx.fillStyle = 'rgba(203, 213, 225, 0.75)';
    ctx.fillText(`Detections: ${detectionCount.toLocaleString()}`, hudX + 10, hudY + 36);
    ctx.fillText(`Range: ${SENSOR_RANGE}m`, hudX + 10, hudY + 52);
    ctx.fillText(`Update Rate: ${updateHz} Hz`, hudX + 10, hudY + 68);
    ctx.fillText(`Ego Speed: ${(stats?.speed_kmh || 0).toFixed(1)} km/h`, hudX + 10, hudY + 84);

    // --- FORWARD label ---
    ctx.font = '10px Inter, system-ui, sans-serif';
    ctx.fillStyle = 'rgba(0, 180, 255, 0.25)';
    ctx.textAlign = 'center';
    ctx.fillText('FORWARD', egoX, 22);
    ctx.textAlign = 'start';

    animFrameRef.current = requestAnimationFrame(render);
  }, [detectionCount, updateHz, stats]);

  // Start render loop
  useEffect(() => {
    animFrameRef.current = requestAnimationFrame(render);
    return () => {
      if (animFrameRef.current) cancelAnimationFrame(animFrameRef.current);
    };
  }, [render]);

  return (
    <div ref={containerRef} style={{ width: '100%', height: '100%', position: 'relative', minHeight: '380px' }}>
      <canvas
        ref={canvasRef}
        style={{
          display: 'block',
          width: '100%',
          height: '100%',
          borderRadius: '12px',
        }}
      />
    </div>
  );
}
