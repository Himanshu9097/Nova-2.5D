# Nova-2.5D Full Pipeline Pitch Demo
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "🚀 STARTING NOVA-2.5D END-TO-END PIPELINE" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan

# 1. Start Data Streaming Server (Backend)
Write-Host "[1/3] Starting Python Backend Streamer..." -ForegroundColor Yellow
Start-Process -FilePath "powershell.exe" -ArgumentList "-NoExit -Command `".\.venv\Scripts\python.exe dashboard\server.py`""

# 2. Start React Dashboard (Frontend)
Write-Host "[2/3] Booting Premium React Dashboard..." -ForegroundColor Yellow
Start-Process -FilePath "cmd.exe" -ArgumentList "/k cd dashboard\client && npm run dev"

# Give services 3 seconds to bind ports
Start-Sleep -Seconds 3

# 3. Start The Master Pipeline
Write-Host "[3/3] Starting End-to-End LiDAR Pipeline..." -ForegroundColor Yellow
Start-Process -FilePath "powershell.exe" -ArgumentList "-NoExit -Command `".\.venv\Scripts\python.exe simulation\run_pipeline.py`""

Write-Host ""
Write-Host "==================================================" -ForegroundColor Green
Write-Host "🎉 PIPELINE IS LIVE!" -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Look at your web browser to see the Dashboard!"
