# ========================================
# HypeLens Startup Script (PowerShell)
# One-Click Launch for Frontend + Backend
# ========================================

$ErrorActionPreference = "Continue"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   HypeLens - AI Shopping Assistant" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Get script directory
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

# Check Python virtual environment
if (-not (Test-Path "venv\Scripts\python.exe")) {
    Write-Host "[ERROR] Python virtual environment not found!" -ForegroundColor Red
    Write-Host "Please set up the project first." -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check Node.js
try {
    $nodeVersion = node --version
    Write-Host "[✓] Node.js found: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Node.js not found! Please install Node.js first." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "[1/5] Checking dependencies..." -ForegroundColor Yellow

# Check if frontend dependencies are installed
if (-not (Test-Path "frontend-nextjs\node_modules")) {
    Write-Host "[!] Installing frontend dependencies..." -ForegroundColor Yellow
    Set-Location frontend-nextjs
    npm install
    Set-Location ..
}

Write-Host "[2/5] Cleaning up old processes..." -ForegroundColor Yellow

# Kill processes on ports 3000 and 8000
$port3000 = Get-NetTCPConnection -LocalPort 3000 -ErrorAction SilentlyContinue
$port8000 = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue

if ($port3000) {
    Stop-Process -Id $port3000.OwningProcess -Force -ErrorAction SilentlyContinue
    Write-Host "  [✓] Cleared port 3000" -ForegroundColor Green
}

if ($port8000) {
    Stop-Process -Id $port8000.OwningProcess -Force -ErrorAction SilentlyContinue
    Write-Host "  [✓] Cleared port 8000" -ForegroundColor Green
}

Start-Sleep -Seconds 2

Write-Host ""
Write-Host "[3/5] Starting Backend (FastAPI + CLIP Model)..." -ForegroundColor Yellow
Write-Host "      Loading AI model (takes 3-4 seconds)..." -ForegroundColor Gray

# Start backend in new window
$backendJob = Start-Process powershell -ArgumentList "-NoExit", "-Command", "& {
    Set-Location '$scriptPath'
    Write-Host '========================================' -ForegroundColor Cyan
    Write-Host '   HypeLens Backend (FastAPI)' -ForegroundColor Cyan
    Write-Host '========================================' -ForegroundColor Cyan
    Write-Host ''
    & '.\venv\Scripts\python.exe' -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload
}" -PassThru

Write-Host "  [✓] Backend starting (PID: $($backendJob.Id))..." -ForegroundColor Green

# Wait for backend to initialize
Write-Host ""
Write-Host "[4/5] Waiting for backend to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 6

# Check if backend is running
$backendRunning = $false
for ($i = 0; $i -lt 10; $i++) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/" -TimeoutSec 2 -ErrorAction SilentlyContinue
        $backendRunning = $true
        break
    } catch {
        Start-Sleep -Seconds 1
    }
}

if ($backendRunning) {
    Write-Host "  [✓] Backend is running!" -ForegroundColor Green
} else {
    Write-Host "  [!] Backend may still be loading..." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "[5/5] Starting Frontend (Next.js)..." -ForegroundColor Yellow

# Start frontend in new window
$frontendJob = Start-Process powershell -ArgumentList "-NoExit", "-Command", "& {
    Set-Location '$scriptPath\frontend-nextjs'
    Write-Host '========================================' -ForegroundColor Cyan
    Write-Host '   HypeLens Frontend (Next.js)' -ForegroundColor Cyan
    Write-Host '========================================' -ForegroundColor Cyan
    Write-Host ''
    npm run dev
}" -PassThru

Write-Host "  [✓] Frontend starting (PID: $($frontendJob.Id))..." -ForegroundColor Green

# Summary
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "   HypeLens is Running!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Backend:  http://localhost:8000" -ForegroundColor Cyan
Write-Host "Frontend: http://localhost:3000" -ForegroundColor Cyan
Write-Host ""
Write-Host "Two terminal windows have opened:" -ForegroundColor White
Write-Host "  1. Backend Terminal (Python/FastAPI)" -ForegroundColor Gray
Write-Host "  2. Frontend Terminal (Next.js)" -ForegroundColor Gray
Write-Host ""
Write-Host "Wait 5-10 seconds for everything to load..." -ForegroundColor Yellow
Write-Host "Then open: http://localhost:3000" -ForegroundColor Green
Write-Host ""
Write-Host "To stop both servers:" -ForegroundColor Yellow
Write-Host "  - Close both terminal windows" -ForegroundColor Gray
Write-Host "  - Or run: .\stop_hypelens.ps1" -ForegroundColor Gray
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

# Wait for user
Read-Host "Press Enter to close this window (servers will keep running)"
