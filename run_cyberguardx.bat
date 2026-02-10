@echo off
REM CyberGuardX launcher script
REM This script starts the backend (FastAPI) and frontend (static server).

cd /d "%~dp0"

echo.
echo ═══════════════════════════════════════════════════════
echo    🛡️  CyberGuardX — Security Analysis Platform
echo ═══════════════════════════════════════════════════════
echo.

REM Activate virtual environment if available
if exist ".venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call ".venv\Scripts\activate.bat"
)

REM Check and install dependencies if needed
echo Checking dependencies...
python -c "import pydantic.networks" >nul 2>&1
if errorlevel 1 (
    echo Installing missing dependencies...
    pip install "pydantic[email]" >nul 2>&1
)

REM Start backend API server on port 8000
cd backend
start "CyberGuardX Backend" cmd /c "python -m uvicorn app.main:app --reload --port 8000"

REM Start frontend web UI on port 3000
cd ..\frontend
start "CyberGuardX Frontend" cmd /c "python -m http.server 3000"

cd /d "%~dp0"

echo.
echo CyberGuardX is starting...
echo   Backend API:  http://localhost:8000
echo   Frontend UI:  http://localhost:3000
echo.
pause
