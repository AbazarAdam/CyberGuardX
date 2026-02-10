@echo off
REM ============================================================================
REM CyberGuardX - Development Environment Setup
REM ============================================================================
REM One-time setup for local development

echo.
echo ============================================================================
echo   CyberGuardX - Development Environment Setup
echo ============================================================================
echo.

REM Check Python
echo [1/6] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed!
    echo Please install Python 3.10+ from https://www.python.org/
    pause
    exit /b 1
)
python --version

REM Check Docker
echo [2/6] Checking Docker installation...
docker --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not installed!
    echo Please install Docker Desktop from https://www.docker.com/
    pause
    exit /b 1
)
docker --version

REM Create virtual environment
echo [3/6] Creating Python virtual environment...
cd backend
if exist "venv\" (
    echo Virtual environment already exists, skipping...
) else (
    python -m venv venv
    echo Virtual environment created!
)

REM Install dependencies
echo [4/6] Installing Python dependencies...
call venv\Scripts\activate.bat
pip install --upgrade pip
pip install -r ..\requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)

REM Pull Docker images
cd ..
echo [5/6] Pulling Docker images...
docker-compose pull postgres redis

REM Create .env file if it doesn't exist
echo [6/6] Checking environment configuration...
if not exist ".env" (
    if exist ".env.example" (
        echo Creating .env from .env.example...
        copy .env.example .env
        echo [!] Please update .env with your configuration
    ) else (
        echo [WARNING] .env.example not found
    )
) else (
    echo .env file already exists
)

echo.
echo ============================================================================
echo   Setup Complete!
echo ============================================================================
echo.
echo   Next steps:
echo   1. Review and update .env file if needed
echo   2. Run: scripts\run_docker.bat        (for Docker setup)
echo      OR:  scripts\run_full_local.bat   (for local development)
echo.
echo   Development workflow:
echo   - Docker-only:     scripts\run_docker.bat
echo   - Local backend:   scripts\run_backend_local.bat
echo   - Local frontend:  scripts\run_frontend_local.bat
echo   - Full local:      scripts\run_full_local.bat
echo.
echo ============================================================================
echo.

pause
