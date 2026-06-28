# 🎯 PHASE 2: CONNECT ALL SYSTEMS TOGETHER
## Integration Architecture & Implementation Plan

---

## 2.1 SYSTEM ARCHITECTURE DIAGRAM

```
┌─────────────────────────────────────────────────────────────────────┐
│                    OPENCODECLI (30 SKILLS)                          │
│     archon-integration │ ollama-management │ docker-compose        │
└─────────────────────────────────────────────────────────────────────┘
                                  ↓
┌─────────────────────────────────────────────────────────────────────┐
│                    CLAUDE CODE LAYER                                 │
│         Claude Code │ .claude config │ Skills                      │
└─────────────────────────────────────────────────────────────────────┘
                                  ↓
┌─────────────────────────────────────────────────────────────────────┐
│                    AI ORCHESTRATION LAYER                           │
│    claude-flow │ zen-mcp-server │ claude-conductor                 │
└─────────────────────────────────────────────────────────────────────┘
                                  ↓
┌──────────────┬──────────────┬──────────────┬──────────────┐
│   MCP        │   TRADING    │  KNOWLEDGE   │  AUTOMATION  │
│   SERVERS    │   SYSTEMS    │    BASE      │    (n8n)     │
├──────────────┼──────────────┼──────────────┼──────────────┤
│ zen-mcp      │ ccxt         │ quivr        │ n8n          │
│ mcp-zero     │ Superalgos   │ perplexica   │ n8n-workflows│
│ crawl4ai-rag│ 47 repos     │ deepwiki     │ aether-flow   │
│ context7     │ crypto-*     │ RAG          │ auto-synth    │
└──────────────┴──────────────┴──────────────┴──────────────┘
                                  ↓
┌─────────────────────────────────────────────────────────────────────┐
│                    DATA & STORAGE LAYER                             │
│         Supabase (PostgreSQL + pgvector)                            │
│         Ollama (Local LLMs)                                        │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 2.2 CONNECTION POINTS

### MCP → AI Agents Connections
| From | To | Connection Type | Status |
|------|-----|-----------------|--------|
| zen-mcp-server | claude-flow | HTTP/WS | Ready |
| zen-mcp-server | claude-code | HTTP/WS | Ready |
| mcp-zero | All agents | HTTP | Ready |
| mcp-crawl4ai-rag | quivr | Direct | Ready |

### Trading → n8n Connections
| From | To | Connection Type | Status |
|------|-----|-----------------|--------|
| ccxt | n8n | API | Ready |
| Superalgos | n8n | Webhook | Ready |
| 47 crypto repos | n8n | Various | To build |

### Knowledge Base Connections
| From | To | Connection Type | Status |
|------|-----|-----------------|--------|
| mcp-crawl4ai-rag | Supabase | Direct | Ready |
| quivr | Supabase | Client | Ready |
| perplexica | Various | API | Ready |

---

## 2.3 INTEGRATION IMPLEMENTATION

### Integration 1: MCP to Claude Flow
```
File: /c/Users/karma/ACTIVE_PROJECTS/claude-flow/.env
Add:
MCP_SERVER_URL=http://localhost:8051
MCP_SERVER_TOKEN=your-token
```

### Integration 2: Trading Bots to n8n
```
Create n8n workflow that:
1. Receives webhook from trading bot
2. Processes signal
3. Executes trade via ccxt
4. Logs to Supabase
```

### Integration 3: RAG to Knowledge Base
```
mcp-crawl4ai-rag → crawl websites → 
store in Supabase (pgvector) → 
quivr for querying →
display in dashboard
```

---

## 2.4 WEBHOOK CONFIGURATIONS

### Trading Webhooks
| System | Webhook URL | Purpose |
|--------|-------------|---------|
| crypto-beacon | http://localhost:5678/webhook/crypto | Trade signals |
| Superalgos | http://localhost:5678/webhook/super | Execute trades |
| All 47 repos | Individual webhooks | Unified via n8n |

### MCP Webhooks
| MCP | Endpoint | Purpose |
|-----|----------|---------|
| zen-mcp | /tools/* | Execute tools |
| crawl4ai-rag | /crawl | Crawl websites |

---

## 2.5 ENVIRONMENT VARIABLES NEEDED

### Required for Full Integration
```bash
# Supabase
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_SERVICE_KEY=xxx

# OpenRouter (all AI)
OPENROUTER_API_KEY=xxx

# Ollama (local)
OLLAMA_HOST=http://localhost:11434

# MCP Servers
MCP_ZEN_URL=http://localhost:8051
MCP_CRAWL_URL=http://localhost:8052

# n8n
N8N_URL=http://localhost:5678
N8N_API_KEY=xxx
```

---

## 2.6 CONNECTION TESTING PLAN

### Test 1: MCP → Claude Code
```bash
# Test MCP tools accessible
curl http://localhost:8051/tools
```

### Test 2: n8n → Trading
```bash
# Test webhook
curl -X POST http://localhost:5678/webhook/test
```

### Test 3: RAG → Knowledge
```bash
# Test search
curl -X POST http://localhost:8052/search \
  -d '{"query": "test"}'
```

---

## 2.7 PHASE 2 COMPLETION CHECKLIST

- [ ] Connect zen-mcp-server to claude-flow
- [ ] Connect all trading bots to n8n
- [ ] Connect RAG to knowledge base
- [ ] Configure all environment variables
- [ ] Test all webhooks
- [ ] Verify data flow

---

## PHASE 2 STATUS: READY TO IMPLEMENT

**Next:** Execute each integration step by step
