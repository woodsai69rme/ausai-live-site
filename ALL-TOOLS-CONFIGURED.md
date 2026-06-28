# All Tools Configured — Master Fleet Documentation

> **Scope:** Local AI fleet at `C:\Users\karma\`
> **Updated:** June 2026
> **Launcher:** `START-ALL-AI-TOOLS.bat` (menu 0-16)
> **Dashboard:** http://localhost:3142

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [System Overview](#system-overview)
3. [Launcher Menu Reference](#launcher-menu-reference)
4. [Agent Personas](#agent-personas)
5. [Local AI Models](#local-ai-models)
6. [Creative Tools](#creative-tools)
7. [Dashboard & Utilities](#dashboard--utilities)
8. [Config File Reference](#config-file-reference)
9. [Model IDs](#model-ids)
10. [Port Map](#port-map)
11. [Directory Structure](#directory-structure)
12. [Dependencies](#dependencies)
13. [Security](#security)
14. [Troubleshooting](#troubleshooting)
15. [Related Documentation](#related-documentation)

---

## Quick Start

1. Double-click `START-ALL-AI-TOOLS.bat` or run it from CMD.
2. Type a number (0-16) and press Enter.
3. Press `0` to exit, or press Enter without typing to redraw the menu.

### First-time setup checklist

- [ ] Ollama installed with `qwen2.5-coder:latest` and `phi3:latest`
- [ ] `uv` package manager installed
- [ ] OpenRouter API key set (for cloud fallback)
- [ ] `npx` / Node.js available (for skills list, dashboard)
- [ ] Clone `oracle-agent/`, `jarvis-agent/`, `paperclip-agent/` when URLs are provided

---

## Getting Started for New Operators

### The 5-minute first launch

```
Step 1: Open CMD
    │
    ▼
Step 2: Run launcher
    START-ALL-AI-TOOLS.bat
    │
    ▼
Step 3: Pick a tool
    ├─ Need to chat?          → 6 (Hermes) or 4/5 (Ollama local)
    ├─ Need to code?          → 1 (Kilo) or 3 (OpenCode)
    ├─ Need to route agents?  → 2 (OpenClaw gateway)
    ├─ Need music/video?      → 11 (Tadpole) or 12 (ComfyUI)
    └─ Just browsing?         → 13 (Dashboard) or 16 (this doc)
    │
    ▼
Step 4: When done, press 0
```

### Decision tree: which agent do I use?

```
What do you need?
    │
    ├─► Chat / reasoning / general help
    │       │
    │       ├─ Internet available? ──► Hermes (option 6)
    │       │   Uses OpenRouter free tier
    │       │
    │       └─ Offline only? ────────► Ollama qwen2.5-coder (option 4)
    │
    ├─► Search documents / knowledge base
    │       │
    │       └─► Oracle (option 8) — once cloned
    │
    ├─► Write code / run terminal commands
    │       │
    │       └─► Jarvis (option 9) — once cloned
    │
    ├─► Move files / archive / cleanup
    │       │
    │       └─► Paperclip (option 10) — once cloned
    │
    └─► Orchestrate multiple agents
            │
            └─► OpenClaw (option 2) — use /steer to switch mid-session
```

### Typical daily workflow

| Time | Task | Launcher option | Fallback if offline |
|------|------|-----------------|---------------------|
| Morning standup | Review code | 1 (Kilo) or 9 (Jarvis) | 4 (Ollama coder) |
| Deep work | Write features | 9 (Jarvis) | 4 (Ollama coder) |
| Research | Search docs | 8 (Oracle) | 4 (Ollama coder) |
| Cleanup | File ops | 10 (Paperclip) | Manual |
| Break | Chat / questions | 6 (Hermes) | 4 (Ollama coder) |
| End of day | Check fleet status | 13 (Dashboard) | — |

### Offline vs. online mode

**Online (recommended):** Agents use OpenRouter free tier for strong models. Rate limit: 20 req/min, 200 req/day. If you hit the limit, wait 1 min or switch to local.

**Offline:** Agents fall back to Ollama local models. No rate limits, but models are smaller (7B parameters vs. 80B MoE in cloud). Good for airplane mode, sensitive data, or when OpenRouter is down.

To force offline: disconnect internet, or set `cloud_model_id` to `null` in the persona config. The agent will automatically use `local_model_id`.

---

## System Overview

The fleet is a **local-first, cloud-fallback** AI toolchain. Every agent can run entirely offline via Ollama; when internet is available, agents escalate to OpenRouter's free tier for stronger models.

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    User (CMD / Dashboard)                    │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│              START-ALL-AI-TOOLS.bat (menu 0-16)             │
└───────────────────────────┬─────────────────────────────────┘
                            │
    ┌───────────┬───────────┼───────────┬───────────┐
    │           │           │           │           │
┌───▼───┐  ┌───▼───┐  ┌────▼────┐ ┌───▼───┐  ┌────▼────┐
│ Coding│  │ OpenClaw│  │ Hermes  │ │ Local │  │ Creative│
│ Tools │  │gateway  │  │ (chat)  │ │Models │  │  Tools  │
│Kilo   │  │:18789   │  │         │ │Ollama │  │         │
│OpenCode│  └────┬────┘  └─────────┘ │:11434 │  │Tadpole  │
└───────┘       │                   └───────┘  │ComfyUI  │
                │                              └─────────┘
           ┌────┼────┬────────┐
           │    │    │        │
        ┌──▼─┐┌─▼─┐┌─▼──┐  ┌──▼──┐
        │Orcl││Jrv││Pprc│  │Agent│
        │RAG ││Sys││File│  │Zero │
        └────┘└───┘└────┘  └─────┘
```

