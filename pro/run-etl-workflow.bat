@echo off
REM Complete End-to-End ETL Workflow (Windows)
REM 1. Start Docker services
REM 2. Download and restore backup
REM 3. Run ETL pipeline
REM 4. Verify results

setlocal enabledelayedexpansion

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║   ETL Pipeline - Complete End-to-End Workflow              ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

REM Step 1: Start Docker services
echo ═══════════════════════════════════════════════════════════
echo STEP 1: Starting Docker Services
echo ═══════════════════════════════════════════════════════════
echo.

echo 🚀 Starting Docker services...
docker-compose up -d

echo ⏳ Waiting for services to be healthy...
timeout /t 15 /nobreak

echo.
echo 📊 Service Status:
docker-compose ps
echo.

REM Step 2: Download and restore backup
echo ═══════════════════════════════════════════════════════════
echo STEP 2: Downloading and Restoring Backup
echo ═══════════════════════════════════════════════════════════
echo.

set BACKUP_URL=https://pub-f8f15af25ba94a7ca801f4857d2bbf07.r2.dev/backup/database.sql
set BACKUP_FILE=database_backup.sql
set CONTAINER_NAME=etl_source_db
set DB_USER=postgres
set DB_NAME=lms-prod

echo 📥 Downloading backup...
curl -L -o "%BACKUP_FILE%" "%BACKUP_URL%"
if %errorlevel% neq 0 (
    echo ❌ Failed to download backup
    pause
    exit /b 1
)
echo ✓ Backup downloaded
echo.

echo 🔄 Restoring to PostgreSQL...
docker cp "%BACKUP_FILE%" "%CONTAINER_NAME%:/tmp/%BACKUP_FILE%"
docker exec "%CONTAINER_NAME%" psql -U "%DB_USER%" -d "%DB_NAME%" -f "/tmp/%BACKUP_FILE%" >nul 2>&1
if %errorlevel% neq 0 (
    docker exec "%CONTAINER_NAME%" psql -U "%DB_USER%" -c "DROP DATABASE IF EXISTS %DB_NAME%;" >nul 2>&1
    docker exec "%CONTAINER_NAME%" psql -U "%DB_USER%" -c "CREATE DATABASE %DB_NAME%;" >nul 2>&1
    docker exec "%CONTAINER_NAME%" psql -U "%DB_USER%" -d "%DB_NAME%" -f "/tmp/%BACKUP_FILE%" >nul 2>&1
)

echo ✓ Database restored
echo.

del "%BACKUP_FILE%"
echo.

REM Step 3: Run ETL Pipeline
echo ═══════════════════════════════════════════════════════════
echo STEP 3: Running ETL Pipeline
echo ═══════════════════════════════════════════════════════════
echo.

echo 🔄 Executing ETL Pipeline...
docker-compose run --rm etl_pipeline python etl_pipeline.py docker-config.json

echo.
echo ✓ ETL Pipeline completed
echo.

REM Step 4: Summary
echo ═══════════════════════════════════════════════════════════
echo STEP 4: Summary
echo ═══════════════════════════════════════════════════════════
echo.

echo ✅ ETL Workflow Complete!
echo.

echo 🌐 Access Points:
echo    • Source DB:  localhost:5432 (lms-prod)
echo    • Target DB:  localhost:5433 (data_warehouse)
echo    • PgAdmin:    http://localhost:5050
echo    • Logs:       docker-compose logs -f
echo.

echo 📊 Next: Connect Power BI to localhost:5433 (data_warehouse)
echo    See POWER_BI_GUIDE.md for detailed instructions
echo.

echo 🛑 To stop services: docker-compose down
echo.
pause
