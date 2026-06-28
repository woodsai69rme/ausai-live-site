# Complete Project Documentation

## Overview

This document captures all the work completed for setting up and configuring Kilo CLI, MCP servers, skills, and best coding practices for this project.

---

## 1. MCP Server Fixes

### Issues Fixed

#### 1.1 Missing Import in mcp_server.py
**File**: `python/src/mcp/mcp_server.py`

**Problem**: Missing `field` import from dataclasses module
```python
# Before (broken):
from dataclasses import dataclass

# After (fixed):
from dataclasses import dataclass, field
```

#### 1.2 Non-existent Module References
**Problem**: References to modules that don't exist:
- `serena_integration_module`
- `claude_context_module`  
- `spec_driven_development_module`

**Solution**: These modules were conditionally disabled in `.env`:
```
SERENA_ENABLED=false
CLAUDE_CONTEXT_ENABLED=false
SPEC_DRIVEN_DEVELOPMENT_ENABLED=false
```

#### 1.3 Type Annotations in RAG Module
**File**: `python/src/mcp/modules/rag_module.py`

**Problem**: Missing `Optional` type for nullable parameters in tool functions

**Solution**: Added proper Optional type hints:
```python
# Before:
def get_available_sources(source: str = None)

# After:
def get_available_sources(source: Optional[str] = None)
```

---

## 2. Test Infrastructure

### Test File Created
**Location**: `python/tests/test_mcp_server.py`

### Test Cases (5 tests)

1. **test_mcp_server_import** - Verifies MCP server module can be imported
2. **test_mcp_server_initialization** - Verifies MCP server initializes correctly
3. **test_mcp_tool_registration** - Verifies all tools are registered with correct names:
   - `get_available_sources`
   - `perform_rag_query`
   - `search_code_examples`
4. **test_rag_tool_signatures** - Verifies tool parameters are correct
5. **test_module_imports** - Verifies all related modules can be imported

### Running Tests
```bash
cd python
python -m pytest tests/test_mcp_server.py -v
```

---

## 3. Environment Configuration

### Environment File
**Location**: `python/.env`

### Configuration Variables

| Variable | Value | Description |
|----------|-------|-------------|
| ARCHON_SERVER_PORT | 8181 | Main server port |
| ARCHON_MCP_PORT | 8051 | MCP server port |
| ARCHON_AGENTS_PORT | 8052 | Agents service port |
| ARCHON_UI_PORT | 3737 | Frontend UI port |
| SUPABASE_URL | https://example.supabase.co | Database URL |
| SUPABASE_SERVICE_KEY | example-key | Database service key |
| OPENROUTER_API_KEY | - | AI routing (required) |
| LOGFIRE_TOKEN | - | Observability (optional) |
| DEBUG_MODE | false | Debug flag |
| ARCHON_ENV | development | Environment |
| CORS_ORIGINS | http://localhost:3737 | CORS settings |
| SOCKETIO_CORS_ORIGINS | http://localhost:3737 | Socket.IO CORS |
| USE_AGENTIC_RAG | true | Enable RAG |
| PROJECTS_ENABLED | false | Projects feature |
| SERENA_ENABLED | false | Serena integration |
| CLAUDE_CONTEXT_ENABLED | false | Claude context |
| SPEC_DRIVEN_DEVELOPMENT_ENABLED | false | Spec-driven dev |

---

## 4. Kilo CLI Setup

### Installation
- **Method**: Bun package manager
- **Version**: 5.10.x
- **Location**: `.config/kilo/`

### Configuration File
**Location**: `.claude.json`

### MCP Servers Configured

#### Archon MCP Server
```json
{
  "mcpServers": {
    "archon-mcp": {
      "command": "python",
      "args": ["-m", "src.mcp.mcp_server"],
      "env": {
        "ARCHON_MCP_PORT": "8051"
      }
    }
  }
}
```

#### Additional MCP Servers
- **filesystem**: Access local filesystem
- **github**: GitHub integration

---

## 5. Skills System

### Available Skills Categories

