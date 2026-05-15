# AL Dashboard - Railway Deployment Script
# Run this from your Windows PowerShell

Write-Host "🚀 AL Dashboard - Railway Deployment" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Navigate to dashboard directory
Set-Location "C:\Windows\System32\al\al-dashboard"

# Step 1: Check Railway login
Write-Host "Step 1: Checking Railway authentication..." -ForegroundColor Yellow
$railwayWhoami = railway whoami 2>&1
if ($railwayWhoami -match "Unauthorized") {
    Write-Host "  ⚠️  Not logged in. Opening browser for login..." -ForegroundColor Yellow
    railway login
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  ❌ Login failed. Please try again." -ForegroundColor Red
        exit 1
    }
    Write-Host "  ✅ Logged in successfully!" -ForegroundColor Green
} else {
    Write-Host "  ✅ Already logged in as: $railwayWhoami" -ForegroundColor Green
}

Write-Host ""

# Step 2: Initialize project
Write-Host "Step 2: Initializing Railway project..." -ForegroundColor Yellow
if (Test-Path ".railway") {
    Write-Host "  ℹ️  Project already initialized" -ForegroundColor Cyan
} else {
    railway init
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  ❌ Project initialization failed" -ForegroundColor Red
        exit 1
    }
    Write-Host "  ✅ Project initialized!" -ForegroundColor Green
}

Write-Host ""

# Step 3: Deploy
Write-Host "Step 3: Deploying to Railway..." -ForegroundColor Yellow
Write-Host "  ⏳ This may take 2-5 minutes..." -ForegroundColor Cyan

railway up
if ($LASTEXITCODE -ne 0) {
    Write-Host "  ❌ Deployment failed" -ForegroundColor Red
    exit 1
}

Write-Host "  ✅ Deployment successful!" -ForegroundColor Green

Write-Host ""

# Step 4: Get URL
Write-Host "Step 4: Getting your dashboard URL..." -ForegroundColor Yellow
$projectInfo = railway list --json 2>$null
if ($projectInfo) {
    Write-Host "  📊 Project Info:" -ForegroundColor Cyan
    Write-Host "  $projectInfo" -ForegroundColor Gray
} else {
    Write-Host "  ℹ️  Check Railway dashboard for URL:" -ForegroundColor Cyan
    Write-Host "     https://railway.app/dashboard" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "🎉 Deployment Complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "1. Open Railway dashboard: https://railway.app/dashboard" -ForegroundColor White
Write-Host "2. Set environment variables (see DEPLOY_RAILWAY.md)" -ForegroundColor White
Write-Host "3. Open your dashboard URL in browser" -ForegroundColor White
Write-Host ""
