# 📚 PROJECT ENCYCLOPEDIA — Foundation Index  *(OPT-1.2)*

**Generated:** June 17, 2026
**Scope:** Index for `ACTIVE_PROJECTS/` (102 entries) + `EXPERIMENTAL/` (140+) + `COMPLETED_PROJECTS/` + `04_DEVELOPMENT/youtube_enhancement_tools/`.
**Compliance:** Add · Integrate · Connect · Document · Enhance.  No deletions.  No personal-folder touch.

> **Read with:** `HOME_INDEX.md` (the *map*), `AGENT_REGISTRY.md` (the *who*), `SKILLS_MATRIX.md` (the *what*).

---

## 🪙 GOLDEN RULES

```
⭐ Rule #1  NOTHING IS OBSOLETE         — no project is "old" or "abandoned"
⭐ Rule #2  ALL PROJECTS ARE PERMANENT  — every project stays
⭐ Rule #6  ALL EXPERIMENTS ARE RESEARCH
⭐ Rule #7  ENHANCEMENT NOT REDUCTION
⭐ Rule #9  ADD · INTEGRATE · CONNECT · DOCUMENT
```

This index **adds metadata** to projects. It does not move, rename, delete, or relocate any project file.

---

## 🧭 PROJECT REGISTRY SCHEMA (apply to every project)

| Field | Type | Example |
|---|---|---|
| `id` | slug | `claude-flow` |
| `name` | display | `Claude Flow` |
| `path` | relative | `ACTIVE_PROJECTS/claude-flow` |
| `kind` | enum | `agent-runtime · CLI · IDE · webapp · microservice · library · mcp · docs · dashboard · game · experimental` |
| `primary_language` | enum | `py · ts · go · rust · rb · sh · ps1 · multi · n/a` |
| `entry_points` | list of commands | `["npm run dev", "python cli.py"]` |
| `description` | one line | "Claude Flow orchestration runtime" |
| `golden_rules_compliant` | bool | `true` |
| `last_touched` | date | `2026-04-25` |
| `home_in_brain` | bool | `true` (will be indexed by Project Brain 2.0) |
| `notes` | freeform | per project |

---

## 🏷️ KIND DISTRIBUTION (top-level tagging)

| Kind | Count (ACTIVE_PROJECTS) | Examples |
|---|---|---|
| agent-runtime | ~22 | `claude-flow`, `agent-zero`, `hermes-agent`, `claudia`, `octofriend`, `reddix`, `serena` |
| CLI | ~14 | `codebuff`, `opencode`, `kilo`, `crush`-via-charmclones, `mise` |
| IDE / Tooling | ~8 | `Cursor`-adjacent clones, `claude-code-*` derivatives, `claudepro-directory` |
| webapp / dashboard | ~16 | `UniversalDashboard`, `project-heartbeat-dashboard`, `favorite-flow-dashboard`, `emergency-dashboard-services`, `dev-forge-omni` |
| library / framework | ~6 | `fastapi`, `ccxt`, `mise`, `plandex`, `spec-kit` |
| MCP server | ~6 | `mcp-zero`, `mcp-crawl4ai-rag`, `mcp-ecosystem-platform`, `zen-mcp-server`, `n8n-mcp` |
| workflow / n8n | ~5 | `n8n`, `n8n_agent`, `n8n-workflows`, `pipedream` |
| AI / LLM | ~9 | `Perplexica`, `fireplexity`, `claude-conductor`, `deepwiki-open` |
| builder / IDE-clone | ~6 | `bolt.diy`, `bolt2`, `lovable-custom-gpt`, `tell-me-that-clone`, `mimic-youware-clone` |
| experimental / clone | ~12 | `charm-clone-…`, `idea-fusion-alchemy`, `gemini-interpreter`, `instant-code-smith`, `newbeg` |
| game / media | ~6 | `engine-craft-games`, `gamedevforusers`, `gemcopilot-media-scribe`, `crystal` |
| knowledge / docs | ~2 | `system-prompts-and-models-of-ai-tools`, `QUICK_START.md`-clones |
| recovery / system | ~3 | `sos-recovery`, `woods-android-v2`, `SynapseAutoClaw` |