#### Cloud & Infrastructure (50+ skills)
- Azure: Compute, AI, Storage, Observability, etc.
- AWS: Various AWS services
- GCP: Google Cloud Platform
- Kubernetes: K8s manifests, security

#### Security (40+ skills)
- Authentication patterns
- Compliance (GDPR, PCI)
- Security auditing
- Threat modeling

#### Development (60+ skills)
- Python: Design patterns, testing, type safety
- JavaScript/TypeScript
- React/Next.js
- Node.js backend

#### Testing (30+ skills)
- Unit testing
- Integration testing
- E2E testing (Playwright, Cypress)
- Fuzzing (Atheris, LibAFL, AFL++)

#### Database (15+ skills)
- PostgreSQL table design
- SQL optimization
- Supabase operations

#### DevOps (25+ skills)
- Docker Compose
- GitHub Actions
- GitLab CI/CD
- Deployment pipelines

### Skills Location
- Primary: `.agents/skills/`
- Total: 200+ skills available

---

## 6. MCP Server Tools

### Available Tools

#### RAG Tools
| Tool | Description |
|------|-------------|
| `get_available_sources` | List knowledge base sources |
| `perform_rag_query` | Search vector database |
| `search_code_examples` | Find code examples |

### MCP Server Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/sse` | GET | SSE connection |
| `/messages` | POST | Send messages |

---

## 7. Project Structure

```
python/
├── src/
│   ├── mcp/
│   │   ├── mcp_server.py          # Main MCP server (fixed)
│   │   └── modules/
│   │       ├── rag_module.py      # RAG tools (fixed types)
│   │       └── project_module.py  # Project tools
│   ├── server/
│   │   ├── main.py               # FastAPI server
│   │   ├── config/
│   │   │   └── service_discovery.py
│   │   └── services/
│   │       ├── mcp_service_client.py
│   │       └── mcp_session_manager.py
│   └── agents/                   # PydanticAI agents
├── tests/
│   └── test_mcp_server.py         # MCP tests (created)
├── .env                          # Environment config (created)
└── pyproject.toml

.agents/
├── skills/                       # 200+ skills
└── CLAUDE.md                     # Agent instructions

.claude/
├── CLAUDE.md                     # Main CLI instructions
└── settings.json                 # Claude settings

.config/kilo/                     # Kilo CLI installation
```

---

## 8. Coding Standards

### Python (per CLAUDE.md)

#### Error Handling
- **Fail Fast**: Service startup, missing config, auth failures
- **Complete with Log**: Batch processing, background tasks, WebSocket events
- **Never Corrupt Data**: Skip failed items instead of storing null/zero

#### Code Quality
- Use type hints
- Implement proper error handling
- Add detailed logging
- Follow PEP 8 (120 char line length)
- Use Ruff for linting
- Use MyPy for type checking

#### Logging Guidelines
- Include context about what was being attempted
- Preserve full stack traces with `exc_info=True`
- Use specific exception types
- Include relevant IDs, URLs, data for debugging
- Never return None/null to indicate failure

---

## 9. Quick Reference

### Start MCP Server
```bash
cd python
python -m src.mcp.mcp_server
```

### Test MCP Server
```bash
cd python
python -m pytest tests/test_mcp_server.py -v
```

### Check MCP Health
```bash
curl http://localhost:8051/health
```

### List Available Skills
```bash
kilo skills list
```

### Run Kilo
```bash
kilo --help
```

---

## 10. Known Issues

### Port Conflicts
- Port 8000 already in use on system
- Port 8051 may conflict with other services

### Platform Issues
- Unicode logging errors on Windows (cosmetic)

---

## 11. Resources

