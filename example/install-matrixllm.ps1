# MatrixLLM One-Click Installer for Windows (PowerShell)
# This script installs MatrixLLM and creates a default configuration

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  MatrixLLM One-Click Installer" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ $pythonVersion detected" -ForegroundColor Green
} catch {
    Write-Host "❌ Error: Python is not installed." -ForegroundColor Red
    Write-Host "   Please install Python 3.8 or higher from https://www.python.org" -ForegroundColor Yellow
    exit 1
}

# Upgrade pip
Write-Host ""
Write-Host "📦 Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip --quiet

# Install MatrixLLM
Write-Host ""
Write-Host "📥 Installing MatrixLLM..." -ForegroundColor Yellow
python -m pip install matrixllm

# Check if .env already exists
if (Test-Path ".env") {
    Write-Host ""
    Write-Host "⚠️  .env file already exists. Skipping configuration." -ForegroundColor Yellow
    Write-Host "   If you want to reconfigure, delete .env and run this script again." -ForegroundColor Yellow
} else {
    Write-Host ""
    Write-Host "⚙️  Creating default .env configuration..." -ForegroundColor Yellow

    @"
# ---- Server Configuration ----
HOST=0.0.0.0
PORT=11435

# ---- Authentication ----
# IMPORTANT: Change this to a secure key in production!
API_KEYS=dev-key-change-me

# ---- CORS Origins ----
# Add your client URLs here (comma-separated)
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# ---- Ollama Upstream ----
# Default Ollama endpoint
OLLAMA_BASE_URL=http://localhost:11434

# ---- Default Model ----
# Change this to your preferred model
DEFAULT_MODEL=deepseek-r1
"@ | Out-File -Encoding utf8 .env

    Write-Host "✓ Configuration file created: .env" -ForegroundColor Green
}

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  ✅ Installation Complete!" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Make sure Ollama is installed and running:" -ForegroundColor White
Write-Host "   → Download from: https://ollama.ai" -ForegroundColor Cyan
Write-Host "   → Run: ollama serve" -ForegroundColor Cyan
Write-Host ""
Write-Host "2. Pull a model (if you haven't already):" -ForegroundColor White
Write-Host "   → ollama pull deepseek-r1" -ForegroundColor Cyan
Write-Host ""
Write-Host "3. Start MatrixLLM:" -ForegroundColor White
Write-Host "   → matrixllm start" -ForegroundColor Cyan
Write-Host ""
Write-Host "4. Open the demo client:" -ForegroundColor White
Write-Host "   → cd example" -ForegroundColor Cyan
Write-Host "   → python -m http.server 3000" -ForegroundColor Cyan
Write-Host "   → Open http://localhost:3000 in your browser" -ForegroundColor Cyan
Write-Host ""
Write-Host "For more information, visit:" -ForegroundColor White
Write-Host "https://github.com/ruslanmv/matrixllm" -ForegroundColor Cyan
Write-Host ""
