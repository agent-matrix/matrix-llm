.PHONY: help install run test clean check-ollama check-matrixllm check-setup start debug

# Default target
help:
	@echo ""
	@echo "╭────────────────────────────────────────────────────╮"
	@echo "│                                                    │"
	@echo "│  🎯 matrixllm Demo Client - Super Easy! 🎯       │"
	@echo "│                                                    │"
	@echo "╰────────────────────────────────────────────────────╯"
	@echo ""
	@echo "🚀 SUPER QUICK START (RECOMMENDED):"
	@echo ""
	@echo "  ⭐ make start       👈 Start ALL services automatically!"
	@echo "  ⭐ make run         👈 Open the demo"
	@echo ""
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo ""
	@echo "🛠️  Manual Setup (if needed):"
	@echo ""
	@echo "  1️⃣  make install    👈 Install matrixllm"
	@echo "  2️⃣  make run        👈 Start the demo"
	@echo ""
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo ""
	@echo "💡 Other helpful commands:"
	@echo ""
	@echo "  make debug            - Debug connection issues 🔍"
	@echo "  make check-setup      - Check if everything is configured"
	@echo "  make test             - Run connection tests"
	@echo "  make check-ollama     - Is Ollama running?"
	@echo "  make check-matrixllm - Is matrixllm running?"
	@echo "  make clean            - Stop all servers"
	@echo ""
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo ""
	@echo "❓ FIRST TIME USER?"
	@echo ""
	@echo "  Just type:  make start    (starts everything!)"
	@echo "  Then type:  make run      (opens the demo)"
	@echo ""
	@echo "  Having issues? Run: make debug 🔍"
	@echo ""
	@echo "  That's it! Follow the instructions on screen 🎉"
	@echo ""

# Install matrixllm
install:
	@echo "📦 Installing matrixllm..."
	@if python3 -c "import matrixllm" 2>/dev/null; then \
		echo "✓ matrixllm is already installed"; \
		python3 -c "import matrixllm; print(f'Version: {matrixllm.__version__ if hasattr(matrixllm, \"__version__\") else \"installed\"}')" 2>/dev/null || echo "Version: installed"; \
	else \
		echo "Installing matrixllm via pip..."; \
		python3 -m pip install --upgrade pip; \
		python3 -m pip install matrixllm; \
		echo "✓ matrixllm installed successfully"; \
	fi
	@echo ""
	@echo "Next steps:"
	@echo "  1. Ensure Ollama is running (ollama serve)"
	@echo "  2. Pull a model (ollama pull deepseek-r1)"
	@echo "  3. Start matrixllm (matrixllm start)"
	@echo "  4. Run: make run"
	@echo ""

