@echo off
REM ========================================
REM HypeLens Startup Script
REM One-Click Launch for Frontend + Backend
REM ========================================

echo.
echo ========================================
echo    HypeLens - AI Shopping Assistant
echo ========================================
echo.

REM Change to project root directory (parent of launch_scripts)
cd /d "%~dp0\.."

REM Check if virtual environment exists
if not exist "venv\Scripts\python.exe" (
    echo [ERROR] Python virtual environment not found!
    echo Please run setup first.
    pause
    exit /b 1
)

REM Check if Node.js is installed
where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Node.js not found! Please install Node.js first.
    pause
    exit /b 1
)

echo [1/4] Checking dependencies...
echo.

REM Kill any existing processes on ports 3000 and 8000
echo [2/4] Cleaning up existing processes...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :3000') do taskkill /F /PID %%a >nul 2>nul
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000') do taskkill /F /PID %%a >nul 2>nul
timeout /t 2 /nobreak >nul

echo [3/4] Starting Backend (FastAPI + CLIP Model)...
echo This will take 3-4 seconds to load the AI model...
echo.
start "HypeLens Backend" cmd /k "venv\Scripts\python.exe -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload"

REM Wait for backend to start
timeout /t 5 /nobreak >nul

echo [4/4] Starting Frontend (Next.js)...
echo.
cd frontend-nextjs
start "HypeLens Frontend" cmd /k "npm run dev"

cd ..

echo.
echo ========================================
echo    HypeLens is Starting!
echo ========================================
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:3000
echo.
echo Two terminal windows will open:
echo  1. Backend Terminal (Python/FastAPI)
echo  2. Frontend Terminal (Next.js)
echo.
echo Wait 5-10 seconds for everything to load...
echo Then open: http://localhost:3000
echo.
echo Press any key to exit this window...
echo (The servers will continue running)
echo ========================================
pause >nul
