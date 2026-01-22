<div align="center">

<img src="assets/logo.svg" alt="MatrixLLM Logo" width="500"/>

# MatrixLLM

**OpenAI-compatible multi-provider LLM router (OpenRouter-style) with optional relay nodes.**

[![PyPI version](https://badge.fury.io/py/matrixllm.svg)](https://badge.fury.io/py/matrixllm)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-yellow.svg)](https://opensource.org/licenses/Apache-2.0)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

[Quick Start](#-60-second-start) | [Multi-Provider Routing](#-multi-provider-routing) | [Distributed Compute](#-distributed-compute-relay-nodes) | [API Reference](#-api-reference)

</div>

---

## What is MatrixLLM?

> **One gateway. Multiple providers. OpenAI-compatible API.**

MatrixLLM is an **OpenAI-compatible multi-provider LLM router** that lets you:

- **Route to multiple providers** (OpenAI, Anthropic, Gemini, watsonx, local Ollama) through a single API
- **Use namespaced models** like `openai/gpt-4o-mini`, `anthropic/claude-3-5-sonnet-latest`, `google/gemini-1.5-pro`
- **Connect distributed GPU nodes** (laptop, cloud, gaming PC) via relay fabric
- **Teams agents compatibility** - works as a drop-in OpenAI endpoint

```
              Your Apps (OpenAI SDK)
                       |
                       v
               +---------------+
               |   MatrixLLM   |  <-- Single endpoint
               |   Gateway     |
               +---------------+
                 /    |    |    \
                v     v    v     v
           OpenAI  Claude Gemini MatrixNodes
           (compat) (native) (native) (relay/local)
```

---

## Features

### Multi-Provider Routing
- **OpenAI-compatible** upstream (OpenAI, Azure OpenAI, vLLM, OpenRouter)
- **Anthropic** native API (Claude 3.5 Sonnet, Haiku)
- **Google Gemini** native API (Gemini 1.5 Pro/Flash)
- **IBM watsonx.ai** native API (Granite models)
- **Local Ollama** and relay nodes (MatrixNode)

### Routing Modes
- **Prefix routing**: `openai/gpt-4o-mini` routes to OpenAI, `anthropic/claude-3-5-sonnet-latest` to Anthropic
- **Fallback routing**: Tries providers in chain until one succeeds

### Distributed Compute (Relay Nodes)
- **Nodes dial OUT** to your gateway (no port forwarding needed)
- **Works from anywhere**: Colab, Kaggle, behind firewalls
- **Auto load balancing** across healthy nodes

### Enterprise Ready
- **API key authentication**
- **Rate limiting**
- **Request logging** with latency tracking
- **Health checks** and monitoring

---

## 60-Second Start

### Step 1: Install

```bash
pip install matrixllm
```

### Step 2: Configure

```bash
cp .env.example .env
# Edit .env with your provider API keys
```

Example `.env`:
```env
API_KEYS=dev-key-change-me

# Local Ollama (default provider)
OLLAMA_BASE_URL=http://localhost:11434
DEFAULT_MODEL=deepseek-r1

# Add other providers (optional)
OPENAI_COMPAT_BASE_URL=https://api.openai.com/v1
OPENAI_COMPAT_API_KEY=sk-...

ANTHROPIC_API_KEY=sk-ant-...

GEMINI_API_KEY=AIza...
```

### Step 3: Start

```bash
matrixllm start
```

Or with uvicorn:
```bash
uvicorn matrixllm.api.main:app --host 0.0.0.0 --port 11435
```

### Step 4: Use It!

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:11435/v1",
    api_key="dev-key-change-me"
)

# Route to local Ollama (default)
response = client.chat.completions.create(
    model="deepseek-r1",
    messages=[{"role": "user", "content": "Hello!"}]
)

# Route to OpenAI (prefix routing)
response = client.chat.completions.create(
    model="openai/gpt-4o-mini",
    messages=[{"role": "user", "content": "Hello!"}]
)

# Route to Anthropic (prefix routing)
response = client.chat.completions.create(
    model="anthropic/claude-3-5-sonnet-latest",
    messages=[{"role": "user", "content": "Hello!"}]
)

# Route to Gemini (prefix routing)
response = client.chat.completions.create(
    model="google/gemini-1.5-pro",
    messages=[{"role": "user", "content": "Hello!"}]
)
```

---

## Multi-Provider Routing

### Prefix Routing (Default)

Use namespaced model IDs to route to specific providers:

| Model ID | Routes To |
|----------|-----------|
| `deepseek-r1` | Local Ollama / MatrixNode |
| `matrixnode/llama3.1` | MatrixNode (relay/local) |
| `openai/gpt-4o-mini` | OpenAI-compatible endpoint |
| `anthropic/claude-3-5-sonnet-latest` | Anthropic API |
| `google/gemini-1.5-pro` | Google Gemini API |
| `ibm/granite-3-8b-instruct` | IBM watsonx.ai |

### Fallback Routing

Set `ROUTING_MODE=fallback` to try providers in order:

1. MatrixNode (local/relay)
2. OpenAI-compatible
3. Anthropic
4. Google Gemini
5. IBM watsonx

---

## Distributed Compute (Relay Nodes)

Add GPUs from anywhere without port forwarding:

### On Your Gateway

```bash
matrixllm start
# Copy the enrollment token
```

### On Remote GPU/Machine

```bash
pip install matrixllm

matrixllm-node join \
  --control http://YOUR_GATEWAY_IP:11435 \
  --token eyJ0eXAi...
```

The node:
- Auto-installs Ollama if needed
- Auto-downloads models
- **Dials OUT** to your gateway
- Appears as available compute

### Use Cases

- **Gaming PC at home**: Join from anywhere
- **Free Colab GPUs**: No port forwarding needed
- **Cloud instances**: Auto load balancing

---

## API Reference

### Core Endpoints (OpenAI-compatible)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Gateway health + provider count |
| `/v1/chat/completions` | POST | Chat completions |
| `/v1/embeddings` | POST | Generate embeddings |
| `/v1/models` | GET | List available models (from all providers) |

### Admin Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/admin/recent` | GET | Recent request logs |
| `/admin/runtimes` | GET | Connected relay nodes |
| `/admin/enroll` | POST | Create enrollment token |

### Example Requests

```bash
# Health check
curl http://localhost:11435/health

# List models
curl -H "Authorization: Bearer dev-key-change-me" \
  http://localhost:11435/v1/models

# Chat completion
curl -X POST http://localhost:11435/v1/chat/completions \
  -H "Authorization: Bearer dev-key-change-me" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "anthropic/claude-3-5-sonnet-latest",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

---

## Configuration

### Environment Variables

```env
# Server
PORT=11435
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# Authentication
API_KEYS=dev-key-change-me

# Rate Limiting
RATE_LIMIT=60/minute

# Local Ollama
OLLAMA_BASE_URL=http://localhost:11434
DEFAULT_MODEL=deepseek-r1
DEFAULT_EMBED_MODEL=nomic-embed-text

# Routing
ROUTING_MODE=prefix  # prefix | fallback

# Relay Fabric
RELAY_ENABLED=true
ENROLLMENT_SECRET=dev-enroll-change-me
LOCAL_RUNTIME_ENABLED=true

# Providers (add API keys for those you want)
OPENAI_COMPAT_BASE_URL=https://api.openai.com/v1
OPENAI_COMPAT_API_KEY=

ANTHROPIC_API_KEY=

GEMINI_API_KEY=

WATSONX_BASE_URL=https://us-south.ml.cloud.ibm.com
WATSONX_API_KEY=
WATSONX_PROJECT_ID=
```

---

## CLI Commands

### Gateway

```bash
# Start gateway
matrixllm start

# Start with LAN URLs
matrixllm start --lan

# Start with public URL (ngrok)
matrixllm start --share

# Create enrollment token
matrixllm enroll-create --ttl 3600

# Diagnostics
matrixllm doctor
matrixllm models --api-key <key>
matrixllm test-chat "Hello" --api-key <key>
```

### Node

```bash
# Join a gateway
matrixllm-node join --control http://gateway:11435 --token <token>

# Cloud pairing (optional)
matrixllm-node cloud-pair --cloud https://cloud-url.com
matrixllm-node cloud-connect
```

---

## Teams Agents Compatibility

MatrixLLM works as a drop-in replacement for OpenAI endpoints:

```python
# In your Teams agent config
base_url = "https://your-matrixllm-gateway/v1"
api_key = "your-matrixllm-key"
model = "anthropic/claude-3-5-sonnet-latest"  # or any other model
```

Authentication supports:
- `Authorization: Bearer <key>`
- `X-API-Key: <key>`

---

## Development

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black src/matrixllm tests
ruff check src/matrixllm

# Type check
mypy src/matrixllm
```

---

## License

Apache License 2.0 - see [LICENSE](LICENSE)

---

## Built With

- [FastAPI](https://fastapi.tiangolo.com/) - Async web framework
- [httpx](https://www.python-httpx.org/) - Async HTTP client
- [SQLModel](https://sqlmodel.tiangolo.com/) - Database ORM
- [Pydantic](https://pydantic.dev/) - Data validation

---

<div align="center">

**MatrixLLM - Your unified gateway to all LLM providers**

</div>
