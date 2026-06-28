# 🎛️ INTERACTIVE SCRIPT MENU — Script Command Reference  *(OPT-1.3)*

**Generated:** June 17, 2026
**Scope:** Reference for **93** scripts indexed by `SCRIPTS/ORCHESTRATION_INDEXER.py` (`MASTER_ORCHESTRATION_INDEX.json`).
**Compliance:** Add · Integrate · Connect · Document · Enhance.  No deletions.  No personal-folder touch.

> **Read with:** `HOME_INDEX.md`, `TODO_TRACKER.md`, and `EXHAUSTIVE_IMPLEMENTATION_PLAN.md`.

---

## 🪙 GOLDEN RULES IN EFFECT

```
⭐ Rule #1  Nothing is obsolete — never delete any script.
⭐ Rule #2  All projects are permanent — all 93 scripts stay.
⭐ Rule #7  Enhancement not reduction — we document, never remove.
⭐ Rule #9  Add · Integrate · Connect · Document.
```

---

## 📂 SCRIPT ARCHETYPES (8 categories — derived from the 93 indexed scripts)

| # | Archetype | Purpose | Typical invocation |
|---|---|---|---|
| 1 | **Orchestrators (registry builders)** | Build the master index from on-disk artifacts | `python3 SCRIPTS/ORCHESTRATION_INDEXER.py` |
| 2 | **Launcher / dispatchers** | Multi-tool launchers | `START_MASTER_ORCHESTRATION.bat`, `SCRIPTS/COMMAND_CENTER.py` |
| 3 | **Maintenance / cleanup** | Disk health, sorted dirs | `python3 08_SCRIPTS/cleanup.py`, `disk_monitor.py`, `sort_directories.py` |
| 4 | **Audits / inspections** | Gitleaks, security audit, repo scan | `GITLEAKS_REPORT.md` re-run; `08_SCRIPTS/SECURITY_AUDIT_REPORT.md` |
| 5 | **Self-healing / fixers** | Repair, restart, recover | `STABILIZE.py`, `STABILIZE_PHASE2.py`, `verify_backups.ps1`, `self-healing` log readers |
| 6 | **Reporting / dashboards** | HTML/TSX renderers and pullers | `REVENUE_DASHBOARD.html`, `ULTIMATE_AI_EMPIRE_ENHANCED_DASHBOARD_V2.html`, `MARKETPLACE_DASHBOARD.tsx` |
| 7 | **Integrations / bridges** | Cross-service sync (Aether, GitHub) | `REVENUE_N8N_CONNECTOR.py` |
| 8 | **Catalogs / documenters** | AI doc populators | `OMNI_AUTO_DOCUMENTER.py`, `OMNI_AGGREGATOR.py`, `OMNI_CATALOGER.py`, `OMNI_DOC_POPULATOR.py` |

---

## 🔢 93 SCRIPTS — TOPIC GROUPED (additive index from orchestration)

> **Source:** `SCRIPTS/MASTER_ORCHESTRATION_INDEX.json` (built by `ORCHESTRATION_INDEXER.py` on April 18, 2026 and re-runnable any time).
> **All entries below are script pointers; each script remains on disk untouched.**

### Group 1 — Orchestrators (registry builders)
- `SCRIPTS/ORCHESTRATION_INDEXER.py` — Top-level indexer; canonical scan; re-run any time. *Producer of `MASTER_ORCHESTRATION_INDEX.json`.*

### Group 2 — Launcher / dispatcher
- `START_MASTER_ORCHESTRATION.bat` — Boot launcher (depends on ORCHESTRATION_INDEXER being up to date).
- `SCRIPTS/COMMAND_CENTER.py` — Dynamic command-center menu.

### Group 3 — Maintenance / cleanup utilities
- `08_SCRIPTS/cleanup.py`
- `08_SCRIPTS/cleanup_safe_temp.bat`
- `08_SCRIPTS/delete_npm_cache.bat`
- `08_SCRIPTS/disk_monitor.py`
- `08_SCRIPTS/sort_directories.py`
- `08_SCRIPTS/run_maintenance.sh`
- `08_SCRIPTS/verify_backups.ps1` *(built this session; not runtime-tested here)*

### Group 4 — Audits / inspections
- `08_SCRIPTS/SECURITY_AUDIT_REPORT.md` (output of an audit script)
- `08_SCRIPTS/AUDIT_COMPLETED_ACTIONS.txt` (audit log)
- `mass_reviewer.py` (root)
- `repo_audit_full.txt` (audit output)
- `repo_audit_report.md` (audit output)
- `MASTER_100_PERCENT_EXECUTION_PLAN.md` (read-only)

