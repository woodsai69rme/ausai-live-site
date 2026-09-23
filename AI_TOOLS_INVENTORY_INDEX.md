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

### 🔧 Mobile Recovery Suite *(NEW 2026-07-09)*

| Path | Purpose |
|---|---|
| `COMPLETED_PROJECTS/mobile_backup/MOBILE_TOOLS_INDEX.md` | Master inventory (16 new files, 12-position menu dispatcher) |
| `COMPLETED_PROJECTS/mobile_backup/RECOVERY_QUICKSTART.md` | Scenario-driven runbook (6 situations: broken screen, forgotten PIN, ADB-alive lock, dead brick, iPhone backup) |
| `COMPLETED_PROJECTS/mobile_backup/RECOVERY_SUITE.bat` | 12-position `choice /c 123456789PIX` menu dispatcher (Android unlock GUI + iPhone suite + Oppo specialist + 4 Flask reference UIs) |
| `COMPLETED_PROJECTS/mobile_backup/iphone_recovery.py` | iPhone plumbing — libimobiledevice + pymobiledevice3 wrapper (`idevice_id` / `ideviceinfo` / `idevicebackup2` / `idevicerestore` / `idevicesyslog`; correct `lockdown list` cmd + `list-devices` fallback) |
| `COMPLETED_PROJECTS/mobile_backup/oppo_broken_screen.py` | Oppo broken-screen specialist (chipset-aware flow planner: Qualcomm-EDL / MediaTek-SP-Flash / fastboot-format / scrcpy-OTG; reads `oppo_model_quickref.json`) |
| `COMPLETED_PROJECTS/mobile_backup/tests/test_mobile_recovery.py` | 15/15 PASS stdlib unittest suite (public-surface checks; caught the oneplus-substring regression) |
| `C:\Users\karma\recovery.bat` | Top-level shim — from any cwd, reaches `COMPLETED_PROJECTS\mobile_backup\RECOVERY_SUITE.bat` in one keystroke |

### 🔧 Reference Docs *(NEW 2026-07-09)*

Workspace-level reference docs (research + shopping + setup guides). Each is a self-contained top-level .md; `REFERENCE_DOCS_INDEX.md` is the single-page nav that points at the other four. Portable offline copies (HTML + binary PDF) live in `_DOCS_ARCHIVE/`.

| Path | Purpose |
|---|---|
| `REFERENCE_DOCS_INDEX.md` | Single-page index + reading-order guide; entry point for the 4 reference docs below (Building / Discovering / Buying / Installing lanes) |
| `YOUTUBE_GITHUB_DEEP_RESEARCH_2026.md` | 2026 YouTube transcript + AI content-factory + ComfyUI-video + voice-cloning GitHub ecosystem deep-dive (~400 lines, 7 sections, prioritised actions in 3 ROI tiers, NOT-TO-DO list) |
| `HARDWARE_SHOPPING_LIST_2026.md` | Exhaustive 14-category catalogue of every laptop→display+peripheral connection method + tier 1/2/3 hardware tables + virtual connections + cables + mega-decision-tree (~600 lines) |
| `SUNSHINE_MOONLIGHT_SETUP.md` | 6-step install guide for the GPU-accelerated remote-desktop pipeline (Step 0 PowerShell diag + host install + client install + pairing + firewall + uninstall) (~250 lines; documented, NOT auto-installed) |
| `AWESOME_YOUTUBE_REPOS_2026.md` | Curated-list-of-curated-lists companion to the YouTube research; Big Three front-ends + 15-niche catalog + champion picks + maintenance warning (~250 lines) |
| `DAILY_REFERENCE_DIGEST_2026-07-09.md` | One-page daily digest linking to all 5 reference docs + 3 index updates with one-line summaries, reading paths by use-case, and commit SHA index (~80 lines) |

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
| Mobile Recovery Suite (16 files) | `COMPLETED_PROJECTS/mobile_backup/MOBILE_TOOLS_INDEX.md` |
| Workspace Master | `WORKSPACE_INDEX.md` |
| Reference Docs (5 docs + daily digest) | `REFERENCE_DOCS_INDEX.md` |

---

| Operator Self-Use Toolkit (NEW 2026-07-09) | [`AI_AND_IT_TOOLKIT.md`](AI_AND_IT_TOOLKIT.md) |
| Dot-directory integration audit (NEW 2026-07-13) | [`DOTDIR_INTEGRATION_AUDIT_2026-07-13.md`](DOTDIR_INTEGRATION_AUDIT_2026-07-13.md) — 124+ dot-dirs mapped with cross-tool integration opportunities |
| OpenCode DB investigation (NEW 2026-07-13) | [`OPENCODE_DB_INVESTIGATION_2026-07-13.md`](OPENCODE_DB_INVESTIGATION_2026-07-13.md) — 15GB session DB structure, purpose, non-destructive optimization options |
| Root docs master index (NEW 2026-07-13) | [`ROOT_DOCS_MASTER_INDEX.md`](ROOT_DOCS_MASTER_INDEX.md) — comprehensive categorized index of 120+ root documentation files |

*Designed under Golden Rules: append, never delete; preserve, never relabel; protect, never rewrite. Rule #3: ALL AI TOOLS ARE ESSENTIAL.*
