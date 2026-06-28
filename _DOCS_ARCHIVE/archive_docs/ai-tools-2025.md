# Local AI Tools 2025 — Free & Uncensored

This is your comprehensive guide to running AI coding, image, video, and music generation entirely on your local machine — no cloud, no API limits, no censorship. Every tool listed here can run on consumer hardware or a personal server.

---

## 1. Local AI Coding Models (CLI)

These are inference engines and models you run locally to generate code.

### 1.1 Model Runtimes (Install First)

| Tool | Description | Install |
|------|-------------|---------|
| **Ollama** | The most popular local LLM runner. Mac/Linux/Windows. One command to pull and run models. | `curl -fsSL https://ollama.com/install.sh \| sh` |
| **LM Studio** | GUI for discovering, downloading, and running local LLMs. Built-in model chat, API server, and performance tuning. | lmstudio.ai |
| **llama.cpp** | C/C++ inference engine. The backbone of most local LLM tools. High performance, CPU + GPU. | `git clone https://github.com/ggerganov/llama.cpp` |
| **vLLM** | High-throughput inference engine for production-grade local serving. Optimized for GPU. | `pip install vllm` |
| **SGLang** | Fast serving framework for LLMs and vision-language models. Supports Radix Attention. | `pip install sglang` |
| **KoboldCpp** | One-click GGUF inference with GUI. Optimized for low-VRAM GPUs. | GitHub: `github.com/LostRuins/koboldcpp` |
| **Jan** | Open-source offline ChatGPT alternative. Runs 100% locally. | jan.ai |
| **LocalAI** | Open-source alternative to OpenAI API. Supports images, audio, embeddings locally. | `docker run -p 8080:8080 quay.io/mudler/localai` |

### 1.2 Recommended Coding Models

Run these with Ollama or llama.cpp:

| Model | Size | VRAM | Best For |
|-------|------|------|----------|
| **DeepSeek Coder 2** | 7B–33B | 8–24GB | Best open-source coding model. Matches GPT-4 level. |
| **Qwen 3.5 Coder** | 3B–14B | 4–16GB | Alibaba's coding model. Excellent reasoning, 128K context. |
| **Qwen 2.5 Coder** | 14B | 16GB | Strong at codebase understanding, tool use. |
| **CodeLlama** | 7B–34B | 8–32GB | Meta's coding model. Good general purpose. |
| **Hermes 3** | 8B | 6GB | Agent-focused, excellent tool calling, uncensored. |
| **Devstral** | 14B | 16GB | Agentic coding model, excels at SWE-bench. |
| **Phi-4-mini** | 4B | 4GB | Microsoft's lightweight coding model. Fast. |
| **MiniMax-M2** | — | — | SOTA for real-world dev and agents. |

Run with:

```bash
ollama pull deepseek-coder:7b
ollama pull qwen2.5-coder:14b
ollama pull hermes3:8b
```

### 1.3 Uncensored Coding Models

These have safety filters removed:

| Model | Description |
|-------|-------------|
| **DeepSeek Coder Abliterated** | Uncensored version of DeepSeek Coder. |
| **LLaMA-3.2 Dark Champion Abliterated** | DavidAU's abliterated Llama 3.2 128K context. |
| **Dolphin 3.0** | Uncensored, focuses on precision and control. |
| **Qwen 2.5 72B Instruct Abliterated** | Community abliterated Qwen, fully unrestricted. |
| **Nous Hermes 2** | Mixtral 8x7B version, excellent at instructions. |

---

## 2. AI Coding Agents (CLI & GUI)

These are autonomous agents that can edit files, run commands, and execute multi-step tasks on your codebase.

### 2.1 Major Coding Agents

