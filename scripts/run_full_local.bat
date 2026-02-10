@echo off
REM ============================================================================
REM CyberGuardX - Full Local Development Setup
REM ============================================================================
REM Starts infrastructure in Docker + Backend + Frontend locally

echo.
echo ============================================================================
echo   CyberGuardX - Full Local Development Setup
echo ============================================================================
echo.

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not running!
    echo Please start Docker Desktop and try again.
    echo.
    pause
    exit /b 1
)

REM Start infrastructure
echo [1/3] Starting PostgreSQL + Redis in Docker...
docker-compose up -d postgres redis

echo [2/3] Waiting for services to be healthy (10 seconds)...
timeout /t 10 /nobreak >nul

echo [3/3] Opening Backend and Frontend in new windows...
echo.

REM Start backend in new window
start "CyberGuardX Backend" cmd /k "cd /d %~dp0 && call run_backend_local.bat"

REM Wait a bit for backend to start
timeout /t 5 /nobreak >nul

REM Start frontend in new window
start "CyberGuardX Frontend" cmd /k "cd /d %~dp0 && call run_frontend_local.bat"

echo.
echo ============================================================================
echo   SUCCESS! Services are starting in separate windows...
echo ============================================================================
echo.
echo   Backend API:      http://localhost:8000
echo   Frontend UI:      http://localhost:3000
echo   PostgreSQL:       localhost:5432
echo   Redis:            localhost:6379
echo.
echo   Check the opened windows for logs
echo   Close each window to stop the respective service
echo.
echo ============================================================================
echo.

pause
