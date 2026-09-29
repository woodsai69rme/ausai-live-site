# FOOTCLAN OS — System Index

> **Master entry point** for the FOOTCLAN OS documentation suite and its mapping onto the existing workspace.

| Field | Value |
|-------|-------|
| **Root** | `C:\Users\karma\FOOTCLAN_OS\` |
| **Version** | 1.0.0 |
| **Generated** | 2026-07-17 |
| **Status** | Documentation complete · Implementation-ready |
| **Philosophy** | 70% existing OSS · 20% integration · 10% custom |

---

## What Is FOOTCLAN OS?

Self-hosted AI operating system for:

- Opportunity **discovery** and **research**
- **Automation** (n8n) and **agents** (Footclan / AI Army)
- **Knowledge** (Archon + Qdrant + AnythingLLM)
- Monitoring: **AI · crypto · YouTube · social · music · music video**
- **Coding assist**, **content/media production**, **affiliate/referral/revenue**
- Path to multi-user **SaaS** (Canvases 38–40)

---

## Start Here

| Order | Document | Path |
|------:|----------|------|
| 1 | README | `FOOTCLAN_OS/README.md` |
| 2 | Master Index | `FOOTCLAN_OS/deliverables/00_MASTER_INDEX.md` |
| 3 | Executive Vision | `FOOTCLAN_OS/canvases/CANVAS_01_Executive_Vision.md` |
| 4 | Program Roadmap | `FOOTCLAN_OS/canvases/CANVAS_02_Program_Roadmap.md` |
| 5 | Full PRD | `FOOTCLAN_OS/canvases/CANVAS_03_Full_PRD.md` |
| 6 | Deployment Guide | `FOOTCLAN_OS/deliverables/DEPLOYMENT_GUIDE.md` |

### Launch core stack

```powershell
cd C:\Users\karma\FOOTCLAN_OS
copy compose\.env.example compose\.env
# edit passwords in compose\.env
docker compose -f compose/docker-compose.footclan.yml --profile core --profile monitoring up -d
```

---

## Suite Inventory

| Area | Count | Location |
|------|------:|----------|
| Canvases | **40** | `FOOTCLAN_OS/canvases/` |
| Deliverable guides/plans | **9+** | `FOOTCLAN_OS/deliverables/` |
| DB schema | 1 | `FOOTCLAN_OS/schemas/database_schema.sql` |
| Docker Compose | 1 | `FOOTCLAN_OS/compose/docker-compose.footclan.yml` |
| Agent definitions | 1 | `FOOTCLAN_OS/agents/agent_definitions.yaml` |
| Workflow catalog | 1 | `FOOTCLAN_OS/workflows/WORKFLOW_CATALOG.md` |
| Model / watch catalogs | 3 | `FOOTCLAN_OS/catalogs/` |

### Canvas map

| Range | Theme |
|-------|--------|
| 01–02 | Vision & roadmap |
| 03 | Full PRD |
| 04–06 | Technical, infrastructure, security architecture |
| 07–08 | Local AI stack & model catalog |
| 09–11 | Agents, n8n library, workflow marketplace |
| 12–14 | GitHub discovery, AI tool discovery, evaluation engine |
| 15–16 | Knowledge base & research intelligence |
| 17–19 | Crypto division |
| 20–23 | YouTube & social intelligence |
| 24–27 | Music & music video |
| 28–31 | Image/video generation & asset systems |
| 32–35 | Business & revenue |
| 36–37 | Operations |
| 38–40 | SaaS evolution |

---

## Existing Workspace Anchors (Reuse First)

| Asset | Path / Port | FOOTCLAN Role |
|-------|-------------|---------------|
| Archon V2 | `docker-compose.yml` · 8181/8051/8052/3737 | Knowledge / RAG backbone |
| AI Army | `AI_ARMY/` · 8001 | Agent fleet API |
| Footclan Executor | `FOOTCLAN_EXECUTOR.py` | Dispatch spine (dry-run default) |
| Footclan revenue plan | `FOOTCLAN_TO_REVENUE.md` | Monetization seed |
| ComfyUI studio | `C:\Users\karma\ComfyUI\` | Media / MV division |
| n8n workflows | `n8n-workflows/` | Automation seeds |
| Revenue scripts | `REVENUE_GENERATORS/` | Revenue plane |
| Agent registry | `AGENT_REGISTRY*.md` | Agent pool metadata |
| Dashboards | `UNIFIED_MASTER_DASHBOARD.html`, `AI_TOOLS_DASHBOARD.html` | Operator UX patterns |

---

## Required Stack Coverage

| Required | Documented in | Compose / Host |
|----------|---------------|----------------|
| Ollama | Canvas 07–08 | Host recommended |
| Open WebUI | Canvas 07 | compose profile `ai` |
| AnythingLLM | Canvas 07 | host/docker (document attach) |
| LM Studio | Canvas 07 | Desktop optional |
| n8n | Canvas 10–11 | compose profile `core` |
| PostgreSQL | Schema + Canvas 05 | compose `core` |
| Redis | Canvas 05 | compose `core` |
| Qdrant | Canvas 15 | compose `core` |
| Docker Compose | compose/ | yes |
| VS Code / OpenCode | PRD / ops | host |
| Prometheus / Grafana | Canvas 36 | compose `monitoring` |

---

## Final Deliverables Checklist

- [x] All 40 canvases
- [x] Complete PRD (Canvas 03)
- [x] Technical / Infrastructure / Security architecture (04–06)
- [x] Database schema
- [x] Docker Compose design
- [x] Agent definitions
- [x] Workflow catalog
- [x] GitHub + tool watchlists
- [x] Model catalog
- [x] Monetization + revenue plans
- [x] Deployment / Ops / Backup / DR guides
- [x] Testing + scalability strategies

---

## Implementation Sequence (Short)

1. **Week 1** — Compose core + monitoring; passwords; health green  
2. **Week 2** — Ollama + Open WebUI + model pulls  
3. **Week 3** — n8n WF-01/03/05/08/11; Footclan dry-run ops  
4. **Week 4** — Research + Coding agents; backup restore drill  
5. **Days 31–90** — Crypto, YouTube, knowledge scale, first revenue path  

Full detail: `canvases/CANVAS_02_Program_Roadmap.md`

---

## Related Indexes

| Index | Topic |
|-------|--------|
| `AI_ARMY_SYSTEM_INDEX.md` | Footclan / AI Army |
| `ARCHON_V2_SYSTEM_INDEX.md` | Archon knowledge OS |
| `N8N_AUTOMATION_SYSTEM_INDEX.md` | n8n |
| `REFERENCE_DOCS_INDEX.md` | YouTube / hardware research docs |
| `ALL_PLANS_AND_PROJECTS_MASTER.md` | Master plans register |

---

## Regenerating Docs

```powershell
python C:\Users\karma\FOOTCLAN_OS\_generate_suite.py
python C:\Users\karma\FOOTCLAN_OS\_enhance_domains.py
```

> Re-running `_generate_suite.py` overwrites canvases 01–40 from the generator. Prefer editing individual canvas files after v1 freeze, or update the generator first.