**Routing:** OpenClaw receives intent, then Hermes routes to Oracle (data), Jarvis (code), or Paperclip (admin). Each persona has its own model + tool allow-list.

---

## Launcher Menu Reference

| # | Name | What it does | Status |
|---|------|--------------|--------|
| 1 | **Kilo AI** | Code generation CLI (`kilo`) | ✅ Ready |
| 2 | **OpenClaw** | Gateway agent with `/steer` routing (`openclaw agent --agent test`) | ✅ Active |
| 3 | **OpenCode** | General AI coding assistant (`opencode`) | ✅ Ready |
| 4 | **Ollama qwen2.5-coder** | Best local coding chat | ✅ Ready |
| 5 | **Ollama phi3** | Fastest local chat | ✅ Ready |
| 6 | **Hermes** | Self-improving chat agent (`uv run python run_agent.py`) | ✅ Active |
| 7 | **Agent Zero** | Dynamic AI framework UI (`python run_ui.py`) | ✅ Cloned |
| 8 | **Oracle** | RAG / Data persona (`uv run python main.py`) | ⚠️ Needs clone |
| 9 | **Jarvis** | Coding / System persona (`uv run python main.py`) | ⚠️ Needs clone |
| 10 | **Paperclip** | Admin / File-ops persona (`uv run python main.py`) | ⚠️ Needs clone |
| 11 | **Tadpole Studio** | Music generation (`python start.py`) | ✅ Ready |
| 12 | **ComfyUI** | Video/image generation (`python main.py`) | ✅ Ready |
| 13 | **God-Mode Dashboard** | Web dashboard on port 3142 | ✅ Ready |
| 14 | **List models** | `ollama list` | ✅ Ready |
| 15 | **List skills** | `npx skills list` | ✅ Ready |
| 16 | **Docs** | Opens this file in Notepad | ✅ Ready |
| 0 | **Exit** | Closes launcher | — |

> Options 8-10 print a TODO message with clone instructions until the matching repo is cloned into `<persona>-agent/`.

---

## Agent Personas

### OpenClaw (Gateway / Orchestrator)

- **Role:** Entry point for multi-agent routing.
- **Port:** 18789
- **Config:** `.openclaw/openclaw.json`
- **Workspace:** `.openclaw/workspace/` (AGENTS.md, BOOTSTRAP.md, HEARTBEAT.md, IDENTITY.md, SOUL.md, TOOLS.md, USER.md)
- **Key command:** `/steer` — redirect mid-session to another persona without losing context.

### Hermes (Chat / Reasoning)

- **Role:** Default conversational agent.
- **Clone:** `hermes-agent/`
- **Config:** `.hermes/config/hermes.config.json`
- **Identity:** `.hermes/SOUL.md` (Nous Research persona)
- **Entry:** `hermes-agent/run_agent.py`
- **Three-tier fallback:**
  1. OpenRouter free: `qwen/qwen3-next-80b-a3b-instruct:free`
  2. OpenRouter internal fallback
  3. Local Ollama: `qwen2.5-coder:7b` @ `127.0.0.1:11434`

### Oracle (RAG / Data)

- **Role:** Long-context retrieval, document search, knowledge base queries.
- **Clone:** `oracle-agent/` *(pending URL)*
- **Config:** `.oracle/oracle.config.json`
- **Audit log:** `.oracle/logs/oracle.actions.jsonl`
- **Tools:** `rag_query`, `code_search`, `retrieve_doc`
- **Vector store:** chromadb (local) or Supabase pgvector

