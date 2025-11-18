# ForgeAI Setup Script for Windows
Write-Host "🚀 ForgeAI Setup Script" -ForegroundColor Cyan
Write-Host "======================" -ForegroundColor Cyan
Write-Host ""

# Check Python
Write-Host "Checking Python installation..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Python not found. Please install Python 3.9+" -ForegroundColor Red
    exit 1
}
Write-Host "✅ $pythonVersion" -ForegroundColor Green

# Check Node.js
Write-Host "Checking Node.js installation..." -ForegroundColor Yellow
$nodeVersion = node --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Node.js not found. Please install Node.js 18+" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Node.js $nodeVersion" -ForegroundColor Green

# Check Ollama
Write-Host "Checking Ollama installation..." -ForegroundColor Yellow
$ollamaVersion = ollama --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  Ollama not found. Please install from https://ollama.ai/download" -ForegroundColor Yellow
    Write-Host "   After installation, run: ollama pull llama3.1:8b" -ForegroundColor Yellow
} else {
    Write-Host "✅ Ollama installed" -ForegroundColor Green
}

# Setup Backend
Write-Host ""
Write-Host "📦 Setting up backend..." -ForegroundColor Cyan
Set-Location backend

# Create virtual environment if it doesn't exist
if (-not (Test-Path "venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

# Install dependencies
Write-Host "Installing backend dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

Set-Location ..

# Setup Frontend
Write-Host ""
Write-Host "📦 Setting up frontend..." -ForegroundColor Cyan
Set-Location frontend

Write-Host "Installing frontend dependencies..." -ForegroundColor Yellow
npm install

Set-Location ..

Write-Host ""
Write-Host "✅ Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Install Ollama: https://ollama.ai/download" -ForegroundColor White
Write-Host "2. Pull model: ollama pull llama3.1:8b" -ForegroundColor White
Write-Host "3. Set up PostgreSQL database: forgeai" -ForegroundColor White
Write-Host "4. Configure backend/.env with database credentials" -ForegroundColor White
Write-Host "5. Run migrations: cd backend && alembic upgrade head" -ForegroundColor White
Write-Host "6. Start backend: cd backend && uvicorn app.main:app --reload" -ForegroundColor White
Write-Host "7. Start frontend: cd frontend && npm run dev" -ForegroundColor White

