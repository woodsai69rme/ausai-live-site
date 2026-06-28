# OpenCode CLI - Complete Summary & Options Guide

## Executive Summary

OpenCode CLI v1.2.27 has been fully configured and optimized for your development environment. This document provides a complete overview of all configuration options, available features, and possible next steps.

---

## Current State

### What's Configured

| Component | Status | Details |
|-----------|--------|---------|
| OpenCode CLI | ✅ v1.2.27 | Installed globally via npm |
| Skills | ✅ 269 loaded | `.agents/skills/` directory |
| API Keys | ✅ 15 providers | Environment variables set |
| MCP Servers | ✅ 3 configured | filesystem, memory, context7 |
| Agents | ✅ 1 primary | `build` agent + oracle/librarian |
| Plugins | ✅ 1 installed | oh-my-opencode |
| Documentation | ✅ Created | `OPENCODE_CONFIG.md` |
| Disk Space | ✅ Optimized | Freed 9GB (was 99% full) |

---

## All Configuration Options

### 1. AI Models (Available)

#### Free Models
| Model | Use Case |
|-------|----------|
| `opencode/big-pickle` | Fast general tasks |
| `opencode/gpt-5-nano` | Lightweight operations |
| `opencode/mimo-v2-omni-free` | Multi-modal |
| `opencode/mimo-v2-pro-free` | Advanced multi-modal |
| `opencode/minimax-m2.5-free` | General purpose |
| `opencode/nemotron-3-super-free` | NVIDIA optimized |

#### Paid Models (via API keys)
| Model | Provider | Use Case |
|-------|----------|----------|
| `opencode-go/glm-5` | OpenCode Go | General coding |
| `opencode-go/kimi-k2.5` | Moonshot | Advanced reasoning |
| `opencode-go/minimax-m2.5` | MiniMax | Long context |
| `alibaba/qwen-max` | Alibaba | Complex tasks |
| `alibaba/qwen3-coder-flash` | Alibaba | Code generation |
| `alibaba/qwq-plus` | Alibaba | Reasoning |

#### External Providers
| Provider | Models Available |
|----------|-------------------|
| Anthropic | Claude 3.5, Claude 3, Claude 4 |
| OpenAI | GPT-4o, GPT-4-turbo, GPT-3.5 |
| Google | Gemini Pro, Gemini Ultra |
| GitHub | GitHub Models catalog |

---

### 2. MCP Server Options

#### Currently Configured
```json
{
  "filesystem": {
    "type": "stdio",
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-filesystem", "C:\\Users\\karma"]
  },
  "memory": {
    "type": "stdio",
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-memory"]
  },
  "context7": {
    "type": "remote",
    "url": "https://mcp.context7.com/sse"
  }
}
```

#### Available to Add
| MCP Server | Install Command | Purpose |
|------------|----------------|---------|
| GitHub | `npx -y @modelcontextprotocol/server-github` | Repository operations |
| Brave Search | `npx -y @modelcontextprotocol/server-brave-search` | Web search |
| Sequential Thinking | `npx -y @modelcontextprotocol/server-sequential-thinking` | Structured reasoning |
| Puppeteer | `npx -y @modelcontextprotocol/server-puppeteer` | Browser automation |
| Slack | `npx -y @modelcontextprotocol/server-slack` | Slack integration |
| Postgres | `npx -y @modelcontextprotocol/server-postgres` | Database queries |
| SQLite | `npx -y @modelcontextprotocol/server-sqlite` | Local database |
| Fetch | `npx -y @modelcontextprotocol/server-fetch` | HTTP requests |

**To add new MCP server:**
```json
"new-server": {
  "type": "stdio",
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-NEW-SERVER"]
}
```

For remote servers:
```json
"remote-server": {
  "type": "remote",
  "url": "https://server-url/sse"
}
```

---

### 3. Skills (269 Total)

#### By Category

##### Development (40+ skills)
- `python-testing-patterns` - pytest, fixtures, mocking
- `javascript-testing-patterns` - Jest, Vitest, Testing Library
- `test-driven-development` - TDD workflow
- `e2e-testing-patterns` - Playwright, Cypress
- `debugging-strategies` - Debugging techniques
- `code-review-excellence` - Review best practices
- `git-advanced-workflows` - Git workflows
- `modern-javascript-patterns` - ES6+ patterns
- `typescript-advanced-types` - TypeScript patterns

