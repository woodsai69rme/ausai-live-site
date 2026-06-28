# AI CODING & VIBE CODING - COMPLETE ECOSYSTEM GUIDE 2025-2026

## 📋 SYSTEM STATUS

| Component | Status | Location |
|-----------|--------|----------|
| Ollama | ✅ Installed (v0.21.0) | C:\Users\karma\ |
| Node.js | ✅ Installed (v22.19.0) | C:\Program Files\nodejs\ |
| npm | ✅ Installed | Included with Node |
| Python | ✅ Installed (v3.13) | C:\Users\karma\AppData\Roaming\Python\Python313\ |
| Git | ⚠️ Need to verify | Usually C:\Program Files\Git\ |
| pnpm | ⚠️ Not in PATH | Needs setup |

---

## 🚀 QUICK START (3 Methods)

### METHOD 1: OpenClaw (Easiest - Full-Featured Agent)
```bash
# Clone and install
git clone https://github.com/openclaw/openclaw.git
cd openclaw
npm install
npm run build
npx openclaw onboard --install-daemon

# Connect your model
openclaw model set openai/gpt-oss-20b:free  # Via OpenRouter
# OR local model
openclaw model set ollama/llama3.2:3b

# Start agent
openclaw agent --message "build a todo app"
```

### METHOD 2: Hermes Agent (Self-Improving)
```bash
# Install uv (Python package manager)
powershell -Command "irm https://astral.sh/uv/install.ps1 | iex"

# Clone and setup
git clone https://github.com/NousResearch/hermes-agent.git
cd hermes-agent
.\setup-hermes.sh

# Install to PATH
.\venv\Scripts\activate
pip install -e ".[all]"
cd ..

# Run
hermes
hermes model  # Choose provider
```

### METHOD 3: free-code (Claude Code Fork - No Limits)
```bash
curl -fsSL https://raw.githubusercontent.com/paoloanzn/free-code/main/install.sh | bash
# Then:
export ANTHROPIC_API_KEY="sk-ant-..."
free-code
```

---

## 🤖 LOCAL AI MODELS (Via Ollama)

### Essential Models to Pull
```bash
# Daily driver (fast, reliable)
ollama pull llama3.2:3b

# Best coding agent
ollama pull qwen2.5-coder:7b

# Uncensored general intelligence
ollama pull hermes3:8b

# Uncensored best all-rounder
ollama pull qwen3:8b

# Reasoning specialist
ollama pull deepseek-r1:7b

# Vision capable
ollama pull gemma4:27b

# Small & fast
ollama pull phi4:mini
```

### Check Running Models
```bash
ollama list
ollama run llama3.2:3b
```

---

## 🌐 FREE CLOUD MODELS (OpenRouter)

### Setup OpenRouter
1. Go to https://openrouter.ai
2. Sign up (email only, no credit card)
3. Get API key from dashboard
4. Add to environment:

```bash
# PowerShell
$env:OPENROUTER_API_KEY="sk-or-v1-..."

# Or add to ~/.bashrc / ~/.zshrc
echo 'export OPENROUTER_API_KEY="sk-or-v1-..."' >> ~/.bashrc
```

### Top FREE Models via OpenRouter
```bash
# Free models router (auto-selects best available)
openrouter/free

# Specific free models (add :free suffix)
openai/gpt-oss-20b:free      # Best coding
deepseek/deepseek-r1:free    # Reasoning
meta-llama/llama-3.3-70b:free
google/gemini-2.0-flash-exp:free
microsoft/phi-4-reasoning:free
```

### Python Example
```python
from openai import OpenAI

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="YOUR_KEY"
)

response = client.chat.completions.create(
    model="openai/gpt-oss-20b:free",
    messages=[{"role": "user", "content": "Write Python code"}]
)
print(response.choices[0].message.content)
```

---

## 🎨 VIDEO GENERATION

