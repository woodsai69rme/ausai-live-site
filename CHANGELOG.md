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

### Revenue Agent Suite
- **Shared module** — `REVENUE_GENERATORS/revenue_utils.py` created with `setup_logging()`, `REVENUE_DIR`, `ensure_revenue_dir()`, and `write_json()` helpers.
- **Stub refactor** — All 5 revenue stubs refactored to use the shared module with type hints (`-> Dict[str, Any]`, `-> List[Dict[str, Any]]`):
  - `AUTONOMOUS_CONTENT_FACTORY.py` — content plan generation
  - `AUTONOMOUS_SAAS_LAUNCHER.py` — vertical SaaS launch planner
  - `GLOBAL_BRAIN_CRAWLER.py` — filesystem indexer, `PermissionError` now logs full path
  - `REVENUE_SINGULARITY_ENGINE.py` — source discovery + readiness scoring
  - `SELF_HEALING_DAEMON.py` — service health checks, `httpx.Client` replaces `urllib`, `attempt_heal` renamed to `plan_heal`
- **Suite documentation** — `REVENUE_GENERATORS/README.md` created: 6-script overview, dispatch API examples, output file reference, architecture diagram, changelog.
- **All 6 revenue actions verified live** — `deploy_revenue`, `content_factory`, `saas_launcher`, `brain_crawler`, `singularity`, `self_healing` — all dispatch via AI Army `:8001` and return success.
- **Service health monitor** — `REVENUE_GENERATORS/SERVICE_HEALTH_MONITOR.py` added.

### Archon V2 Server Live
- **Lazy Supabase init** — Three files converted from eager `create_client()` at module-import time to lazy initialization, so the server no longer crashes when Supabase credentials are missing/invalid:
  - `python/src/server/middleware/auth_middleware.py` — thread-safe `_get_supabase()` with `threading.Lock` and double-check locking; `authenticate_api_key` short-circuits to skip DB validation when Supabase is unavailable.
  - `python/src/server/api_routes/auth_api.py` — endpoints (`register`, `login`) call `_get_supabase()` first and return `503 Service Unavailable` when None.
  - `python/src/server/services/cost_optimization_service.py` — thread-safe `supabase_client` property (per-instance `_client_lock`), thread-safe `_cost_optimization_service` singleton (module-level lock), DB methods gracefully handle empty Supabase.
- **Server starts successfully** — `uv run python -m src.server.main` now boots cleanly without `SUPABASE_URL`/`SUPABASE_SERVICE_KEY` in `.env`.
- **Verified** — `curl http://localhost:8181/health` responds.

### Github Push Resolved
- **Auth fixed** — `gh auth switch -u woodsai69rme` activated the keyring PAT; `GITHUB_TOKEN` env var was previously overriding it.
- **All session commits pushed** — 19 unpushed commits pushed to `origin/master`. Latest: `aa981e8a`.

### n8n Automation Stack
- **Recreated** — Stopped broken `archon-n8n` container. Recreated from `n8n-automation-stack/docker-compose.yml` with port mapping fixed.
- **All endpoints 200** — `/`, `/home`, `/healthz` return 200 on `:5678`.

### Code Review
- **9 files reviewed** — Lazy initialization, thread-safety, None-safety, type hints. Three must-fix items flagged, all addressed:
  1. Added `threading.Lock` to `auth_middleware._get_supabase()` with double-check locking.
  2. Added `threading.Lock` to `cost_optimization_service.CostOptimizationService.supabase_client` property and `get_cost_optimization_service()` singleton.
  3. Verified `auth_api.py` short-circuits to `503` BEFORE any `.supabase.<attr>` access (already correct, no change needed).
- **Verified `write_json` default** — already `indent=2` for human-readable reports (no change needed).

### Unit tests for lazy Supabase initialization
- **`python/tests/test_lazy_supabase_init.py`** created (14 tests, all passing in 9.1s):
  - `_get_supabase()` — missing-env (parametrized for URL/KEY), create-raises, cached-client, thread-safe single-call (20-thread barrier).
  - `CostOptimizationService.supabase_client` property — injected-client, lazy caching, failure-path caching, thread-safe single-init.
  - `get_cost_optimization_service()` singleton — same-instance, thread-safe single-construct (counts `__init__` calls).
  - `auth_api` 503 short-circuit — `/register` and `/login` return 503 when `_get_supabase()` returns None; no `create_user` / `table` calls leak past the short-circuit.
- **Code review passed** — reviewer confirmed mock targets match each module's `from … import …` bindings, double-check locking tests use real contention via `Barrier(20) + ThreadPoolExecutor(20)`, and fixes (re-read `__init__` from class dict, parametrized missing-env, isolated `TestClient` bound directly to the auth router) addressed prior failures.
- **Lint clean** — `ruff check` passes; `from __future__ import annotations` keeps type evaluation lazy at runtime; `CostOptimizationService` import hoisted to module top; unused local removed.

### MCP / Agents runtime hardening
- **`python/src/mcp/mcp_server.py`** — replaced 11 unicode emoji chars in Python `logger.info/warning/error` calls with ASCII bracket tags (`[OK]`/`[SECURE]`/`[NET]`/`[CLEANUP]`/`[FAIL]`/`[WARN]`/`[STOP]`). Fixes `UnicodeEncodeError: 'charmap' codec can't encode character '\u2713'` on Windows cp1252 default encoding; bracketed form remains grok-friendly.
- **`python/src/agents/server.py`** — replaced `uvicorn.run("server:app", ...)` with `uvicorn.run(app, host="0.0.0.0", port=port, ...)`. The string form returned `[FAIL] Could not import module "server"` when launched via `python -m src.agents.server`; passing the in-scope FastAPI `app` directly avoids the string-based import lookup entirely.
- **Docker-compose requirement** — `src/agents/server.py` fetches credentials from `http://archon-server:8181/internal/credentials/agents` and `src/mcp/mcp_server.py`'s service_client targets the same hostname. Both services are designed to run as part of the Archon Docker stack on the `default` Docker network; running them as bare Windows processes requires a hosts alias for `archon-server → 127.0.0.1` plus a working `/internal/credentials/agents` endpoint on Archon.
- **Code review passed** — reviewer endorsed both fixes and noted `uvicorn.run(app, ...)` is more robust than the string form.

### Service status (final 2026-06-29)
- 🟢 **n8n** `:5678` — all endpoints 200
- 🟢 **Archon** `:8181` — `/health` 200, lazy-init Supabase, threading-safe
- 🟢 **ComfyUI** `:8188` — `/system_stats` 200
- 🟢 **Ollama** `:11434` — `/api/tags` 200
- 🔴 **MCP** `:8051` — service designed for Docker stack; standalone Windows startup blocked by missing service-client hostnames
- 🔴 **Agents** `:8052` — service designed for Docker stack; standalone Windows startup blocked by `archon-server` credential-fetch hostname
- 🔴 **AI Army** `:8001` — `AI_EMPIRE_EXPANSION.py` is a one-shot deployer (writes `ai_agent_api.py` files into AI projects), not a server; the `:8001` service that was running was a separate launcher (FOOTCLAN), now down.

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
