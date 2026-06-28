# 📂 WORKSPACE_ORGANIZATION_PLAN.md

> **Plan for organizing 318 .md + 78 .py + 40 .ps1 + 34 .html + 22 .json top-level files into logical project directories.** Non-destructive — nothing deleted, only moved. Respects Golden Rules #1, #2, #3, #7, #9.

**Generated:** 2026-06-28

---

## ⚠️ GOLDEN RULES — NON-NEGOTIABLE

```
⭐ Rule #1  NOTHING IS OBSOLETE
⭐ Rule #2  ALL PROJECTS ARE PERMANENT
⭐ Rule #3  ALL AI TOOLS ARE ESSENTIAL
⭐ Rule #7  ENHANCEMENT NOT REDUCTION
⭐ Rule #9  ADD · INTEGRATE · CONNECT · DOCUMENT
```

**No file is deleted. No file is renamed. Files are only moved into project directories.**

---

## 📊 CURRENT STATE

| Type | Count | Location |
|---|---|---|
| .md files | 318 | Top-level |
| .py files | 78 | Top-level |
| .ps1 files | 40 | Top-level |
| .html files | 34 | Top-level |
| .json files | 22 | Top-level |
| **Total top-level** | **492** | Root (C:\Users\karma\) |

| Existing project dir | Items | Purpose |
|---|---|---|
| `ACTIVE_PROJECTS/` | 102 | Active projects |
| `_DOCS_ARCHIVE/` | 65 | Archived documentation |
| `DASHBOARD_SYSTEM_SCRIPTS/` | 61 | Dashboard scripts |
| `_LAUNCHER_ARCHIVE/` | 55 | Launcher configs |
| `SCRIPTS/` | 30 | General scripts |
| `TOOLS/` | 25 | Tool configs |
| `08_SCRIPTS/` | 12 | Script batch #8 |
| `COMPLETED_PROJECTS/` | 9 | Finished projects |
| `_LOGS_ARCHIVE_2026/` | 8 | Old logs |
| `_archive_2026-06-25/` | 7 | Recent archive |
| `04_DEVELOPMENT/` | 4 | Dev phase #4 |
| `01_AI_DEVELOPMENT/` | 3 | Dev phase #1 |
| `ARCHIVED_PROJECTS/` | 1 | Old projects |

---

## 🗂️ ORGANIZATION MAP

### Phase 1: Already Organized ✅

These files are committed and documented — move nothing:

| System | Files | Status |
|---|---|---|
| AusAI Tech | 80 files | ✅ Committed (`90cd2f6a`) |
| Agent Registry | 14 files | ✅ Committed (`fe9c4c1b`) |
| AI Army / Footclan | 16 files | ✅ Committed (`4e8d4081`) |
| Voice PA | 8 files | ✅ Committed (`48b32d14`) |
| Aether Core | 3 files | ✅ Committed (`48b32d14`) |
| ComfyUI | In `ComfyUI/` | ✅ Committed (`6029c488`) |
| System Indexes | 7 files | ✅ Committed |

### Phase 2: Move System Documentation → `_DOCS_ARCHIVE/`

These are self-contained documentation files with no runtime dependencies:

