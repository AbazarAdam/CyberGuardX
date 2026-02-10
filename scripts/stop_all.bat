@echo off
REM ============================================================================
REM CyberGuardX - Stop All Services
REM ============================================================================
REM Stops Docker containers and cleans up

echo.
echo ============================================================================
echo   CyberGuardX - Stopping All Services
echo ============================================================================
echo.

echo [1/2] Stopping Docker containers...
docker-compose down

echo [2/2] Checking for running processes...
REM Kill any uvicorn or python server processes if needed
taskkill /F /IM uvicorn.exe >nul 2>&1
taskkill /F /IM python.exe /FI "WINDOWTITLE eq CyberGuardX*" >nul 2>&1

echo.
echo ============================================================================
echo   All services stopped!
echo ============================================================================
echo.

pause