### Local Options
| Tool | Install Command | Hardware |
|------|----------------|----------|
| **ComfyUI** (best overall) | git clone ComfyUI repo | 8-40GB VRAM |
| **Wan 2.1** | Follow Wan repo | 8-16GB VRAM |
| **OpenSora** | Clone opensora repo | 8-16GB VRAM |

### Quickest Setup - ComfyUI + Custom Nodes
```bash
# Windows Portable (recommended)
# Download from: https://github.com/comfyanonymous/ComfyUI/releases
# Extract and run ComfyUI_windows_portable.bat

# Install video nodes
cd ComfyUI/custom_nodes
git clone https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite.git
git clone https://github.com/Kosinkadink/ComfyUI-AnimateDiff-Evolved.git
```

### Cloud (Free Tiers)
- **Luma Dream Machine** - 30 secs/day free
- **Pika** - 750 credits free
- **Kling** - Free tier with watermarks

---

## 🎵 MUSIC GENERATION

### Local Options

#### ACE-Step 1.5 (Best Quality)
```bash
pip install ace-step

# Or GUI via Tadpole Studio
git clone https://github.com/proximasan/tadpole-studio.git
cd tadpole-studio
python start.py
# Opens at http://localhost:3000
```

#### HeartMuse (Gradio UI)
```bash
git clone https://github.com/strnad/HeartMuse.git
cd HeartMuse
./install.sh  # or install.bat on Windows
./run.sh
# Opens at http://localhost:7860
```

### Cloud Options
- **MiniMax Music** - via mmx-cli
- **Suno AI** - 50 credits free/month

---

## 🔧 AGENT SKILLS MARKETPLACE

### Install Skills CLI
```bash
# Install global (may need admin)
npm install -g @lobehub/market-cli

# Or use npx (no install needed)
npx @lobehub/market-cli skills search "react"
```

### Top Skills to Install
```bash
# Development skills
npx skills add vercel-labs/agent-skills
npx skills add microsoft/azure-skills
npx skills add supabase/supabase

# Web scraping
npx skills add firecrawl/firecrawl-cli

# Testing
npx skills add playwright-cli

# Browser automation
npx skills add agent-browser
```

### Browse Skills
- **skills.sh** - https://skills.sh (Vercel's curated marketplace)
- **SkillsMP** - https://skillsmp.com (400K+ skills)

---

## 🔄 AUTOMATION (n8n)

### Docker Setup
```bash
# Requires Docker Desktop
docker pull n8nio/n8n
docker run -d --name n8n -p 5678:5678 -v n8n_data:/home/node/.n8n n8nio/n8n

# Access at http://localhost:5678
# Create workflow, add webhook, add AI Agent node
```

### Without Docker
```bash
npm install -g n8n
n8n start
```

### Example Workflow: AI Research Bot
1. Trigger: Webhook / Cron
2. AI Agent: "Research latest AI news"
3. HTTP Request: Fetch URLs
4. Write File: Save summary
5. Email: Send digest

---

## 📂 CONFIG FILES

### ~/.openclaw/config.yaml
```yaml
llm:
  provider: openrouter
  model: openrouter/free
  api_key: ${OPENROUTER_API_KEY}
  temperature: 0.7
  max_tokens: 4096

tools:
  - search
  - browser
  - code_execution
```

### ~/.hermes/config.yaml
```yaml
model:
  provider: openrouter
  model: openrouter/free
  api_key: ${OPENROUTER_API_KEY}

tools:
  enabled:
    - web_search
    - code_execution
    - memory

gateway:
  platforms:
    telegram: null
    discord: null
```

### ~/.env
```bash
OPENROUTER_API_KEY=sk-or-v1-your-key-here
OPENROUTER_DEFAULT_MODEL=openrouter/free
OLLAMA_MODELS_PATH=~/ollama/models
```

---

## 🎯 RECOMMENDED WORKFLOW