### Group 5 — Self-healing / state recovery
- `STABILIZE.py`
- `STABILIZE_PHASE2.py`

### Group 6 — Reporting / dashboards (HTML/TSX outputs)
- `LIVE_SYSTEM_STATUS.html`
- `REVENUE_DASHBOARD.html`
- `ULTIMATE_AI_EMPIRE_ENHANCED_DASHBOARD_V2.html`
- `COMPREHENSIVE_EMPIRE_DASHBOARD.html`
- `project_dashboard.html`
- `MARKETPLACE_DASHBOARD.tsx`
- `WEEK_1_TRACKER.html`
- `LANDING_PAGE_SECURITY_AUDIT.html`
- `UNIFIED_DASHBOARD_INDEX.html` *(built this session)*
- `BACKUP_STATUS.html` *(built this session)*

### Group 7 — Integrations / bridges
- `REVENUE_N8N_CONNECTOR.py`

### Group 8 — Catalog / documenter AI agents
- `OMNI_AUTO_DOCUMENTER.py`
- `OMNI_AGGREGATOR.py`
- `OMNI_CATALOGER.py`
- `OMNI_DOC_POPULATOR.py`

### Group 9 — Discovery / support (categorized under other groups but flagged for readability)
- `inspect_data.py`
- `inspect_44gb_gal.py`
- `search_crypto.py`
- `query_metrics.py`
- `Revenue_Tracking_System.py`
- `INSTALLATION_STATUS.md` (output)
- `install_all.ps1`
- `setup_all_ai_tools.ps1`
- `install_stack.py`
- `START-ALL-AI-TOOLS.bat`
- `temp_ram_check.ps1`
- `read_bytes.ps1`
- `scan_files.ps1`
- `scan_folders2.ps1`
- `scan_installers.ps1`
- `verify_backups.ps1`
- `verify_gal_files.py`
- `verify_gal_11checks.py`
- `triplecheck_both_gal.py`
- `test_extract_both_gal.py`
- `test_agent.py`
- `test_api_v2.py`
- `test_api_v3.py`
- `test_github_tokens.py`
- `test_provided_token.py`
- `test_transcript.py`
- `upload_docs_to_github.py`
- `Organize_bookmarks.py`
- `simple_explanation.py`
- `Master_Storage_Optimizer.ps1`
- `08_SCRIPTS/cleanup.py`
- … and many more.

> **Note:** Total scripts as reported by `ALL_OPTIONS_EXECUTION_SUMMARY.md`: **93**. The selective list above illustrates archetypes; the orchestrator's full JSON is authoritative.

---

## 🧭 HOW TO USE THIS REFERENCE

For any task in `WEEK_1_QUICKWINS.md` or `EXHAUSTIVE_IMPLEMENTATION_PLAN.md`, the typical lookup is:

1. Find the closest archetype above.
2. Inspect `MASTER_ORCHESTRATION_INDEX.json` for the exact name + invocation.
3. Run inside the right sub-folder; do **not** rename or relocate.

Example:
- "I want to verify today's backups." → Archetype 5 → `verify_backups.ps1` (NEW)
- "I want to register a recurring integrity check." → Archetype 5 → `Register-BackupTask.ps1` (NEW)

---

## 🛠️ THIS SESSION'S NEW SCRIPTS  *(append-only)*

| Script | Archetype | Invocation |
|---|---|---|
| `verify_backups.ps1` | Audits / inspections + self-healing | `powershell -ExecutionPolicy Bypass -File .\verify_backups.ps1` |
| `Register-BackupTask.ps1` | Self-healing / scheduler | Admin: `powershell -ExecutionPolicy Bypass -File .\Register-BackupTask.ps1` |
| `PROJECT_BRAIN_2_0/ingest.py` | Orchestrator (new lineage) | `python3 PROJECT_BRAIN_2_0/ingest.py --registry REPO_REGISTRY.csv --out PROJECT_BRAIN_2_0/INDEX/chunks.jsonl` |

*Note: Python3 is not available in this Windows-bash shell; runtime verification of `ingest.py` is deferred to a session where Python is reachable. The script is statically reviewed and structurally correct.*

---

## 📦 NEW FILES THIS TURN

- `INTERACTIVE_SCRIPT_MENU.md` (this file)
- `Register-BackupTask.ps1`
- `BACKUP_STATUS.html`

**No existing script removed or modified.**

---

## ✅ COMPLIANCE FOOTER

```
✅ COMPLIANCE: This artifact is ADDITIVE only.
✔ Adds: NEW reference doc + 2 new scripts. 0 modifications.
✦ Does NOT delete, archive-as-cleanup, or relabel anything.
✦ Does NOT touch Documents, Downloads, Pictures, Videos, Music, Desktop, OneDrive.
```
