# ========================================
# HypeLens Stop Script
# Stops all Frontend + Backend processes
# ========================================

Write-Host ""
Write-Host "========================================" -ForegroundColor Red
Write-Host "   Stopping HypeLens..." -ForegroundColor Red
Write-Host "========================================" -ForegroundColor Red
Write-Host ""

# Stop Node.js processes (Frontend)
Write-Host "[1/3] Stopping Frontend (Node.js)..." -ForegroundColor Yellow
Get-Process -Name "node" -ErrorAction SilentlyContinue | Stop-Process -Force
Write-Host "  [✓] Frontend stopped" -ForegroundColor Green

# Stop Python/Uvicorn processes (Backend)
Write-Host "[2/3] Stopping Backend (Python/Uvicorn)..." -ForegroundColor Yellow
Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*uvicorn*" } | Stop-Process -Force
Write-Host "  [✓] Backend stopped" -ForegroundColor Green

# Clear ports
Write-Host "[3/3] Releasing ports..." -ForegroundColor Yellow
$port3000 = Get-NetTCPConnection -LocalPort 3000 -ErrorAction SilentlyContinue
$port8000 = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue

if ($port3000) {
    Stop-Process -Id $port3000.OwningProcess -Force -ErrorAction SilentlyContinue
}

if ($port8000) {
    Stop-Process -Id $port8000.OwningProcess -Force -ErrorAction SilentlyContinue
}

Write-Host "  [✓] Ports released" -ForegroundColor Green

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "   HypeLens Stopped Successfully!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

Read-Host "Press Enter to exit"
