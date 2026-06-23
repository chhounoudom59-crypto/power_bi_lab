@echo off
REM Quick Docker Startup Script for ETL Pipeline (Windows PowerShell)

setlocal enabledelayedexpansion

echo.
echo ╔════════════════════════════════════════════╗
echo ║   ETL Pipeline Docker Startup              ║
echo ╚════════════════════════════════════════════╝
echo.

REM Check if Docker is installed
where docker >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ Docker is not installed. Please install Docker Desktop.
    pause
    exit /b 1
)

echo ✓ Docker is installed

REM Check if Docker daemon is running
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker daemon is not running. Please start Docker Desktop.
    pause
    exit /b 1
)

echo ✓ Docker daemon is running
echo.

REM Build images
echo 🔨 Building Docker images...
docker-compose build --quiet

if %errorlevel% neq 0 (
    echo ❌ Docker build failed
    pause
    exit /b 1
)

echo ✓ Docker build successful
echo.

REM Start services
echo 🚀 Starting services...
docker-compose up -d

if %errorlevel% neq 0 (
    echo ❌ Docker start failed
    pause
    exit /b 1
)

echo ✓ Services started
echo.

REM Wait for databases
echo ⏳ Waiting for databases to be ready...
timeout /t 10 /nobreak

REM Check services status
echo.
echo 📊 Service Status:
docker-compose ps

echo.
echo ✅ ETL Pipeline is running!
echo.
echo 🌐 Access Points:
echo    • Source DB:  localhost:5432
echo    • Target DB:  localhost:5433
echo    • PgAdmin:    http://localhost:5050
echo      (admin@example.com / admin)
echo.
echo 📝 View Logs:
echo    docker-compose logs -f etl_pipeline
echo    docker-compose logs -f etl_scheduler
echo.
echo 🛑 Stop Services:
echo    docker-compose down
echo.
pause
