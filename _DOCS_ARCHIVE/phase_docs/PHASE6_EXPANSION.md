# 🎯 PHASE 6: EXPANSION PLAN
## New Skills, MCPs, Models to Add

---

## 6.1 NEW SKILLS TO CREATE

### Skill 1: trading-integration
```yaml
name: trading-integration
description: Connect and manage all trading systems, bots, and exchanges
```
**Purpose:** Unified trading control

### Skill 2: rag-automation
```yaml
name: rag-automation
description: Automate knowledge ingestion and RAG pipeline management
```
**Purpose:** Knowledge automation

### Skill 3: webhook-manager
```yaml
name: webhook-manager
description: Central webhook management for all systems
```
**Purpose:** Integration hub

### Skill 4: model-manager
```yaml
name: model-manager
description: Manage Ollama models, downloads, and configurations
```
**Purpose:** Local LLM management

### Skill 5: api-gateway
```yaml
name: api-gateway
description: Unified API gateway for all services
```
**Purpose:** Single API entry point

---

## 6.2 NEW MCPS TO INSTALL

### MCP 1: Filesystem MCP
- **Purpose:** Local file operations
- **Repo:** modelcontextprotocol/filesystem
- **Use:** Read/write files across all projects

### MCP 2: GitHub MCP
- **Purpose:** GitHub API operations
- **Repo:** modelcontextprotocol/github
- **Use:** Manage repos, issues, PRs

### MCP 3: Slack MCP
- **Purpose:** Slack integration
- **Repo:** modelcontextprotocol/slack
- **Use:** Send notifications, manage channels

### MCP 4: Notion MCP
- **Purpose:** Notion integration
- **Repo:** notion of Notion official
- **Use:** Manage Notion databases

---

## 6.3 NEW OLLAMA MODELS TO PULL

```bash
# General purpose
ollama pull llama3
ollama pull llama3.2
ollama pull mistral
ollama pull mixtral

# Code generation
ollama pull codellama
ollama pull codeqwen

# Reasoning
ollama pull deepseek-r1
ollama pull qwen2.5

# Multimodal
ollama pull llava
ollama pull bakllava
```

---

## 6.4 NEW n8n WORKFLOWS TO CREATE

### Workflow 1: Trading Signal Aggregator
```
- Webhook from all 47 crypto repos
- Aggregate signals
- Execute via ccxt
- Log to Supabase
```

### Workflow 2: Daily Report Generator
```
- Collect data from all systems
- Generate summary
- Send via Slack/Email
```

### Workflow 3: Backup Automation
```
- Schedule daily backups
- Compress and store
- Verify integrity
```

---

## 6.5 IMPLEMENTATION STATUS

| Item | Status | Notes |
|------|--------|-------|
| trading-integration skill | ⏳ Ready to create | Need to build |
| rag-automation skill | ⏳ Ready to create | Need to build |
| webhook-manager skill | ⏳ Ready to create | Need to build |
| model-manager skill | ⏳ Ready to create | Need to build |
| api-gateway skill | ⏳ Ready to create | Need to build |
| Filesystem MCP | ⏳ Ready to install | Need repo |
| GitHub MCP | ⏳ Ready to install | Need repo |
| Slack MCP | ⏳ Ready to install | Need repo |
| Ollama models | ⏳ Ready to pull | Need to run |
| n8n workflows | ⏳ Ready to create | Need to build |

---

## 6.6 EXPANSION COMMANDS

### Pull Ollama Models
```bash
ollama pull llama3
ollama pull mistral
ollama pull codellama
```

### Install MCPs
```bash
# Example: Clone and install
git clone https://github.com/modelcontextprotocol/filesystem-mcp
cd filesystem-mcp
npm install
```

### Create Skills
```bash
# New skill structure
mkdir -p ~/.claude/skills/new-skill
echo "---" > ~/.claude/skills/new-skill/SKILL.md
```

---

## PHASE 6 STATUS: READY TO EXECUTE

**To expand:**
1. Pull Ollama models
2. Install new MCPs
3. Create new skills
4. Build n8n workflows