### Jarvis (Coding / System)

- **Role:** File operations, terminal commands, git workflows, code generation.
- **Clone:** `jarvis-agent/` *(pending URL)*
- **Config:** `.jarvis/jarvis.config.json`
- **Audit log:** `.jarvis/logs/jarvis.actions.jsonl`
- **Tools:** `bash`, `read_file`, `write_file`, `git`
- **Sandbox:** `C:/Users/karma/workspaces`
- **Terminal proxy:** OpenClaw gateway port 18789

### Paperclip (Admin / File-ops)

- **Role:** File movement, archiving, cleanup, administrative glue work.
- **Clone:** `paperclip-agent/` *(pending URL)*
- **Config:** `.paperclip/paperclip.config.json`
- **Audit log:** `.paperclip/logs/paperclip.actions.jsonl`
- **Tools:** `move_file`, `copy_file`, `delete_file`, `archive`
- **Concurrency:** 1 (no parallel writes to same directory)

---

## Local AI Models

Managed by **Ollama** (`127.0.0.1:11434`).

| Model | Use case | Launcher option |
|-------|----------|-----------------|
| `qwen2.5-coder:latest` | Coding, reasoning, long context | 4 |
| `phi3:latest` | Fast responses, lightweight tasks | 5 |

Install additional models: `ollama pull <model>`

---

## Creative Tools

### Tadpole Studio (Music)

- **Path:** `tadpole-studio/`
- **Entry:** `python start.py`
- **Note:** First run downloads ~10GB of models.

### ComfyUI (Video / Image)

- **Path:** `ComfyUI/`
- **Entry:** `python main.py`
- **Sub-launcher:** `launch_music_video_studio.bat` (21-option menu)
- **Free models list:** `ComfyUI/config/openrouter_free_models.txt`
- **Workflow recipes:** `ComfyUI/workflow_templates/workflow_recipes.md`
- **GPU:** Optimized for RTX 4060 8GB

---

## Dashboard & Utilities

### God-Mode Dashboard

- **URL:** http://localhost:3142
- **Source:** `ACTIVE_PROJECTS/ai-tools-suite/`
- **Start:** `npm run dev`
- **Purpose:** Fleet overview, project status, quick links.

### List models (option 14)

Runs `ollama list` — shows all downloaded local models.

### List skills (option 15)

Runs `npx skills list` — shows installed npx skills.

---

## Config File Reference

| Config | Path | Controls |
|--------|------|----------|
| OpenClaw | `.openclaw/openclaw.json` | Gateway settings, agent registry |
| Hermes | `.hermes/config/hermes.config.json` | Model IDs, fallback tiers, tool allowlist |
| Oracle | `.oracle/oracle.config.json` | RAG settings, vector store, context window |
| Jarvis | `.jarvis/jarvis.config.json` | Sandbox path, terminal proxy, tool allowlist |
| Paperclip | `.paperclip/paperclip.config.json` | Concurrency, tool allowlist, audit log path |

All configs use the **same field names** for cross-model swapping:
- `cloud_model_id` — OpenRouter free-tier model
- `local_model_id` — Ollama local fallback
- `tool_allowlist` — permitted tools for this persona
- `audit_log` — append-only JSONL action log

### Side-by-side schema comparison

Hermes is a **universal orchestrator** with a rich nested schema. Oracle, Jarvis, and Paperclip are **specialized personas** with flat minimal schemas.

**Flat persona schema** (Oracle / Jarvis / Paperclip):

| Field | Oracle | Jarvis | Paperclip |
|-------|--------|--------|-----------|
| `cloud_model_id` | `qwen/qwen3-next-80b-a3b-instruct:free` | `qwen/qwen3-next-80b-a3b-instruct:free` | `meta-llama/llama-3.3-70b-instruct:free` |
| `local_model_id` | `qwen2.5-coder:7b` | `qwen2.5-coder:7b` | `phi3:latest` |
| `tool_allowlist` | `rag_query`, `code_search`, `retrieve_doc` | `bash`, `read_file`, `write_file`, `git` | `move_file`, `copy_file`, `delete_file`, `archive` |
| `audit_log` | `.oracle/logs/oracle.actions.jsonl` | `.jarvis/logs/jarvis.actions.jsonl` | `.paperclip/logs/paperclip.actions.jsonl` |
| **Persona-specific** | `context_window: 8192`, `vector_store: chromadb` | `file_sandbox`, `terminal_proxy: http://127.0.0.1:18789` | `concurrency: 1` |

