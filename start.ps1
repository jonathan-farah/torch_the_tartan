# Start both backend and frontend servers

Write-Host "🚀 Starting Voice/Face Recognition App..." -ForegroundColor Cyan

# Kill any existing processes
Write-Host "Stopping any existing servers..." -ForegroundColor Yellow
Stop-Process -Name python,node -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

# Start backend in a new PowerShell window
Write-Host "🐍 Starting Flask backend..." -ForegroundColor Green
$backendPath = Join-Path $PSScriptRoot "backend"
$ffmpegPath = "C:\Users\Owner\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.0.1-full_build\bin"

Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$backendPath'; `$env:PATH += ';$ffmpegPath'; python app.py" -WindowStyle Normal

# Wait a moment for backend to start
Start-Sleep -Seconds 3

# Start frontend in a new PowerShell window
Write-Host "⚛️  Starting React frontend..." -ForegroundColor Blue
$frontendPath = Join-Path $PSScriptRoot "frontend"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$frontendPath'; npm start" -WindowStyle Normal

Write-Host ""
Write-Host "✅ Servers starting!" -ForegroundColor Green
Write-Host "Backend will be at: http://localhost:5000" -ForegroundColor Cyan
Write-Host "Frontend will be at: http://localhost:3000" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press any key to stop both servers..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

# Stop servers when user presses a key
Write-Host "Stopping servers..." -ForegroundColor Red
Stop-Process -Name python,node -Force -ErrorAction SilentlyContinue
Write-Host "Servers stopped." -ForegroundColor Green
