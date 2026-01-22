# 🚀 Quick Start Guide

## The Problem You're Seeing

```bash
curl: (7) Failed to connect to localhost port 11435 after 0 ms: Connection refused
```

**This means:** MatrixLLM is not running. Nothing is listening on port 11435.

---

## ✅ The Solution (Copy & Paste These Commands)

### On Your WSL Terminal:

```bash
# 1. Go to the example folder
cd /mnt/c/workspace/matrixllm/example

# 2. Start ALL services automatically
make start
```

**This will:**
- ✅ Start Ollama on port 11434
- ✅ Pull a model if you don't have one
- ✅ Create/update .env with correct CORS settings
- ✅ Start MatrixLLM on port 11435
- ✅ Verify everything is working

### After `make start` succeeds:

```bash
# 3. Run the demo
make run
```

### Then in your browser:

1. Open: **`http://localhost:3000`** (NOT 127.0.0.1:3000)
2. Click "Connect" (values are auto-filled)
3. Type: "What is the capital of Italy?"
4. Click "Send Prompt"
5. You should see: "Rome" ✅

---

## 🔍 If `make start` Fails

### Check what's failing:

```bash
make debug
```

This will show you exactly what's wrong.

### Common issues:

#### 1. Ollama not installed

**Error:** `Ollama is not installed`

**Fix:**
```bash
curl https://ollama.ai/install.sh | sh
```

#### 2. Python module not found

**Error:** `ModuleNotFoundError: No module named 'matrixllm'`

**Fix:**
```bash
cd /mnt/c/workspace/matrixllm
pip install -e .
```

#### 3. Port already in use

**Error:** `Address already in use`

**Fix:**
```bash
# Find what's using the port
lsof -i :11435
# Kill it
kill -9 <PID>
# Or change the port in .env
```

---

## 📋 Step-by-Step Manual Setup (If Automatic Fails)

### Terminal 1: Start Ollama

```bash
ollama serve
```

Leave this running. You should see:
```
Listening on 127.0.0.1:11434
```

### Terminal 2: Pull a Model (if you haven't)

```bash
ollama pull llama3
```

### Terminal 3: Configure MatrixLLM

```bash
cd /mnt/c/workspace/matrixllm

# Create .env if it doesn't exist
cat > .env << 'EOF'
# Server Configuration
HOST=0.0.0.0
PORT=11435

# Authentication
API_KEYS=dev-key-change-me

# CORS - CRITICAL for browser demo!
CORS_ORIGINS=http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000

# Ollama Backend
OLLAMA_BASE_URL=http://localhost:11434

# Default Model
DEFAULT_MODEL=llama3
EOF
```

### Terminal 4: Start MatrixLLM

```bash
cd /mnt/c/workspace/matrixllm
matrixllm start
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:11435
```

### Verify Services Are Running:

```bash
# Test Ollama
curl http://localhost:11434/api/tags

# Test MatrixLLM
curl http://localhost:11435/health

# Test with API key
curl -H "Authorization: Bearer dev-key-change-me" \
  http://localhost:11435/v1/models
```

All should return JSON responses (not "Connection refused").

### Terminal 5: Run Demo

```bash
cd /mnt/c/workspace/matrixllm/example
make run
```

---

## 🎯 Verify Everything Works

### From WSL terminal:

```bash
# This should work:
curl http://localhost:11435/health

# This should also work:
curl -H "Authorization: Bearer dev-key-change-me" \
  http://localhost:11435/v1/models
```

### From browser:

1. Open `http://localhost:3000` (exact URL!)
2. Click "Connect"
3. Should see "Connected ✅"
4. Send test: "What is the capital of Italy?"
5. Should get response: "Rome"

---

## ⚠️ Critical Points

### 1. URL Must Be EXACT

- ✅ `http://localhost:3000` - Works
- ❌ `http://127.0.0.1:3000` - CORS error
- ❌ `file:///path/to/index.html` - Won't work

### 2. CORS Must Match

Your `.env` must include:
```env
CORS_ORIGINS=http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000
```

If you change it, restart MatrixLLM:
```bash
pkill -f matrixllm
matrixllm start
```

### 3. All 3 Services Must Run

| Service | Port | Check Command |
|---------|------|---------------|
| Ollama | 11434 | `curl http://localhost:11434/api/tags` |
| MatrixLLM | 11435 | `curl http://localhost:11435/health` |
| Demo Client | 3000 | Open in browser |

---

## 🛟 Still Not Working?

### Run full diagnostics:

```bash
cd /mnt/c/workspace/matrixllm/example
make check-setup > ~/diagnostics.txt 2>&1
make debug >> ~/diagnostics.txt 2>&1
cat ~/diagnostics.txt
```

### Check logs:

```bash
# Ollama log
tail -f /tmp/ollama.log

# MatrixLLM log
tail -f /tmp/matrixllm.log
```

### Common error messages:

#### "Failed to fetch"
- MatrixLLM not running → `make start`
- Wrong URL → Use `http://localhost:3000`
- CORS issue → Check `.env` CORS_ORIGINS

#### "Connection refused"
- Service not started → `make start`
- Wrong port → Check `.env` PORT setting
- Firewall blocking → Check WSL firewall

#### "401 Unauthorized"
- Wrong API key → Check `.env` API_KEYS
- Not using Bearer token → Should be automatic

---

## 🎉 Success Checklist

- [ ] `make start` completes without errors
- [ ] `curl http://localhost:11435/health` returns JSON
- [ ] `make run` starts without errors
- [ ] Browser opens `http://localhost:3000` (not 127.0.0.1)
- [ ] Click "Connect" → Status shows "Connected ✅"
- [ ] Send prompt "What is the capital of Italy?"
- [ ] Get response "Rome" or "Roma"

**If all checked ✅ - You're done!** 🎉

---

## 📞 Get More Help

- Run: `make help` - See all available commands
- Read: `TROUBLESHOOTING.md` - Detailed problem solutions
- Check: example/README.md - Full documentation
