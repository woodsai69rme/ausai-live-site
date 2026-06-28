# ⚙️ N8N_AUTOMATION_SYSTEM_INDEX.md

> **Master index for n8n automation stack.** Covers 4 components — Docker stack, workflow templates, revenue webhook connector, and local .n8n config. Automation bridge between revenue systems, Ollama AI pipeline, and webhook-driven workflows.

**Generated:** 2026-06-28
**Parent systems:** Revenue Dashboard, Agent Registry, AI Tools Dashboard

---

## 📁 FILE INVENTORY (4 components)

| Component | Location | Purpose |
|---|---|---|
| Docker stack | `n8n-automation-stack/docker-compose.yml` | Orchestrates n8n via Docker — single-file deployment |
| Workflow templates | `n8n-templates/workflows/` | 91 workflow templates for automation patterns |
| Revenue connector | `REVENUE_N8N_CONNECTOR.py` | Python bridge: revenue projects → n8n webhooks |
| Local config | `.n8n/` (10 items) | n8n runtime config, credentials, local state |

---

## 🔌 WEBHOOK ENDPOINTS (REVENUE_N8N_CONNECTOR.py)

| Webhook | Purpose |
|---|---|
| `/webhook/revenue/status` | Revenue project status updates |
| `/webhook/revenue/metrics` | Revenue project metrics push |
| `/webhook/ollama/generate` | AI coding pipeline trigger via Ollama |

---

## 🏗️ ARCHITECTURE

```
Revenue_Tracking_System.py ──► REVENUE_N8N_CONNECTOR.py
                                      │
                                      ├─► /webhook/revenue/status  ──┐
                                      ├─► /webhook/revenue/metrics ──┤
                                      └─► /webhook/ollama/generate  ──┤
                                                                       │
                                                                       ▼
                                                              n8n (port 5678)
                                                                       │
                                                          ┌────────────┼────────────┐
                                                          ▼            ▼            ▼
                                                    Docker stack   Templates    .n8n config
```

---

## 🚀 DEPLOYMENT

```bash
# Start n8n via Docker
cd n8n-automation-stack && docker-compose up -d
# Access at http://localhost:5678

# Test revenue connector
python REVENUE_N8N_CONNECTOR.py
```

---

## 🔒 SECURITY BOUNDARIES

- **Rule #8 fence:** Connector and workflows operate outside personal folders.
- **Credentials:** Stored in `.n8n/` (gitignored) — never committed.
- **Additive:** Templates and workflows are append-only.

---

## 🔗 CROSS-REFERENCES

| System | Index |
|---|---|
| Revenue Dashboard | `Revenue_Dashboard_Static.html` |
| Agent Registry | `AGENT_REGISTRY_SYSTEM_INDEX.md` |
| AI Tools Dashboard | `AI_TOOLS_DASHBOARD.html` |
| Workspace Master | `WORKSPACE_INDEX.md` |

---

*Designed under Golden Rules: append, never delete; preserve, never relabel; protect, never rewrite.*
