# 🚀 MatrixLLM Quick Start Guide

**For Complete Beginners — Get Running in 5 Minutes**

---

## What You'll Do

1. Install MatrixLLM
2. Start your gateway
3. Run your first AI request
4. (Optional) Add a remote GPU

**No prior experience needed!**

---

## Step 1: Install MatrixLLM

Open your terminal and run:

```bash
pip install matrixllm
```

**Windows users:** Open Command Prompt or PowerShell
**Mac/Linux users:** Open Terminal

---

## Step 2: Start Your Gateway

```bash
matrixllm start
```

### What You'll See

MatrixLLM will:
- ✅ Check if Ollama is installed (install it if needed)
- ✅ Download a default AI model (if needed)
- ✅ Start your gateway
- ✅ Give you an API key

**Example output:**
```
✅ Ollama installed successfully!
✅ Model 'deepseek-r1' ready.

╭─────────────────── 🚀 Gateway Ready ────────────────────╮
│ ✅ MatrixLLM is Online                                  │
│                                                          │
│ Local API:    http://localhost:11435/v1                 │
│ Key:          sk-matrixllm-abc123xyz                   │
│                                                          │
│ Node join token:  eyJhbGc...                            │
╰──────────────────────────────────────────────────────────╯
```

**Important:** Save your API key! You'll need it in the next step.

---

## Step 3: Run Your First AI Request

### Option A: Python (Easiest)

Create a file called `test.py`:

```python
from openai import OpenAI

# Use your API key from Step 2
client = OpenAI(
    base_url="http://localhost:11435/v1",
    api_key="sk-matrixllm-abc123xyz"  # ← Your key here
)

# Ask the AI a question
response = client.chat.completions.create(
    model="deepseek-r1",
    messages=[
        {"role": "user", "content": "Explain what Python is in simple terms"}
    ]
)

# Print the answer
print(response.choices[0].message.content)
```

Run it:
```bash
python test.py
```

**You did it!** You just ran an AI model on your own computer! 🎉

### Option B: Test with cURL (Command Line)

```bash
curl -X POST http://localhost:11435/v1/chat/completions \
  -H "Authorization: Bearer sk-matrixllm-abc123xyz" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "deepseek-r1",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

---

## Step 4 (Optional): Add a Remote GPU

Have another computer with a GPU? Add it to your gateway!

### On Your Remote Machine:

```bash
# 1. Install MatrixLLM
pip install matrixllm

# 2. Join your gateway (copy the command from Step 2's output)
matrixllm-node join \
  --control http://YOUR_MAIN_COMPUTER_IP:11435 \
  --token eyJhbGc...
```

**What This Does:**
- Automatically installs Ollama on the remote machine
- Downloads the AI model
- Connects to your gateway
- Shares its GPU power with all your apps

**Your apps don't need to change!** They keep using the same API URL, and MatrixLLM automatically uses both computers.

---

## Common Questions

### "Where is my API key stored?"

In a `.env` file in your current directory. You can open it with:
```bash
cat .env
```

### "How do I use a different model?"

```python
response = client.chat.completions.create(
    model="llama3.1",  # or "mixtral", "codellama", etc.
    messages=[...]
)
```

MatrixLLM will download the model if you don't have it.

### "How do I check if my gateway is running?"

```bash
curl http://localhost:11435/health
```

You should see:
```json
{
  "status": "ok",
  "mode": "gateway",
  "detail": "runtimes=1"
}
```

### "How do I see connected computers?"

```bash
curl -H "X-API-Key: your-key-here" \
     http://localhost:11435/admin/runtimes
```

### "How do I stop the gateway?"

Press `Ctrl+C` in the terminal where it's running.

---

## Next Steps

### Use It in Your Apps

MatrixLLM works with:
- ✅ **OpenAI SDK** (Python, Node.js, etc.)
- ✅ **LangChain** (for AI agents and RAG)
- ✅ **Any tool that supports OpenAI API**

Just point to `http://localhost:11435/v1` instead of OpenAI's URL!

### Share Your Gateway Publicly (Optional)

Want to access your gateway from anywhere?

```bash
matrixllm start --share
```

This gives you a public URL (via ngrok). Great for demos!

**⚠️ Security:** Only share with people you trust, or use the API key for protection.

### Add Free Cloud GPUs

You can add GPUs from:
- Google Colab (free tier)
- Kaggle Notebooks (free tier)
- Any cloud provider

Just run the `matrixllm-node join` command on those machines!

---

## Troubleshooting

### "pip: command not found"

Install Python first:
- **Windows:** https://www.python.org/downloads/
- **Mac:** `brew install python3`
- **Linux:** `sudo apt install python3-pip`

### "Ollama installation failed"

Install Ollama manually: https://ollama.com/download

Then run `matrixllm start` again.

### "Connection refused"

Make sure your gateway is running:
```bash
matrixllm start
```

Keep that terminal open!

### "Model not found"

MatrixLLM will download it automatically. If it fails:
```bash
ollama pull deepseek-r1
```

---

## Need Help?

- 📖 [Full Documentation](../README.md)
- 🐛 [Report Issues](https://github.com/ruslanmv/matrixllm/issues)
- 💬 [Ask Questions](https://github.com/ruslanmv/matrixllm/discussions)

---

## What You've Learned

✅ How to start an AI gateway on your computer
✅ How to run AI requests using the OpenAI API
✅ How to add remote GPUs to your setup
✅ How to check if everything is working

**Congratulations!** You now have your own private AI infrastructure! 🎉

---

**Next:** Check out [EXAMPLES.md](EXAMPLES.md) for real-world use cases and code samples.
