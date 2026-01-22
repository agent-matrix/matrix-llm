# MatrixLLM Makefile
# Cross-platform (Linux/macOS + Windows via Git Bash/MSYS2 + WSL)
# - Uses uv if available, otherwise falls back to pip
# - Automatically creates a virtual environment (.venv) for uv installs
# - Works even if you're on Windows (Git Bash) where venv paths differ

.DEFAULT_GOAL := help

# ================================
# Platform detection + paths
# ================================

# If we're on Windows (MSYS/MinGW/Cygwin/Git Bash), venv scripts live in .venv/Scripts
UNAME_S := $(shell uname -s 2>/dev/null || echo Unknown)
IS_WINDOWS := $(shell echo "$(UNAME_S)" | grep -Eqi 'mingw|msys|cygwin' && echo 1 || echo 0)

ifeq ($(IS_WINDOWS),1)
  VENV_BIN := .venv/Scripts
  VENV_PYTHON := $(VENV_BIN)/python.exe
  PATHSEP := ;
else
  VENV_BIN := .venv/bin
  VENV_PYTHON := $(VENV_BIN)/python3
  PATHSEP := :
endif

# Prefer venv python if it exists, else system python
PYTHON := $(shell if [ -x "$(VENV_PYTHON)" ] || [ -f "$(VENV_PYTHON)" ]; then echo "$(VENV_PYTHON)"; else echo python3; fi)

UV := uv
PIP := pip

# Prefer venv tools if available, otherwise fall back to global
PYTEST := $(shell if [ -x "$(VENV_BIN)/pytest" ] || [ -f "$(VENV_BIN)/pytest.exe" ]; then echo "$(VENV_BIN)/pytest"; else echo pytest; fi)
BLACK  := $(shell if [ -x "$(VENV_BIN)/black"  ] || [ -f "$(VENV_BIN)/black.exe"  ]; then echo "$(VENV_BIN)/black";  else echo black;  fi)
RUFF   := $(shell if [ -x "$(VENV_BIN)/ruff"   ] || [ -f "$(VENV_BIN)/ruff.exe"   ]; then echo "$(VENV_BIN)/ruff";   else echo ruff;   fi)
MYPY   := $(shell if [ -x "$(VENV_BIN)/mypy"   ] || [ -f "$(VENV_BIN)/mypy.exe"   ]; then echo "$(VENV_BIN)/mypy";   else echo mypy;   fi)

SRC_DIR := src/matrixllm
TESTS_DIR := tests
DIST_DIR := dist
BUILD_DIR := build

