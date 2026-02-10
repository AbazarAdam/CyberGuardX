@echo off
REM ============================================================================
REM CyberGuardX - Frontend Local Development Script
REM ============================================================================
REM Runs frontend using Python's built-in HTTP server

echo.
echo ============================================================================
echo   CyberGuardX - Frontend Local Development
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

cd frontend

echo.
echo ============================================================================
echo   Starting Frontend Server...
echo ============================================================================
echo.
echo   Frontend:         http://localhost:3000
echo   Index:            http://localhost:3000/index.html
echo.
echo   Press CTRL+C to stop the server
echo.
echo ============================================================================
echo.

python server.py
