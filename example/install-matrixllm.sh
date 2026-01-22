#!/usr/bin/env bash
# MatrixLLM One-Click Installer for Mac/Linux
# This script installs MatrixLLM and creates a default configuration

set -e

echo "================================================"
echo "  MatrixLLM One-Click Installer"
echo "================================================"
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed."
    echo "   Please install Python 3.8 or higher first."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✓ Python $PYTHON_VERSION detected"

# Upgrade pip
echo ""
echo "📦 Upgrading pip..."
python3 -m pip install --upgrade pip --quiet

# Install MatrixLLM
echo ""
echo "📥 Installing MatrixLLM..."
python3 -m pip install matrixllm

# Check if .env already exists
if [ -f ".env" ]; then
    echo ""
    echo "⚠️  .env file already exists. Skipping configuration."
    echo "   If you want to reconfigure, delete .env and run this script again."
else
    echo ""
    echo "⚙️  Creating default .env configuration..."

    cat > .env << 'EOF'
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
EOF

    echo "✓ Configuration file created: .env"
fi

echo ""
echo "================================================"
echo "  ✅ Installation Complete!"
echo "================================================"
echo ""
echo "Next steps:"
echo ""
echo "1. Make sure Ollama is installed and running:"
echo "   → Download from: https://ollama.ai"
echo "   → Run: ollama serve"
echo ""
echo "2. Pull a model (if you haven't already):"
echo "   → ollama pull deepseek-r1"
echo ""
echo "3. Start MatrixLLM:"
echo "   → matrixllm start"
echo ""
echo "4. Open the demo client:"
echo "   → cd example"
echo "   → python3 -m http.server 3000"
echo "   → Open http://localhost:3000 in your browser"
echo ""
echo "For more information, visit:"
echo "https://github.com/ruslanmv/matrixllm"
echo ""
