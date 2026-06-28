# Free Options - Local AI Without API Keys

## ✅ **UPGRADED** - Latest Enhancements (2026.5.x)

**OpenClaw 2026.5.6** now installed with:
- `/steer` command - Redirect active agents mid-task
- `/side` command - Ask side questions without interrupting
- `file-transfer` plugin - Binary file ops on paired nodes
- Streaming progress mode available
- Grok 4.3 ready (requires xAI setup)

All tools below are **100% free** and work **offline**.

## Quick Reference Card

```
┌─────────────────────────────────────────────┐
│  🤖 CODING AGENTS                           │
├─────────────────────────────────────────────┤
│  OpenClaw  → openclaw agent --agent myagent │
│  Hermes    → cd hermes-agent; uv run ...    │
│  Claude    → claude (if installed)          │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│  🎵 CREATIVE TOOLS                           │
├─────────────────────────────────────────────┤
│  Music     → tadpole-studio\python start.py │
│  Video     → ComfyUI\python main.py         │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│  💬 LOCAL MODELS                             │
├─────────────────────────────────────────────┤
│  Coding    → qwen2.5-coder:latest (4.7GB)  │
│  Fast      → phi3:latest (2.2GB)            │
│  General   → qwen2.5:latest (4.7GB)         │
└─────────────────────────────────────────────┘
```

## Detailed Instructions

### OpenClaw (Autonomous Coding Agent)
```powershell
# Create and run agent
openclaw agents add myagent
openclaw agent --agent myagent

# Example tasks:
# "Build a Flask API with user CRUD"
# "Create a React todo app"
# "Fix this bug in my code"
```

### Hermes Agent (Self-Improving)
```powershell
cd C:\Users\karma\hermes-agent
$env:Path="C:\Users\karma\.local\bin;$env:Path"
uv run python run_agent.py
```

### Ollama Chat
```powershell
ollama run qwen2.5-coder:latest  # Best coding
ollama run phi3:latest             # Fastest
ollama run gemma4:latest           # General purpose
```

### Tadpole Studio (AI Music)
```powershell
cd C:\Users\karma\tadpole-studio
python start.py
# Opens http://localhost:3000
# First run: downloads ~10GB models
```

### ComfyUI (AI Video/Image)
```powershell
cd C:\Users\karma\ComfyUI
python main.py
# Opens http://127.0.0.1:8188
```

## Installed Skills (17 total)

**Matt Pocock Skills:**
- caveman, diagnose, grill-me, grill-with-docs
- improve-codebase-architecture, setup-matt-pocock-skills
- to-issues, to-prd, write-a-skill, zoom-out, find-skills, pinokio

**Vercel Skills:**
- deploy-to-vercel, vercel-react-*, vercel-cli-with-tokens
- web-design-guidelines

## Batch File Launcher

Double-click `START-AI-TOOLS.bat` for menu-driven launcher.