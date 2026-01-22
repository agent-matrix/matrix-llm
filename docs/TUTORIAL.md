# MatrixLLM Complete Tutorial

**Your Gateway to Private AI - Run LLMs Everywhere**

---

## 📚 Table of Contents

1. [What is MatrixLLM?](#what-is-matrixllm)
2. [Why Should You Care?](#why-should-you-care)
3. [How It Works](#how-it-works)
4. [Getting Started](#getting-started)
5. [For Gamers & Power Users](#for-gamers--power-users)
6. [For Developers](#for-developers)
7. [Cloud Mode (Multi-User)](#cloud-mode-multi-user)
8. [Advanced Usage](#advanced-usage)
9. [Troubleshooting](#troubleshooting)
10. [FAQ](#faq)

---

## What is MatrixLLM?

**MatrixLLM is your single API gateway to ALL your AI models - running on your laptop, gaming PC, free cloud GPUs, anywhere.**

Think of it as a **smart router for AI**:
- You have models running everywhere (laptop, gaming PC, cloud)
- Every app needs different configs
- **MatrixLLM solves this:** Apps connect to ONE place, MatrixLLM routes to the right compute automatically

### The Problem MatrixLLM Solves

**Before MatrixLLM:**
```
Your App ──❌──> Try to connect to laptop (wrong IP)
Your App ──❌──> Try to connect to gaming PC (firewall)
Your App ──❌──> Try to connect to cloud GPU (expired)
Your App ──❌──> Give up
```

**With MatrixLLM:**
```
Your App ──✅──> MatrixLLM ──> Routes to best available GPU
                  ↓
            (laptop, gaming PC, or cloud - automatically)
```

---

## Why Should You Care?

### For Everyone
- ✅ **Run AI models 100% free** (no OpenAI bills)
- ✅ **Privacy:** Your data never leaves your devices
- ✅ **One API for everything:** Works with ANY app that supports OpenAI
- ✅ **Zero config hell:** Add GPUs without changing your apps

### For Gamers
- ✅ **Use your gaming PC's GPU** for AI when you're not gaming
- ✅ **Access from anywhere:** Use your gaming rig from your laptop, phone, or Quest headset
- ✅ **No port forwarding:** Works behind routers and firewalls
- ✅ **Quest/VR ready:** Run AI in your VR apps with streaming support

### For Developers
- ✅ **OpenAI-compatible API:** Drop-in replacement
- ✅ **Self-healing:** Auto-installs Ollama, auto-downloads models
- ✅ **Multi-node load balancing:** Scale across unlimited GPUs
- ✅ **Free cloud GPUs:** Use Colab/Kaggle without port forwarding

---

## How It Works

### Architecture

```
┌─────────────────────────────────────────────────────┐
│  YOUR APPS (Python, JavaScript, curl, anything)     │
│  Use ONE API: http://localhost:11435/v1             │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│  matrixllm GATEWAY (your computer)                 │
│  - Receives requests                                │
│  - Routes to best GPU                               │
│  - Returns results                                  │
└──────────────┬──────────┬──────────┬────────────────┘
               │          │          │
       ┌───────▼──┐  ┌────▼─────┐  ┌▼──────────┐
       │ Laptop   │  │ Gaming   │  │ Free GPU  │
       │ (local)  │  │ PC       │  │ (Colab)   │
       │ llama3   │  │ deepseek │  │ mixtral   │
       └──────────┘  └──────────┘  └───────────┘
```

### Magic Features

1. **Nodes Dial OUT** (no port forwarding needed)
   - Gaming PC calls Gateway
   - Gateway never calls Gaming PC
   - Works through firewalls automatically

2. **Smart Routing**
   - MatrixLLM picks the fastest available GPU
   - If one fails, automatically tries another
   - Load balances across all your machines

3. **Self-Healing**
   - Detects if Ollama isn't installed → installs it
   - Detects if model missing → downloads it
   - Just works™

---

## Getting Started

### Installation (60 Seconds)

#### Step 1: Install MatrixLLM

```bash
pip install matrixllm
```

That's it! MatrixLLM auto-installs Ollama if needed.

#### Step 2: Start Your Gateway

```bash
matrixllm start
```

**You'll see:**
```
✅ Ollama installed (if needed)
✅ Model downloaded (if needed)
✅ Gateway online at http://localhost:11435

╭─────────────────── 🚀 Gateway Ready ────────────────────╮
│                                                          │
│ ✅ MatrixLLM is Online                                  │
│                                                          │
│ Model:        deepseek-r1                                │
│ Local API:    http://localhost:11435/v1                 │
│ Key:          sk-matrixllm-xY9kL2mN8pQ4rT6vW1zA        │
│                                                          │
│ Send as X-API-Key or Authorization: Bearer ...          │
│                                                          │
╰──────────────────────────────────────────────────────────╯
```

**Save your API key!** You'll need it for all requests.

#### Step 3: Test It!

##### Option A: Python
```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:11435/v1",
    api_key="sk-matrixllm-xY9kL2mN8pQ4rT6vW1zA"  # Use YOUR key
)

response = client.chat.completions.create(
    model="deepseek-r1",
    messages=[{"role": "user", "content": "Explain quantum computing in simple terms"}]
)

print(response.choices[0].message.content)
```

##### Option B: Command Line
```bash
# Using the built-in test command
matrixllm test-chat "Explain quantum computing" --api-key sk-matrixllm-xY9kL2mN8pQ4rT6vW1zA

# Or using curl
curl -X POST http://localhost:11435/v1/chat/completions \
  -H "Authorization: Bearer sk-matrixllm-xY9kL2mN8pQ4rT6vW1zA" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "deepseek-r1",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

### Quick Diagnostic Commands

MatrixLLM includes helpful diagnostic tools:

```bash
# Check if everything is working
matrixllm doctor

# List available models
matrixllm models --api-key YOUR_KEY

# Test chat completion
matrixllm test-chat "Hello AI!" --api-key YOUR_KEY
```

---

## For Gamers & Power Users

### Use Case 1: "Access My Gaming PC's GPU From Anywhere"

#### On Your Gaming PC:

```bash
# 1. Install MatrixLLM on gaming PC
pip install matrixllm

# 2. Start the gateway on gaming PC
matrixllm start --lan

# You'll see your LAN IP:
# LAN API base: http://192.168.1.50:11435/v1
```

#### On Your Laptop/Phone/Quest:

```python
from openai import OpenAI

# Connect to your gaming PC
client = OpenAI(
    base_url="http://192.168.1.50:11435/v1",  # Your gaming PC's IP
    api_key="sk-matrixllm-..."  # Key from gaming PC
)

# Now you're using your gaming PC's GPU from anywhere on your network!
response = client.chat.completions.create(
    model="deepseek-r1",
    messages=[{"role": "user", "content": "Write a story"}]
)
```

### Use Case 2: "Use My Gaming PC When I'm At a Coffee Shop"

You have two options:

#### Option A: Public URL (Quick & Easy)
```bash
# On gaming PC:
matrixllm start --share

# Shows:
# 🌍 Public URL: https://abc123.ngrok.io
```

Now use `https://abc123.ngrok.io/v1` from anywhere in the world!

#### Option B: MatrixLLM Cloud (Advanced - see Cloud section)

### Use Case 3: "VR/Quest AI Apps"

MatrixLLM supports **streaming** in Cloud mode for real-time AI in VR:

```javascript
// In your Quest app (JavaScript)
const response = await fetch('http://YOUR_GATEWAY/v1/chat/completions', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer YOUR_KEY',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    model: 'deepseek-r1',
    messages: [{role: 'user', content: 'Help me in VR'}],
    stream: true  // Enable streaming for real-time responses
  })
});

// Stream tokens as they arrive
const reader = response.body.getReader();
// ... handle streaming
```

**Important:** Enable CORS for browser/VR apps:
```bash
# In .env file:
CORS_ORIGINS=http://localhost:5173,http://192.168.1.100:3000
```

### Use Case 4: "Multiple GPUs (Load Balancing)"

**Scenario:** You have a gaming PC + laptop + friend's PC

#### Step 1: Start Gateway (Main Computer)
```bash
matrixllm start
# Note the "Node join token" shown
```

#### Step 2: Add Gaming PC as Node
```bash
# On gaming PC:
pip install matrixllm

matrixllm-node join \
  --control http://YOUR_GATEWAY_IP:11435 \
  --token eyJ0eXAi...  # Token from step 1
```

#### Step 3: Add Laptop as Node
```bash
# On laptop:
matrixllm-node join \
  --control http://YOUR_GATEWAY_IP:11435 \
  --token eyJ0eXAi...
```

**Now MatrixLLM automatically load-balances across all 3 machines!**

---

## For Developers

### OpenAI SDK Compatibility

MatrixLLM is 100% compatible with OpenAI SDK:

#### Python
```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:11435/v1",
    api_key="sk-matrixllm-..."
)

# Chat
response = client.chat.completions.create(
    model="deepseek-r1",
    messages=[{"role": "user", "content": "Hello"}]
)

# Embeddings
embeddings = client.embeddings.create(
    model="nomic-embed-text",
    input="Hello world"
)
```

#### JavaScript/TypeScript
```javascript
import OpenAI from "openai";

const client = new OpenAI({
  baseURL: "http://localhost:11435/v1",
  apiKey: process.env.matrixllm_KEY
});

const completion = await client.chat.completions.create({
  model: "deepseek-r1",
  messages: [{ role: "user", content: "Hello" }]
});
```

### LangChain Integration
```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    base_url="http://localhost:11435/v1",
    api_key="sk-matrixllm-...",
    model="deepseek-r1"
)

response = llm.invoke("What is the meaning of life?")
```

### Free Cloud GPUs (Colab/Kaggle)

**Scenario:** You want to use free Colab GPUs without port forwarding

#### Step 1: Start Gateway at Home
```bash
matrixllm start --share
# Note the public URL: https://xyz.ngrok.io
```

#### Step 2: In Colab Notebook
```python
!pip install matrixllm

# Get enrollment token from gateway startup output
!matrixllm-node join \
  --control https://xyz.ngrok.io \
  --token YOUR_TOKEN
```

**When Colab disconnects:** Just re-run step 2. Zero config changes needed!

---

## Cloud Mode (Multi-User)

**MatrixLLM Cloud** enables multi-user, multi-device deployments.

### What is Cloud Mode?

| Feature | Local Mode | Cloud Mode |
|---------|------------|------------|
| **Users** | Single (you) | Multiple users |
| **Devices** | Manual management | Per-user ownership |
| **Setup** | Self-hosted | Hosted service |
| **Streaming** | Coming soon | ✅ Available |
| **Authentication** | Tokens | Device pairing |

### How to Join MatrixLLM Cloud

#### Step 1: Pair Your Device

```bash
matrixllm-node cloud-pair --cloud https://your-cloud-url.com
```

**You'll see:**
```
╭─────────────── 🔗 MatrixLLM Cloud Pairing ───────────────╮
│                                                            │
│ User code:     ABC-123                                     │
│ Verify at:     https://your-cloud-url.com/pair            │
│                                                            │
│ Open the verification URL, log in, and enter the code.    │
│ This code expires in ~300 seconds.                        │
│                                                            │
╰────────────────────────────────────────────────────────────╯

⠋ Waiting for approval...
```

#### Step 2: Approve on Cloud Website

1. Open `https://your-cloud-url.com/pair`
2. Log in to your account
3. Enter code: `ABC-123`
4. Click "Approve Device"

#### Step 3: Connect

```bash
matrixllm-node cloud-connect
```

**Done!** Your device is now connected to MatrixLLM Cloud.

### Cloud Advantages

- ✅ **Multi-device:** Use PC + Quest + phone under one account
- ✅ **Team sharing:** Share access with team members
- ✅ **Streaming:** Real-time token-by-token responses
- ✅ **Billing & quotas:** Enterprise features
- ✅ **Web dashboard:** Manage devices via web UI

---

## Advanced Usage

### Custom Models

```bash
# Start with specific model
matrixllm start --model llama3.1

# Ensure model exists on node
matrixllm-node join \
  --control http://gateway:11435 \
  --token TOKEN \
  --ensure-model codellama
```

### LAN Mode (Classroom/Network)

Perfect for sharing with students, family, or LAN party:

```bash
matrixllm start --lan
```

Shows:
```
🌐 LAN Access
LAN API base:    http://192.168.1.50:11435/v1
LAN Health:      http://192.168.1.50:11435/health

Example (with API key):
curl -H 'Authorization: Bearer <API_KEY>' http://192.168.1.50:11435/v1/models
```

**Everyone on your network can now use your gateway!**

### Environment Configuration

Create `.env` file:

```env
# API Keys (comma-separated for multiple)
API_KEYS=sk-matrixllm-abc123,sk-matrixllm-def456

# Server
HOST=0.0.0.0
PORT=11435

# CORS (for browser apps)
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# Models
DEFAULT_MODEL=deepseek-r1
DEFAULT_EMBED_MODEL=nomic-embed-text

# Rate limiting
RATE_LIMIT=60/minute
```

### Multiple Workers (Scalability)

```bash
# Run with 4 worker processes
matrixllm start --workers 4

# Use PostgreSQL for shared state
pip install psycopg2-binary
export DATABASE_URL=postgresql://user:pass@localhost/matrixllm
matrixllm start --workers 8
```

---

## Troubleshooting

### Diagnostic Command

**First, always run:**
```bash
matrixllm doctor
```

Shows:
```
                     MatrixLLM Doctor
┏━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Check               ┃ Result                  ┃
┡━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Ollama /api/tags    │ ✅ OK                   │
│ MatrixLLM /health  │ ✅ OK                   │
│ API_KEYS configured │ ✅ yes                  │
│ CORS_ORIGINS        │ http://localhost:5173   │
│ Auth usage          │ Use Authorization...    │
└─────────────────────┴─────────────────────────┘
```

### Common Issues

#### "Connection refused"
```bash
# Check if MatrixLLM is running
curl http://localhost:11435/health

# If not, start it
matrixllm start
```

#### "Invalid API key"
```bash
# Check your API key
cat .env | grep API_KEYS

# Or generate a new one (starts MatrixLLM)
matrixllm start
```

#### "No models available"
```bash
# List available models
matrixllm models --api-key YOUR_KEY

# If empty, Ollama might not be running
# MatrixLLM auto-starts it, but you can manually:
ollama serve
```

#### "CORS error" (browser apps)
```bash
# Add your app's URL to .env:
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# Restart MatrixLLM
matrixllm start
```

#### Browser shows "Failed to fetch"
- ✅ Check CORS is configured
- ✅ Make sure you're using correct API key
- ✅ Verify URL: `http://localhost:11435/v1` (note `/v1`)

---

## FAQ

### Is MatrixLLM free?
**Yes!** MatrixLLM Local is 100% free and open-source. MatrixLLM Cloud (multi-user) may have pricing in the future.

### Do I need an internet connection?
**No!** Local mode works 100% offline. Cloud mode requires internet only for pairing and relay.

### Is my data private?
**Yes!** In local mode, data never leaves your devices. In cloud mode, Cloud only relays encrypted messages; it doesn't store your data.

### What models can I use?
Any model supported by Ollama:
- deepseek-r1 (reasoning)
- llama3.1 (general)
- codellama (coding)
- mixtral (large context)
- nomic-embed-text (embeddings)

Full list: https://ollama.ai/library

### Can I use this for commercial projects?
**Yes!** Apache 2.0 license. Use it for anything.

### How is this different from Ollama?
MatrixLLM **uses** Ollama but adds:
- Multi-node support
- Load balancing
- OpenAI-compatible API
- Cloud connectivity
- No port forwarding needed

Think: **Ollama = engine, MatrixLLM = smart router**

### Can I use GPU acceleration?
**Yes!** If you have NVIDIA GPU, Ollama automatically uses it. No config needed.

### What if I don't have a GPU?
**Works fine on CPU!** Just slower. Or use MatrixLLM to connect to a friend's GPU / free cloud GPU.

### How many devices can I connect?
**Unlimited!** Connect as many nodes as you want.

### Can I run multiple gateways?
**Yes!** You can run multiple independent gateways. Each has its own API key.

---

## Next Steps

### Beginner
1. ✅ Install: `pip install matrixllm`
2. ✅ Start: `matrixllm start`
3. ✅ Test: `matrixllm test-chat "Hello"`
4. ✅ Use in your apps!

### Intermediate
1. ✅ Set up LAN access: `matrixllm start --lan`
2. ✅ Add your gaming PC as a node
3. ✅ Configure CORS for browser apps
4. ✅ Try different models

### Advanced
1. ✅ Set up multi-node cluster
2. ✅ Use free cloud GPUs (Colab)
3. ✅ Integrate with LangChain/LlamaIndex
4. ✅ Try MatrixLLM Cloud for multi-user

---

## Get Help

- 📖 **Documentation:** https://github.com/ruslanmv/matrixllm
- 🐛 **Report Bug:** https://github.com/ruslanmv/matrixllm/issues
- 💬 **Discussions:** https://github.com/ruslanmv/matrixllm/discussions
- 🎥 **YouTube Tutorial:** [Coming soon]

---

**Made with ❤️ for the local-first AI community**

**Stop paying cloud tokens. Use your own compute.**