| Agent | Stars | Description | Install |
|-------|-------|-------------|---------|
| **OpenCLAW** | 346k | The most popular local AI agent. Multi-channel (Telegram, Discord, Slack, WhatsApp), persistent memory, skills, MCP, cron scheduling. | `pip install openclaw` |
| **Hermes Agent** (Nous Research) | 95k | Self-improving agent with 3-layer memory, auto-skill creation, SQLite FTS5 search, subagents, MCP. 30+ native tools. Migrates from OpenCLAW automatically. | `curl -fsSL https://raw.githubusercontent.com/nousresearch/hermes-agent/main/install.sh \| bash` |
| **Claude Code** (Anthropic) | — | Anthropic's CLI coding agent. Deep codebase understanding. Requires API key (free tier available). | `npm install -g @anthropic-ai/claude-code` |
| **OpenCode** | 136k | Provider-agnostic TUI coding agent. MCP, multiple LLM backends, IDE extensions. | `pip install opencode` |
| **Codex CLI** (OpenAI) | — | Lightweight CLI coding agent. Native OpenAI backend. | `npm i -g @openai/codex` |
| **Qwen Code** (Alibaba) | — | Fork of Gemini CLI. 1000 free requests/day via Qwen OAuth. VS Code, Zed, JetBrains integration. | `npm i -g @qwen-code/qwen-code` |
| **Aider** | — | AI pair programming in terminal. Works with local models via Ollama/LiteLLM. | `pip install aider-chat` |
| **OpenHands** (formerly OpenDevin) | 70k | AI-driven development platform. Runs in sandboxed environment, supports many backends. | `pip install openhands` |
| **Cline** (VS Code extension) | — | Autonomous coding agent in your IDE. Creates/edits files, runs commands, uses browser. | VS Code Marketplace |
| **Continue.dev** | — | Open-source IDE extension. Creates custom AI code assistants. | VS Code Marketplace |
| **Goose** (Block) | — | Open-source extensible AI agent. Linux Foundation, MCP-native. | `pip install goose` |
| **Roo-Code** (VS Code) | — | AI dev team in your editor. Multiple specialized agents. | VS Code Marketplace |
| **Void** | — | Open-source Cursor alternative. Use AI agents on your codebase, checkpoint changes. | GitHub void |
| **Localforge** | — | Free local Codex AI GUI for any LLM. Multi-file tasks, visual diffs. | localforge.dev |

### 2.2 Comparison Table

| Feature | OpenCLAW | Hermes | Claude Code | Codex CLI | OpenCode |
|---------|----------|--------|------------|-----------|----------|
| **Persistent Memory** | ✅ | ✅ | ❌ | ❌ | ❌ |
| **MCP Support** | ✅ | ✅ | ❌ | ❌ | ✅ |
| **Skills System** | ✅ | ✅ 80+ | ❌ | ❌ | ✅ |
| **Messaging Gateway** | 20+ channels | 20+ channels | CLI only | CLI only | CLI only |
| **Sub-agents** | ✅ | ✅ 3 parallel | ❌ | ❌ | ❌ |
| **Self-improving** | ❌ | ✅ | ❌ | ❌ | ❌ |
| **Local Models** | Ollama | Ollama | ❌ | ❌ | Ollama |
| **Open Source** | ✅ | ✅ | ❌ | ❌ | ✅ |

### 2.3 Smaller / Niche Agents

| Agent | Description |
|-------|-------------|
| **Open Codex** | CLI for natural language → shell commands. Supports Ollama. |
| **Serena** | Open-source coding agent toolkit. Semantic search, runs locally. |
| **Kilocode** | Open source AI coding assistant. Planning, building, fixing code. |
| **Crush** | Glamorous AI coding agent for terminal. |
| **99** | Neovim AI agent. |
| **ProxyAI** | Open-source copilot for JetBrains IDEs. |
| **Toad** | Unified interface for AI in terminal. |
| **Vibe** | Minimal CLI coding agent by Mistral. |

---

## 3. Skills & Agent Extensions

Skills are reusable capability packages that extend what agents can do.

### 3.1 Skills Marketplaces

| Marketplace | Skills Count | Description |
|-------------|--------------|-------------|
| **skills.sh** | 107,000+ | The main directory. Open standard, works with Claude Code, Cursor, Codex, more. |
| **SkillsGate** | 91,000+ | Visual skill manager. Install to 18+ agents with one click. `npx skillsgate` |
| **AgentSkills.to** | 24,000+ | Production-ready skills. Claude Code, Codex CLI, Cursor, Amp. |
| **SkillDB** | 5,877+ | Agent auto-discovers skills via MCP. Claude Code, Cursor, Windsurf. |
| **mdskills.ai** | — | Community layer. Skill Advisor reviews for quality. |
| **SkillsMK** | 14,896 | Development, AI/ML, productivity categories. |
| **SkillHub** | — | One-line install. `npx skillhub install owner/repo` |

### 3.2 Installing Skills