- [Kilo Documentation](https://kilo.ai/docs)
- [MCP Protocol](https://modelcontextprotocol.io)
- [Skills Library](https://github.com/kilo-ai/skills)
- [Supabase](https://supabase.com)
- [OpenRouter](https://openrouter.ai)

---

## 12. Files Created/Modified

### Created
- `python/tests/test_mcp_server.py`
- `python/.env`
- `KILO_CLI_COMPLETE_SETUP.md`

### Modified
- `python/src/mcp/mcp_server.py` (fixed imports)
- `python/src/mcp/modules/rag_module.py` (fixed type annotations)

---

## 13. Quick Start

### First Time Setup

1. **Configure Environment**
   ```bash
   # Edit python/.env with your credentials
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_SERVICE_KEY=your-key
   OPENROUTER_API_KEY=your-key
   ```

2. **Start Services**
   ```bash
   # Option 1: Docker Compose
   cd python
   docker-compose up --build -d

   # Option 2: Manual
   cd python
   uv sync
   python -m src.mcp.mcp_server  # MCP Server
   python -m src.server.main     # Main Server
   ```

3. **Start Frontend**
   ```bash
   cd archon-ui-main
   npm run dev
   ```

### Daily Development

1. Check MCP health: `curl http://localhost:8051/health`
2. Open frontend: http://localhost:3737
3. Use Archon task management for all tasks

---

## 14. Archon MCP Workflow

### Critical Rules

#### ARCHON-FIRST RULE
Before doing ANY task management:
1. STOP and check if Archon MCP server is available
2. Use Archon task management as PRIMARY system
3. TodoWrite is ONLY for personal, secondary tracking AFTER Archon setup

#### CODE OPERATIONS RULE
For ALL code search and editing:
1. Use Serena MCP tools as PRIMARY method
2. Use Archon MCP for documentation research
3. Traditional tools (grep, sed) are FALLBACK ONLY

### Archon MCP Tools

| Tool | Description |
|------|-------------|
| `archon:manage_project` | Create/list projects |
| `archon:manage_task` | CRUD operations on tasks |
| `archon:perform_rag_query` | Search knowledge base |
| `archon:search_code_examples` | Find code snippets |
| `archon:get_available_sources` | List knowledge sources |
| `archon:get_project_features` | Get project feature list |

### Task Status Flow
```
todo → doing → review → done
```

### Archon Commands Examples

```bash
# Create project
archon:manage_project(action="create", title="Project Name", github_repo="...")

# Get current tasks
archon:manage_task(action="list", filter_by="status", filter_value="todo")

# Update task
archon:manage_task(action="update", task_id="...", update_fields={"status": "doing"})

# Research
archon:perform_rag_query(query="JWT authentication best practices", match_count=5)
archon:search_code_examples(query="React custom hook implementation", match_count=3)
```

---

## 14. Development Services

### Service Ports

| Service | Port | Description |
|---------|------|-------------|
| Frontend | 3737 | React + Vite dev server |
| Main Server | 8181 | FastAPI + Socket.IO |
| MCP Server | 8051 | HTTP-based MCP protocol |
| Agents | 8052 | PydanticAI agents |

### Docker Services

```bash
# Start all services
docker-compose up --build -d

# View logs
docker-compose logs -f

# Restart specific service
docker-compose restart archon-mcp
```

---

## 15. Database Schema (Supabase)

### Tables

| Table | Description |
|-------|-------------|
| `sources` | Crawled websites and uploaded documents |
| `documents` | Processed chunks with embeddings |
| `projects` | Project management (optional) |
| `tasks` | Task tracking |
| `code_examples` | Extracted code snippets |

---

## 16. API Endpoints

### Knowledge Base
- `POST /api/knowledge/crawl` - Crawl website
- `POST /api/knowledge/upload` - Upload documents
- `GET /api/knowledge/items` - List items
- `POST /api/knowledge/search` - RAG search

### MCP Integration
- `GET /api/mcp/health` - Health check
- `POST /api/mcp/tools/{tool_name}` - Execute tool
- `GET /api/mcp/tools` - List tools

### Projects
- `GET /api/projects` - List projects
- `POST /api/projects` - Create project
- `GET /api/projects/{id}/tasks` - Get tasks
- `POST /api/projects/{id}/tasks` - Create task

---

## 17. Socket.IO Events

- `crawl_progress` - Website crawling progress
- `project_creation_progress` - Project setup progress
- `task_update` - Task status changes
- `knowledge_update` - Knowledge base changes

---

*Last Updated: 2026-03-20*
