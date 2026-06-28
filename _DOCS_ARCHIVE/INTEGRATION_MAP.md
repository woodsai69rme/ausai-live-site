# 🎯 INTEGRATION MAP - SYSTEM CONNECTIONS

---

## 1. ARCHITECTURE OVERVIEW

```
┌──────────────────────────────────────────────────────────────────────┐
│                         USER LAYER                                     │
│    OpenCode CLI (30 skills) │ Claude Code │ Cursor │ Windsurf      │
└──────────────────────────────────────────────────────────────────────┘
                                    ↓
┌──────────────────────────────────────────────────────────────────────┐
│                    ORCHESTRATION LAYER                                │
│              claude-flow │ zen-mcp-server │ MCPs                    │
└──────────────────────────────────────────────────────────────────────┘
                                    ↓
┌───────────────┬───────────────┬───────────────┬───────────────┐
│   TRADING     │  AI CODING    │   KNOWLEDGE   │  AUTOMATION   │
│   (47 repos)  │  (23 repos)   │    BASE       │    (n8n)      │
├───────────────┼───────────────┼───────────────┼───────────────┤
│ ccxt          │ bolt.diy      │ quivr         │ n8n           │
│ Superalgos    │ bolt2         │ perplexica    │ workflows     │
│ crypto-beacon │ cherry-studio │ deepwiki      │ aether-flow   │
│ 47 crypto     │ InstantCoder  │ RAG           │ auto-synth    │
└───────────────┴───────────────┴───────────────┴───────────────┘
                                    ↓
┌──────────────────────────────────────────────────────────────────────┐
│                      DATA LAYER                                      │
│          Supabase (PostgreSQL + pgvector)                          │
│          Ollama (Local LLMs)                                         │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 2. CONNECTION POINTS

### 2.1 MCP Connections
```
zen-mcp-server (8051)
    ├── → Claude Flow (orchestration)
    ├── → All AI Agents
    ├── → OpenRouter (all models)
    ├── → Gemini API
    ├── → OpenAI API
    └── → Ollama (local)

mcp-crawl4ai-rag (8052)
    ├── → Web Crawling
    ├── → Supabase (embeddings)
    ├── → quivr (knowledge base)
    └── → All dashboards

mcp-zero
    ├── → Lightweight operations
    └── → All tools
```

### 2.2 n8n Connections
```
n8n (5678)
    ├── → Webhooks from 47 crypto repos
    ├── → ccxt (trading execution)
    ├── → Supabase (data storage)
    ├── → Slack (notifications)
    ├── → Email (alerts)
    └── → Schedule (automation)
```

### 2.3 Knowledge Base Connections
```
quivr
    ├── → Supabase (vector store)
    ├── → File uploads
    ├── → Web content
    └── → Query interface

perplexica
    ├── → Search APIs
    ├── → Web indexing
    └── → AI search

deepwiki-open
    ├── → Code documentation
    └── → Project wikis
```

---

## 3. DATA FLOWS

### 3.1 Trading Signal Flow
```
Crypto Bot (47 repos)
    ↓ (webhook)
n8n Workflow
    ↓ (process)
ccxt (execute trade)
    ↓ (log)
Supabase (store)
    ↓ (notify)
Dashboard (display)
```

### 3.2 RAG Query Flow
```
User Query
    ↓
mcp-crawl4ai-rag
    ↓ (embed)
Supabase (pgvector)
    ↓ (retrieve)
Context + Query
    ↓
LLM (generate)
    ↓
User (response)
```

### 3.3 Agent Orchestration Flow
```
User Task
    ↓
Claude Code / claude-flow
    ↓ (select tools)
zen-mcp-server
    ↓ (execute)
Various APIs
    ↓ (return)
Result to User
```

---

## 4. API ENDPOINTS

### 4.1 Backend API (8181)
| Endpoint | Method | Purpose |
|----------|--------|---------|
| /health | GET | Health check |
| /api/knowledge/search | POST | RAG search |
| /api/knowledge/crawl | POST | Crawl website |
| /api/projects | GET/POST | Project CRUD |
| /api/tasks | GET/POST | Task CRUD |
| /socket.io | WS | Real-time updates |

### 4.2 MCP Server (8051)
| Endpoint | Method | Purpose |
|----------|--------|---------|
| /tools/list | GET | List tools |
| /tools/execute | POST | Execute tool |
| /health | GET | Health check |

### 4.3 n8n Webhooks
| Webhook | Purpose |
|---------|---------|
| /webhook/crypto | Trading signals |
| /webhook/agent | Agent triggers |
| /webhook/rag | RAG queries |

---

## 5. ENVIRONMENT VARIABLES

### 5.1 Required
```bash
# Supabase
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_SERVICE_KEY=xxx

# OpenRouter (all AI)
OPENROUTER_API_KEY=sk-or-v1-xxx

# Ollama (local)
OLLAMA_HOST=http://localhost:11434
```

### 5.2 Service Ports
```bash
ARCHON_UI_PORT=3737
ARCHON_SERVER_PORT=8181
ARCHON_MCP_PORT=8051
ARCHON_AGENTS_PORT=8052
N8N_PORT=5678
OLLAMA_PORT=11434
```

---

## 6. WEBSOCKET CONNECTIONS

| Service | Protocol | Purpose |
|---------|----------|---------|
| Backend | Socket.IO | Real-time updates |
| n8n | WS | Workflow triggers |
| MCP | SSE | Tool responses |
| Ollama | HTTP | Model inference |

---

## 7. DATABASE SCHEMAS

### Supabase Tables
- sources (websites, documents)
- documents (chunks with embeddings)
- projects (project containers)
- tasks (task tracking)
- code_examples (extracted code)

### pgvector
- Embedding dimension: 1536
- Distance metric: cosine

---

## 8. INTEGRATION STATUS

| Connection | Status | Notes |
|------------|--------|-------|
| n8n ↔ ccxt | ✅ Ready | Webhook configured |
| MCP ↔ Supabase | ✅ Ready | env vars needed |
| claude-flow ↔ MCP | ✅ Ready | HTTP connection |
| Trading ↔ n8n | ⏳ Pending | Webhook setup |
| RAG ↔ Knowledge | ⏳ Pending | Configuration |

---

## 9. FIREWALL/PORTS NEEDED

| Port | Service | Protocol |
|------|---------|-----------|
| 3737 | Frontend | HTTP |
| 8181 | Backend | HTTP/WS |
| 8051 | MCP | HTTP/SSE |
| 8052 | Agents | HTTP |
| 5678 | n8n | HTTP |
| 11434 | Ollama | HTTP |

---

*Last Updated: March 4, 2026*
