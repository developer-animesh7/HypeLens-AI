@echo off
REM ========================================
REM HypeLens Stop Script
REM Stops all Frontend + Backend processes
REM ========================================

echo.
echo ========================================
echo    Stopping HypeLens...
echo ========================================
echo.

echo [1/3] Stopping Frontend (Node.js)...
taskkill /F /IM node.exe >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo   [OK] Frontend stopped
) else (
    echo   [OK] No frontend processes found
)

echo [2/3] Stopping Backend (Python)...
taskkill /F /IM python.exe >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo   [OK] Backend stopped
) else (
    echo   [OK] No backend processes found
)

echo [3/3] Releasing ports...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :3000') do taskkill /F /PID %%a >nul 2>nul
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000') do taskkill /F /PID %%a >nul 2>nul
echo   [OK] Ports released

echo.
echo ========================================
echo    HypeLens Stopped Successfully!
echo ========================================
echo.
pause