| Category | Files (~114) | Move to |
|---|---|---|
| PHASE_* docs | `PHASE1_TEST_RESULTS.md`, `PHASE2_INTEGRATION_PLAN.md`, `PHASE3_ENHANCEMENT_PLAN.md`, `PHASE4_DOCUMENTATION_PLAN.md`, `PHASE5_REORGANIZE_PLAN.md`, `PHASE6_EXPANSION.md`, `PHASE6_EXPANSION_PLAN.md`, `PHASES_1-4_STATUS.md` | `_DOCS_ARCHIVE/phase_docs/` |
| PROJECT_* reports | `PROJECT_AUDIT_BATCH_1.txt`, `PROJECT_BRAIN_2_0_SPEC.md`, `PROJECT_BRAIN_PHASE_A_REPORT.md`, `PROJECT_COMPLETE_DOCUMENTATION.md`, `PROJECT_STATUS_REPORT.md` | `_DOCS_ARCHIVE/project_reports/` |
| COMPLETE_* docs | `COMPLETE_ENHANCEMENTS_MENU.md`, `COMPLETE_MASTER_ACTION_PLAN.md`, `COMPLETE_NEXT_STEPS.md`, `COMPLETE_OPTIONS_AND_NEXT_STEPS.md`, `COMPLETE_RESEARCH_AI_REVIEW_OPTIONS.md`, `COMPLETE_SYSTEM_*` | `_DOCS_ARCHIVE/complete_docs/` |
| MCP_* docs | `MCP_REGISTRY.md`, `MCP_REMOTE_QUERY.md`, `MCP_SERVER_COMPLETION.md`, `MCP_SERVER_FULL_DOCUMENTATION.md`, `MCP_SERVER_OPTIMIZED.md`, `MCP_SERVER_SETUP_SUMMARY.md`, `MCP_REMOTE_QUERY.ps1` | `_DOCS_ARCHIVE/mcp_docs/` |
| SETUP_* docs | `ALL-SETUP-COMPLETE.md`, `ALL-TOOLS-CONFIGURED.md`, `ALL-TOOLS-SETUP-SUMMARY.md`, `QWEN_SETUP_COMPLETE.md`, `QWEN_SETUP_COMPLETE_FINAL.md`, `START_HERE.md` | `_DOCS_ARCHIVE/setup_docs/` |
| OPEN* docs | `OPENCODE_ALL_OPTIONS.md`, `OPENCODE_COMPLETE_GUIDE.md`, `OPENCODE_CONFIG.md`, `OPENCODE_FULL_DOCUMENTATION.md`, `OPENCODE_MASTER.md`, `OPENCODE_SUMMARY.md`, `OPENCLAW_HERMES_SETUP_AND_RESEARCH.md` | `_DOCS_ARCHIVE/opencode_docs/` |
| ULTIMATE_* docs | `ULTIMATE_AI_DEEP_DIVE_2026.md`, `ULTIMATE_GUIDE_ALL_OPTIONS_DETAILED.md`, `ULTIMATE_KNOWLEDGE_AND_QA_CODEX.md`, `ULTIMATE_OMNI_EXECUTION_PROTOCOL_2026.md` | `_DOCS_ARCHIVE/ultimate_docs/` |
| WEEK_* plans | `WEEK_1_ACTION_PLAN.md`, `WEEK_1_QUICKWINS.md`, `WEEK_3_4_EXECUTION_PLAN.md`, `WHATS_NEXT_ALL_OPTIONS.md`, `WHATS_NEXT_GUIDE.md` | `_DOCS_ARCHIVE/weekly_plans/` |
| README_* variants | `README-QUICK-REF.md`, `README_GOD_MODE.md`, `README_QUICK_START.md`, `README_QWEN_SETUP.md`, `README_template.md` | `_DOCS_ARCHIVE/readme_variants/` |
| OPTIMIZATION_* | `OPTIMIZATION_COMPLETE_2026-03-04.md` | `_DOCS_ARCHIVE/` |
| OPTION_* docs | `OPTION_4_SETUP_GUIDE.md` | `_DOCS_ARCHIVE/` |
| ORACLE_* docs | `ORACLE_JARVIS_PAPERCLIP_SETUP.md` | `_DOCS_ARCHIVE/` |
| ORCHESTRATION_* | `ORCHESTRATION_LEARNINGS.md` | `_DOCS_ARCHIVE/` |
| PERFORMANCE_* | `PERFORMANCE_BENCHMARK_RESULTS.md` | `_DOCS_ARCHIVE/` |
| PLUGIN_* | `PLUGIN_SYSTEM_SUMMARY.md` | `_DOCS_ARCHIVE/` |
| PRODUCTION_* | `PRODUCTION_CONFIG.md`, `PRODUCTION_DEPLOYMENT_CONFIG.md`, `PRODUCTION_READINESS_CERTIFICATE.md` | `_DOCS_ARCHIVE/` |
| REVIEW_* | `REVIEW_PROGRESS_LIVE.md` | `_DOCS_ARCHIVE/` |
| ROADMAP_* | `ROADMAP_ULTIMATE.md` | `_DOCS_ARCHIVE/` |
| ROGUE_SUN_* | `ROGUE_SUN_STATE_REPORT.md` | `_DOCS_ARCHIVE/` |
| SECURITY_* | `SECURITY_VALIDATION_REPORT.md`, `SERVICE_AI_SECURITY_AUDIT.md` | `_DOCS_ARCHIVE/` |
| SELF_TEST_* | `SELF_TEST_RUN.md` | `_DOCS_ARCHIVE/` |
| SERVERS_* | `SERVERS_RUNNING_STATUS.md` | `_DOCS_ARCHIVE/` |
| SESSION_* | `SESSION_COMPLETE_LOG.md` | `_DOCS_ARCHIVE/` |
| SINGULARITY_* | `SINGULARITY_COMPLETION_REPORT.md`, `SINGULARITY_DEPLOYMENT_OPTIONS.md`, `SINGULARITY_MASTER_EXECUTION_PLAN.md` | `_DOCS_ARCHIVE/` |
| SOVEREIGN_* | `SOVEREIGN_EXECUTION_REPORT.md` | `_DOCS_ARCHIVE/` |
| STORAGE_* | `STORAGE_OPTIMIZATION_RECOMMENDATION.md` | `_DOCS_ARCHIVE/` |
| SYSTEM_* | `SYSTEM_DOMINATION_OPTIONS.md`, `SYSTEM_QUICK_REFERENCE.md` | `_DOCS_ARCHIVE/` |
| TASK_* | `TASK_COMPLETION_SUMMARY.md` | `_DOCS_ARCHIVE/` |
| THE_OMNI_* | `THE_OMNI_PORT_AND_TOOL_REGISTER_2026.md` | `_DOCS_ARCHIVE/` |
| TOOL_* | `TOOL_COMPARISON.md` | `_DOCS_ARCHIVE/` |
| TODO_* | `TODO_TRACKER.md` | `_DOCS_ARCHIVE/` |
| UX_UI_* | `UX_UI_ELITE_AUDIT.md` | `_DOCS_ARCHIVE/` |
| VOICE_* docs | `VOICE_PA_BRIDGE.md` (keep in Voice PA system?) | Already tracked |
| YOUTUBE_* docs | `YOUTUBE-ENHANCEMENTS.md`, `youtube_transcript_harvest.md`, `YOUTUBE_TRANSCRIPT_HARVEST_DESIGN.md` | `_DOCS_ARCHIVE/youtube_docs/` |
| QWEN_* docs | `QWEN_ADDITIONAL_SUGGESTIONS.md`, `QWEN_CODE_INDEX.md`, `QWEN_FINAL_SUMMARY.md`, `QWEN_QUICK_REFERENCE.md`, `QWEN_RECOMMENDATIONS.md`, `QWEN_WHAT_NEXT_GUIDE.md` | `_DOCS_ARCHIVE/qwen_docs/` |
| ALL_OPTIONS_* | `ALL_OPTIONS_COMPLETED.md`, `ALL_OPTIONS_EXECUTION_PLAN.md`, `ALL_OPTIONS_EXECUTION_SUMMARY.md`, `ALL_OPTIONS_MENU.md`, `ALL_OPTIONS_PROCEEDED_SUMMARY.md` | `_DOCS_ARCHIVE/all_options/` |
| ALL_SYSTEMS_* | `ALL_SYSTEMS_GO.md` | `_DOCS_ARCHIVE/` |
| AMD-NVIDIA_* | `AMD-NVIDIA-GPU-SETUP.md` | `_DOCS_ARCHIVE/` |
| API_* docs | `API_KEY_REGISTRY.json`, `API_KEY_ROTATION.md`, `API_REFERENCE.md` | `_DOCS_ARCHIVE/api_docs/` |
| APPEND_ONLY_* | `APPEND_ONLY_HYGIENE_RUNNER.md` | `_DOCS_ARCHIVE/` |
| ARCHON_* | `ARCHON_CODEBASE_REVIEW.md`, `ARCHON_COMPREHENSIVE_ANALYSIS.md` | `_DOCS_ARCHIVE/` |
| AUDIT_* | `AUDIT_SESSION_LOG.md`, `AUDIT_SUMMARY_2026-03-04.md` | `_DOCS_ARCHIVE/` |
| AWESOME_* | `AWESOME_INDEX.md` | `_DOCS_ARCHIVE/` |
| AI_ECOSYSTEM_* | `AI_ECOSYSTEM_GUIDE.md`, `AI_POWERED_SYSTEM_REVIEW.md` | `_DOCS_ARCHIVE/` |
| AI-Models_* | `AI-Models-Complete-Guide-2026.md`, `AI-Models-Complete-Guide-2026-FULL.md` | `_DOCS_ARCHIVE/` |
| AI_VOICE_PA* | `AI_VOICE_PA.md`, `AI_VOICE_PA_DESIGN.md` | Already in Voice PA system |
| BACKUP_* | `BACKUP_AUDIT_RUN.md`, `BACKUP_STATUS.html` | `_DOCS_ARCHIVE/` |
| CLEANUP_* | `CLEANUP_INVENTORY.md`, `CLEANUP_OPTIONS_EXPLAINED.md` | `_DOCS_ARCHIVE/` |
| BOOKMARK_* | `BOOKMARK_MANAGER_PRO/` | Already in subdir |
| BUILD_* | `Build_EmpireOS.py` | `_DOCS_ARCHIVE/` |
| APPEND-* | `Append-RevenueAggregator.md` | `_DOCS_ARCHIVE/` |
| ARCHIVE_* | `ARCHIVE_OLD_INVESTIGATION.md` | `_DOCS_ARCHIVE/` |
| BRAND_* | `BRAND_IDENTITY.md` | `_DOCS_ARCHIVE/` |

