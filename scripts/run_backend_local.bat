@echo off
REM ============================================================================
REM CyberGuardX - Backend Local Development Script
REM ============================================================================
REM Runs backend locally (requires PostgreSQL + Redis in Docker)

echo.
echo ============================================================================
echo   CyberGuardX - Backend Local Development
echo ============================================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH!
    echo Please install Python 3.10+ and try again.
    echo.
    pause
    exit /b 1
)

REM Start infrastructure services
echo [1/5] Starting PostgreSQL + Redis in Docker...
docker-compose up -d postgres redis
if errorlevel 1 (
    echo [ERROR] Failed to start Docker services
    pause
    exit /b 1
)

echo [2/5] Waiting for services to be healthy (10 seconds)...
timeout /t 10 /nobreak >nul

REM Check if virtual environment exists
if not exist "backend\venv\" (
    echo [3/5] Creating virtual environment...
    cd backend
    python -m venv venv
    cd ..
) else (
    echo [3/5] Virtual environment already exists
)

REM Activate virtual environment and install dependencies
echo [4/5] Installing dependencies...
cd backend
call venv\Scripts\activate.bat
pip install -q --upgrade pip
pip install -q -r ..\requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)

REM Run database migrations
echo [5/5] Running database migrations...
alembic upgrade head
if errorlevel 1 (
    echo [WARNING] Migrations failed - database might not be initialized
)

echo.
echo ============================================================================
echo   Starting FastAPI Backend Server...
echo ============================================================================
echo.
echo   Backend API:      http://localhost:8000
echo   API Docs:         http://localhost:8000/docs
echo   Interactive:      http://localhost:8000/redoc
echo.
echo   Press CTRL+C to stop the server
echo.
echo ============================================================================
echo.

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
