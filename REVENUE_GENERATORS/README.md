# REVENUE_GENERATORS — AI Army Revenue Agent Suite

> **6 executable revenue scripts dispatchable via the AI Army API.** Each script is independently runnable and produces JSON output reports.

---

## 🚀 Quick Start

```bash
# Run any script directly
cd C:/Users/karma/REVENUE_GENERATORS
python REVENUE_DEPLOY_ENGINE.py
python AUTONOMOUS_CONTENT_FACTORY.py
python SELF_HEALING_DAEMON.py

# Or dispatch via AI Army API
curl -X POST http://localhost:8001/dispatch \
  -H "Content-Type: application/json" \
  -d '{"title":"Deploy revenue","type":"revenue","action":"deploy_revenue"}'
```

---

## 📚 Scripts

### 1. REVENUE_DEPLOY_ENGINE.py — `deploy_revenue`

Scans `REVENUE_GENERATORS/` for deployable projects (directories containing `package.json`, `main.py`, `app.py`, `pyproject.toml`, or `Cargo.toml`) and triggers deployment via the local orchestrator API.

**Output:** Deployment log to console  
**Max concurrent:** 3 deployments  
**API endpoint:** `http://localhost:8000/api/v3/revenue/deploy`

### 2. AUTONOMOUS_CONTENT_FACTORY.py — `content_factory`

Generates a weekly content plan with 5 scheduled posts across LinkedIn, Twitter/X, YouTube, Blog, and Newsletter.

**Output:** `content_plan.json`  
**Topics:** AI automation, no-code tools, productivity hacks, revenue growth

### 3. AUTONOMOUS_SAAS_LAUNCHER.py — `saas_launcher`

Scans `REVENUE_GENERATORS/` for SaaS-ready projects and generates a 6-step launch checklist for each.

**Output:** `saas_launch_manifests.json`  
**Checklist steps:** Validate env → Run tests → Build Docker → Push registry → Deploy prod → Configure monitoring

### 4. GLOBAL_BRAIN_CRAWLER.py — `brain_crawler`

Recursively crawls the home directory for indexable files (`.md`, `.txt`, `.pdf`, `.py`, `.json`, `.html`) and builds a searchable brain index.

**Output:** `brain_index.json`  
**Max files:** 100  
**Root:** `os.path.expanduser("~")`

### 5. REVENUE_SINGULARITY_ENGINE.py — `singularity`

Aggregates revenue signals from local sources (`revenue_stats.json`, `affiliate_review.md`, `saas_launch_manifests.json`, `content_plan.json`) into a unified snapshot.

**Output:** `revenue_singularity_snapshot.json`  
**Currency:** AUD

### 6. SELF_HEALING_DAEMON.py — `self_healing`

Monitors 4 critical services (AI Army :8001, n8n :5678, ComfyUI :8188, Ollama :11434) and generates a health report with healing plans for any down services.

**Output:** `healing_report.json`  
**HTTP client:** `httpx` (sync)  
**Timeout:** 5 seconds per service

---

## 🔌 AI Army Dispatch API

### List Available Actions

```bash
curl -X POST http://localhost:8001/dispatch \
  -H "Content-Type: application/json" \
  -d '{"title":"List","type":"revenue","action":"list"}'
```

### Dispatch an Action

```bash
curl -X POST http://localhost:8001/dispatch \
  -H "Content-Type: application/json" \
  -d '{
    "title": "My task",
    "type": "revenue",
    "action": "self_healing"
  }'
```

**Valid actions:** `deploy_revenue`, `content_factory`, `saas_launcher`, `brain_crawler`, `singularity`, `self_healing`, `list`

### View Reports

```bash
curl http://localhost:8001/reports
```

---

## 🏗️ Architecture

```
revenue_utils.py              # Shared: logging, REVENUE_DIR, write_json()
├── REVENUE_DEPLOY_ENGINE.py      # Async HTTP deployment (matches deploy_revenue.py style)
├── AUTONOMOUS_CONTENT_FACTORY.py # JSON content plan generator
├── AUTONOMOUS_SAAS_LAUNCHER.py   # Project scanner + launch manifests
├── GLOBAL_BRAIN_CRAWLER.py       # File system crawler + indexer
├── REVENUE_SINGULARITY_ENGINE.py # Revenue signal aggregator
└── SELF_HEALING_DAEMON.py        # Service health monitor (httpx)
```

All scripts:
- Use `revenue_utils.setup_logging()` for consistent log formatting
- Write JSON output via `revenue_utils.write_json()`
- Resolve paths via `os.path.expanduser("~")` (portable)
- Include type hints on all functions
- Handle `KeyboardInterrupt` gracefully

---

## 📊 Output Files

| File | Producer | Description |
|---|---|---|
| `content_plan.json` | content_factory | Weekly content schedule |
| `saas_launch_manifests.json` | saas_launcher | Per-project launch checklists |
| `brain_index.json` | brain_crawler | 100-file knowledge index |
| `revenue_singularity_snapshot.json` | singularity | Unified revenue dashboard |
| `healing_report.json` | self_healing | Service health + healing plans |

---

## 📝 Changelog

| Date | Change |
|---|---|
| 2026-06-29 | Created 5 stub scripts + deploy_revenue.py |
| 2026-06-29 | Refactored: shared `revenue_utils.py`, type hints, httpx, import fixes |
| 2026-06-29 | All 6 actions verified via AI Army dispatch API |

---

*Part of the AI Army (Foot Clan) system. Dispatch via `http://localhost:8001`.*