### Phase 3: Move Scripts → `SCRIPTS/` or `08_SCRIPTS/`

| Category | Files (~78 .py + 40 .ps1) | Move to |
|---|---|---|
| .ps1 scripts | `*.ps1` files (scan, verify, register, test, etc.) | `SCRIPTS/powershell/` |
| .py utility scripts | `test_*.py`, `verify_*.py`, `search_*.py`, `run_*.py`, `organize_*.py`, `query_*.py`, `simple_*.py` | `SCRIPTS/python/` |
| .bat launchers | `*.bat` files (start, launch, run, etc.) | `SCRIPTS/batch/` |
| OMNI_* scripts | `OMNI_AGGREGATOR.py`, `OMNI_AUTO_DOCUMENTER.py`, `OMNI_CATALOGER.py`, `OMNI_DOC_POPULATOR.py` | `SCRIPTS/omni/` |
| Revenue scripts | `Revenue_Tracking_System.py`, `REVENUE_N8N_CONNECTOR.py` | `ACTIVE_PROJECTS/revenue/` |
| AI scripts | `AETHER_SYNC_BRIDGE.py`, `VOICE_PA_BRIDGE.py`, `ARCHON_MEMORY_INGESTION.py`, `AUTO_ENHANCER.py`, `ai_voice_pa.py`, `STABILIZE.py`, `STABILIZE_PHASE2.py` | Keep at root (cross-system dependencies) or `SCRIPTS/ai_bridges/` |
| test_agent.py | `test_agent.py` | `SCRIPTS/python/` |

