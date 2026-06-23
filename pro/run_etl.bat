@echo off
REM ETL Pipeline Scheduler for Windows Task Scheduler
REM This script is executed by Windows Task Scheduler

setlocal enabledelayedexpansion

REM Set working directory
cd /d "%~dp0"

REM Activate virtual environment (if using venv)
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

REM Run ETL pipeline with config
python etl_pipeline.py config.json

REM Check if successful
if %errorlevel% equ 0 (
    echo [%date% %time%] ETL Pipeline executed successfully >> etl_execution.log
) else (
    echo [%date% %time%] ETL Pipeline FAILED with error code %errorlevel% >> etl_execution.log
)

endlocal
