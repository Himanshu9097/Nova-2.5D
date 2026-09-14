# launch_sih_demo.ps1
# Master Automation Script for Nova-2.5D SIH Pitch

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "🚀 STARTING NOVA-2.5D HACKATHON DEMO" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan

# 0. Kill existing ghost instances to free up VRAM
Write-Host "[0/4] Freeing up Video Memory..." -ForegroundColor Yellow
Stop-Process -Name "CarlaUE4" -Force -ErrorAction SilentlyContinue
Stop-Process -Name "CarlaUE4-Win64-Shipping" -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

# 1. Start CARLA Simulator (Background)
Write-Host "[1/4] Launching CARLA Simulator..." -ForegroundColor Yellow
Start-Process -FilePath "E:\SIH\CARLA_0.9.16\CarlaUE4.exe" -ArgumentList "-quality-level=Low -windowed -ResX=320 -ResY=240 -NoVSync -dx11" -WindowStyle Minimized

# Give CARLA 5 seconds to warm up
Start-Sleep -Seconds 5

# 2. Start Data Streaming Server (Backend)
Write-Host "[2/4] Starting Python Backend Streamer..." -ForegroundColor Yellow
Start-Process -FilePath "powershell.exe" -ArgumentList "-NoExit -Command `".\.venv\Scripts\python.exe dashboard\server.py`""

# 3. Start React Dashboard (Frontend)
Write-Host "[3/4] Booting Premium React Dashboard..." -ForegroundColor Yellow
Start-Process -FilePath "cmd.exe" -ArgumentList "/k cd dashboard\client && npm run dev -- --host"

# Give services 3 seconds to bind ports
Start-Sleep -Seconds 3

# Open dashboard in default browser (Vite default is usually 5173)
Start-Process "http://localhost:5173"

# 4. Start Live CARLA Script (Data generator)
Write-Host "[4/4] Starting Command Center & Radar..." -ForegroundColor Yellow
Start-Process -FilePath "powershell.exe" -ArgumentList "-NoExit -Command `".\.venv\Scripts\python.exe simulation\live_demo.py`""


Write-Host ""
Write-Host "==================================================" -ForegroundColor Green
Write-Host "✅ DEMO IS LIVE!" -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Green
Write-Host "Look at your web browser to see the Dashboard,"
Write-Host "And open the CARLA window to see the car driving."
