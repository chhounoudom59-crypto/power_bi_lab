# PowerShell Script to Setup Windows Task Scheduler for ETL Pipeline
# Run as Administrator

# Get the directory where this script is located
$ScriptDir = Split-Path -Parent -Path $MyInvocation.MyCommand.Definition

$TaskName = "ETL_Data_Warehouse_Pipeline"
$ScriptPath = Join-Path -Path $ScriptDir -ChildPath "run_etl.bat"
$LogPath = Join-Path -Path $ScriptDir -ChildPath "etl_execution.log"

# Check if running as Administrator
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Host "Please run this script as Administrator!" -ForegroundColor Red
    exit 1
}

# Create scheduled task
Write-Host "Creating scheduled task: $TaskName" -ForegroundColor Green

# Define task action (execute batch file directly)
$TaskAction = New-ScheduledTaskAction -Execute "$ScriptPath"

# Define task trigger (Daily at 2 AM)
$TaskTrigger = New-ScheduledTaskTrigger -Daily -At 2:00AM

# Define task settings
$TaskSettings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RunOnlyIfNetworkAvailable

# Register the task
Register-ScheduledTask -TaskName $TaskName `
    -Action $TaskAction `
    -Trigger $TaskTrigger `
    -Settings $TaskSettings `
    -Description "Automated ETL Pipeline: PostgreSQL to Data Warehouse" `
    -Force

Write-Host "✓ Task created successfully!" -ForegroundColor Green
Write-Host "Task Name: $TaskName" -ForegroundColor Cyan
Write-Host "Schedule: Daily at 2:00 AM" -ForegroundColor Cyan
Write-Host "Script Path: $ScriptPath" -ForegroundColor Cyan
Write-Host "Log File: $LogPath" -ForegroundColor Cyan

# Show task details
Get-ScheduledTask -TaskName $TaskName | Get-ScheduledTaskInfo
