# Changelog

> Human-readable history of the local AI fleet at `C:\Users\karma\`.
> For the raw append-only tracker, see `TODO_TRACKER.md`.

---

## 2026-06-29

### Documentation
- **Master fleet docs** — `ALL-TOOLS-CONFIGURED.md` created (411 lines). Covers the entire fleet: quick start, system overview, launcher menu reference (0-16), 5 agent personas, local models, creative tools, dashboard, config file reference with side-by-side schema comparison, model IDs, port map, directory structure, dependencies, security, troubleshooting, changelog.
- **Quick reference** — `ALL_TOOLS_QUICK_REFERENCE.md` created (89 lines). One-page index of all 16 menu options with status, paths, model IDs, and routing diagram.
- **README refresh** — `README.md` rewritten from generic dev-env template to fleet-specific landing page.
- **New operator walkthrough** — Added to `ALL-TOOLS-CONFIGURED.md`: 5-minute first launch guide, decision tree for picking the right agent, typical daily workflow table, offline vs. online mode explanation.
- **Config schema comparison** — Added side-by-side table comparing Hermes, Oracle, Jarvis, and Paperclip config fields.

## 2026-06-26

### Launcher
- **Unified menu** — `START-ALL-AI-TOOLS.bat` rebuilt with single source-of-truth menu (0-16). Fixed dual-menu desync bug. Added empty-input guard (blank Enter redraws menu).
- **New agent slots** — Options 8 (Oracle), 9 (Jarvis), 10 (Paperclip) added with `IF EXIST` clone-then-launch pattern.
- **Utility shift** — List models / List skills / Open docs moved to options 14/15/16.

### Agent configs
- **Oracle** — `.oracle/oracle.config.json` created with `qwen/qwen3-next-80b-a3b-instruct:free`.
- **Jarvis** — `.jarvis/jarvis.config.json` created with `qwen/qwen3-next-80b-a3b-instruct:free`.
- **Paperclip** — `.paperclip/paperclip.config.json` created with `meta-llama/llama-3.3-70b-instruct:free`.
- **Model IDs filled** — All placeholders replaced with verified free models from `ComfyUI/config/openrouter_free_models.txt`.

### Documentation
- **Oracle/Jarvis/Paperclip setup** — `ORACLE_JARVIS_PAPERCLIP_SETUP.md` created with JSON schemas, model mapping, and TODO slots for repo URLs.
- **OpenClaw/Hermes setup** — `OPENCLAW_HERMES_SETUP_AND_RESEARCH.md` created (107 lines). Covers gateway (port 18789), `/steer` command, Hermes 3-tier fallback, routing architecture.
- **Git history scrub** — 4 GitHub PATs removed from commit `36462146` via `git filter-branch` + `GIT_LFS_SKIP_SMUDGE=1`. Backup refs deleted. Push successful.

### Git hygiene
- `.gitignore` updated with targeted rules for `.oracle/`, `.jarvis/`, `.paperclip/` (allows config JSONs + `.gitkeep`, ignores runtime data).

## 2026-06-17

### Project tracking
- **TODO tracker created** — `TODO_TRACKER.md` established as append-only project tracker. 131 items across OPT-1..10, ENH-S/I/R/H/M tiers, and 3 followups. Status legend: ⬜ 🟨 🟦 ✅ 🟪 🟥.

### Prior milestones (pre-launcher)
- Agent registry audit tools (`AGENT_REGISTRY_AUDIT_RUN.ps1`)
- Backup integrity verifier (`verify_backups.ps1`)
- Revenue tracking design (`REVENUE_TRACKING_DESIGN.md`)
- MCP host connector (`MCP_HOST_CONNECTOR.ps1`)
- Index delta scanners (`INDEX_DELTA_SCANNER.py`, `INDEX_DELTA_RECURSIVE.py`)
- Cross-tool audit aggregator (`CROSS_TOOL_AGGREGATOR.py`)
- Dotdir catalog (`DOTDIR_CATALOG_RUN.py`) — 81 names classified
- Environment sanitizer (`EnvironmentSanitizer.ps1`)

---

## Versioning Notes

This fleet uses **continuous deployment** — no version numbers. Each commit is a snapshot. The changelog above captures major milestones; for granular per-commit history, run:

```bash
git log --oneline --graph --all
```