##### Security (30+ skills)
- `solidity-security` - Smart contract security
- `sast-configuration` - Static analysis
- `auth-implementation-patterns` - Auth/JWT/OAuth
- `pci-compliance` - Payment security
- `gdpr-data-handling` - Privacy compliance
- `threat-mitigation-mapping` - Security controls
- `attack-tree-construction` - Threat modeling
- `security-requirement-extraction` - Security requirements

##### Cloud & DevOps (35+ skills)
- `azure-deploy` - Azure deployment
- `azure-prepare` - Azure app setup
- `azure-diagnostics` - Azure troubleshooting
- `k8s-manifest-generator` - Kubernetes YAML
- `k8s-security-policies` - K8s security
- `terraform-module-library` - IaC modules
- `github-actions-templates` - CI/CD workflows
- `docker-compose` - Container orchestration
- `gitops-workflow` - ArgoCD/Flux

##### AI & Machine Learning (25+ skills)
- `rag-implementation` - RAG systems
- `llm-evaluation` - LLM testing
- `mcp-builder` - MCP server development
- `langchain-architecture` - LangChain patterns
- `embedding-strategies` - Vector embeddings
- `hybrid-search-implementation` - Search systems
- `vector-index-tuning` - Vector DB optimization
- `prompt-engineering-patterns` - Prompt design

##### Web Development (30+ skills)
- `next-best-practices` - Next.js patterns
- `nextjs-app-router-patterns` - App Router
- `react-state-management` - Redux/Zustand/Jotai
- `vercel-react-best-practices` - Vercel optimization
- `tailwind-design-system` - Tailwind CSS
- `shadcn-ui` - UI components
- `frontend-design` - UI/UX design
- `responsive-design` - Responsive layouts

##### Database (15+ skills)
- `postgresql-table-design` - PostgreSQL schema
- `sql-optimization-patterns` - Query optimization
- `dbt-transformation-patterns` - dbt models
- `database-migration` - Migration strategies
- `cqrs-implementation` - CQRS patterns
- `event-store-design` - Event sourcing

##### Mobile (10+ skills)
- `react-native-architecture` - React Native
- `react-native-design` - Mobile styling
- `expo-deployment` - Expo deployment
- `expo-cicd-workflows` - Expo CI/CD
- `mobile-ios-design` - iOS patterns
- `mobile-android-design` - Android patterns

##### Data & Analytics (15+ skills)
- `data-quality-frameworks` - Data validation
- `data-storytelling` - Data visualization
- `kpi-dashboard-design` - Dashboards
- `backtesting-frameworks` - Trading systems
- `risk-metrics-calculation` - Risk analysis

##### Specialized Skills (50+ skills)
- `d3-viz` - D3.js visualizations
- `algorithmic-art` - p5.js generative art
- `canvas-design` - Poster/art creation
- `web-asset-generator` - Favicons, icons
- `pdf` - PDF manipulation
- `xlsx` - Spreadsheet operations
- `docx` - Word documents
- `pptx` - PowerPoint slides

##### Startup/Business (10+ skills)
- `startup-financial-modeling` - Financial projections
- `startup-metrics-framework` - Key metrics
- `market-sizing-analysis` - Market analysis
- `competitive-landscape` - Competition
- `team-composition-analysis` - Team planning

##### Automation (10+ skills)
- `slack-gif-creator` - Animated GIFs
- `webhook-manager` - Webhook management
- `api-gateway` - API management
- `trading-integration` - Trading systems

---

### 4. Agent Configuration Options

#### Current Primary Agent
```json
{
  "build": {
    "model": "opencode-go/glm-5",
    "systemPrompt": "...",
    "permissions": [
      { "permission": "*", "action": "allow", "pattern": "*" }
    ]
  }
}
```

#### oh-my-opencode Agents
```json
{
  "oracle": {
    "enabled": true,
    "model": "claude-sonnet-4"
  },
  "librarian": {
    "enabled": true,
    "model": "gpt-4o"
  }
}
```

#### Creating Custom Agents
Add to `~/.opencode/config.json`:
```json
{
  "agents": {
    "security-auditor": {
      "model": "alibaba/qwq-plus",
      "systemPrompt": "You are a security expert...",
      "permissions": [
        { "permission": "external_directory", "pattern": "*", "action": "allow" }
      ]
    },
    "test-writer": {
      "model": "opencode-go/glm-5",
      "systemPrompt": "Write comprehensive tests...",
      "permissions": [
        { "permission": "*", "action": "allow", "pattern": "*.test.*" }
      ]
    }
  }
}
```

---

### 5. Plugin Options