### Phase 4: Move HTML Tools → `TOOLS/` or `ACTIVE_PROJECTS/`

| Category | Files (~34 .html) | Move to |
|---|---|---|
| Revenue dashboards | `Revenue_Dashboard_Static.html`, `REVENUE_DASHBOARD.html`, `REVENUE_READINESS_REPORT.md`, `REVENUE_TRACKING_DESIGN.md`, `REVENUE_STATUS_*.csv` | Already in AusAI — committed |
| ULTIMATE dashboard | `ULTIMATE_AI_EMPIRE_ENHANCED_DASHBOARD_V2.html` | `ACTIVE_PROJECTS/ultimate_empire/` |
| UNIFIED dashboard | `UNIFIED_DASHBOARD_INDEX.html` | `ACTIVE_PROJECTS/dashboards/` |
| Project dashboard | `project_dashboard.html` | `ACTIVE_PROJECTS/dashboards/` |
| REAL_TIME dashboard | `REAL_TIME_DASHBOARD.md` | `ACTIVE_PROJECTS/dashboards/` |
| WEEK_1 tracker | `WEEK_1_TRACKER.html` | `_DOCS_ARCHIVE/weekly_plans/` |
| API_USAGE | `API_USAGE.html` | `_DOCS_ARCHIVE/api_docs/` |
| BACKUP_STATUS | `BACKUP_STATUS.html` | `_DOCS_ARCHIVE/` |
| AI_TOOLS_DASHBOARD | `AI_TOOLS_DASHBOARD.html` | Keep at root (system index) |

### Phase 5: Move JSON/CSV Data → `_DOCS_ARCHIVE/data/`