**Hermes nested schema** (universal orchestrator):

| Section | Key fields |
|---------|-----------|
| `orchestration` | `agents[]` (OpenClaw bridge, Pi agent, Claude, Ollama), `routing.strategy: cost-optimized`, `loadBalancing: round-robin` |
| `models.openrouter` | `baseUrl`, `apiKey: ${OPENROUTER_API_KEY}`, `freeModels[]` (Gemini, DeepSeek, Shuttle), `routing.byTask` (code/reasoning/fast/creative), `rateLimits` (20/min, 200/day) |
| `models.local` | `ollama.baseUrl: http://localhost:11434`, `models[]` (llama3.2, phi3, qwen2.5-coder, gemma2, mistral, nomic-embed-text), `autoDownload: true` |
| `features` | `mcp.servers[]` (filesystem, web-search, github, brave-search, openrouter-stats), `code.execution.sandbox`, `search.hybrid`, `memory.ragEnabled` |
| `workflow` | `subAgents.enabled`, `maxConcurrent: 4`, `parallelExecution`, `checkpoints` |
| `logging` | `file: ~/.hermes/logs/hermes.log`, `rotation: daily`, `maxFiles: 7` |

> **Why two schema shapes?** The flat schema makes it trivial to copy a config, swap the model ID, and spin up a new persona in minutes. The nested schema gives Hermes the flexibility to route between multiple backends, switch models by task type, and manage sub-agent concurrency.

---

## Model IDs

### OpenRouter Free Tier (source of truth)

List refreshed by: `music_video_studio.py list-free-models`

Current verified free models (from `ComfyUI/config/openrouter_free_models.txt`):

| Model ID | Parameters | Use |
|----------|-----------|-----|
| `qwen/qwen3-next-80b-a3b-instruct:free` | 80B MoE | Coding, reasoning, chat |
| `meta-llama/llama-3.3-70b-instruct:free` | 70B | General instruct, admin tasks |
| `google/gemma-4-26b-a4b-it:free` | 26B | Lightweight instruct |
| `google/gemma-4-31b-it:free` | 31B | General instruct |
| `nvidia/nemotron-nano-9b-v2:free` | 9B | Fast, lightweight |
| `nex-agi/nex-n2-pro:free` | — | Pro variant |
| `meta-llama/llama-3.2-3b-instruct:free` | 3B | Ultra-fast edge |
| `liquid/lfm-2.5-1.2b-instruct:free` | 1.2B | Minimal latency |
| `deepseek/deepseek-r1:free` | — | Reasoning |
| `deepseek/deepseek-chat:free` | — | General chat |
| `shuttleai/shuttle-3:free` | — | General |

**Free tier limits:** 20 req/min, 200 req/day.

### Fleet assignment

| Persona | Cloud model | Local fallback |
|---------|-------------|----------------|
| Hermes | `qwen/qwen3-next-80b-a3b-instruct:free` | `qwen2.5-coder:7b` |
| Oracle | `qwen/qwen3-next-80b-a3b-instruct:free` | `qwen2.5-coder:7b` |
| Jarvis | `qwen/qwen3-next-80b-a3b-instruct:free` | `qwen2.5-coder:7b` |
| Paperclip | `meta-llama/llama-3.3-70b-instruct:free` | `phi3:latest` |

> Oracle and Jarvis share the only Qwen free model. If more Qwen free variants appear, split them to avoid shared rate limits.

---

## Port Map

| Service | Port | Protocol | Notes |
|---------|------|----------|-------|
| Ollama | 11434 | HTTP | Local model server |
| OpenClaw | 18789 | HTTP | Gateway / routing layer |
| Supabase (Archon) | 8181 | HTTP | pgvector / RAG backend *(when running)* |
| God-Mode Dashboard | 3142 | HTTP | Web UI |
| Archon MCP | 8051 | HTTP | MCP protocol server *(when running)* |
| Archon Agents | 8052 | HTTP | PydanticAI service *(when running)* |

---

## Directory Structure

