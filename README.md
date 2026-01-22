<div align="center">

<img src="assets/logo.svg" alt="MatrixLLM Logo" width="500"/>

# MatrixLLM

**OpenAI-compatible multi-provider LLM router with optional relay nodes.**

[![PyPI version](https://badge.fury.io/py/matrixllm.svg)](https://badge.fury.io/py/matrixllm)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-yellow.svg)](https://opensource.org/licenses/Apache-2.0)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

[Quick Start](#-quick-start-for-beginners) | [How It Works](#-how-it-works) | [Multi-Provider Routing](#-multi-provider-routing) | [OllaBridge Compatible](#-ollabridge-compatibility)

</div>

---

## What is MatrixLLM?

**MatrixLLM turns your computer into a private OpenAI-compatible API server.**

Instead of sending your data to OpenAI, you can:
- Run AI models **locally** on your own computer
- Connect to **multiple providers** (OpenAI, Anthropic, Google, IBM) through one API
- Use the **same code** you'd use with OpenAI

```
Your App (uses OpenAI SDK)
         |
         v
+------------------+
|    MatrixLLM     |  <-- Runs on localhost:11435
+------------------+
    /     |     \
   v      v      v
Ollama  OpenAI  Anthropic  (etc.)
(local) (cloud) (cloud)
```

---

## Quick Start for Beginners

### What You Need

- **Python 3.10 or newer** ([Download Python](https://www.python.org/downloads/))
- **5 minutes** of your time

### Step 1: Install MatrixLLM

Open your terminal (Command Prompt on Windows, Terminal on Mac/Linux) and run:

```bash
pip install matrixllm
```

### Step 2: Start the Server

```bash
matrixllm start
```

**That's it!** You'll see something like this:

```
╭─────────────────── Gateway Ready ───────────────────╮
│                                                      │
│ ✅ MatrixLLM is Online                              │
│                                                      │
│ Model:        deepseek-r1                           │
│ Local API:    http://localhost:11435/v1             │
│ Health:       http://localhost:11435/health         │
│ Key:          sk-matrixllm-xY9kL2mN8pQ4rT6v        │
│                                                      │
│ Ollabridge compatible:                              │
│   OLLAS_BASE_URL=http://localhost:11435/v1          │
│   OLLAS_API_KEY=sk-matrixllm-xY9kL2mN8pQ4rT6v      │
│   OLLAS_MODEL=deepseek-r1                           │
│                                                      │
╰──────────────────────────────────────────────────────╯
```

**Important:** Copy the API key shown (starts with `sk-matrixllm-`). You'll need it!

### Step 3: Use It in Your Code

```python
from openai import OpenAI

# Connect to your local MatrixLLM server
client = OpenAI(
    base_url="http://localhost:11435/v1",
    api_key="sk-matrixllm-YOUR-KEY-HERE"  # Use the key from Step 2
)

# Send a message to the AI
response = client.chat.completions.create(
    model="deepseek-r1",
    messages=[{"role": "user", "content": "Hello! What can you do?"}]
)

# Print the AI's response
print(response.choices[0].message.content)
```

### Step 4: Test with curl (Optional)

You can also test from the command line:

```bash
curl http://localhost:11435/v1/chat/completions \
  -H "Authorization: Bearer sk-matrixllm-YOUR-KEY-HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "deepseek-r1",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

---

## How It Works

### API Keys Explained

When you run `matrixllm start`, it automatically generates a secure API key:

```
sk-matrixllm-xY9kL2mN8pQ4rT6vW1zA...
```

**What does this mean?**
- `sk-` = "secret key" (standard prefix)
- `matrixllm-` = identifies this as a MatrixLLM key
- `xY9kL2mN...` = random secure characters

**You can set your own key** by creating a `.env` file:

```env
API_KEYS=my-custom-api-key
```

Or use multiple keys (comma-separated):

```env
API_KEYS=key-for-app-1,key-for-app-2,key-for-testing
```

### Authentication Methods

MatrixLLM accepts API keys in two ways:

```python
# Method 1: Authorization header (recommended)
headers = {"Authorization": "Bearer sk-matrixllm-xxx"}

# Method 2: X-API-Key header
headers = {"X-API-Key": "sk-matrixllm-xxx"}
```

Both work identically. The OpenAI SDK uses Method 1 automatically.

### Authentication Modes

MatrixLLM supports three authentication modes for different use cases:

| Mode | Flag | Description |
|------|------|-------------|
| `required` | `--auth required` | **Default.** API key required for all requests |
| `local-trust` | `--auth local-trust` | Localhost requests allowed without key; remote requires key |
| `pairing` | `--auth pairing` | For MatrixShell integration; uses short-lived pairing codes |

**Examples:**

```bash
# Default mode (API key required)
matrixllm start

# Trust localhost connections (no key needed from 127.0.0.1)
matrixllm start --auth local-trust

# Pairing mode for MatrixShell (displays pairing code)
matrixllm start --auth pairing --host 127.0.0.1
```

**Pairing mode** is designed for seamless local integration with [MatrixShell](https://github.com/agent-matrix/matrixshell):

```
╭─────────────────── Gateway Ready ───────────────────╮
│ ✅ MatrixLLM is Online                              │
│                                                      │
│ Auth:          pairing                              │
│ Pairing code:  483-921                              │
│ Enter this code in MatrixShell to pair.             │
╰──────────────────────────────────────────────────────╯
```

---

## OllaBridge Compatibility

MatrixLLM is **fully compatible** with [OllaBridge](https://github.com/ruslanmv/ollabridge). Both projects share the same API interface, making it easy to switch between them or migrate your applications.

### When to Use Each

| Feature | OllaBridge | MatrixLLM |
|---------|------------|-----------|
| **Use Case** | Simple local-only proxy | Multi-provider enterprise router |
| **Ollama Support** | Local only | Local + distributed nodes |
| **Cloud Providers** | No | OpenAI, Anthropic, Google, IBM |
| **Distributed Compute** | No | Yes (relay nodes) |
| **Complexity** | Minimal | Full-featured |

**Choose OllaBridge when:**
- You only need local Ollama models
- You want a lightweight, simple setup
- You don't need cloud provider integration

**Choose MatrixLLM when:**
- You need multi-provider routing (OpenAI, Anthropic, Google, IBM)
- You want distributed compute across multiple machines
- You need enterprise features like load balancing and failover

### Shared Configuration

Both projects use the same:
- Port: `11435`
- API structure: `/v1/chat/completions`, `/v1/embeddings`, `/v1/models`
- Environment variables: `API_KEYS`, `OLLAMA_BASE_URL`, `DEFAULT_MODEL`

### Using OLLAS_* Environment Variables

MatrixLLM supports OllaBridge-style environment variables for seamless migration:

| Variable | Description | Example |
|----------|-------------|---------|
| `OLLAS_API_KEY` | API key (alias for `API_KEYS`) | `sk-matrixllm-xxx` |
| `OLLAS_BASE_URL` | Server URL | `http://localhost:11435/v1` |
| `OLLAS_MODEL` | Default model (alias for `DEFAULT_MODEL`) | `deepseek-r1` |

**Example `.env` file:**

```env
# OllaBridge-compatible configuration
OLLAS_API_KEY=sk-matrixllm-your-key-here
OLLAS_BASE_URL=http://localhost:11435/v1
OLLAS_MODEL=deepseek-r1
```

**Example Python code:**

```python
import os
from openai import OpenAI

# Works with both MatrixLLM and OllaBridge
client = OpenAI(
    base_url=os.getenv("OLLAS_BASE_URL", "http://localhost:11435/v1"),
    api_key=os.getenv("OLLAS_API_KEY", "your-key-here"),
)

response = client.chat.completions.create(
    model=os.getenv("OLLAS_MODEL", "deepseek-r1"),
    messages=[{"role": "user", "content": "Hello!"}]
)
```

### Migration Path

Switch between OllaBridge and MatrixLLM without changing your application code:

```bash
# Start with OllaBridge (simple local setup)
pip install ollabridge
ollabridge start

# Upgrade to MatrixLLM (when you need more features)
pip install matrixllm
matrixllm start
```

Your application code stays exactly the same!

---

## Multi-Provider Routing

MatrixLLM can route requests to different AI providers based on the model name.

### Supported Providers

| Provider | Model Prefix | Example |
|----------|--------------|---------|
| Local Ollama | (no prefix) | `deepseek-r1`, `llama3` |
| OpenAI | `openai/` | `openai/gpt-4o-mini` |
| Anthropic | `anthropic/` | `anthropic/claude-3-5-sonnet-latest` |
| Google Gemini | `google/` | `google/gemini-1.5-pro` |
| IBM watsonx | `ibm/` | `ibm/granite-3-8b-instruct` |

### Setup Multi-Provider

Create a `.env` file with your API keys:

```env
# Your MatrixLLM API key
API_KEYS=my-secure-key

# OpenAI (optional)
OPENAI_COMPAT_BASE_URL=https://api.openai.com/v1
OPENAI_COMPAT_API_KEY=sk-...

# Anthropic (optional)
ANTHROPIC_API_KEY=sk-ant-...

# Google Gemini (optional)
GEMINI_API_KEY=AIza...

# IBM watsonx (optional)
WATSONX_BASE_URL=https://us-south.ml.cloud.ibm.com
WATSONX_API_KEY=...
WATSONX_PROJECT_ID=...
```

### Use Different Providers

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:11435/v1",
    api_key="my-secure-key"
)

# Use local Ollama (default)
response = client.chat.completions.create(
    model="deepseek-r1",
    messages=[{"role": "user", "content": "Hello!"}]
)

# Use OpenAI
response = client.chat.completions.create(
    model="openai/gpt-4o-mini",
    messages=[{"role": "user", "content": "Hello!"}]
)

# Use Anthropic Claude
response = client.chat.completions.create(
    model="anthropic/claude-3-5-sonnet-latest",
    messages=[{"role": "user", "content": "Hello!"}]
)

# Use Google Gemini
response = client.chat.completions.create(
    model="google/gemini-1.5-pro",
    messages=[{"role": "user", "content": "Hello!"}]
)
```

---

## Distributed Compute (Relay Nodes)

Add GPUs from anywhere without port forwarding. Nodes **dial out** to your gateway.

### On Your Gateway (Control Plane)

```bash
matrixllm start
# Note the enrollment token shown
```

### On Remote GPU/Machine (Node)

```bash
pip install matrixllm

matrixllm-node join \
  --control http://YOUR_GATEWAY_IP:11435 \
  --token YOUR_ENROLLMENT_TOKEN
```

### Use Cases

- **Gaming PC at home**: Join your gateway from anywhere
- **Free Colab/Kaggle GPUs**: No port forwarding needed
- **Cloud instances**: Auto load balancing across nodes

---

## API Reference

### Endpoints

| Endpoint | Method | Auth Required | Description |
|----------|--------|---------------|-------------|
| `/health` | GET | No | Check if server is running |
| `/v1/models` | GET | Yes | List available models |
| `/v1/chat/completions` | POST | Yes | Generate chat responses |
| `/v1/embeddings` | POST | Yes | Generate text embeddings |
| `/pair/info` | GET | No* | Get pairing status (pairing mode only) |
| `/pair` | POST | No* | Submit pairing code for token (pairing mode only) |

*Pairing endpoints are only available in `--auth pairing` mode and restricted to localhost by default.

### Quick Examples

```bash
# Check health (no auth needed)
curl http://localhost:11435/health

# List models
curl -H "Authorization: Bearer YOUR-KEY" \
  http://localhost:11435/v1/models

# Chat completion
curl -X POST http://localhost:11435/v1/chat/completions \
  -H "Authorization: Bearer YOUR-KEY" \
  -H "Content-Type: application/json" \
  -d '{"model": "deepseek-r1", "messages": [{"role": "user", "content": "Hi!"}]}'
```

---

## CLI Commands

```bash
# Start the server
matrixllm start

# Start with options
matrixllm start --port 8080 --model llama3

# Start with different auth modes
matrixllm start --auth local-trust    # Trust localhost
matrixllm start --auth pairing        # Pairing mode for MatrixShell

# Show LAN URLs (for other devices on your network)
matrixllm start --lan

# Create public URL (via ngrok)
matrixllm start --share

# Check system health
matrixllm doctor

# List available models
matrixllm models --api-key YOUR-KEY

# Test chat
matrixllm test-chat "Hello!" --api-key YOUR-KEY
```

---

## Configuration Reference

### All Environment Variables

```env
# === Server ===
PORT=11435                    # Server port
HOST=0.0.0.0                  # Bind address
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# === Authentication ===
API_KEYS=dev-key-change-me    # Comma-separated API keys
AUTH_MODE=required            # required | local-trust | pairing

# === Pairing (for MatrixShell) ===
PAIRING_CODE_TTL_SECONDS=120  # Pairing code expiry time
PAIRING_LOCAL_ONLY=true       # Only allow pairing from localhost

# === Rate Limiting ===
RATE_LIMIT=60/minute          # Requests per minute

# === Local Ollama ===
OLLAMA_BASE_URL=http://localhost:11434
DEFAULT_MODEL=deepseek-r1
DEFAULT_EMBED_MODEL=nomic-embed-text

# === Routing ===
ROUTING_MODE=prefix           # prefix | fallback

# === Multi-Provider (Optional) ===
OPENAI_COMPAT_BASE_URL=https://api.openai.com/v1
OPENAI_COMPAT_API_KEY=

ANTHROPIC_API_KEY=

GEMINI_API_KEY=

WATSONX_BASE_URL=https://us-south.ml.cloud.ibm.com
WATSONX_API_KEY=
WATSONX_PROJECT_ID=

# === Relay Fabric ===
RELAY_ENABLED=true
ENROLLMENT_SECRET=dev-enroll-change-me
LOCAL_RUNTIME_ENABLED=true

# === OllaBridge Compatibility ===
# OLLAS_API_KEY=              # Alias for API_KEYS
# OLLAS_BASE_URL=             # Client base URL
# OLLAS_MODEL=                # Alias for DEFAULT_MODEL
```

---

## Troubleshooting

### "Connection refused" error

Make sure the server is running:
```bash
matrixllm start
```

### "Invalid API key" error

Check that you're using the correct key:
```bash
# The key is shown when you start the server
matrixllm start
# Look for: Key: sk-matrixllm-xxxxx
```

### "Model not found" error

1. Check available models:
   ```bash
   curl -H "Authorization: Bearer YOUR-KEY" http://localhost:11435/v1/models
   ```

2. For local models, make sure Ollama is running:
   ```bash
   ollama list
   ```

### Server won't start

Check if another service is using port 11435:
```bash
# Use a different port
matrixllm start --port 8080
```

---

## Development

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
make test

# Format code
make format

# Type check
make typecheck
```

---

## License

Apache License 2.0 - see [LICENSE](LICENSE)

---

## Built With

- [FastAPI](https://fastapi.tiangolo.com/) - Async web framework
- [httpx](https://www.python-httpx.org/) - Async HTTP client
- [Ollama](https://ollama.com/) - Local LLM runtime
- [Pydantic](https://pydantic.dev/) - Data validation

---

<div align="center">

**MatrixLLM - Your unified gateway to all LLM providers**

[Report Bug](https://github.com/agent-matrix/matrix-llm/issues) | [Request Feature](https://github.com/agent-matrix/matrix-llm/issues)

</div>