| Category | Files | Move to |
|---|---|---|
| .json configs | `*.json` files (not in subdirs) | `_DOCS_ARCHIVE/data/` or `SCRIPTS/data/` |
| .csv reports | `*.csv` files | `_DOCS_ARCHIVE/data/` |

### Phase 6: Files NOT to Move (cross-system dependencies)

| File | Reason |
|---|---|
| `AI_TOOLS_DASHBOARD.html` | System index — cross-references all tools |
| `MASTER_INDEX_1PAGE.md` | Primary reference — printed and used daily |
| `CHANGELOG.md` | Cross-system history |
| `CLAUDE.md` | Required by Claude/Codebuff at root |
| `README.md` | Repo root README |
| `.gitignore` | Git config — must be root |
| `package.json` | Project manifest |
| `pyproject.toml` | Python project config |
| `uv.lock` | Python lockfile |
| `sitemap.xml` | SEO — root required |
| `MIT_LICENSE` | License — root |
| `.github/` | GitHub Actions — required location |

---

## 🚀 EXECUTION ORDER (lowest risk first)

### Batch 1: Safe — pure docs, zero dependencies
```bash
# Move MCP docs (purely reference material)
mkdir -p _DOCS_ARCHIVE/mcp_docs
move MCP_REGISTRY.md MCP_SERVER_*.md MCP_REMOTE_QUERY.* _DOCS_ARCHIVE/mcp_docs/

# Move week plans
mkdir -p _DOCS_ARCHIVE/weekly_plans
move WEEK_*.md WHATS_NEXT_*.md _DOCS_ARCHIVE/weekly_plans/

# Move setup docs
mkdir -p _DOCS_ARCHIVE/setup_docs
move ALL-SETUP-*.md ALL-TOOLS-*.md START_HERE.md QWEN_SETUP_*.md _DOCS_ARCHIVE/setup_docs/

# Move OPENCODE docs
mkdir -p _DOCS_ARCHIVE/opencode_docs
move OPENCODE_*.md OPENCLAW_*.md _DOCS_ARCHIVE/opencode_docs/
```

### Batch 2: Moderate — grouped docs
```bash
mkdir -p _DOCS_ARCHIVE/phase_docs
move PHASE*.md PHASES_*.md _DOCS_ARCHIVE/phase_docs/

mkdir -p _DOCS_ARCHIVE/project_reports
move PROJECT_*.md PROJECT_*.txt _DOCS_ARCHIVE/project_reports/

mkdir -p _DOCS_ARCHIVE/ultimate_docs
move ULTIMATE_*.md _DOCS_ARCHIVE/ultimate_docs/

mkdir -p _DOCS_ARCHIVE/qwen_docs
move QWEN_*.md _DOCS_ARCHIVE/qwen_docs/

mkdir -p _DOCS_ARCHIVE/all_options
move ALL_OPTIONS_*.md _DOCS_ARCHIVE/all_options/
```

### Batch 3: Scripts — run a test first
```bash
mkdir -p SCRIPTS/powershell
move *.ps1 SCRIPTS/powershell/  # Check none are in PATH first
```

---

## 🛡️ SAFETY RULES

1. **Never `del` or `rm`.** Only `move` (Windows) or `mv` (bash).
2. **Test one batch at a time.** Run `git status` after each batch to confirm only moves.
3. **Update cross-references after moves.** Search for old paths and update them.
4. **Update MASTER_INDEX_1PAGE.md** last, to reflect new locations.
5. **Commit after each batch** with descriptive message.
6. **Keep a recovery log** — save the `move` commands executed so you can undo.

---

## 📏 ESTIMATED IMPACT

| Phase | Files moved | Risk | Time |
|---|---|---|---|
| Batch 1: Safe docs | ~30 | Low | 5 min |
| Batch 2: Grouped docs | ~80 | Low | 10 min |
| Batch 3: Scripts | ~120 | Medium (PATH issues) | 15 min |
| Batch 4: HTML tools | ~20 | Medium | 5 min |
| Batch 5: Data files | ~44 | Low | 5 min |
| Batch 6: Update refs + commit | n/a | Low | 15 min |
| **Total** | **~294** | | **~55 min** |

---

*Designed under the user's Golden Rules: append, never delete; preserve, never relabel; protect, never rewrite.*