```
C:\Users\karma\
├── START-ALL-AI-TOOLS.bat          ← Master launcher
├── ALL-TOOLS-CONFIGURED.md         ← This file
├── ALL_TOOLS_QUICK_REFERENCE.md    ← One-page menu index
│
├── .openclaw/                      ← OpenClaw gateway config
│   ├── openclaw.json
│   └── workspace/
│
├── .hermes/                        ← Hermes agent config
│   └── config/hermes.config.json
│
├── .oracle/                        ← Oracle config (ready)
│   ├── oracle.config.json
│   └── logs/
│
├── .jarvis/                        ← Jarvis config (ready)
│   ├── jarvis.config.json
│   └── logs/
│
├── .paperclip/                     ← Paperclip config (ready)
│   ├── paperclip.config.json
│   └── logs/
│
├── hermes-agent/                   ← Hermes clone ✅
├── agent-zero/                     ← Agent Zero clone ✅
├── ComfyUI/                        ← Video/image studio ✅
├── tadpole-studio/                 ← Music studio ✅
│
├── oracle-agent/                   ← Oracle clone (pending URL)
├── jarvis-agent/                   ← Jarvis clone (pending URL)
└── paperclip-agent/                ← Paperclip clone (pending URL)
```

---

## Dependencies

### Required

| Tool | Purpose | Verify |
|------|---------|--------|
| Git | Clone / push repos | `git --version` |
| Ollama | Local AI models | `ollama --version` |
| Python 3.12+ | Agent runtimes | `python --version` |
| `uv` | Python package manager | `uv --version` |
| Node.js 20+ | Dashboard, skills | `node --version` |
| `npx` | Skill listings | `npx --version` |

### Optional

| Tool | Purpose | Verify |
|------|---------|--------|
| `gh` | GitHub CLI auth | `gh auth status` |
| `npm` | Dashboard dev server | `npm --version` |
| CUDA / ROCm | GPU acceleration for ComfyUI | `nvidia-smi` |

---

## Security

- **No hardcoded API keys** in any config file. `cloud_model_id` fields contain public model identifiers only.
- **OpenRouter key** should be set via environment variable or secure key store — never committed to git.
- **Git history scrubbed** for PATs and secrets. Run `gitleaks` periodically: `gitleaks detect --source . --verbose`.
- **Audit logs** are append-only (`*.actions.jsonl`) and isolated per persona.
- **File sandbox:** Jarvis is restricted to `C:/Users/karma/workspaces`. Paperclip uses concurrency=1 to prevent race conditions.
- **Rule #8:** Personal folders (Documents, Downloads, Pictures, Videos, Music, Desktop, OneDrive, ARCHIVE_OLD) are never touched by automation.

---

## Troubleshooting

### Launcher shows "NOT yet cloned" for options 8-10

You need the repo URLs for Oracle, Jarvis, and Paperclip agents. Once you have them:

```bat
git clone <ORACLE_URL> C:\Users\karma\oracle-agent
git clone <JARVIS_URL> C:\Users\karma\jarvis-agent
git clone <PAPERCLIP_URL> C:\Users\karma\paperclip-agent
```

Then re-run the launcher.

### Ollama model not found

```bash
ollama pull qwen2.5-coder:latest
ollama pull phi3:latest
```

### OpenRouter rate limit (429)

The free tier allows 20 req/min, 200 req/day. Wait 1 minute and retry, or switch to local Ollama fallback.

### `uv` command not found

Install `uv`: https://docs.astral.sh/uv/getting-started/installation/

### Dashboard (port 3142) not loading

```bash
cd C:\Users\karma\ACTIVE_PROJECTS\ai-tools-suite
npm install
npm run dev
```

### God-Mode Dashboard vs. Archon Dashboard

- **God-Mode Dashboard** (port 3142): General fleet overview — part of this launcher ecosystem.
- **Archon Dashboard** (port 3737): Knowledge-base RAG interface — separate project. See `archon-ui-main/`.

---

## Related Documentation

| Document | What it covers |
|----------|---------------|
| `ALL_TOOLS_QUICK_REFERENCE.md` | One-page index of all 16 menu options |
| `OPENCLAW_HERMES_SETUP_AND_RESEARCH.md` | OpenClaw gateway + Hermes agent deep dive |
| `ORACLE_JARVIS_PAPERCLIP_SETUP.md` | Oracle, Jarvis, Paperclip setup + config schemas |
| `ComfyUI/README.md` | ComfyUI Music Video Studio full guide |
| `TODO_TRACKER.md` | Append-only project tracker (131 items) |

---

## Changelog

| Date | Change |
|------|--------|
| 2026-06-26 | Created unified launcher `START-ALL-AI-TOOLS.bat` with single menu (0-16) |
| 2026-06-26 | Added Oracle, Jarvis, Paperclip configs with real OpenRouter model IDs |
| 2026-06-26 | Created `ALL_TOOLS_QUICK_REFERENCE.md` |
| 2026-06-29 | Created `ALL-TOOLS-CONFIGURED.md` (this master document) |