# Run the demo client web server
run:
	@echo ""
	@echo "╭───────────────────────────────────────────────────────╮"
	@echo "│                                                       │"
	@echo "│  🚀 matrixllm Demo Client Starting...               │"
	@echo "│                                                       │"
	@echo "╰───────────────────────────────────────────────────────╯"
	@echo ""
	@echo "🔍 Pre-flight checks..."
	@echo ""
	@# Check if matrixllm is running
	@if ! curl -s --connect-timeout 2 http://localhost:11435/health > /dev/null 2>&1; then \
		echo "❌ ERROR: matrixllm is NOT running!"; \
		echo ""; \
		echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"; \
		echo ""; \
		echo "🚀 QUICK FIX:"; \
		echo ""; \
		echo "   Option 1 (Recommended - Automatic):"; \
		echo "   ════════════════════════════════════"; \
		echo "   make start    👈 Starts Ollama + matrixllm automatically"; \
		echo "   make run      👈 Then run this command again"; \
		echo ""; \
		echo "   Option 2 (Manual):"; \
		echo "   ══════════════════"; \
		echo "   Terminal 1: ollama serve"; \
		echo "   Terminal 2: matrixllm start"; \
		echo "   Terminal 3: make run"; \
		echo ""; \
		echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"; \
		echo ""; \
		echo "💡 Need help? Run: make debug"; \
		echo ""; \
		exit 1; \
	fi
	@# Check if Ollama is running
	@if ! curl -s --connect-timeout 2 http://localhost:11434/api/tags > /dev/null 2>&1; then \
		echo "⚠️  WARNING: Ollama may not be running"; \
		echo "   matrixllm needs Ollama to function properly"; \
		echo ""; \
		echo "   Quick fix: make start"; \
		echo ""; \
	fi
	@echo "✅ matrixllm is running!"
	@echo ""
	@echo "📋 Auto-configuring connection settings..."
	@echo ""
	@if [ -f ../.env ]; then \
		API_KEY=$$(grep "^API_KEYS=" ../.env | cut -d'=' -f2 | cut -d',' -f1 | tr -d ' "' || echo "dev-key-change-me"); \
	else \
		API_KEY="dev-key-change-me"; \
	fi; \
	echo "// Auto-generated config - DO NOT EDIT" > config.js; \
	echo "window.matrixllm_CONFIG = {" >> config.js; \
	echo "  serverUrl: 'http://localhost:11435'," >> config.js; \
	echo "  apiKey: '$$API_KEY'" >> config.js; \
	echo "};" >> config.js; \
	echo "✓ Configuration ready"
	@echo ""
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo ""
	@echo "📋 Connection Details (auto-filled in browser)"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo ""
	@echo "  Server URL:  http://localhost:11435"
	@echo ""
	@if [ -f ../.env ]; then \
		API_KEY=$$(grep "^API_KEYS=" ../.env | cut -d'=' -f2 | cut -d',' -f1 | tr -d ' "' || echo "dev-key-change-me"); \
		echo "  API Key:     $$API_KEY"; \
	else \
		echo "  API Key:     dev-key-change-me"; \
	fi
	@echo ""
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo ""
	@echo "🎯 SUPER EASY MODE ACTIVATED!"
	@echo ""
	@echo "  👉 Open: http://localhost:3000"
	@echo ""
	@echo "  ✨ Values are auto-filled - just click 'Connect'!"
	@echo ""
	@echo "  ⚠️  Use http://localhost:3000 (NOT 127.0.0.1:3000)"
	@echo ""
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo ""
	@echo "⚡ Press Ctrl+C to stop the server"
	@echo ""
	@cd $$(pwd) && python3 -m http.server 3000 --bind 127.0.0.1

# Run comprehensive tests
test: check-ollama check-matrixllm
	@echo ""
	@echo "================================================"
	@echo "  Running Demo Client Tests"
	@echo "================================================"
	@echo ""
	@echo "Testing matrixllm endpoints..."
	@echo ""
	@echo "1. Health Check:"
	@curl -s http://localhost:11435/health | python3 -m json.tool || echo "❌ Health check failed"
	@echo ""
	@echo "2. Models List (requires API key):"
	@curl -s -H "Authorization: Bearer dev-key-change-me" http://localhost:11435/v1/models | python3 -m json.tool || echo "❌ Models check failed"
	@echo ""
	@echo "✅ All tests completed!"
	@echo ""
	@echo "You can now run 'make run' to start the demo client"
	@echo ""

# Check if Ollama is running
check-ollama:
	@echo "Checking Ollama..."
	@if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then \
		echo "✓ Ollama is running"; \
	else \
		echo "❌ Ollama is not running"; \
		echo "   Start it with: ollama serve"; \
		exit 1; \
	fi

# Check if matrixllm is running
check-matrixllm:
	@echo "Checking matrixllm..."
	@if curl -s http://localhost:11435/health > /dev/null 2>&1; then \
		echo "✓ matrixllm is running"; \
	else \
		echo "❌ matrixllm is not running"; \
		echo "   Start it with: matrixllm start"; \
		exit 1; \
	fi

# Check complete setup (with fix for Windows line endings)
check-setup:
	@echo "Sanitizing script..."
	@sed -i 's/\r$$//' check-setup.sh 2>/dev/null || true
	@chmod +x check-setup.sh
	@bash check-setup.sh

# Start all services (with fix for Windows line endings)
start:
	@echo "Sanitizing script..."
	@sed -i 's/\r$$//' start-services.sh 2>/dev/null || true
	@chmod +x start-services.sh
	@bash start-services.sh

# Debug connection issues (with fix for Windows line endings)
debug:
	@echo "Sanitizing script..."
	@sed -i 's/\r$$//' debug-connection.sh 2>/dev/null || true
	@chmod +x debug-connection.sh
	@bash debug-connection.sh

# Clean up
clean:
	@echo "🧹 Cleaning up..."
	@pkill -f "http.server 3000" 2>/dev/null || echo "No web server to stop"
	@rm -f config.js 2>/dev/null || true
	@echo "✓ Cleanup complete"
	@echo ""