# Colors for pretty output (works in most terminals; harmless if unsupported)
COLOR_RESET := \033[0m
COLOR_BOLD := \033[1m
COLOR_GREEN := \033[32m
COLOR_BLUE := \033[34m
COLOR_YELLOW := \033[33m
COLOR_CYAN := \033[36m

# ================================
# Internal helpers
# ================================

.PHONY: venv
venv: ## Create .venv (uv venv if uv exists, else python -m venv)
	@echo "$(COLOR_BOLD)$(COLOR_GREEN)Creating virtual environment (.venv)...$(COLOR_RESET)"
	@if [ -d .venv ]; then \
		echo "$(COLOR_CYAN)✓ .venv already exists$(COLOR_RESET)"; \
	elif command -v $(UV) >/dev/null 2>&1; then \
		echo "$(COLOR_CYAN)✓ Using uv venv$(COLOR_RESET)"; \
		$(UV) venv .venv; \
	else \
		echo "$(COLOR_YELLOW)⚠ uv not found; using python -m venv$(COLOR_RESET)"; \
		python3 -m venv .venv || python -m venv .venv; \
	fi
	@echo "$(COLOR_GREEN)✓ Virtual environment ready: .venv$(COLOR_RESET)"

# Fix empty .pth file for editable installs (can happen with uv/pip + src layout)
.PHONY: fix-pth
fix-pth:
	@PTH_FILE=$$(find .venv -type f -name "_matrixllm.pth" 2>/dev/null | head -1); \
	if [ -n "$$PTH_FILE" ]; then \
		if [ ! -s "$$PTH_FILE" ]; then \
			echo "$(COLOR_CYAN)Fixing editable install path...$(COLOR_RESET)"; \
			echo "$$(pwd)/src" > "$$PTH_FILE"; \
		fi; \
	fi

# ================================
# Help Target (Default)
# ================================

.PHONY: help
help: ## Show this help message
	@echo "$(COLOR_BOLD)$(COLOR_CYAN)MatrixLLM - Professional Makefile$(COLOR_RESET)"
	@echo ""
	@echo "$(COLOR_BOLD)Usage:$(COLOR_RESET)"
	@echo "  make $(COLOR_GREEN)<target>$(COLOR_RESET)"
	@echo ""
	@echo "$(COLOR_BOLD)Installation:$(COLOR_RESET)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; /^install|^venv/ {printf "  $(COLOR_GREEN)%-20s$(COLOR_RESET) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(COLOR_BOLD)Development:$(COLOR_RESET)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; /^(dev|start|start-share|mcp|logs|env)/ {printf "  $(COLOR_GREEN)%-20s$(COLOR_RESET) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(COLOR_BOLD)Testing & Quality:$(COLOR_RESET)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; /^(test|test-all|test-integration|test-cov|test-watch|test-fast|format|lint|type|check)/ {printf "  $(COLOR_GREEN)%-20s$(COLOR_RESET) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(COLOR_BOLD)Build & Publish:$(COLOR_RESET)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; /^(build|publish|publish-test|clean|clean-all)/ {printf "  $(COLOR_GREEN)%-20s$(COLOR_RESET) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(COLOR_BOLD)Examples:$(COLOR_RESET)"
	@echo "  $(COLOR_CYAN)make venv$(COLOR_RESET)         # Create .venv"
	@echo "  $(COLOR_CYAN)make install$(COLOR_RESET)      # Install MatrixLLM (uv if available)"
	@echo "  $(COLOR_CYAN)make dev$(COLOR_RESET)          # Start in development mode with auto-reload"
	@echo "  $(COLOR_CYAN)make test$(COLOR_RESET)         # Run unit tests"
	@echo "  $(COLOR_CYAN)make check$(COLOR_RESET)        # Format + lint + type-check"
	@echo ""

# ================================
# Installation Targets
# ================================

.PHONY: install
install: venv ## Install MatrixLLM (ultra-fast with uv)
	@echo "$(COLOR_BOLD)$(COLOR_GREEN)Installing MatrixLLM...$(COLOR_RESET)"
	@if command -v $(UV) >/dev/null 2>&1; then \
		echo "$(COLOR_CYAN)✓ Using uv (inside .venv)$(COLOR_RESET)"; \
		$(UV) pip install -e .; \
	else \
		echo "$(COLOR_YELLOW)⚠ uv not found. Falling back to pip$(COLOR_RESET)"; \
		$(VENV_PYTHON) -m pip install -e .; \
	fi
	@$(MAKE) fix-pth
	@echo "$(COLOR_GREEN)✓ Installation complete!$(COLOR_RESET)"
	@echo "$(COLOR_BOLD)Try: make dev$(COLOR_RESET)"

.PHONY: install-dev
install-dev: venv ## Install with development dependencies (testing, linting)
	@echo "$(COLOR_BOLD)$(COLOR_GREEN)Installing MatrixLLM with dev dependencies...$(COLOR_RESET)"
	@if command -v $(UV) >/dev/null 2>&1; then \
		echo "$(COLOR_CYAN)✓ Using uv (inside .venv)$(COLOR_RESET)"; \
		$(UV) pip install -e ".[dev]"; \
	else \
		echo "$(COLOR_YELLOW)⚠ uv not found. Falling back to pip$(COLOR_RESET)"; \
		$(VENV_PYTHON) -m pip install -e ".[dev]"; \
	fi
	@$(MAKE) fix-pth
	@echo "$(COLOR_GREEN)✓ Development installation complete!$(COLOR_RESET)"

.PHONY: install-pip
install-pip: venv ## Install with pip (fallback if uv unavailable)
	@echo "$(COLOR_BOLD)$(COLOR_GREEN)Installing MatrixLLM with pip...$(COLOR_RESET)"
	@$(VENV_PYTHON) -m pip install -e .
	@$(MAKE) fix-pth
	@echo "$(COLOR_GREEN)✓ Installation complete!$(COLOR_RESET)"

.PHONY: install-uv
install-uv: ## Install uv package manager
	@echo "$(COLOR_BOLD)$(COLOR_GREEN)Installing uv...$(COLOR_RESET)"
	@if command -v $(UV) >/dev/null 2>&1; then \
		echo "$(COLOR_GREEN)✓ uv already installed$(COLOR_RESET)"; \
		$(UV) --version; \
	else \
		echo "$(COLOR_YELLOW)Install uv from: https://astral.sh/uv$(COLOR_RESET)"; \
		echo "$(COLOR_YELLOW)(Use your OS-specific method; curl installer works on Linux/macOS/WSL.)$(COLOR_RESET)"; \
		exit 1; \
	fi

.PHONY: upgrade
upgrade: ## Upgrade all dependencies to latest versions
	@echo "$(COLOR_BOLD)$(COLOR_GREEN)Upgrading dependencies...$(COLOR_RESET)"
	@if command -v $(UV) >/dev/null 2>&1; then \
		$(UV) pip install --upgrade -e ".[dev]"; \
	else \
		$(VENV_PYTHON) -m pip install --upgrade -e ".[dev]"; \
	fi
	@echo "$(COLOR_GREEN)✓ Dependencies upgraded!$(COLOR_RESET)"

# ================================
# Development Targets
# ================================

.PHONY: dev
dev: ## Start MatrixLLM in development mode (auto-reload)
	@echo "$(COLOR_BOLD)$(COLOR_GREEN)Starting MatrixLLM in development mode...$(COLOR_RESET)"
	@echo "$(COLOR_CYAN)Auto-reload enabled. Edit code and see changes instantly.$(COLOR_RESET)"
	$(PYTHON) -m matrixllm.cli.main start --host 0.0.0.0 --port 11435 --reload --log-level info

.PHONY: start
start: env ## Start MatrixLLM gateway
	@echo "$(COLOR_BOLD)$(COLOR_GREEN)Starting MatrixLLM gateway...$(COLOR_RESET)"
	$(PYTHON) -m matrixllm.cli.main start

.PHONY: start-share
start-share: env ## Start MatrixLLM with public URL (ngrok tunnel)
	@echo "$(COLOR_BOLD)$(COLOR_GREEN)Starting MatrixLLM with public sharing...$(COLOR_RESET)"
	$(PYTHON) -m matrixllm.cli.main start --share

.PHONY: mcp
mcp: ## Start MCP server (Model Context Protocol)
	@echo "$(COLOR_BOLD)$(COLOR_GREEN)Starting MatrixLLM MCP server...$(COLOR_RESET)"
	@echo "$(COLOR_CYAN)MCP server running in stdio mode. Connect with MCP clients.$(COLOR_RESET)"
	$(PYTHON) -m matrixllm.mcp.server

.PHONY: env
env: ## Create .env file from example if not exists
	@if [ ! -f .env ]; then \
		if [ -f .env.example ]; then \
			echo "$(COLOR_CYAN)Creating .env from .env.example...$(COLOR_RESET)"; \
			cp .env.example .env; \
			echo "$(COLOR_GREEN)✓ .env created. Edit it with your configuration.$(COLOR_RESET)"; \
		else \
			echo "$(COLOR_YELLOW)⚠ .env.example not found$(COLOR_RESET)"; \
		fi \
	fi

.PHONY: logs
logs: ## View recent request logs
	@echo "$(COLOR_BOLD)$(COLOR_CYAN)Recent MatrixLLM logs:$(COLOR_RESET)"
	@if [ -f matrixllm.db ]; then \
		sqlite3 matrixllm.db "SELECT datetime(timestamp, 'unixepoch'), model, status FROM request_logs ORDER BY timestamp DESC LIMIT 10;"; \
	else \
		echo "$(COLOR_YELLOW)No logs found. Start MatrixLLM to generate logs.$(COLOR_RESET)"; \
	fi

# ================================
# Testing Targets
# ================================

.PHONY: test
test: ## Run unit tests only (fast, no Ollama required)
	@echo "$(COLOR_BOLD)$(COLOR_GREEN)Running unit tests...$(COLOR_RESET)"
	@code=0; \
	$(PYTEST) $(TESTS_DIR) -v --ignore=$(TESTS_DIR)/integration/ || code=$$?; \
	if [ $$code -eq 0 ]; then exit 0; fi; \
	if [ $$code -eq 5 ]; then \
		echo "$(COLOR_YELLOW)⚠ No unit tests collected (only integration tests exist).$(COLOR_RESET)"; \
		exit 0; \
	fi; \
	exit $$code

.PHONY: test-all
test-all: ## Run all tests (unit + integration, requires Ollama)
	@echo "$(COLOR_BOLD)$(COLOR_GREEN)Running all tests (unit + integration)...$(COLOR_RESET)"
	$(PYTEST) $(TESTS_DIR) -v

.PHONY: test-integration
test-integration: ## Run integration tests (requires Ollama running)
	@echo "$(COLOR_BOLD)$(COLOR_GREEN)Running integration tests...$(COLOR_RESET)"
	@echo "$(COLOR_YELLOW)⚠ Requires: Ollama installed and running (ollama serve)$(COLOR_RESET)"
	@echo "$(COLOR_YELLOW)⚠ Requires: Model pulled (e.g., ollama pull tinyllama)$(COLOR_RESET)"
	@if command -v ollama >/dev/null 2>&1; then \
		$(PYTEST) $(TESTS_DIR)/integration/ -v -s; \
	else \
		echo "$(COLOR_YELLOW)Ollama not found. Install from: https://ollama.com$(COLOR_RESET)"; \
		exit 1; \
	fi

.PHONY: test-cov
test-cov: ## Run tests with coverage report
	@echo "$(COLOR_BOLD)$(COLOR_GREEN)Running tests with coverage...$(COLOR_RESET)"
	$(PYTEST) $(TESTS_DIR) --cov=$(SRC_DIR) --cov-report=html --cov-report=term --ignore=$(TESTS_DIR)/integration/
	@echo "$(COLOR_CYAN)Coverage report: htmlcov/index.html$(COLOR_RESET)"

.PHONY: test-watch
test-watch: ## Run tests in watch mode (requires pytest-watch)
	@echo "$(COLOR_BOLD)$(COLOR_GREEN)Running tests in watch mode...$(COLOR_RESET)"
	@if command -v ptw >/dev/null 2>&1; then \
		ptw $(TESTS_DIR) --ignore=$(TESTS_DIR)/integration/; \
	else \
		echo "$(COLOR_YELLOW)pytest-watch not installed. Install with: pip install pytest-watch$(COLOR_RESET)"; \
	fi

.PHONY: test-fast
test-fast: ## Run tests in parallel (faster, requires pytest-xdist)
	@echo "$(COLOR_BOLD)$(COLOR_GREEN)Running tests in parallel...$(COLOR_RESET)"
	$(PYTEST) $(TESTS_DIR) -v -n auto --ignore=$(TESTS_DIR)/integration/

# ================================
# Code Quality Targets
# ================================

.PHONY: format
format: ## Format code with black and ruff
	@echo "$(COLOR_BOLD)$(COLOR_GREEN)Formatting code...$(COLOR_RESET)"
	$(BLACK) $(SRC_DIR) $(TESTS_DIR)
	$(RUFF) check $(SRC_DIR) $(TESTS_DIR) --fix
	@echo "$(COLOR_GREEN)✓ Code formatted!$(COLOR_RESET)"

.PHONY: lint
lint: ## Check code quality with ruff
	@echo "$(COLOR_BOLD)$(COLOR_GREEN)Linting code...$(COLOR_RESET)"
	$(RUFF) check $(SRC_DIR) $(TESTS_DIR)

.PHONY: type
type: ## Run type checking with mypy
	@echo "$(COLOR_BOLD)$(COLOR_GREEN)Type checking...$(COLOR_RESET)"
	$(MYPY) $(SRC_DIR)

.PHONY: check
check: format lint type ## Run all quality checks (format, lint, type)
	@echo "$(COLOR_BOLD)$(COLOR_GREEN)✓ All quality checks passed!$(COLOR_RESET)"

# ================================
# Build & Publish Targets
# ================================

.PHONY: build
build: clean ## Build distribution packages
	@echo "$(COLOR_BOLD)$(COLOR_GREEN)Building MatrixLLM...$(COLOR_RESET)"
	$(PYTHON) -m build
	@echo "$(COLOR_GREEN)✓ Build complete: $(DIST_DIR)/$(COLOR_RESET)"
	@ls -lh $(DIST_DIR) 2>/dev/null || true

.PHONY: publish
publish: build ## Publish to PyPI (requires twine)
	@echo "$(COLOR_BOLD)$(COLOR_GREEN)Publishing to PyPI...$(COLOR_RESET)"
	@echo "$(COLOR_YELLOW)⚠ This will upload to production PyPI. Continue? [y/N]$(COLOR_RESET)"
	@read -r REPLY; \
	if [ "$$REPLY" = "y" ] || [ "$$REPLY" = "Y" ]; then \
		twine upload $(DIST_DIR)/*; \
		echo "$(COLOR_GREEN)✓ Published to PyPI!$(COLOR_RESET)"; \
	else \
		echo "$(COLOR_CYAN)Aborted.$(COLOR_RESET)"; \
	fi

.PHONY: publish-test
publish-test: build ## Publish to TestPyPI (for testing)
	@echo "$(COLOR_BOLD)$(COLOR_GREEN)Publishing to TestPyPI...$(COLOR_RESET)"
	twine upload --repository testpypi $(DIST_DIR)/*
	@echo "$(COLOR_GREEN)✓ Published to TestPyPI!$(COLOR_RESET)"
	@echo "$(COLOR_CYAN)Install with: pip install --index-url https://test.pypi.org/simple/ matrixllm$(COLOR_RESET)"

.PHONY: clean
clean: ## Clean build artifacts and cache files
	@echo "$(COLOR_BOLD)$(COLOR_YELLOW)Cleaning build artifacts...$(COLOR_RESET)"
	rm -rf $(BUILD_DIR) $(DIST_DIR) *.egg-info
	rm -rf .pytest_cache .mypy_cache .ruff_cache htmlcov
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type f -name "*.coverage" -delete 2>/dev/null || true
	@echo "$(COLOR_GREEN)✓ Cleaned!$(COLOR_RESET)"

.PHONY: clean-all
clean-all: clean ## Clean everything including .env and databases
	@echo "$(COLOR_BOLD)$(COLOR_YELLOW)Cleaning everything (including .env and databases)...$(COLOR_RESET)"
	rm -f .env matrixllm.db
	@echo "$(COLOR_GREEN)✓ Deep clean complete!$(COLOR_RESET)"

# ================================
# Docker Targets (Optional)
# ================================

.PHONY: docker-build
docker-build: ## Build Docker image
	@echo "$(COLOR_BOLD)$(COLOR_GREEN)Building Docker image...$(COLOR_RESET)"
	docker build -t matrixllm:latest .
	@echo "$(COLOR_GREEN)✓ Docker image built!$(COLOR_RESET)"

.PHONY: docker-run
docker-run: ## Run MatrixLLM in Docker
	@echo "$(COLOR_BOLD)$(COLOR_GREEN)Running MatrixLLM in Docker...$(COLOR_RESET)"
	docker run -p 11435:11435 --env-file .env matrixllm:latest

# ================================
# Utility Targets
# ================================

.PHONY: version
version: ## Show MatrixLLM version
	@echo "$(COLOR_BOLD)$(COLOR_CYAN)MatrixLLM Version:$(COLOR_RESET)"
	@$(PYTHON) -c "import tomli; print(tomli.load(open('pyproject.toml', 'rb'))['project']['version'])" 2>/dev/null || \
		grep "version" pyproject.toml | head -1 | cut -d'"' -f2

.PHONY: info
info: ## Show system information
	@echo "$(COLOR_BOLD)$(COLOR_CYAN)System Information:$(COLOR_RESET)"
	@echo "OS: $(UNAME_S)"
	@echo "Python: $$($(PYTHON) --version 2>/dev/null || true)"
	@echo "pip: $$($(PIP) --version 2>/dev/null | cut -d' ' -f1-2)"
	@if command -v $(UV) >/dev/null 2>&1; then \
		echo "uv: $$($(UV) --version)"; \
	else \
		echo "uv: $(COLOR_YELLOW)not installed$(COLOR_RESET)"; \
	fi
	@echo ""
	@echo "$(COLOR_BOLD)MatrixLLM:$(COLOR_RESET)"
	@if command -v matrixllm >/dev/null 2>&1; then \
		echo "Status: $(COLOR_GREEN)installed$(COLOR_RESET)"; \
	else \
		echo "Status: $(COLOR_YELLOW)not installed$(COLOR_RESET)"; \
	fi

.PHONY: docs
docs: ## Open documentation in browser
	@echo "$(COLOR_BOLD)$(COLOR_CYAN)Opening documentation...$(COLOR_RESET)"
	@if command -v open >/dev/null 2>&1; then \
		open https://github.com/ruslanmv/matrixllm#readme; \
	elif command -v xdg-open >/dev/null 2>&1; then \
		xdg-open https://github.com/ruslanmv/matrixllm#readme; \
	elif command -v powershell.exe >/dev/null 2>&1; then \
		powershell.exe -NoProfile -Command "Start-Process 'https://github.com/ruslanmv/matrixllm#readme'"; \
	else \
		echo "Visit: https://github.com/ruslanmv/matrixllm#readme"; \
	fi

# ================================
# CI/CD Targets
# ================================

.PHONY: ci
ci: install-dev check test ## Run full CI pipeline (install, check, test)
	@echo "$(COLOR_BOLD)$(COLOR_GREEN)✓ CI pipeline complete!$(COLOR_RESET)"

.PHONY: pre-commit
pre-commit: format lint ## Run pre-commit checks (format + lint)
	@echo "$(COLOR_BOLD)$(COLOR_GREEN)✓ Pre-commit checks passed!$(COLOR_RESET)"

# ================================
# Special Targets
# ================================

.PHONY: all
all: clean install-dev check test build ## Do everything (clean, install, check, test, build)
	@echo "$(COLOR_BOLD)$(COLOR_GREEN)✓ All tasks complete!$(COLOR_RESET)"

# Declare all targets as phony (not files)
.PHONY: help venv fix-pth install install-dev install-pip install-uv upgrade \
        dev start start-share mcp env logs \
        test test-all test-integration test-cov test-watch test-fast \
        format lint type check \
        build publish publish-test clean clean-all \
        docker-build docker-run \
        version info docs \
        ci pre-commit all