```bash
# General
npx skills add owner/repo

# SkillsGate (visual manager)
npx skillsgate

# SkillHub
npx skillhub install owner/repo

# SkillDB (auto-discovery)
npx skilldb use auto
```

### 3.3 Top Skills

| Skill | Installs | Description |
|-------|----------|-------------|
| **find-skills** (vercel-labs) | 576K | Discover and install related skills. |
| **vercel-labs/agent-skills** | 19K | Vercel's official collection. |
| **azure-ai** | — | Azure AI integration. |
| **n8n-skills** (haunchen) | — | n8n workflow automation. 545 nodes covered. |
| **pdf** (anthropics) | — | PDF handling for agents. |
| **mcp-developer** | — | Model Context Protocol specialist. |

---

## 4. Multi-Agent Orchestration

Frameworks for running teams of AI agents together.

| Tool | Description |
|------|-------------|
| **Paperclip** | Open-source OS for multi-agent companies. Coordinates OpenCLAW, Hermes, Claude, custom agents. Node.js + React dashboard. |
| **SwarmClaw** | Self-hosted runtime for multi-agent orchestration. Heartbeats, schedules, delegation, memory, skills. Electron + CLI. |
| **Maestro** | Framework for Claude Opus to orchestrate subagents. Multi-agent workflows. |
| **Dorothy** | Desktop app orchestrating Claude Code, Codex, Gemini simultaneously. Kanban, automations, MCP. |
| **Aeon** | Runs unattended via GitHub Actions. Self-healing skills, 90+ built-in skills, MCP + A2A. |
| **Hive** | Goal-driven self-improving agents. Auto-generates agent graphs with evolution loops. |
| **MiroShark** | Swarm-intelligence engine. Simulate Twitter, Reddit, prediction markets with hundreds of agents. |

---

## 5. Automation & Workflow (n8n)

### 5.1 n8n — Self-Hosted Workflow Automation

**n8n** is a free, open-source workflow automation platform — self-hosted Zapier alternative.

- **Self-hosted**: Free and unlimited.
- **Cloud**: Starts at $20/month.
- **400+ integrations**: Slack, Gmail, Airtable, Stripe, GitHub, etc.
- **Code nodes**: Full JavaScript/Python support.
- **AI capabilities**: Built-in LangChain integration, AI agent workflows.

**Install**:

```bash
# Docker
docker run -it --name n8n -p 5678:5678 n8nio/n8n

# Or npm
npm install n8n -g
n8n start
```

**AI Agent Setup in n8n**:

1. Add Agent node → connects to LangChain.
2. Configure LLM (use Ollama, OpenAI, Anthropic).
3. Add tools: HTTP Request, Webhook, custom code.
4. Connect to your data sources.

### 5.2 n8n CLI & Skills

| Tool | Description |
|------|-------------|
| **n8n-cli** (Gladium-AI) | AI-agent-friendly CLI. Node-level operations on n8n REST API. |
| **@n8n-as-code/skills** | AI skill layer for coding agents. 600+ nodes, 7000+ workflows indexed. |
| **n8n Boy** | Chrome extension. Natural language → n8n workflow nodes. Uses your OpenAI/Gemini key. |

Install n8n skills for Claude/Codex:

```bash
curl -fsSL https://raw.githubusercontent.com/Gladium-AI/n8n-cli/main/install-skill.sh | sh
```

---

## 6. Image Generation (Local)

### 6.1 Top Local Image Models

| Model | Description | VRAM |
|-------|-------------|------|
| **HunyuanImage-3.0** (Tencent) | 80B MoE, best open-source T2I. Comparable to DALL-E 4. | 3×80GB (full) |
| **HunyuanImage-3.0-Instruct-Distil** | Distilled version. 8 steps sampling. | 8×80GB |
| **FLUX.1** | State-of-the-art open image generation. | 16GB+ |
| **Stable Diffusion 3.5** | Medium/large/turbo variants. | 8–16GB |
| **Stable Diffusion XL (SDXL)** | Standard for open image generation. | 8–12GB |
| **PixArt** | DiT-based text-to-image. Fast. | 12GB+ |

### 6.2 Running Image Models

| Tool | Description |
|------|-------------|
| **ComfyUI** | The most powerful modular diffusion GUI. Node-based, API + backend. Supports all major models. |
| **Diffusers** (HuggingFace) | Python library for running diffusion models. |
| **WebUI** (AUTOMATIC1111) | Popular web interface for Stable Diffusion. |