### For Local-Only (No Internet)
1. Install Ollama
2. Pull local models: `ollama pull llama3.2:3b qwen2.5-coder:7b`
3. Run: `ollama run llama3.2:3b`

### For Hybrid (Local + Cloud Fallback)
1. Install OpenClaw
2. Set OpenRouter API key (free tier)
3. Configure fallback to local Ollama
4. Use `openrouter/free` for complex tasks, local for simple

### For Full Automation
1. Install Hermes Agent
2. Set up Telegram gateway
3. Configure scheduled tasks
4. Let it run 24/7 on VPS or home server

---

## 📚 AWESOME LISTS & RESOURCES

### GitHub Repositories
- **awesome-local-llm**: https://github.com/rafska/awesome-local-llm (1.5K ⭐)
- **awesome-local-ai**: https://github.com/janhq/awesome-local-ai (1.9K ⭐)
- **Agent Skills**: https://github.com/heilcheng/awesome-agent-skills
- **LLMs-local**: https://github.com/0xSojalSec/LLMs-local

### Communities
- **Reddit**: r/LocalLLaMA, r/Ollama, r/OpenClaw
- **Discord**: Hermes Agent Discord, OpenClaw Discord
- **YouTube**: Search "local AI coding agent 2025"

### Documentation
- OpenClaw: https://docs.openclaw.ai
- Hermes Agent: https://hermes-agent.nousresearch.com/docs
- OpenRouter: https://openrouter.ai/docs
- Skills.sh: https://skills.sh/docs

---

## ⚠️ TROUBLESHOOTING

### "Command not found" errors
Add to PATH:
```bash
# Windows PowerShell
$env:Path += ";C:\Users\karma\AppData\Local\pnpm"
$env:Path += ";C:\Users\karma\.local\bin"
$env:Path += ";%APPDATA%\Python\Python313\Scripts"
```

Persistent (add to Environment Variables GUI):
```
User Variables → Path → New:
C:\Users\karma\AppData\Local\pnpm
C:\Users\karma\.local\bin
%APPDATA%\Python\Python313\Scripts
```

### npm/pnpm timeout
Use npx instead, or increase timeout:
```bash
npm config set timeout 600000
```

### Ollama model download stuck
Check disk space, GPU drivers, or use `OLLAMA_LLM_LIBRARY=CPU` on low-VRAM systems.

### Windows permissions
Run PowerShell as Administrator for global installs.

---

## 🎬 NEXT STEPS

1. **Test local model**:
   ```bash
   ollama run llama3.2:3b
   ollama run qwen2.5-coder:7b
   ```

2. **Try an agent**:
   ```bash
   cd openclaw
   npx openclaw agent --message "create a hello world in python"
   ```

3. **Install first skill**:
   ```bash
   npx skills add vercel-labs/agent-skills
   ```

4. **Set up automation**:
   Start n8n, create a simple webhook → AI → email workflow

5. **Generate media**:
   - Video: Start ComfyUI, try text-to-video workflow
   - Music: Start Tadpole Studio, generate a 30-second track

---

## 💡 PRO-TIPS

1. **Start small**: Use `llama3.2:3b` first, then scale up
2. **Free tier only**: OpenRouter free models + local Ollama = fully free
3. **Skill economy**: Install only 5-10 top skills, not hundreds
4. **Video locally**: Requires good GPU (RTX 3060+ with 12GB+ VRAM)
5. **Music locally**: ACE-Step needs ~4GB VRAM, runs on most GPUs
6. **n8n on VPS**: For 24/7 automation, use a $5/month VPS
7. **Mix & match**: Use OpenClaw for orchestration, Hermes for memory, local models for privacy

---

## 📞 NEED HELP?

- **OpenClaw Issues**: https://github.com/openclaw/openclaw/issues
- **Hermes Discord**: Check repo for invite
- **Ollama Community**: https://discord.gg/ollama
- **r/LocalLLaMA**: Reddit community

All tools are either MIT/Apache licensed or open-source. Free to use, modify, distribute.
