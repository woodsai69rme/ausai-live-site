# 🔧 AI_TOOLS_INVENTORY_INDEX.md

> **Master index for AI Tools inventory.** Covers the installed AI coding tools ecosystem — integration configs (ChatGPT, Claude, Gemini), functional tool categories (automation, browser, voice), model guides, and ecosystem overview. All tools are essential per Rule #3.

**Generated:** 2026-06-28
**Parent systems:** Agent Registry, AI Tools Dashboard, Skills Matrix

---

## 📁 FILE INVENTORY

### 🔷 AI_TOOLS/ — Integration Configs (6+ items)

| Directory | Purpose |
|---|---|
| `AI_TOOLS/CHATGPT/` | ChatGPT integration configs and exports (237MB documented intelligence) |
| `AI_TOOLS/CLAUDE/` | Claude integration configs and project blueprints |
| `AI_TOOLS/GEMINI/` | Gemini IDE integration and Antigravity CLI configs |
| `AI_TOOLS/GENERAL/` | Cross-tool general configuration |
| `AI_TOOLS/RAG_Ingestor/` | RAG memory ingestion pipeline |

### 🔷 ai-tools/ — Functional Categories

| Directory | Purpose |
|---|---|
| `ai-tools/automation/` | Automation scripts and workflows |
| `ai-tools/browser-extentions/` | Browser extension tools |
| `ai-tools/voice-assistants/` | Voice assistant integrations |

### 🔷 Model & Ecosystem Guides (4 files)

| File | Purpose |
|---|---|
| `AI-Models-Complete-Guide-2026.md` | Full guide: cloud models (Gemini, GPT, Claude, DeepSeek), hardware reqs, RAG setup |
| `AI-Models-Complete-Guide-2026-FULL.md` | Extended version with more depth |
| `AI_ECOSYSTEM_GUIDE.md` | Ecosystem overview: Ollama v0.21.0, Python 3.13, Node.js 22.19.0, local runtimes |
| `ai-tools-2025.md` | AI tools landscape circa 2025 |

---

## 🏗️ ARCHITECTURE

```
┌──────────────────────────────────────────────┐
│           AI TOOLS ECOSYSTEM                  │
│                                               │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐       │
│  │ CHATGPT  │ │  CLAUDE  │ │  GEMINI  │       │
│  │ exports  │ │ blueprints│ │  config  │       │
│  └──────────┘ └──────────┘ └──────────┘       │
│                                               │
│  ┌──────────────────────────────────────┐     │
│  │         RAG_Ingestor                  │     │
│  │   (feeds Project Brain 2.0)           │     │
│  └──────────────────────────────────────┘     │
│                                               │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐       │
│  │automation│ │ browser  │ │  voice   │       │
│  │ scripts  │ │extensions│ │assistants│       │
│  └──────────┘ └──────────┘ └──────────┘       │
└──────────────────────────────────────────────┘
```

---

## 🖥️ LOCAL AI RUNTIMES

| Runtime | Role |
|---|---|
| Ollama (v0.21.0) | General local LLM execution — port 11434 |
| LM Studio | Alternative local model serving — port 1234 |
| Jan | Desktop AI assistant |
| llama.cpp / vLLM / SGLang / KoboldCpp | High-performance inference engines |
| DeepSeek Coder 2 | Top recommended open-source coding model |

---

## 🔒 SECURITY BOUNDARIES

- **Rule #8 fence:** Integration configs and tools operate outside personal folders.
- **Credentials:** API keys in `.env*` files (gitignored). No keys in these docs.
- **All tools essential (Rule #3):** No tool is deprecated or removed from inventory.

---

## 🔗 CROSS-REFERENCES

| System | Index |
|---|---|
| Agent Registry (2,793 agents) | `AGENT_REGISTRY_SYSTEM_INDEX.md` |
| Skills Matrix (13 tools × 12 skills) | `SKILLS_MATRIX.md` |
| AI Tools Dashboard | `AI_TOOLS_DASHBOARD.html` |
| Workspace Master | `WORKSPACE_INDEX.md` |

---

*Designed under Golden Rules: append, never delete; preserve, never relabel; protect, never rewrite. Rule #3: ALL AI TOOLS ARE ESSENTIAL.*
