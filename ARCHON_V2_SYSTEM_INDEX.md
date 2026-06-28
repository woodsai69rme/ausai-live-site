# 📚 ARCHON_V2_SYSTEM_INDEX.md

> **Master index for Archon V2 — the knowledge management and MCP integration platform.** Covers 4 services (FastAPI, MCP, Agents, Frontend), 10+ pages, 20+ components, and the documentation suite. Microservices architecture with Socket.IO real-time updates.

**Generated:** 2026-06-28
**Parent systems:** Project Brain 2.0, Agent Registry, AI Tools Dashboard

---

## 📁 FILE INVENTORY

### 🔷 Backend Services (Python/FastAPI)

| Service | Location | Port |
|---|---|---|
| Main Server | `python/src/server/main.py` | 8181 |
| MCP Server | `python/src/mcp/` | 8051 |
| Agents Service | `python/src/agents/` | 8052 |
| API Routes | `python/src/server/api_routes/` | — |
| Services | `python/src/server/services/` | — |
| Middleware | `python/src/server/middleware/` | — |

### 🔷 Frontend (React + TypeScript + Vite)

| Layer | Location | Port |
|---|---|---|
| App Entry | `archon-ui-main/src/App.tsx` | 3737 |
| Pages | `archon-ui-main/src/pages/` (KB, MCP, Onboarding) | — |
| Components | `archon-ui-main/src/components/` (20+) | — |
| Services | `archon-ui-main/src/services/` | — |
| Config | `archon-ui-main/package.json` | — |

### 🔷 Documentation

| Document | Purpose |
|---|---|
| `CLAUDE.md` | Development guidelines and architecture overview |
| `docs/ARCHITECTURE.md` | Full system architecture |
| `docs/COMPLETE_API_REFERENCE_v3.2.md` | API reference |
| `docs/DEPLOYMENT_GUIDE.md` | Deployment instructions |
| `docs/DEVELOPER_GUIDE_v3.2.md` | Developer guide |
| `docs/INTEGRATION_GUIDE.md` | Integration guide |
| `docs/SECURITY_GUIDE_COMPLETE.md` | Security guide |
| `docs/RELEASE_NOTES_V3.2.0.md` | Release notes |

---

## 🖥️ PORTS & SERVICES

| Port | Service | Framework |
|---|---|---|
| 3737 | Frontend (Vite dev) | React + TypeScript + TailwindCSS |
| 8181 | Main Server | FastAPI + Socket.IO |
| 8051 | MCP Server | HTTP-based MCP protocol |
| 8052 | Agents Service | PydanticAI agents |

---

## 🏗️ ARCHITECTURE

```
Browser (port 3737)
     │
     ▼
React Frontend (Vite + TailwindCSS)
     │
     ├──► API calls → Main Server (FastAPI, port 8181)
     │         │
     │         ├──► Knowledge Base (crawl, upload, RAG search)
     │         ├──► Projects & Tasks (optional)
     │         ├──► MCP Tools (execute, list)
     │         │
     │         ├──► MCP Server (port 8051)
     │         │      └── Model Context Protocol tools
     │         │
     │         └──► Agents Service (port 8052)
     │                └── PydanticAI agents for AI/ML
     │
     └──► Socket.IO (real-time)
              ├── crawl_progress
              ├── project_creation_progress
              ├── task_update
              └── knowledge_update
```

---

## 🗄️ DATABASE

| System | Purpose |
|---|---|
| Supabase (PostgreSQL) | Primary database |
| pgvector | Embedding storage for RAG |
| ChromaDB | Alternative vector store |

### Key Tables
`sources`, `documents`, `projects`, `tasks`, `code_examples`

---

## 🧩 FRONTEND STRUCTURE

| Directory | Purpose |
|---|---|
| `components/` | Reusable UI: animations, code, jarvis, knowledge-base, mcp, prp |
| `pages/` | Knowledge Base, MCP, Onboarding |
| `services/` | API communication, jarvisService, business logic |
| `hooks/` | Custom React hooks |
| `contexts/` | React context providers |
| `config/` | Application configuration |
| `lib/` | Utility libraries |
| `types/` | TypeScript type definitions |

### Key Libraries
- **Milkdown** — Rich text editing
- **XYFlow** — Node-based graph visualization
- **Vitest** — Testing framework

---

## 🚀 DEVELOPMENT COMMANDS

```bash
# Frontend
cd archon-ui-main && npm run dev        # Dev server on port 3737
cd archon-ui-main && npm run build      # Production build
cd archon-ui-main && npm run test       # Vitest tests

# Backend
cd python && uv sync                    # Install dependencies
cd python && uv run pytest              # Run tests
uv run python -m src.server.main        # Run server

# Docker
docker-compose up --build -d            # Start all services
docker-compose logs -f                  # View logs
```

---

## 🔌 KEY API ENDPOINTS

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/api/knowledge/crawl` | Crawl a website |
| `POST` | `/api/knowledge/upload` | Upload documents (PDF, DOCX, MD) |
| `GET` | `/api/knowledge/items` | List knowledge items |
| `POST` | `/api/knowledge/search` | RAG search |
| `GET` | `/api/mcp/health` | MCP server status |
| `POST` | `/api/mcp/tools/{tool}` | Execute MCP tool |
| `GET` | `/api/mcp/tools` | List available tools |
| `GET` | `/api/projects` | List projects (optional) |
| `POST` | `/api/projects` | Create project (optional) |

### MCP Tools Available
`archon:perform_rag_query`, `archon:search_code_examples`, `archon:manage_project`, `archon:manage_task`, `archon:get_available_sources`

---

## 🔒 SECURITY BOUNDARIES

- **OpenRouter only:** All AI requests route through OpenRouter — no direct provider keys
- **Supabase RLS:** Row-level security on database
- **Rule #8 fence:** Crawler excludes personal folders from ingestion
- **Auth middleware:** Token-based authentication with rate limiting

---

## 🔗 CROSS-REFERENCES

| System | Index |
|---|---|
| Project Brain 2.0 | `PROJECT_BRAIN_2_0_SYSTEM_INDEX.md` |
| Agent Registry | `AGENT_REGISTRY_SYSTEM_INDEX.md` |
| AI Tools Dashboard | `AI_TOOLS_DASHBOARD.html` |
| Workspace Master | `WORKSPACE_INDEX.md` |

---

*Designed under Golden Rules: append, never delete; preserve, never relabel; protect, never rewrite.*