**Install ComfyUI**:

```bash
git clone https://github.com/comfyanonymous/ComfyUI
pip install -r requirements.txt
# Run
python main.py
```

**HuggingFace Example**:

```python
from diffusers import HunyuanImagePipeline
pipe = HunyuanImagePipeline.from_pretrained("Tencent-Hunyuan/HunyuanImage-3.0")
pipe.to("cuda")
image = pipe("a cat sitting on a couch").images[0]
```

---

## 7. Video Generation (Local)

### 7.1 Local Video Models

| Model | Description | VRAM |
|-------|-------------|------|
| **Wan2.1** | Text-to-video, image-to-video, text-to-image, video-to-audio. 14B and 1.3B variants. | 16GB+ (14B) |
| **LTX-2** (Lightricks) | First open-source 4K 50FPS video + audio generation. 19B parameters. 6–20 sec clips. | 24GB+ |
| **OpenSora** | Open-source Sora-like text-to-video. 2–16 seconds. | 12GB+ |
| **Allegro** (Rhymes AI) | Text-to-video, 6 seconds @ 720p, 15 FPS. | 9GB (with offload) |
| **Ovi** (Character AI) | Video + audio simultaneous generation. 10s @ 960×960. | 32GB (with fp8) |

### 7.2 Running Video Models

**Wan2.1 (recommended)**:

```bash
git clone https://github.com/Wan-Video/Wan2.1
cd Wan2.1
# Run T2V 14B
python infer/t2v.py --prompt "your prompt" --model_path Wan2.1-T2V-14B
```

**ComfyUI Integration**: Wan2.1 and LTX-2 have ComfyUI nodes available.

---

## 8. Music Generation (Local)

### 8.1 Top Music Models

| Model | Description | Speed (A100) |
|-------|-------------|---------------|
| **ACE-Step 1.5** | Best open-source music generation. Full songs with vocals. LoRA personalization. | <2 sec/song |
| **ACE-Step 1.5 XL** | 4B DiT. Higher quality. | ~2 sec/song |
| **Allegro** | Text-to-music. High quality. | — |
| **MusicGen** (Meta) | Text/melody to music. | — |
| **Riffusion** | Music generation via stable diffusion. | — |

### 8.2 ACE-Step Studio (Recommended)

ACE-Step Studio is a complete Windows app for local music generation:

- **Full songs with vocals**: Up to 8 minutes, any language/genre.
- **AI lyrics & style**: LLM generates lyrics.
- **Music videos**: NCS-style visualizers, karaoke LRC, effects.
- **One-click install**: Windows .bat files.

```bash
# Install
git clone https://github.com/timoncool/ACE-Step-Studio
cd ACE-Step-Studio
./install.bat

# Run
./run.bat
```

**Requirements**: NVIDIA GPU, 12GB VRAM (recommended 20GB+).

---

## 9. Model Context Protocol (MCP)

MCP is the open standard for connecting AI agents to external tools and data.

### 9.1 MCP Servers

| Server | Description |
|--------|-------------|
| **Playwright MCP** | Browser automation. |
| **GitHub MCP** | GitHub workflows and repo actions. |
| **Chrome DevTools MCP** | Official Chrome DevTools for coding + browser agents. |
| **Filesystem MCP** | Read/write files, run commands. |
| **Puppeteer MCP** | Headless browser control. |
| **Brave Search MCP** | Web search for agents. |
| **Git MCP** | Git operations, commit, branch. |
| **SQLite MCP** | Database queries. |
| **Slack/Discord MCP** | Messaging integrations. |

### 9.2 MCP Tools & Frameworks

| Tool | Description |
|------|-------------|
| **Smithery** | Registry + hosting platform for MCP servers. |
| **mcp-use** | Python library for connecting any LLM to MCP servers. |
| **FastMCP** | Pythonic framework for building MCP servers quickly. |
| **MCP Inspector** | Official debugging tool. |
| **MCP Registry** | Community discovery service. |
| **Natural Context Provider (NCP)** | Enhanced MCP with instant tool discovery, on-demand loading. |

---

## 10. Other Essential Tools

### 10.1 Knowledge & Memory

