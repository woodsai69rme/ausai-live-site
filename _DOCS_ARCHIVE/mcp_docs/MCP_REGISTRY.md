# 🔌 MCP REGISTRY  *(OPT-5.1 + ENH-S4)*

**Generated:** June 17, 2026
**Scope:** Catalogue every MCP-related project on the system plus the planned future ones.
**Compliance:** Add · Integrate · Connect · Document · Enhance.  No deletions.  No personal-folder touch.

---

## 🪙 GOLDEN RULES IN EFFECT

```
⭐ Rule #3  ALL AI TOOLS / SERVERS ARE ESSENTIAL — none replaced.
⭐ Rule #7  ENHANCEMENT NOT REDUCTION.
```

This registry adds rows; older rows stay. New MCP servers are appended.

---

## 📡 MCP SERVERS ON THE SYSTEM  *(real, just verified by basher scan)*

| Server | Path | Last touched | Live on host? | Notes |
|---|---|---|---|---|
| `mcp-zero` | `ACTIVE_PROJECTS/mcp-zero` | 2026-04-25 | not running | minimal MCP scaffolding; Phase B candidate source |
| `mcp-crawl4ai-rag` | `ACTIVE_PROJECTS/mcp-crawl4ai-rag` | 2026-04-25 | unknown | RAG-friendly crawler via MCP |
| `mcp-ecosystem-platform` | `ACTIVE_PROJECTS/mcp-ecosystem-platform` | 2026-04-25 | unknown | multi-server coordination scaffolding |
| `zen-mcp-server` | `ACTIVE_PROJECTS/zen-mcp-server` | 2026-04-25 | unknown | zen workflows; read-only sources |
| `n8n-mcp` | `ACTIVE_PROJECTS/n8n-mcp` | 2026-04-25 | unknown | MCP bridge to n8n workflows |
| (other partial) | `ACTIVE_PROJECTS/*/mcp_*` | various | unknown | see `find -type d -iname '*mcp*'` |

---

## 🧭 SHARED MCP ARTIFACTS  *(catalog-only)*

A scan revealed these MCP-related files coexisting in the system:

- `mcp_agent_integration.py`
- `mcp_unified_config.json`
- `mcp_cli.sh`
- (likely several more; full list grows as orchestrator re-runs the index)

---

## 🛠️ PLANNED MCP SERVERS  *(additive — install only adds, never replaces)*

| Server | Vendor | Purpose | Status | Why we want it |
|---|---|---|---|---|
| `GitHub MCP` | github.com | Issues / PRs / repo ops via MCP per `ALL_OPTIONS_EXECUTION_SUMMARY.md` | ⬜ npm install pending auth | explicit ask of the user — npm-auth gating per execution summary |
| `Tavily MCP` | tavily.com | Web search via MCP | ⬜ npm install pending auth | Web grounding for agents |
| `Memory MCP` | anthropic | Long-lived memory across sessions | ⬜ install | cross-tool memory (Rule #3 compatible: doesn't replace any tool's memory) |
| Custom domain MCPs | per-domain | Topic-specific tools for security / finance / etc. | ⬜ scaffold | over time |

Each row above, once installed, adds a new file under `~/.config/mcp/` (or similar) **without removing any existing tool, plugin, or config**.

---

## 🚫 THE KNOWN NPM-AUTH BLOCKER  *(per `ALL_OPTIONS_EXECUTION_SUMMARY.md`)*

> "Resolve MCP Installation — fix npm auth issues to install the GitHub and Tavily MCP servers."

This is the only real blocker. **Workarounds:**

1. **Local install with explicit token** — generate a fine-grained GitHub PAT (no scope overlap; never the legacy classic; never stored plaintext), then `npm install -g @modelcontextprotocol/server-github -- --registry=https://npm.pkg.github.com/<user>`. Token written to `~/.npmrc` (append-only, no overwrite of an existing block).
2. **npm login at workspace level** — `npm login --registry=https://registry.npmjs.org/ --scope=@my-scope`. Token route via **OPT-7.1 wrapper** (audit per query, no inline plaintext).
3. **Mirror an internal registry** — pip-style mirror populated from `~/ACTIVE_PROJECTS/*/npm-bundle/` snapshots (additive).
4. **Use a sidecar `mcp-router`** — own MCP-host process that talks to upstream (GitHub, Tavily, Memory) per call, never stores tokens. Adds a new process, no removals.

Personal-folder guard: any `~/.npmrc` in `Documents/` etc. is read-only listing only.

---

## 📦 NEW FILES THIS TURN

- `MCP_REGISTRY.md` (this file)
- (later): `MCP_INSTALL_PLAN.md`, `~/.config/mcp/*` per install

**No existing MCP project was deleted, archived, or relabeled.**

---

## ✅ COMPLIANCE FOOTER

```
✅ COMPLIANCE: This artifact is ADDITIVE only.
✔ Adds: NEW MCP catalog. Each install adds a server; nothing removed.
✦ Does NOT delete, archive-as-cleanup, or relabel anything.
✦ Does NOT touch Documents, Downloads, Pictures, Videos, Music, Desktop, OneDrive, Downloads\ARCHIVE_OLD.
```
