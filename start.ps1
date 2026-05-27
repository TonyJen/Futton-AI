<#
.SYNOPSIS
    One-command launcher for the Funton AI full-stack application.
.DESCRIPTION
    Activates the root virtual environment, ensures dependencies are installed,
    seeds the database if needed, then starts both the FastAPI backend and
    the React frontend.
#>

Write-Host "🚀 Starting Funton AI..." -ForegroundColor Cyan

# Ensure we're in the project root
$projectRoot = $PSScriptRoot
Set-Location $projectRoot

# --- 1. Activate root virtual environment ---
$venvActivate = ".\.venv\Scripts\Activate.ps1"

if (-not (Test-Path $venvActivate)) {
    Write-Host "❌ Root virtual environment not found at .\.venv" -ForegroundColor Red
    Write-Host "   Please create it first with: python -m venv .venv" -ForegroundColor Yellow
    exit 1
}

Write-Host "Activating virtual environment..." -ForegroundColor Gray
. $venvActivate

# --- 2. Backend setup ---
Write-Host "`n[Backend] Checking dependencies..." -ForegroundColor Yellow
Set-Location "backend"

# Install backend requirements if needed
if (-not (Test-Path ".\.venv")) {
    # We're using the root venv, so we check if key packages exist
    $python = "..\.venv\Scripts\python.exe"
    
    & $python -c "import fastapi; import sqlalchemy; import langgraph" 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Installing backend dependencies..." -ForegroundColor Yellow
        & $python -m pip install -r requirements.txt --quiet
    }
}

# Seed database if it doesn't exist
$dbPath = "data\futon_manufacturing.db"
if (-not (Test-Path $dbPath)) {
    Write-Host "Seeding database (this may take a moment)..." -ForegroundColor Yellow
    & "..\.venv\Scripts\python.exe" -m app.db.seed
}

# Start backend in a new PowerShell window
Write-Host "Starting FastAPI backend on http://localhost:8000 ..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\backend'; ..\.venv\Scripts\Activate.ps1; python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

# --- 3. Frontend setup ---
Write-Host "`n[Frontend] Checking dependencies..." -ForegroundColor Yellow
Set-Location "$projectRoot\frontend"

if (-not (Test-Path "node_modules")) {
    Write-Host "Installing frontend dependencies (this can take a minute)..." -ForegroundColor Yellow
    npm install
}

Write-Host "Starting React frontend on http://localhost:5173 ..." -ForegroundColor Green
npm run dev

# The script will stay here while the frontend is running.
# When you stop the frontend (Ctrl+C), this window will close.
# The backend will continue running in its own window.