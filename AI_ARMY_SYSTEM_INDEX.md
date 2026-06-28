# ⚔️ AI_ARMY_SYSTEM_INDEX.md

> **Master index for the AI Army (Foot Clan) — agent fleet management system.** Covers 16 files — FastAPI backend, 6 agent classes, Footclan dispatch trilogy, strategic dossier, and 4-week monetization plan. All files are append-only per Golden Rules.

**Generated:** 2026-06-28
**Parent systems:** Agent Registry, Aether Core, Voice PA

---

## 📁 FILE INVENTORY (16 files)

### 🔷 AI Army Core (8 files)

| File | Size | Purpose |
|---|---|---|
| `AI_ARMY/server.py` | ~3 KB | FastAPI backend on port **8001** — 9 REST endpoints for agent orchestration |
| `AI_ARMY/requirements.txt` | ~100 B | Dependencies: fastapi≥0.104, uvicorn≥0.24, pydantic≥2.0 |
| `AI_ARMY/agents/base_agent.py` | ~1 KB | Abstract base class: `execute()`, `pick_up_task()`, `save_report()`, `to_dict()` |
| `AI_ARMY/agents/cleanup_agent.py` | ~2 KB | Finds and purges junk files, duplicates, old caches, temp data |
| `AI_ARMY/agents/github_agent.py` | ~2 KB | Syncs local repos to GitHub using user's PAT |
| `AI_ARMY/agents/monitor_agent.py` | ~2 KB | Watches system resources, produces health reports |
| `AI_ARMY/agents/recon_agent.py` | ~2 KB | Filesystem scanner — audits directories, creates recon reports |
| `AI_ARMY/agents/revenue_agent.py` | ~2 KB | Wraps REVENUE_GENERATORS scripts, dispatches revenue tasks |

### 🔷 Footclan Dispatch Trilogy (5 files)

| File | Size | Lines | Purpose |
|---|---|---|---|
| `FOOTCLAN_SQUAD_DESIGN.md` | 7.7 KB | 142 | Dispatch planner: closed scoring algorithm, CLI surface, acceptance tests |
| `FOOTCLAN_SQUAD.md` | 5.7 KB | — | Operational notes: dry-run default, personal-folder guard, append-only discipline |
| `FOOTCLAN_EXECUTOR.md` | 5.9 KB | 128 | Executor docs: closed status enum (5 values), refusal matrix, append discipline |
| `FOOTCLAN_EXECUTOR.py` | 8.1 KB | — | Python dispatcher/executor: reads registry, scores agents, writes dispatch log |
| `FOOTCLAN_TO_REVENUE.md` | 6.8 KB | 133 | 4-week monetization plan: Footclan as paid code-review service (A$300–$2,000/mo) |

### 🔷 Strategic + Data (3 files)

| File | Size | Purpose |
|---|---|---|
| `AI_ARMY_FOOT_CLAN_DOSSIER.md` | ~2 KB | Strategic overview: 400+ agents, 7 divisions, voice interface, ChromaDB memory |
| `AI_ARMY/reports/` | varies | JSON recon reports (e.g., `recon-001_20260510_033509.json`) |
| `AI_ARMY/tasks/` | varies | Pending task JSON files for agent dispatch |

---

## 🏗️ ARCHITECTURE

