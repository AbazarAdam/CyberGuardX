@echo off
REM ═════════════════════════════════════════════════════════════════════
REM CyberGuardX — Docker Quick Start (Windows Batch)
REM ═════════════════════════════════════════════════════════════════════
REM Simple wrapper to run Docker Compose easily on Windows
REM ═════════════════════════════════════════════════════════════════════

echo.
echo ═════════════════════════════════════════════════════
echo    🛡️  CyberGuardX — Starting Services
echo ═════════════════════════════════════════════════════
echo.

REM Check if .env exists
if not exist .env (
    echo Creating .env from template...
    copy .env.example .env
    echo ✅ Created .env file
    echo.
)

REM Start Docker Compose
echo 🚀 Starting CyberGuardX...
echo.
docker-compose up

echo.
echo Services stopped.
pause
