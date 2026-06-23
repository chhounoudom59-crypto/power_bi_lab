@echo off
REM Docker Health Check Script for Windows

echo.
echo 🔍 ETL Pipeline Docker Health Check
echo ====================================
echo.

echo 1️⃣  Docker Installation:
docker --version >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=*" %%i in ('docker --version') do echo    ✓ %%i
) else (
    echo    ✗ Docker not found. Install Docker Desktop.
    pause
    exit /b 1
)

echo.
echo 2️⃣  Docker Daemon:
docker info >nul 2>&1
if %errorlevel% equ 0 (
    echo    ✓ Docker daemon is running
) else (
    echo    ✗ Docker daemon is not running
    pause
    exit /b 1
)

echo.
echo 3️⃣  Docker Compose:
docker-compose --version >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=*" %%i in ('docker-compose --version') do echo    ✓ %%i
) else (
    echo    ✗ Docker Compose not found
    pause
    exit /b 1
)

echo.
echo 4️⃣  Service Status:
docker-compose ps >nul 2>&1
if %errorlevel% equ 0 (
    echo    ✓ Services defined
    echo.
    docker-compose ps
) else (
    echo    ℹ Services not started yet (this is OK^)
)

echo.
echo 5️⃣  Docker Images:
docker images --filter "reference=*etl*" --filter "reference=*postgres*"

echo.
echo ✅ Health check complete!
echo.
echo 📝 To get started:
echo    1. Run: docker-start.bat (Windows^)
echo    2. Or:  docker-compose up -d
echo    3. Check http://localhost:5050 for PgAdmin
echo.
pause
