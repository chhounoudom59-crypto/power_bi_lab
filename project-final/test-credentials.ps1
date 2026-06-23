#!/usr/bin/env pwsh
# PowerBI MCP Server - Quick Setup Test
# Run this in PowerShell to verify your credentials

Write-Host "=== Power BI MCP Server - Credential Test ===" -ForegroundColor Cyan
Write-Host ""

# Check if credentials are set
$clientId = $env:POWERBI_CLIENT_ID
$clientSecret = $env:POWERBI_CLIENT_SECRET
$tenantId = $env:POWERBI_TENANT_ID

if ($clientId) {
    Write-Host "✅ POWERBI_CLIENT_ID is set" -ForegroundColor Green
    Write-Host "   Value: $($clientId.Substring(0, 8))..." -ForegroundColor Gray
} else {
    Write-Host "❌ POWERBI_CLIENT_ID is NOT set" -ForegroundColor Red
}

if ($clientSecret) {
    Write-Host "✅ POWERBI_CLIENT_SECRET is set" -ForegroundColor Green
    Write-Host "   Value: ****** (hidden)" -ForegroundColor Gray
} else {
    Write-Host "❌ POWERBI_CLIENT_SECRET is NOT set" -ForegroundColor Red
}

if ($tenantId) {
    Write-Host "✅ POWERBI_TENANT_ID is set" -ForegroundColor Green
    Write-Host "   Value: $($tenantId.Substring(0, 8))..." -ForegroundColor Gray
} else {
    Write-Host "❌ POWERBI_TENANT_ID is NOT set" -ForegroundColor Red
}

Write-Host ""

if ($clientId -and $clientSecret -and $tenantId) {
    Write-Host "✅ All credentials configured!" -ForegroundColor Green
    Write-Host ""
    Write-Host "You can now:"
    Write-Host "1. Run: node test-client.js" -ForegroundColor Cyan
    Write-Host "2. Use tools: get_powerbi_workspaces, get_workspace_datasets, etc." -ForegroundColor Cyan
} else {
    Write-Host "⚠️  Missing credentials. Follow POWERBI_SETUP.md to configure." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "To set credentials temporarily (current session only):" -ForegroundColor Yellow
    Write-Host '$env:POWERBI_CLIENT_ID = "your-client-id"' -ForegroundColor Gray
    Write-Host '$env:POWERBI_CLIENT_SECRET = "your-client-secret"' -ForegroundColor Gray
    Write-Host '$env:POWERBI_TENANT_ID = "your-tenant-id"' -ForegroundColor Gray
}

Write-Host ""
Write-Host "For permanent setup, create .env file or update PowerShell profile" -ForegroundColor Gray
