# MatrixLLM Installation Guide

Multiple installation methods to fit your workflow.

---

## 🚀 Quick Install (Recommended - Ultra Fast with `uv`)

**Fastest method** using our Makefile + `uv`:

```bash
# Clone the repo
git clone https://github.com/ruslanmv/matrixllm.git
cd matrixllm

# Install uv (if not already installed)
make install-uv

# Install MatrixLLM (ultra-fast with uv)
make install

# Start the gateway
make start
```

**Why `uv`?**
- ⚡ **10-100x faster** than pip
- 🦀 Written in Rust (blazing fast)
- 🔒 Deterministic installs
- 📦 Drop-in replacement for pip

---

## 📦 Installation Methods

### Method 1: Makefile (Recommended)

**Production installation:**
```bash
make install
```

**Development installation (includes testing, linting tools):**
```bash
make install-dev
```

**See all available commands:**
```bash
make help
```

### Method 2: PyPI (Stable Release)

```bash
pip install matrixllm
```

Or with `uv` (faster):
```bash
uv pip install matrixllm
```

### Method 3: From Source (Development)

```bash
# Clone the repository
git clone https://github.com/ruslanmv/matrixllm.git
cd matrixllm

# Install in editable mode
pip install -e .

# Or with development dependencies
pip install -e ".[dev]"
```

### Method 4: Docker (Containerized)

```bash
# Build the image
make docker-build

# Run MatrixLLM
make docker-run
```

---

## 🛠️ Development Setup

For contributors and developers:

```bash
# Install with dev dependencies
make install-dev

# Run tests
make test

# Format code
make format

# Run linter
make lint

# Run all quality checks
make check

# Start in development mode (auto-reload)
make dev
```

---

## ⚡ Installing `uv` (Recommended)

`uv` is an ultra-fast Python package installer written in Rust.

### Linux / macOS

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Or use our Makefile:
```bash
make install-uv
```

### Windows

```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Verify installation

```bash
uv --version
```

---

## 🔧 Configuration

### Create `.env` file

```bash
make env
```

This creates `.env` from `.env.example`. Edit it with your settings:

```env
# API Keys (comma-separated for multiple keys)
API_KEYS=sk-matrixllm-your-key-here

# Ollama connection
OLLAMA_BASE_URL=http://localhost:11434

# Default models
DEFAULT_MODEL=deepseek-r1
DEFAULT_EMBED_MODEL=nomic-embed-text

# Rate limiting
RATE_LIMIT=60/minute

# Server
HOST=0.0.0.0
PORT=11435

