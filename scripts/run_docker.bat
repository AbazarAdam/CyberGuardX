@echo off
REM ============================================================================
REM CyberGuardX - Docker Compose Startup Script
REM ============================================================================
REM Starts all services (PostgreSQL, Redis, Backend, Frontend) using Docker

echo.
echo ============================================================================
echo   CyberGuardX - Docker Compose Startup
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

echo [1/4] Starting PostgreSQL Database...
docker-compose up -d postgres
if errorlevel 1 (
    echo [ERROR] Failed to start PostgreSQL
    pause
    exit /b 1
)

echo [2/4] Starting Redis Cache...
docker-compose up -d redis
if errorlevel 1 (
    echo [ERROR] Failed to start Redis
    pause
    exit /b 1
)

echo [3/4] Waiting for services to be healthy (10 seconds)...
timeout /t 10 /nobreak >nul

echo [4/4] Starting Backend and Frontend...
docker-compose up -d backend frontend
if errorlevel 1 (
    echo [ERROR] Failed to start application services
    pause
    exit /b 1
)

echo.
echo ============================================================================
echo   SUCCESS! CyberGuardX is now running!
echo ============================================================================
echo.
echo   Backend API:      http://localhost:8000
echo   Frontend UI:      http://localhost:3000
echo   PostgreSQL:       localhost:5432
echo   Redis:            localhost:6379
echo.
echo   API Docs:         http://localhost:8000/docs
echo   Health Check:     http://localhost:8000/
echo.
echo   View logs:        docker-compose logs -f
echo   Stop services:    docker-compose down
echo   Restart:          docker-compose restart
echo.
echo ============================================================================
echo.

pause