> ⚠ Counts here are eyeball estimates from manual review of the `ACTIVE_PROJECTS/` directory. The authoritative numbers live in `SCRIPTS/ORCHESTRATION_INDEXER.py` → `MASTER_ORCHESTRATION_INDEX.json` and the existing 2,793-agent total in `ALL_OPTIONS_EXECUTION_SUMMARY.md`. Use the orchestrator as the source of truth; this document is the human-readable overlay. Each new project registered by the orchestrator appends a row here; no row is ever removed or rewritten — only appended (append-only under Golden Rule #7).

---

## 📋 SAMPLE ENTRIES (taken from `ACTIVE_PROJECTS/<name>`; rows are append-only)

```yaml
- id: codebuff
  name: Codebuff CLI
  path: ACTIVE_PROJECTS/codebuff
  kind: CLI
  primary_language: ts
  description: AI orchestration CLI (the parent tool of this assistant)
  golden_rules_compliant: true
  last_touched: 2026-04-20

- id: claude-flow
  name: Claude Flow
  path: ACTIVE_PROJECTS/claude-flow
  kind: agent-runtime
  primary_language: py
  description: Claude agent orchestration runtime
  last_touched: 2025-12-31

- id: claude-conductor
  name: Claude Conductor
  path: ACTIVE_PROJECTS/claude-conductor
  kind: AI / LLM
  primary_language: py
  description: Conductor of multi-claude sessions
  last_touched: 2026-04-25

- id: claude-code-sub-agents
  name: Claude Code Sub-Agents
  path: ACTIVE_PROJECTS/claude-code-sub-agents
  kind: agent-runtime
  primary_language: py
  description: Library of 100+ Claude Code sub-agent definitions
  golden_rules_compliant: true
  last_touched: 2026-04-25

- id: youtube-enhancement-tools
  name: YouTube Enhancement Tools
  path: ACTIVE_PROJECTS/youtube-enhancement-tools
  kind: pipeline / utility
  primary_language: py
  description: Utilities for transcript harvesting and metadata enhancement
  golden_rules_compliant: true
  last_touched: 2026-04-25

- id: zen-mcp-server
  name: Zen MCP Server
  path: ACTIVE_PROJECTS/zen-mcp-server
  kind: MCP server
  primary_language: py
  description: MCP server for zen workflows (read-only on sources)
  golden_rules_compliant: true
  last_touched: 2026-04-25

- id: mcp-zero
  name: MCP Zero
  path: ACTIVE_PROJECTS/mcp-zero
  kind: MCP server
  primary_language: py
  description: Minimal MCP scaffolding
  last_touched: 2026-04-25

- id: fastapi
  name: FastAPI (clone)
  path: ACTIVE_PROJECTS/fastapi
  kind: library / framework
  primary_language: py
  description: Local clone of FastAPI for documentation tooling
  last_touched: 2026-04-25

- id: bolt-diy
  name: Bolt.diy
  path: ACTIVE_PROJECTS/bolt.diy
  kind: builder / IDE-clone
  primary_language: ts
  description: No-code / vibe-code IDE clone
  last_touched: 2026-04-27

- id: bolt2
  name: Bolt 2
  path: ACTIVE_PROJECTS/bolt2
  kind: builder / IDE-clone
  primary_language: ts
  description: Working fork of bolt.diy
  last_touched: 2026-04-25
```

> Only a subset is shown above for brevity; the full 102 entries can be regenerated by `SCRIPTS/ORCHESTRATION_INDEXER.py`.

---

## 🚀 NEXT STEPS FOR FULL ENCYCLOPEDIA (Week 3-4)

1. **Run the orchestrator indexer weekly** — capture per-project metadata including last commit, primary language, file count.
2. **Add `README.md` to each project** (additive only) — generated by Template Generator (OPT-3.5) using `KNOWN_KINDS` table.
3. **Cross-link to `AGENT_REGISTRY.md` and `SKILLS_MATRIX.md`** — every project's `golden_rules_compliant`, `home_in_brain` flag becomes true once Project Brain 2.0 (ENH-I1) lands.
4. **Render as a dashboard** — connect `MARKETPLACE_DASHBOARD.tsx` and `project_dashboard.html` via `REVENUE_DASHBOARD.html`.

---

## 🛡️ PERSONAL-FILE PROTECTION (Rule #8)

The Encyclopedia's indexer **never** descends into:
- `~/Documents/`, `~/Downloads/`, `~/Pictures/`, `~/Videos/`, `~/Music/`, `~/Desktop/`, `~/OneDrive/`
- `~/Downloads/ARCHIVE_OLD/`

These are scan-excluded; only `ACTIVE_PROJECTS/`, `EXPERIMENTAL/`, `COMPLETED_PROJECTS/`, and similar are included.

---

## ✅ COMPLIANCE FOOTER

```
✅ COMPLIANCE: This artifact is ADDITIVE only.
✔ Adds: NEW encyclopedia index for 200+ projects; no project moved or relabelled.
✦ Does NOT delete, archive-as-cleanup, or relabel anything.
✦ Does NOT touch Documents, Downloads, Pictures, Videos, Music, Desktop, OneDrive.
```