```
┌──────────────────────────────────────────────────────────────┐
│              AI_ARMY_FOOT_CLAN_DOSSIER.md                     │
│   (Strategic: 400+ agents, 7 divisions, voice, ChromaDB)      │
└──────────────────────────┬───────────────────────────────────┘
                           │
          ┌────────────────┼────────────────────┐
          ▼                ▼                     ▼
┌──────────────────┐ ┌──────────────┐ ┌──────────────────────┐
│  AI_ARMY/server.py│ │ FOOTCLAN     │ │ AGENT_REGISTRY.md     │
│  (FastAPI :8001)  │ │ TRILOGY      │ │ (read-only, 2,793     │
│                   │ │              │ │  agents as pool)      │
│  9 REST endpoints │ │ DESIGN.md    │ └──────────────────────┘
│  GET /agents      │ │   ↓          │
│  POST /dispatch   │ │ SQUAD.md     │
│  GET /reports     │ │   ↓          │
│  GET /tasks       │ │ EXECUTOR.py  │
│  DELETE /tasks    │ │ EXECUTOR.md  │
└──────┬───────────┘ │              │
       │             │ TO_REVENUE.md │
       │             │ (monetization)│
       │             └──────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────────┐
│                    6 AGENT CLASSES                            │
│                                                              │
│  BaseAgent (ABC)                                              │
│  ├── CleanupAgent   — junk/purge                              │
│  ├── GitHubAgent    — repo sync via PAT                       │
│  ├── MonitorAgent   — system health                           │
│  ├── ReconAgent     — filesystem audit     ← booted on start  │
│  └── RevenueAgent   — revenue dispatch     ← booted on start  │
│                                                              │
│  reports/  ← JSON output     tasks/  ← JSON input             │
└──────────────────────────────────────────────────────────────┘
```

---

## 🔌 API REFERENCE (port 8001)

| Method | Path | Description |
|---|---|---|
| `GET` | `/` | Health check — service status, uptime |
| `GET` | `/agents` | List all registered agents and statuses |
| `GET` | `/agents/{agent_id}` | Get specific agent status |
| `GET` | `/tasks` | List pending task JSON files |
| `POST` | `/tasks` | Create new task → saves to `TASKS_DIR` |
| `POST` | `/dispatch` | Immediate dispatch → matching agent → results |
| `GET` | `/reports` | Recent report files (top 50) |
| `GET` | `/reports/{filename}` | Specific report contents |
| `DELETE` | `/tasks/{filename}` | Delete pending task |

---

## 🎖️ DOSSIER — 7 Divisions (400+ agents planned)

| Division | Count | Role |
|---|---|---|
| 💻 Coding Agents | 50 | Python, Go, TypeScript, Rust — refactor, debug, spec-driven dev |
| 🔍 Research Agents | 30 | Deep web scraping (Firecrawl), academic papers, competitive intel |
| 📣 Marketing Agents | 40 | SEO, ad creative, copywriting, social media trends |
| 🛡️ Security Agents | 30 | Red Team — local pentesting, vulnerability scanning, code audits |
| 🐙 GitHub Agents | 20 | Repo management, PR reviews, automated commits |
| 🏛️ Archon Agents | 200 | Cognitive Core — RAG memory banks, historical context (ChromaDB) |
| 🎧 Support Agents | 30 | Task triage, communication management |

> **Note:** 6 agent classes implemented (Python). 400+ agents are the strategic target — most exist as registry entries in `AGENT_REGISTRY.md`, not as running services.

---

## 🔧 FOOTCLAN DISPATCH WORKFLOW

```
Operator ──► footclan_squad_dispatch.py --task "refactor auth module"
                  │                                    (Stage 1: Dispatcher)
                  ├─ Read AGENT_REGISTRY.md (read-only, 2,793 agents)
                  ├─ Score agents: overlap_score + 0.5×cluster_affinity
                  ├─ Pick top-N (default 5, max 20)
                  ├─ Assign sub_task from {research, draft, execute, verify, summarize}
                  └─ Append to FOOTCLAN_DISPATCH.log
                           │
                           ▼
                  FOOTCLAN_EXECUTOR.py --dispatch-log FOOTCLAN_DISPATCH.log
                           │                     (Stage 2: Executor)
                           ├─ Read FOOTCLAN_DISPATCH.log (read-only)
                           ├─ Assign status from {started, ok, skipped, refused, noop}
                           ├─ Default: --dry-run (print plan, write nothing)
                           └─ With --run: append N execution rows + 1 summary to FOOTCLAN_EXECUTION.log
```

