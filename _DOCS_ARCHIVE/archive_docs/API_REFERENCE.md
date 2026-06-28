# 🎯 API REFERENCE
## All Endpoints, Webhooks, and Services

---

## 1. BACKEND API (Port 8181)

### Health
```bash
GET http://localhost:8181/health
Response: {"status": "ok"}
```

### Knowledge Base
```bash
# Search (RAG)
POST http://localhost:8181/api/knowledge/search
Body: {"query": "search text", "match_count": 5}

# Crawl website
POST http://localhost:8181/api/knowledge/crawl
Body: {"url": "https://..."}

# Upload document
POST http://localhost:8181/api/knowledge/upload
Body: {"file": "...", "source_type": "pdf|docx|md"}

# List sources
GET http://localhost:8181/api/knowledge/items
```

### Projects
```bash
# List projects
GET http://localhost:8181/api/projects

# Create project
POST http://localhost:8181/api/projects
Body: {"title": "Project Name", "github_repo": "..."}

# Get project
GET http://localhost:8181/api/projects/{id}

# Delete project
DELETE http://localhost:8181/api/projects/{id}
```

### Tasks
```bash
# List tasks
GET http://localhost:8181/api/projects/{id}/tasks

# Create task
POST http://localhost:8181/api/projects/{id}/tasks
Body: {"title": "Task", "status": "todo", "task_order": 1}

# Update task
PATCH http://localhost:8181/api/tasks/{id}
Body: {"status": "doing"}
```

---

## 2. MCP SERVER (Port 8051)

### Tools
```bash
# List tools
GET http://localhost:8051/tools

# Execute tool
POST http://localhost:8051/tools/execute
Body: {"name": "tool_name", "arguments": {...}}
```

### Available Tools
| Tool | Description |
|------|-------------|
| perform_rag_query | Search knowledge base |
| search_code_examples | Find code snippets |
| manage_project | Project CRUD |
| manage_task | Task CRUD |
| get_available_sources | List sources |

### Health
```bash
GET http://localhost:8051/health
```

---

## 3. n8n API (Port 5678)

### Webhooks
```bash
# Trading signals
POST http://localhost:5678/webhook/crypto
Body: {"symbol": "BTC", "action": "buy", "price": 50000}

# Agent triggers
POST http://localhost:5678/webhook/agent
Body: {"agent": "claude", "task": "..."}

# RAG queries
POST http://localhost:5678/webhook/rag
Body: {"query": "..."}
```

### Workflow API
```bash
# Activate workflow
POST http://localhost:5678/api/workflows/{id}/activate

# Deactivate workflow
POST http://localhost:5678/api/workflows/{id}/deactivate

# Get execution
GET http://localhost:5678/api/executions/{id}
```

---

## 4. OLLAMA API (Port 11434)

### Models
```bash
# List models
GET http://localhost:11434/api/tags

# Generate
POST http://localhost:11434/api/generate
Body: {"model": "llama2", "prompt": "Hello", "stream": false}

# Chat
POST http://localhost:11434/api/chat
Body: {"model": "llama2", "messages": [{"role": "user", "content": "..."}]}
```

---

## 5. SUPABASE API

### Database
```sql
-- Sources
SELECT * FROM sources;
INSERT INTO sources (url, source_type) VALUES ('https://...', 'website');

-- Documents
SELECT * FROM documents WHERE source_id = '...';
INSERT INTO documents (content, embedding, source_id) 
VALUES ('text', '[0.1, ...]', 'source-id');

-- Vector Search
SELECT id, content, 1 - (embedding <=> $1) as similarity
FROM documents
ORDER BY embedding <=> $1
LIMIT 5;
```

### Authentication
```bash
# Service role (server)
SUPABASE_SERVICE_KEY=xxx

# Anonymous (client)
SUPABASE_ANON_KEY=xxx
```

---

## 6. WEBSOCKET ENDPOINTS

### Backend Socket.IO
```javascript
// Connect
const socket = io('http://localhost:8181');

// Events
socket.on('crawl_progress', (data) => {...});
socket.on('project_creation_progress', (data) => {...});
socket.on('task_update', (data) => {...});
socket.on('knowledge_update', (data) => {...});
```

---

## 7. ENVIRONMENT VARIABLES REFERENCE

### Required
| Variable | Description | Example |
|----------|-------------|---------|
| SUPABASE_URL | Supabase project URL | https://xxx.supabase.co |
| SUPABASE_SERVICE_KEY | Service role key | eyJxxx... |
| OPENROUTER_API_KEY | OpenRouter key | sk-or-v1-xxx |

### Optional
| Variable | Description | Default |
|----------|-------------|---------|
| ARCHON_UI_PORT | Frontend port | 3737 |
| ARCHON_SERVER_PORT | Backend port | 8181 |
| ARCHON_MCP_PORT | MCP port | 8051 |
| ARCHON_AGENTS_PORT | Agents port | 8052 |
| N8N_PORT | n8n port | 5678 |
| OLLAMA_PORT | Ollama port | 11434 |
| LOG_LEVEL | Log level | INFO |

---

*Last Updated: March 4, 2026*
