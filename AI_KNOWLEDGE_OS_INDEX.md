# AI Knowledge Operating System - Master Index

**Generated:** 2026-07-18  
**Architecture:** Five Pillars Integrated System

---

## Five Core Pillars

| Pillar | Description | API Routes | Frontend |
|--------|-------------|------------|----------|
| **Research Intelligence** | Collect from web, GitHub, YouTube, Reddit, PDFs | `/api/research/*` | `/research` |
| **Knowledge & RAG** | Semantic search, embeddings, document QA | `/api/knowledge/*` | `/` |
| **Media & Digital Assets** | ComfyUI integration, asset management | `/api/media/*` | (coming) |
| **Project & Business** | Tasks, milestones, SOPs, client work | `/api/projects/*` | `/projects` |
| **AI Workspace & Automation** | Models, agents, workflows, prompts | `/api/ai/*` | (coming) |

---

## Service Architecture

```
Browser (port 3737)
    │
    ▼
React Frontend (Vite + TailwindCSS)
    │
    ├──► Knowledge Base (RAG search, upload)
    ├──► Research Intelligence (RSS, Reddit, GitHub, YouTube)
    ├──► Media & DAM (ComfyUI, assets)
    ├──► AI Workspace (models, agents, workflows)
    │
    ▼
Main Server (FastAPI + Socket.IO, port 8181)
    │
    ├──► MCP Server (port 8051) - tools & context
    ├──► Agents Service (port 8052) - PydanticAI agents
    └──► Supabase (PostgreSQL + pgvector)
```

---

## Available API Endpoints

### Research Intelligence (`/api/research/*`)
- `GET /status` - Service status
- `POST /rss` - Fetch RSS feed
- `POST /reddit` - Fetch subreddit posts
- `POST /github` - Fetch repo documentation
- `GET /youtube/{video_id}` - Fetch transcript

### Knowledge & RAG (`/api/knowledge/*`)
- `GET /items` - List knowledge items
- `POST /crawl` - Crawl website
- `POST /upload` - Upload document
- `POST /search` - RAG query
- `GET /sources` - Available sources

### Media & DAM (`/api/media/*`)
- `GET /status` - ComfyUI status
- `POST /generate` - Generate media
- `GET /assets` - List assets

### AI Workspace (`/api/ai/*`)
- `GET /models` - List all models
- `GET /models/{provider}` - Provider-specific models
- `POST /prompt` - Run prompt
- `GET /agents` - List agents
- `POST /agent/{id}` - Run agent
- `GET /workflows` - List workflows

### MCP Integration (`/api/mcp/*`)
- `GET /health` - MCP server status
- `POST /tools/{tool}` - Execute tool
- `GET /tools` - List tools

### Projects (`/api/projects/*`)
- `GET /` - List projects
- `POST /` - Create project
- `GET /{id}/tasks` - Get tasks
- `POST /{id}/tasks` - Create task

---

## Live Services Status

| Port | Service | Status |
|------|---------|--------|
| 3737 | Frontend (React/Vite) | ✅ Running |
| 8181 | Main Server (FastAPI) | ✅ Running |
| 8051 | MCP Server | ✅ Running |
| 8052 | Agents Service | ✅ Running |
| 8188 | ComfyUI | ⚠️ Check via /api/media/status |

---

## Files Created/Modified

### Backend (Python)
- `src/server/api_routes/research_api.py` - NEW Research Intelligence endpoints
- `src/server/api_routes/media_api.py` - NEW Media & DAM endpoints
- `src/server/api_routes/ai_workspace_api.py` - NEW AI Workspace endpoints
- `src/server/main.py` - Updated routers

### Frontend (React/TypeScript)
- `src/pages/ResearchPage.tsx` - NEW Research page
- `src/App.tsx` - Added /research route
- `src/components/layouts/SideNavigation.tsx` - Added Research nav item

### Master Dashboard
- `AI_KNOWLEDGE_OS_DASHBOARD.html` - Glassmorphic overview dashboard

---

## Quick Start

```bash
# Start all services
START_ARCHON_STACK.bat

# Run frontend dev server
cd archon-ui-main && npm run dev

# Test new endpoints
curl http://localhost:8181/api/research/status
curl http://localhost:8181/api/media/status
curl http://localhost:8181/api/ai/models
```

---

## Integration Points

1. **ComfyUI Media Studio** - Port 8188, access via `/api/media/*`
2. **Supabase Database** - Knowledge storage, pgvector embeddings
3. **OpenRouter** - Cloud AI models (all routed through)
4. **Ollama** - Local AI models (9 installed)
5. **MCP Tools** - YouTube, GitHub, RAG modules