# Database (optional - defaults to SQLite)
# DATABASE_URL=postgresql://user:pass@localhost/matrixllm
```

### Auto-generated API key

MatrixLLM auto-generates a secure API key on first run. Check `.env` after starting:

```bash
make start
# Check generated key in .env
cat .env | grep API_KEYS
```

---

## 🚀 Running MatrixLLM

### Standard mode

```bash
make start
```

Or directly:
```bash
matrixllm start
```

### Development mode (auto-reload)

```bash
make dev
```

### With public URL (ngrok tunnel)

```bash
make start-share
```

Or:
```bash
matrixllm start --share
```

### MCP server mode

```bash
make mcp
```

Or:
```bash
matrixllm-mcp
```

---

## 📊 Makefile Commands Reference

### Installation

| Command | Description |
|---------|-------------|
| `make install` | Install MatrixLLM (ultra-fast with uv) |
| `make install-dev` | Install with dev dependencies |
| `make install-pip` | Install with pip (fallback) |
| `make install-uv` | Install uv package manager |
| `make upgrade` | Upgrade all dependencies |

### Development

| Command | Description |
|---------|-------------|
| `make dev` | Start in development mode (auto-reload) |
| `make start` | Start MatrixLLM gateway |
| `make start-share` | Start with public URL (tunnel) |
| `make mcp` | Start MCP server |
| `make env` | Create .env from example |
| `make logs` | View recent request logs |

### Testing & Quality

| Command | Description |
|---------|-------------|
| `make test` | Run all tests |
| `make test-cov` | Run tests with coverage |
| `make test-watch` | Run tests in watch mode |
| `make format` | Format code (black + ruff) |
| `make lint` | Check code quality |
| `make type` | Run type checking |
| `make check` | Run all quality checks |

### Build & Publish

| Command | Description |
|---------|-------------|
| `make build` | Build distribution packages |
| `make publish` | Publish to PyPI |
| `make publish-test` | Publish to TestPyPI |
| `make clean` | Clean build artifacts |

### Utilities

| Command | Description |
|---------|-------------|
| `make version` | Show MatrixLLM version |
| `make info` | Show system information |
| `make docs` | Open documentation |
| `make help` | Show all commands |

---

## 🐍 Python Version Requirements

- **Minimum:** Python 3.10
- **Recommended:** Python 3.11 or 3.12
- **Tested on:** 3.10, 3.11, 3.12

Check your Python version:
```bash
python3 --version
```

---

## 📦 Dependencies

### Core Dependencies

Installed automatically:
- `fastapi>=0.110` - Web framework
- `uvicorn[standard]>=0.27` - ASGI server
- `httpx>=0.26` - Async HTTP client
- `typer>=0.12` - CLI framework
- `rich>=13.7` - Terminal formatting
- `pydantic>=2.6` - Data validation
- `sqlmodel` - Database ORM
- `slowapi` - Rate limiting
- `tenacity>=8.2` - Retry logic

### Development Dependencies

Install with `make install-dev`:
- `pytest>=7.4` - Testing framework
- `pytest-cov>=4.1` - Coverage reporting
- `black>=23.7` - Code formatter
- `ruff>=0.0.280` - Fast linter
- `mypy>=1.4` - Type checker

---

## 🔍 Verification

After installation, verify everything works:

```bash
# Check MatrixLLM is installed
matrixllm --help

# Check version
make version

# Run tests (dev install only)
make test

# Start the gateway
make start
```

You should see:
```
╭─────────────────── 🚀 Gateway Ready ────────────────────╮
│ ✅ MatrixLLM is Online                                  │
│ Model:        deepseek-r1                                │
│ Local API:    http://localhost:11435/v1                 │
│ Health:       http://localhost:11435/health             │
│ Key:          sk-matrixllm-xxxxx                        │
╰──────────────────────────────────────────────────────────╯
```

---

## 🐛 Troubleshooting

### `uv` not found

Install it:
```bash
make install-uv
```

Or manually:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Ollama not installed

MatrixLLM will offer to install it automatically when you run `make start`.

Or install manually:
- **Linux/macOS:** `curl -fsSL https://ollama.com/install.sh | sh`
- **Windows:** Download from https://ollama.com/download

### Model not found

MatrixLLM auto-pulls the default model (`deepseek-r1`) on first run.

To manually pull:
```bash
ollama pull deepseek-r1
```

### Port 11435 already in use

Change the port in `.env`:
```env
PORT=11436
```

Or specify when starting:
```bash
matrixllm start --port 11436
```

### Permission errors

On Linux/macOS, you may need to add execute permissions:
```bash
chmod +x $(which matrixllm)
```

### Import errors

Ensure you're in the correct virtual environment:
```bash
which python3
```

Reinstall:
```bash
make clean
make install-dev
```

---

## 🆘 Getting Help

- **Documentation:** [README.md](README.md)
- **MCP Guide:** [docs/MCP.md](docs/MCP.md)
- **Issues:** https://github.com/ruslanmv/matrixllm/issues
- **Discussions:** https://github.com/ruslanmv/matrixllm/discussions

---

## 🚀 Next Steps

After installation:

1. **Start the gateway:** `make start`
2. **Test with curl:**
   ```bash
   curl http://localhost:11435/health
   ```
3. **Use in your app:**
   ```python
   from openai import OpenAI

   client = OpenAI(
       base_url="http://localhost:11435/v1",
       api_key="your-key-from-env"
   )
   ```

**Happy coding!** 🎉