**Status enum:** `started | ok | skipped | refused | noop`
**Sub-task enum:** `research | draft | execute | verify | summarize`

---

## 💰 MONETIZATION PATH (FOOTCLAN_TO_REVENUE.md)

| Plan | Price (AUD/mo) | PRs/month | Repos |
|---|---|---|---|
| Pilot | $300 | 30 | 1 |
| Indie | $800 | 100 | 3 |
| Team | $2,000 | 500 | unlimited |

First 3 customers get lifetime Pilot rate. Product: AI code review as a service with append-only PROVENANCE.log audit trail.

---

## 🚀 DEPLOYMENT COMMANDS

| Command | Action |
|---|---|
| `cd AI_ARMY && python server.py` | Start FastAPI backend on port 8001 |
| `python FOOTCLAN_EXECUTOR.py --task "..." --dry-run` | Preview dispatch plan |
| `python FOOTCLAN_EXECUTOR.py --task "..." --run` | Execute dispatch, write log |
| `start_enhanced.bat` | Launch 400-agent swarm (from dossier) |

---

## 🔒 SECURITY BOUNDARIES

- **Rule #8 fence:** All files read/write outside personal folders. Executor refuses dispatch/execution log paths inside protected folders (exit 1).
- **Append-only:** Dispatch log and execution log grow monotonically. Registry is read-only. No agent row is ever deleted.
- **Dry-run by default:** Executor requires explicit `--run` to write. Safety valve prevents accidental mutations.
- **Closed enums:** Status (5 values) and sub-task (5 values) are finite — no injection via open strings.
- **Credentials:** GitHubAgent requires user PAT — stored in environment, never in these files.

---

## 📋 ACCEPTANCE TESTS (summary)

| Test | Validates |
|---|---|
| Append-only growth (2× run = 2× rows) | Monotonic log discipline |
| Personal folder refusal (exit 1) | Rule #8 fence |
| Dry-run zero writes | Safety valve |
| Status enum closed (5 values only) | No injection |
| Malformed dispatch rows counted, not fatal | Graceful degradation |
| Summary row present per run | Audit trail completeness |

---

## 🔗 CROSS-REFERENCES

| System | Index |
|---|---|
| Agent Registry | `AGENT_REGISTRY_SYSTEM_INDEX.md` |
| Aether Core | `AETHER_CORE_SYSTEM_INDEX.md` |
| Voice PA | `VOICE_PA_SYSTEM_INDEX.md` |
| AI Tools Dashboard | `AI_TOOLS_DASHBOARD.html` |
| All systems | `CHANGELOG.md` |

---

## ⚠️ KNOWN GAPS

| Gap | Severity | Notes |
|---|---|---|
| 6/400+ agents implemented | High | Dossier targets 400+; 6 Python agent classes exist. Remaining are registry entries only. |
| Executor stubs statuses | Medium | Statuses are deterministic stubs (not actual agent execution). Real logic needs wiring. |
| GitHub webhook consumer not built | Medium | FOOTCLAN_TO_REVENUE.md plans this for Week 1 monetization — not yet implemented. |
| No ChromaDB integration visible | Info | Dossier describes RAG memory; server.py shows no ChromaDB import. |
| Port 8001 vs dossier ports | Info | Dossier mentions ports 8000, 3000, 8765. Actual server.py runs on 8001. |

---

## 🔄 SYSTEM HISTORY

| Date | Event |
|---|---|
| 2026-04 | AI Army dossier written (400+ agents, 7 divisions) |
| 2026-05 | ReconAgent produces first reports (`recon-001_*`) |
| 2026-06-17 | Footclan trilogy designed (squad + executor + revenue) |
| 2026-06-28 | System index created (this file) |

---

*Designed under the user's Golden Rules: append, never delete; preserve, never relabel; protect, never rewrite. Rule #8 personal folders (Documents, Downloads, Pictures, Videos, Music, Desktop, OneDrive, Downloads\ARCHIVE_OLD) are fenced off at every layer.*