#### oh-my-opencode Features
| Feature | Default | Description |
|---------|---------|-------------|
| `multiAgentOrchestration` | true | Multiple agents coordination |
| `lspAstTools` | true | Language server integration |
| `claudeCodeCompatibility` | true | Claude Code interoperability |
| `enhancedSearch` | true | Advanced code search |
| `smartRefactor` | true | Intelligent refactoring |
| `contextAwareCompletion` | true | Smart code completion |
| `aiPoweredDebugging` | true | AI debugging assistance |
| `automatedCodeReview` | true | Automatic code review |
| `intelligentTaskManagement` | true | Task prioritization |

---

### 6. Environment Variables

#### Required API Keys
```bash
# Primary
OPENROUTER_API_KEY=***      # Multi-model access
ANTHROPIC_API_KEY=***       # Claude models
OPENAI_API_KEY=***          # GPT models
GEMINI_API_KEY=***          # Google models

# Cloud
DASHSCOPE_API_KEY=***       # Alibaba/Qwen
MOONSHOT_API_KEY=***        # Moonshot AI
GITHUB_TOKEN=***            # GitHub Models

# Optional
BRAVE_API_KEY=              # Brave Search MCP
GOOGLE_APPLICATION_CREDENTIALS=  # Vertex AI
```

#### Configuration Variables
```bash
OPENCODE_PID=               # Process ID (auto)
OPENCODE=1                  # Flag (auto)
```

---

### 7. CLI Commands Reference

#### Starting OpenCode
```bash
opencode                    # Start TUI (current dir)
opencode /path/to/project   # Start in directory
opencode -m MODEL          # Use specific model
opencode -c                # Continue last session
opencode -s SESSION_ID     # Resume session
opencode --fork            # Fork when continuing
```

#### Running Commands
```bash
opencode run "create a React app"    # Run with message
opencode run -m opencode-go/glm-5 "task"
```

#### Session Management
```bash
opencode session list                # List sessions
opencode session delete SESSION_ID   # Delete session
opencode export SESSION_ID           # Export as JSON
opencode import backup.json          # Import session
```

#### MCP Management
```bash
opencode mcp list           # List servers
opencode mcp add            # Add server (interactive)
opencode mcp auth NAME      # OAuth authentication
opencode mcp logout NAME    # Remove auth
```

#### Provider Management
```bash
opencode providers          # List providers
opencode providers auth     # Authenticate
opencode models             # List all models
opencode models alibaba     # List provider models
```

#### GitHub Integration
```bash
opencode github             # Manage GitHub agent
opencode pr 123             # Fetch and work on PR #123
```

#### Utilities
```bash
opencode stats              # Token usage stats
opencode upgrade            # Update to latest
opencode upgrade@VERSION    # Specific version
opencode uninstall           # Remove OpenCode
opencode db                 # Database tools
opencode debug              # Debugging tools
```

#### Advanced Options
```bash
opencode --port 3000        # Custom port
opencode --hostname 0.0.0.0 # Network access
opencode --mdns             # Enable mDNS discovery
opencode --mdns-domain custom.local
opencode --cors "domain1,domain2"
opencode --log-level DEBUG
opencode --print-logs      # Print logs to stderr
```

---

### 8. Storage Locations

| Path | Description |
|------|-------------|
| `~/.opencode/config.json` | Main configuration |
| `~/.local/share/opencode/auth.json` | API credentials |
| `~/.local/share/opencode/opencode.db` | Session database |
| `~/.local/share/opencode/bin/` | Binaries |
| `~/.agents/skills/` | Skills library |
| `~/.claude/` | Claude Code integration |
| `~/.config/opencode-cli/` | CLI config |

---

## Next Steps Options

### Option 1: Add More MCP Servers

Add these to `~/.opencode/config.json`:

```json
{
  "mcp": {
    "github": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": { "GITHUB_TOKEN": "${GITHUB_TOKEN}" }
    },
    "brave-search": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-brave-search"],
      "env": { "BRAVE_API_KEY": "${BRAVE_API_KEY}" }
    },
    "postgres": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres"],
      "args": ["postgresql://localhost/mydb"]
    }
  }
}
```

### Option 2: Create Custom Skills

Create a new skill in `~/.agents/skills/my-skill/SKILL.md`:

```markdown
---
name: my-custom-skill
description: Description of what this skill does
---

# My Custom Skill

Detailed instructions for the skill...

## When to Use
- Use case 1
- Use case 2

## Implementation
Step-by-step guide...
```

### Option 3: Configure Development Project

