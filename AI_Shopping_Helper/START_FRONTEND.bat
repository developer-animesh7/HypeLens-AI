@echo off
REM Run Frontend (from main branch)
REM =================================

echo.
echo ========================================
echo   HypeLens - Frontend Launcher
echo ========================================
echo.

REM Change to script directory
cd /d "%~dp0"

REM Check current branch
echo Checking Git branch...
for /f "tokens=*" %%i in ('git branch --show-current') do set CURRENT_BRANCH=%%i
echo Current branch: %CURRENT_BRANCH%

REM If not on main, switch to it
if NOT "%CURRENT_BRANCH%"=="main" (
    echo.
    echo Switching to main branch (frontend is there)...
    git checkout main
)

REM Check if frontend folder exists
if NOT EXIST "frontend-nextjs" (
    echo.
    echo ERROR: frontend-nextjs folder not found!
    echo Make sure you're on the main branch.
    pause
    exit /b 1
)

REM Go to frontend folder
cd frontend-nextjs

REM Check if node_modules exists
if NOT EXIST "node_modules" (
    echo.
    echo Installing frontend dependencies...
    echo This may take a few minutes...
    call npm install
    if errorlevel 1 (
        echo.
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
)

REM Start frontend
echo.
echo ========================================
echo   Starting Frontend Server
echo ========================================
echo.
echo Frontend will be at: http://localhost:3000
echo.
echo Press Ctrl+C to stop
echo.

call npm run dev

pause
