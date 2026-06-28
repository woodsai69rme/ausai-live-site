# COMPREHENSIVE SYSTEM DOCUMENTATION
## Last Updated: March 20, 2026

---

# TABLE OF CONTENTS

1. [System Overview](#system-overview)
2. [Kilo CLI Configuration](#kilo-cli-configuration)
3. [MCP Servers](#mcp-servers)
4. [Skills System](#skills-system)
5. [Coding Standards](#coding-standards)
6. [Project Structure](#project-structure)
7. [Environment Configuration](#environment-configuration)
8. [API Endpoints](#api-endpoints)
9. [Testing](#testing)
10. [Troubleshooting](#troubleshooting)

---

# 1. SYSTEM OVERVIEW

## System Information
- **Platform**: Windows 11 (10.0.26200)
- **Python Version**: 3.13.7
- **Node Version**: Bun
- **User**: karma
- **Hostname**: karma

## Installed AI Tools
| Tool | Location | Version |
|------|----------|---------|
| Kilo CLI | .config/kilo/ | Latest |
| Claude | .claude/ | Active |
| Cursor | .cursor/ | Active |
| Windsurf | .windsurf/ | Active |
| Qwen | .qwen/ | Active |
| Trae | .trae/ | Active |
| Kiro | .kiro/ | Active |
| Cline | .cline/ | Active |
| Continue | .continue/ | Active |

## Key Projects
- **python/** - Main backend (FastAPI, MCP server)
- **archon-ui-main/** - Frontend React application
- **skills/** - 200+ skill implementations
- **.agents/** - Agent configurations

---

# 2. KILO CLI CONFIGURATION

## Installation
```bash
# Via Bun
bun install -g @kilocode/cli

# Via npm
npm install -g @kilocode/cli
```

## Configuration Files
- **Primary**: `.claude.json` - Main Claude Code config
- **Kilo Config**: `.config/kilo/` - Kilo CLI settings
- **Skills**: `skills/` - Symlinked to `.agents/skills/`

## MCP Server Integration
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

---

# 3. MCP SERVERS

## Archon MCP Server

### Status
- **Port**: 8051
- **Transport**: SSE (Server-Sent Events)
- **Status**: Operational

### Available Tools

#### 1. get_available_sources
```python
async def get_available_sources(ctx: Context) -> str:
    """
    Get list of available sources in the knowledge base.
    Returns: JSON string with list of sources
    """
```

#### 2. perform_rag_query
```python
async def perform_rag_query(
    ctx: Context,
    query: str,
    source: Optional[str] = None,
    match_count: int = 5
) -> str:
    """
    Perform RAG query on stored content.
    Args:
        query: The search query
        source: Optional source domain to filter results
        match_count: Maximum results to return (default: 5)
    Returns: JSON string with search results
    """
```

#### 3. search_code_examples
```python
async def search_code_examples(
    ctx: Context,
    query: str,
    source_id: Optional[str] = None,
    match_count: int = 5
) -> str:
    """
    Search for code examples relevant to the query.
    Args:
        query: The search query
        source_id: Optional source ID to filter results
        match_count: Maximum results to return (default: 5)
    Returns: JSON string with search results
    """
```

### Environment Variables
```bash
ARCHON_SERVER_PORT=8181
ARCHON_MCP_PORT=8051
ARCHON_AGENTS_PORT=8052
ARCHON_UI_PORT=3737
SUPABASE_URL=https://example.supabase.co
SUPABASE_SERVICE_KEY=example-key
DEBUG_MODE=false
ARCHON_ENV=development
CORS_ORIGINS=http://localhost:3737
SOCKETIO_CORS_ORIGINS=http://localhost:3737
USE_AGENTIC_RAG=true
PROJECTS_ENABLED=false
```

### Running the Server
```bash
cd /c/Users/karma/python
python -m src.mcp.mcp_server
```

### Server Logs
- Output: `INFO: Started server process [PID]`
- URL: `http://0.0.0.0:8051/mcp`

---

# 4. SKILLS SYSTEM

## Total Skills: 200+

## Categories

### Cloud & Infrastructure (50+ skills)
| Skill | Description |
|-------|-------------|
| azure-* | 20+ Azure services |
| aws-* | AWS configuration |
| kubernetes-* | K8s manifests |
| docker-compose | Docker orchestration |
| terraform-* | Infrastructure as Code |

### Security (30+ skills)
| Skill | Description |
|-------|-------------|
| security-auditing | Security audits |
| authentication | Auth patterns |
| compliance | Compliance frameworks |
| threat-modeling | Threat analysis |

### Development (50+ skills)
| Skill | Description |
|-------|-------------|
| python-* | 15+ Python patterns |
| javascript-* | JS best practices |
| typescript-* | TS advanced types |
| react-* | React patterns |

### Testing (20+ skills)
| Skill | Description |
|-------|-------------|
| testing-patterns | Testing strategies |
| e2e-testing | End-to-end tests |
| pytest | Python testing |
| playwright | Browser automation |

### Database (15+ skills)
| Skill | Description |
|-------|-------------|
| postgresql-table-design | PostgreSQL schemas |
| sql-optimization | Query optimization |
| database-migration | DB migrations |

### DevOps (25+ skills)
| Skill | Description |
|-------|-------------|
| github-actions | CI/CD pipelines |
| gitlab-ci | GitLab CI |
| deployment-pipeline | Pipeline design |

## Custom Skills Location
```
skills/
├── api-gateway/          # Custom API gateway
├── archon-integration/   # Archon MCP integration
├── d3js-visualization/   # D3.js charts
├── docker-compose/        # Docker configs
├── ios-development/      # iOS development
├── model-manager/        # Ollama models
├── ollama-management/    # Ollama CLI
├── playwright-skill/      # Playwright testing
├── rag-automation/       # RAG automation
├── supabase-db/          # Supabase integration
├── trading-integration/  # Trading systems
├── webhook-manager/      # Webhook handling
```

---

# 5. CODING STANDARDS

## Python Standards (per CLAUDE.md)

### Error Handling
```python
# FAIL FAST - For critical errors
if not credentials:
    raise ValueError("Credentials are required")

# GRACEFUL DEGRADATION - For optional features
try:
    result = optional_feature()
except Exception as e:
    logger.error(f"Optional feature failed: {e}")
    return default_value
```

### Type Hints
```python
from typing import Optional, List, Dict

def process_data(data: Dict[str, str]) -> List[str]:
    """Process input data and return results."""
    results: List[str] = []
    for key, value in data.items():
        results.append(f"{key}: {value}")
    return results
```

### Logging
```python
import logging

logger = logging.getLogger(__name__)

# Include context
logger.error(f"Failed to process {item_id}: {e}", exc_info=True)
```

### Data Validation
```python
from pydantic import BaseModel, Field

class UserInput(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., pattern=r'^[\w\.-]+@[\w\.-]+\.\w+$')
    age: Optional[int] = Field(None, ge=0, le=150)
```

### Never Do This
```python
# WRONG - Silent corruption
try:
    embedding = create_embedding(text)
except Exception:
    embedding = [0.0] * 1536  # NEVER

# CORRECT - Skip failed items
try:
    embedding = create_embedding(text)
    store_document(doc, embedding)
except Exception as e:
    logger.error(f"Skipping {doc.id}: {e}")
    failed_items.append({'doc': doc.id, 'error': str(e)})
```

---

# 6. PROJECT STRUCTURE

## Main Directories

```
C:\Users\karma\
├── python/                    # Backend server
│   ├── src/
│   │   ├── mcp/             # MCP server
│   │   │   ├── mcp_server.py
│   │   │   └── modules/
│   │   │       ├── rag_module.py
│   │   │       └── project_module.py
│   │   └── server/          # FastAPI server
│   ├── tests/               # Test files
│   └── .env                 # Environment config
│
├── archon-ui-main/           # Frontend React app
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   └── services/
│   └── package.json
│
├── skills/                   # Skills (symlinked)
│   ├── api-gateway/
│   ├── archon-integration/
│   └── [200+ more]
│
└── .agents/                 # Agent configs
    └── skills/              # Skills source
```

## Key Files
| File | Purpose |
|------|---------|
| `CLAUDE.md` | Main Claude Code config |
| `CLAUDE-ARCHON.md` | Archon MCP workflow |
| `GOLDEN_RULES.md` | System rules |
| `docker-compose.yml` | Docker services |

---

# 7. ENVIRONMENT CONFIGURATION

## Python Environment
```bash
Python: 3.13.7
pip: Latest
uv: Available
pytest: 8.3.4
```

## Required Packages
```txt
fastmcp>=2.0.0
mcp>=1.7.0
pydantic>=2.0.0
httpx>=0.24.0
python-dotenv>=1.0.0
logfire>=2.0.0
```

## Environment Variables
```bash
# Core
ARCHON_SERVER_PORT=8181
ARCHON_MCP_PORT=8051
ARCHON_AGENTS_PORT=8052
ARCHON_UI_PORT=3737

# Database
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_SERVICE_KEY=xxx

# AI
OPENAI_API_KEY=
OPENROUTER_API_KEY=xxx
LOGFIRE_TOKEN=

# Config
DEBUG_MODE=false
ARCHON_ENV=development
CORS_ORIGINS=http://localhost:3737
SOCKETIO_CORS_ORIGINS=http://localhost:3737
USE_AGENTIC_RAG=true
PROJECTS_ENABLED=false
```

---

# 8. API ENDPOINTS

## Main Server (Port 8181)
| Endpoint | Method | Description |
|---------|--------|-------------|
| `/health` | GET | Health check |
| `/api/knowledge/crawl` | POST | Crawl website |
| `/api/knowledge/search` | POST | RAG search |
| `/api/projects` | GET/POST | Projects CRUD |
| `/api/tasks` | GET/POST | Tasks CRUD |

## MCP Server (Port 8051)
| Endpoint | Method | Description |
|---------|--------|-------------|
| `/mcp` | GET | MCP SSE endpoint |
| `/health` | GET | Health check |

## Frontend (Port 3737)
| Endpoint | Description |
|----------|-------------|
| `http://localhost:3737` | Main UI |

---

# 9. TESTING

## Running Tests

### MCP Server Tests
```bash
cd /c/Users/karma/python
python -m pytest tests/test_mcp_server.py -v
```

### Output
```
tests/test_mcp_server.py::test_mcp_server_import PASSED
tests/test_mcp_server.py::test_mcp_server_initialization PASSED
tests/test_mcp_server.py::test_mcp_tool_registration PASSED
tests/test_mcp_server.py::test_rag_tool_signatures PASSED
tests/test_mcp_server.py::test_module_imports PASSED

============================== 5 passed ==============================
```

### Test Categories
1. **Unit Tests**: Individual functions
2. **Integration Tests**: Service communication
3. **API Tests**: Endpoint validation

---

# 10. TROUBLESHOOTING

## Common Issues

### 1. Port Already in Use
```bash
# Find process using port
netstat -ano | findstr 8051

# Kill process
taskkill /PID <PID> /F
```

### 2. Import Errors
```bash
# Check Python path
python -c "import sys; print(sys.path)"

# Install dependencies
pip install -r requirements.txt
```

### 3. MCP Connection Failed
```bash
# Test MCP health
curl http://localhost:8051/health

# Check logs
python -m src.mcp.mcp_server 2>&1
```

### 4. Type Errors
```bash
# Run type checker
python -m mypy src/mcp/

# Fix imports
from typing import Optional
```

## Debug Commands
```bash
# Check running servers
netstat -ano | findstr "8051\|8181\|3737"

# View Python processes
tasklist | findstr python

# Check environment
python -c "import os; print(os.environ.get('ARCHON_MCP_PORT'))"
```

---

# QUICK REFERENCE

## Start MCP Server
```bash
cd /c/Users/karma/python
python -m src.mcp.mcp_server
```

## Run Tests
```bash
cd /c/Users/karma/python
python -m pytest tests/test_mcp_server.py -v
```

## Check Ports
```bash
netstat -ano | findstr "8051\|8181"
```

## View Logs
```bash
tail -f python/backend.log
```

---

# END OF DOCUMENTATION
