<#
.SYNOPSIS
    One-command launcher for the Funton AI full-stack application.
.DESCRIPTION
    Uses the root .venv, installs dependencies if needed, seeds the database,
    and starts both the FastAPI backend (with real LLM support for the AI Supervisor)
    and the React frontend.
#>

Write-Host "🚀 Starting Funton AI..." -ForegroundColor Cyan
Write-Host "   (AI Supervisor now uses real LLM - make sure you have API keys in backend/.env)" -ForegroundColor Yellow

$projectRoot = $PSScriptRoot
Set-Location $projectRoot

# --- 1. Root virtual environment ---
$venvPython = ".\.venv\Scripts\python.exe"
$venvActivate = ".\.venv\Scripts\Activate.ps1"

if (-not (Test-Path $venvPython)) {
    Write-Host "❌ Root virtual environment not found!" -ForegroundColor Red
    Write-Host "   Run this first:" -ForegroundColor Yellow
    Write-Host "   python -m venv .venv" -ForegroundColor Yellow
    exit 1
}

# Activate root venv for the current session
. $venvActivate | Out-Null

# --- 2. Backend setup ---
Write-Host "`n[Backend] Preparing..." -ForegroundColor Yellow

Set-Location "backend"

# Install backend dependencies if missing
& $projectRoot\.venv\Scripts\python.exe -c "import fastapi, sqlalchemy, langgraph, langchain" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Installing backend dependencies (this may take a minute)..." -ForegroundColor Yellow
    & $projectRoot\.venv\Scripts\python.exe -m pip install -r requirements.txt --quiet
}

# Seed database if it doesn't exist
$dbPath = "data\futon_manufacturing.db"
if (-not (Test-Path $dbPath)) {
    Write-Host "Seeding database..." -ForegroundColor Yellow
    & $projectRoot\.venv\Scripts\python.exe -m data.seed 2>$null
    if ($LASTEXITCODE -ne 0) {
        # Fallback to root seed script
        & $projectRoot\.venv\Scripts\python.exe "$projectRoot\data\seed.py" 2>$null
    }
}

# Start backend in a dedicated window
Write-Host "Starting FastAPI backend on http://localhost:8000 ..." -ForegroundColor Green
$backendCmd = "cd '$projectRoot\backend'; & '$projectRoot\.venv\Scripts\Activate.ps1'; python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendCmd -WindowStyle Normal

# --- 3. Frontend setup ---
Write-Host "`n[Frontend] Preparing..." -ForegroundColor Yellow
Set-Location "$projectRoot\frontend"

if (-not (Test-Path "node_modules")) {
    Write-Host "Installing frontend dependencies..." -ForegroundColor Yellow
    npm install
}

Write-Host "Starting React frontend on http://localhost:5173 ..." -ForegroundColor Green
npm run dev

# Keep this window open for frontend logs
Write-Host "`n[Info] Backend is running in a separate window." -ForegroundColor Gray
Write-Host "Press Ctrl+C here to stop the frontend (backend will keep running)." -ForegroundColor Gray
