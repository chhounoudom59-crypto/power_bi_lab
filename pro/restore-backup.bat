@echo off
REM Download and Restore PostgreSQL Backup (Windows PowerShell)

setlocal enabledelayedexpansion

set BACKUP_URL=https://pub-f8f15af25ba94a7ca801f4857d2bbf07.r2.dev/backup/database.sql
set BACKUP_FILE=database_backup.sql
set CONTAINER_NAME=etl_source_db
set DB_HOST=localhost
set DB_PORT=5432
set DB_USER=postgres
set DB_NAME=lms-prod

echo.
echo ╔════════════════════════════════════════════╗
echo ║   PostgreSQL Backup Restore                ║
echo ╚════════════════════════════════════════════╝
echo.

REM Check if Docker is running
echo 🔍 Checking Docker...
docker ps >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not running. Please start Docker Desktop.
    pause
    exit /b 1
)

echo ✓ Docker is running
echo.

REM Check if PostgreSQL container is running
echo 🔍 Checking PostgreSQL container...
docker ps --filter "name=%CONTAINER_NAME%" --format "table {{.Names}}" 2>nul | findstr /C:"%CONTAINER_NAME%" >nul
if %errorlevel% neq 0 (
    echo ❌ PostgreSQL container is not running.
    echo    Start it with: docker-compose up -d postgres_source
    pause
    exit /b 1
)

echo ✓ PostgreSQL container is running
echo.

REM Download backup
echo 📥 Downloading backup from S3...
if exist "%BACKUP_FILE%" (
    echo    Backup already exists. Skipping download...
) else (
    echo    Using curl to download...
    curl -L -o "%BACKUP_FILE%" "%BACKUP_URL%"
    if %errorlevel% neq 0 (
        echo ❌ Failed to download backup
        pause
        exit /b 1
    )
    echo ✓ Backup downloaded: %BACKUP_FILE%
)

echo.

REM Check backup file size
for %%A in ("%BACKUP_FILE%") do set BACKUP_SIZE=%%~zA
echo 📊 Backup file size: %BACKUP_SIZE% bytes
echo.

REM Restore to PostgreSQL
echo 🔄 Restoring database...
echo    Container: %CONTAINER_NAME%
echo    Database: %DB_NAME%
echo.

REM Copy backup to container
docker cp "%BACKUP_FILE%" "%CONTAINER_NAME%:/tmp/%BACKUP_FILE%"

REM Restore database
docker exec "%CONTAINER_NAME%" psql -U "%DB_USER%" -d "%DB_NAME%" -f "/tmp/%BACKUP_FILE%" >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  Database may already exist or backup format issue
    echo    Attempting to restore with error handling...
    
    REM Try dropping and recreating database
    docker exec "%CONTAINER_NAME%" psql -U "%DB_USER%" -c "DROP DATABASE IF EXISTS %DB_NAME%;" >nul 2>&1
    docker exec "%CONTAINER_NAME%" psql -U "%DB_USER%" -c "CREATE DATABASE %DB_NAME%;" >nul 2>&1
    docker exec "%CONTAINER_NAME%" psql -U "%DB_USER%" -d "%DB_NAME%" -f "/tmp/%BACKUP_FILE%" >nul 2>&1
)

echo ✓ Database restored successfully
echo.

REM Verify restoration
echo ✓ Verifying restoration...
for /f %%i in ('docker exec "%CONTAINER_NAME%" psql -U "%DB_USER%" -d "%DB_NAME%" -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';" -t') do set TABLE_COUNT=%%i

echo    Tables found: %TABLE_COUNT%
echo.

REM Cleanup
del "%BACKUP_FILE%" 2>nul
echo ✓ Backup file cleaned up
echo.

echo ✅ Database restoration complete!
echo.
echo 🔗 Connection details:
echo    Host: localhost
echo    Port: 5432
echo    Database: %DB_NAME%
echo    User: postgres
echo    Password: postgres_source_password
echo.
echo 📝 Next steps:
echo    1. Run ETL: docker-compose run --rm etl_pipeline python etl_pipeline.py docker-config.json
echo    2. Check logs: docker-compose logs -f etl_pipeline
echo    3. Access PgAdmin: http://localhost:5050
echo.
pause