| Tool | Description |
|------|-------------|
| **Khoj** | AI second brain. Chat, search, agents over your docs. Local + cloud LLMs. |
| **AnythingLLM** | All-in-one Desktop + Docker AI app. RAG, agents, no-code builder, MCP. |
| **Open WebUI** | Web UI for LLMs. RAG, search, TTS, web scraping. |
| **LangChain** | Build context-aware reasoning applications. |
| **Langflow** | Visual workflow builder for AI agents. |
| **LlamaIndex** | LLM data framework. |

### 10.2 Voice & Audio

| Tool | Description |
|------|-------------|
| **faster-whisper** | Fast STT (Speech-to-Text). Local. |
| **Coqui TTS** | Open-source TTS. |
| **Piper** | Neural TTS system. |
| **Whisper** (OpenAI) | STT model. Large/vast small variants. |

### 10.3 Runtimes & Infrastructure

| Tool | Description |
|------|-------------|
| **Docker** | Containerize all your local AI. |
| **Ray Serve** | Scalable model serving on Kubernetes. |
| **Ray** | Distributed computing for AI. |

---

## 11. Awesome Lists (Deep Dive)

These GitHub repos have even more:

| Repo | Description |
|------|-------------|
| **av/awesome-llm-services** | 117+ self-hostable LLM services. Frontends, backends, workflow, CLI, MCP. |
| **rafska/awesome-local-llm** | Curated platforms, tools, models, agent frameworks, MCP, RAG, coding agents. |
| **duarte/awesome-private-ai** | Privacy-first tools. On-prem, air-gapped, self-hosted. |
| **kaushikb11/awesome-llm-agents** | LLM agent frameworks: CrewAI, LangChain, AutoGen, MetaGPT, etc. |
| **kyrolabs/awesome-agents** | Open-source tools to build AI agents. 50+ repos. |
| **e2b-dev/awesome-ai-agents** | Comprehensive list of autonomous agents. |
| **0xNyk/awesome-agent-cortex** | Full agent ecosystem: frameworks, coding, MCP, knowledge graphs, blockchain. |
| **jonradoff/awesome-agent-almanac** | Definitive list of agents, tools, MCP servers. Auto-generated. |
| **VoltAgent/awesome-claude-code-subagents** | 100+ specialized Claude Code subagents. |
| **ShrikeBot/awesome-agent** | Autonomous agent technologies. Platforms, frameworks, standards. |
| **danielrosehill/Local-AI-Agent-Resources** | On-device AI agent runners and tooling. |
| **theihtisham/awesome-ai-coding-7** | AI coding resources: generation, agents, RAG, LLMs. |

---

## 12. Quick Start Commands

```bash
# 1. Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# 2. Pull coding models
ollama pull deepseek-coder:7b
ollama pull qwen2.5-coder:14b
ollama pull hermes3:8b

# 3. Install OpenCLAW
pip install openclaw

# 4. Install Hermes Agent
curl -fsSL https://raw.githubusercontent.com/nousresearch/hermes-agent/main/install.sh | bash

# 5. Install skills CLI
npm install -g skills

# 6. Install n8n (Docker)
docker run -it --name n8n -p 5678:5678 n8nio/n8n

# 7. Install ComfyUI
git clone https://github.com/comfyanonymous/ComfyUI
cd ComfyUI && pip install -r requirements.txt
```

---

## 13. Hardware Recommendations

| Use Case | Minimum | Recommended |
|----------|---------|-------------|
| **LLM Coding (7B)** | 8GB VRAM (RTX 3060) | 16GB (RTX 4080) |
| **LLM Coding (14B)** | 16GB VRAM | 24GB (RTX 3090/4090) |
| **Image Generation** | 8GB VRAM | 16GB+ |
| **Video Generation** | 16GB VRAM | 24GB+ |
| **Music Generation** | 12GB VRAM | 20GB+ |
| **Full Stack (all of above)** | 24GB VRAM | 32GB+ (A100/H100) |

---

## 14. Related Documentation

- [CLAUDE.md](./CLAUDE.md) — This project's agent setup.
- [CLAUDE-ARCHON.md](./CLAUDE-ARCHON.md) — How to use Archon (your knowledge base).
- Look for `docs/agents/` in your project for agent-specific documentation.

---

This list is updated regularly. Star the source repos on GitHub to stay current. Every tool here is free to use (self-hosted) with no API limits.