Create `.opencode.json` in project root:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "model": "opencode-go/glm-5",
  "mcp": {
    "project-filesystem": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "./src"]
    }
  }
}
```

### Option 4: Set Up Custom Agent

Add to `~/.opencode/config.json`:

```json
{
  "agents": {
    "code-reviewer": {
      "model": "alibaba/qwen3-coder-flash",
      "systemPrompt": "Review code for security, performance, and best practices",
      "permissions": [
        { "permission": "read_file", "action": "allow", "pattern": "*" },
        { "permission": "write_file", "action": "deny", "pattern": "*" }
      ]
    }
  }
}
```

### Option 5: Integrate with IDEs

#### VS Code
```bash
code --install-extension tanishqkancharla.opencode-vscode
```

#### Cursor
MCP servers in OpenCode config are automatically available.

#### Windsurf
Add to `~/.windsurf/config.json`:
```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "."]
    }
  }
}
```

### Option 6: Performance Tuning

Edit `~/.opencode/config.json`:

```json
{
  "settings": {
    "maxTokens": 8192,
    "temperature": 0.7,
    "streaming": true,
    "autoSave": true,
    "cacheSize": "1GB"
  }
}
```

### Option 7: Create Project Templates

```bash
# Create template directory
mkdir -p ~/.opencode/templates/web-app

# Add template config
cat > ~/.opencode/templates/web-app/.opencode.json << 'EOF'
{
  "model": "opencode-go/glm-5",
  "skills": ["next-best-practices", "shadcn-ui", "typescript-advanced-types"],
  "mcp": {
    "filesystem": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "."]
    }
  }
}
EOF
```

### Option 8: Automate Workflows

Create `~/.opencode/workflows/build-app.yaml`:

```yaml
name: Build App
steps:
  - name: Plan
    prompt: "Plan the architecture for: ${project_name}"
  - name: Generate
    prompt: "Generate the code based on the plan"
  - name: Test
    prompt: "Write tests for all generated code"
  - name: Review
    prompt: "Review code for security and performance"
```

### Option 9: Security Hardening

```json
{
  "settings": {
    "sandbox": true,
    "allowedDomains": ["github.com", "npmjs.com"],
    "maxFileSize": "10MB",
    "timeout": 300000,
    "rateLimit": {
      "requests": 100,
      "window": 60000
    }
  }
}
```

### Option 10: Multi-Model Strategy

Configure different models for different tasks:

```json
{
  "modelStrategy": {
    "planning": "alibaba/qwq-plus",
    "coding": "alibaba/qwen3-coder-flash",
    "review": "opencode-go/glm-5",
    "documentation": "opencode/big-pickle",
    "testing": "opencode-go/glm-5"
  }
}
```

---

## Recommended Actions in Priority Order

| Priority | Action | Command/Config |
|----------|--------|----------------|
| 1 | Set Brave API key | `export BRAVE_API_KEY=xxx` |
| 2 | Add GitHub MCP | Add to config.json |
| 3 | Create project config | `.opencode.json` in project |
| 4 | Set up IDE integration | Install VSCode extension |
| 5 | Create custom skill | For your specific needs |
| 6 | Configure custom agent | For specialized tasks |
| 7 | Set up automation | Create workflow files |
| 8 | Performance tuning | Adjust settings |
| 9 | Security review | Check permissions |
| 10 | Backup configuration | Export sessions |

---

## Troubleshooting Guide

### Common Issues

| Issue | Solution |
|-------|----------|
| Bun crash on Windows | Edit config.json directly; use TUI mode |
| MCP not connecting | Check npx installation; verify args |
| Skills not loading | Check ~/.agents/skills/ directory |
| API key errors | Verify environment variables |
| Disk full | Clean caches: `npm cache clean --force` |
| Slow responses | Switch to faster model |
| Memory issues | Reduce maxTokens in config |

### Debug Commands
```bash
opencode --log-level DEBUG
opencode --print-logs
opencode debug
tail -f ~/.local/share/opencode/log/opencode.log
```

---

## Support Resources

| Resource | URL |
|----------|-----|
| OpenCode Docs | https://opencode.ai |
| GitHub Issues | https://github.com/sst/opencode/issues |
| Bun Report | https://bun.report |
| MCP Protocol | https://modelcontextprotocol.io |
| Skills Guide | https://agentskills.io |

---

## Quick Reference

```bash
# Start
opencode

# Use model
opencode -m opencode-go/glm-5

# Continue
opencode -c

# Check stats
opencode stats

# List models
opencode models

# Add MCP (if working)
opencode mcp add

# GitHub PR
opencode pr 123

# Export session
opencode export > backup.json
```

---

*Generated: 2025-03-20*
*OpenCode Version: 1.2.27*
*Bun Version: 1.3.10*