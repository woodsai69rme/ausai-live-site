# OpenCode CLI - Master Configuration Documentation

**Generated:** 2025-03-21
**Version:** 1.2.27
**Status:** Fully Configured

---

## Table of Contents

1. [Configuration Summary](#configuration-summary)
2. [MCP Servers](#mcp-servers)
3. [Agents](#agents)
4. [Skills](#skills)
5. [Project Configs](#project-configs)
6. [Security](#security)
7. [Environment Variables](#environment-variables)
8. [Quick Reference](#quick-reference)

---

## Configuration Summary

| Component | Count/Status | Location |
|-----------|--------------|----------|
| MCP Servers | 6 configured | `~/.opencode/config.json` |
| Agents | 5 custom + 2 base | `~/.opencode/config.json` |
| Skills | 270 total | `~/.agents/skills/` |
| API Providers | 15 configured | Environment Variables |
| Project Configs | 2 created | Project directories |
| Security Config | ✅ Enabled | `~/.opencode/security.json` |

### File Locations

```
C:/Users/karma/
├── .opencode/
│   ├── config.json          # Main configuration
│   └── security.json        # Security settings
│
├── .agents/
│   └── skills/              # 270 skills
│       ├── python-testing-patterns/
│       ├── archon-workflow/     # NEW - Custom skill
│       └── ...
│
├── .local/
│   └── share/
│       └── opencode/
│           ├── auth.json        # API credentials
│           └── opencode.db      # Session database
│
├── python/
│   └── .opencode.json       # Archon backend config
│
├── archon-ui-main/
│   └── .opencode.json      # Archon frontend config
│
├── OPENCODE_CONFIG.md          # Technical docs
├── OPENCODE_COMPLETE_GUIDE.md # Full options guide
└── OPENCODE_ALL_OPTIONS.md    # Detailed analysis
```

---

## MCP Servers

### Configured Servers

| Server | Type | Purpose | Status |
|--------|------|---------|--------|
| **filesystem** | stdio | File read/write | ✅ Active |
| **memory** | stdio | Persistent context | ✅ Active |
| **context7** | remote | Documentation lookup | ✅ Active |
| **github** | stdio | Repository operations | ✅ Configured |
| **brave-search** | stdio | Web search | ⚠️ Needs API key |
| **sequential-thinking** | stdio | Structured reasoning | ✅ Active |
| **fetch** | stdio | HTTP requests | ✅ Active |

### Configuration

```json
{
  "mcp": {
    "filesystem": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "C:\\Users\\karma"]
    },
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
    }
  }
}
```

### Setup Required

1. **Brave Search API Key** (Free)
   - Visit: https://brave.com/search/api/
   - Get free API key
   - Set: `export BRAVE_API_KEY=your_key`

2. **GitHub Token** (Already set)
   - Current environment has `GITHUB_TOKEN`
   - No action needed

---

## Agents

### Custom Agents Created

| Agent | Model | Purpose |
|-------|-------|---------|
| **security-auditor** | qwq-plus | Security vulnerability analysis |
| **test-generator** | glm-5 | Comprehensive test generation |
| **code-reviewer** | qwen3-coder-flash | Code quality review |
| **documenter** | big-pickle | Documentation generation |
| **devops** | minimax-m2.5 | Infrastructure and deployment |

### Base Agents (oh-my-opencode)

| Agent | Model | Purpose |
|-------|-------|---------|
| **oracle** | claude-sonnet-4 | Primary reasoning |
| **librarian** | gpt-4o | Knowledge retrieval |

### Model Strategy

| Task | Model | Reason |
|------|-------|--------|
| Planning | qwq-plus | Complex reasoning |
| Coding | qwen3-coder-flash | Fast code generation |
| Review | glm-5 | Balanced analysis |
| Documentation | big-pickle | Quick text generation |
| Testing | glm-5 | Standard output |
| Security | qwq-plus | Deep analysis |
| DevOps | minimax-m2.5 | Infrastructure |

### Usage Examples

```bash
# Use specific agent (when agent selection available)
opencode --agent security-auditor "review my auth code"
opencode --agent test-generator "write tests for api.py"
opencode --agent documenter "create API docs"
```

---

## Skills

### Total: 270 Skills

### Custom Skills Created

#### archon-workflow
**Location:** `~/.agents/skills/archon-workflow/SKILL.md`

**Purpose:** Archon-specific development patterns, API endpoints, Socket.IO events, and best practices.

**When to Use:**
- Developing Archon features
- Working with FastAPI + Socket.IO
- Integrating MCP servers
- Supabase operations
- RAG implementation

### Key Built-in Skills by Category

#### Development (40+)
- `python-testing-patterns`
- `javascript-testing-patterns`
- `test-driven-development`
- `debugging-strategies`
- `code-review-excellence`

#### Security (30+)
- `solidity-security`
- `sast-configuration`
- `auth-implementation-patterns`
- `pci-compliance`

#### Cloud/DevOps (35+)
- `azure-deploy`
- `k8s-manifest-generator`
- `docker-compose`
- `github-actions-templates`

#### AI/ML (25+)
- `rag-implementation`
- `llm-evaluation`
- `mcp-builder`
- `embedding-strategies`

#### Web (30+)
- `next-best-practices`
- `react-state-management`
- `shadcn-ui`
- `tailwind-design-system`

---

## Project Configs

### Archon Backend (`python/.opencode.json`)

```json
{
  "model": "opencode-go/glm-5",
  "skills": [
    "fastapi-templates",
    "python-testing-patterns",
    "python-async-patterns",
    "supabase-db",
    "mcp-builder",
    "rag-implementation"
  ],
  "context": {
    "projectName": "Archon",
    "techStack": {
      "backend": ["Python", "FastAPI", "Socket.IO", "PydanticAI"],
      "database": ["Supabase", "PostgreSQL", "pgvector"]
    },
    "alpha_principles": {
      "backward_compatibility": false,
      "error_handling": "Fail fast with detailed errors"
    }
  }
}
```

### Archon Frontend (`archon-ui-main/.opencode.json`)

```json
{
  "model": "opencode-go/glm-5",
  "skills": [
    "next-best-practices",
    "react-state-management",
    "shadcn-ui",
    "tailwind-design-system",
    "webapp-testing"
  ],
  "context": {
    "projectName": "Archon UI",
    "techStack": {
      "framework": "React 18 + TypeScript",
      "build": "Vite",
      "styling": "TailwindCSS"
    }
  }
}
```

---

## Security

### Configuration File

**Location:** `~/.opencode/security.json`

### Key Settings

| Setting | Value | Description |
|---------|-------|-------------|
| `sandbox.enabled` | true | Run in sandboxed environment |
| `filesystem.maxFileSize` | 10MB | Maximum file size |
| `secrets.stripFromOutput` | true | Remove secrets from output |
| `audit.enabled` | true | Log all security events |
| `defaultAction` | ask | Prompt for permission |

### Protected File Patterns

- `.env`, `.env.local`, `.env.production`
- `credentials.json`, `secrets.json`
- `*.key`, `*.pem`, `*.cert`
- `auth.json`

### Blocked Commands

- `rm -rf /`, `rm -rf ~`
- `format`, `del /f /s`
- `shutdown`, `restart`
- `mkfs`

### Secret Patterns (Auto-Redacted)

- `API_KEY`, `SECRET`, `PASSWORD`
- `TOKEN`, `PRIVATE_KEY`, `CREDENTIALS`
- `AUTH`, `BEARER`, `JWT`, `OAUTH`

### Agent Permissions

| Agent | File Read | File Write | Commands | Network |
|-------|-----------|------------|----------|---------|
| build | ✅ Allow | ⚠️ Ask | ⚠️ Ask | ⚠️ Ask |
| security-auditor | ✅ Allow | ❌ Deny | ❌ Deny | ❌ Deny |
| test-generator | ✅ Allow | ✅ Allow* | ⚠️ Ask | ⚠️ Ask |
| documenter | ✅ Allow | ✅ Allow* | ❌ Deny | ❌ Deny |
| devops | ✅ Allow | ⚠️ Ask | ⚠️ Ask | ⚠️ Ask |

*Only specific file patterns

### Audit Log Location

```
~/.local/share/opencode/security.log
```

---

## Environment Variables

### Required API Keys

```bash
# Primary AI Provider (REQUIRED)
OPENROUTER_API_KEY=***                    # Multi-model access

# Cloud Providers
ANTHROPIC_API_KEY=***                     # Claude models
OPENAI_API_KEY=***                        # GPT models
GEMINI_API_KEY=***                        # Google models
GITHUB_TOKEN=***                          # GitHub Models & MCP

# Regional Providers
DASHSCOPE_API_KEY=***                     # Alibaba/Qwen
ALIBABA_API_KEY=***
MOONSHOT_API_KEY=***                      # Moonshot AI

# Optional
BRAVE_API_KEY=                            # Brave Search MCP
GOOGLE_APPLICATION_CREDENTIALS=***        # Vertex AI
```

### OpenCode Specific

```bash
OPENCODE_PID=                             # Process ID (auto)
OPENCODE=1                                # Flag (auto)
```

### Status

| Provider | Status |
|----------|--------|
| OpenCode Go | ✅ Configured |
| OpenRouter | ✅ Configured |
| Anthropic | ✅ Configured |
| OpenAI | ✅ Configured |
| Google/Gemini | ✅ Configured |
| GitHub | ✅ Configured |
| Alibaba | ✅ Configured |
| Moonshot | ✅ Configured |
| Brave Search | ⚠️ Needs key |

---

## Quick Reference

### Start OpenCode
```bash
opencode                    # Start TUI
opencode -m opencode-go/glm-5  # Specific model
opencode -c                 # Continue last session
```

### MCP Commands
```bash
opencode mcp list           # List servers
# MCP add crashes on Windows - edit config.json directly
```

### Model Selection
```bash
opencode models             # List all models
opencode models alibaba     # List Alibaba models
```

### Files Modified
```bash
# Configuration
~/.opencode/config.json     # Main config
~/.opencode/security.json   # Security settings

# Project configs
python/.opencode.json       # Archon backend
archon-ui-main/.opencode.json  # Archon frontend

# Custom skill
~/.agents/skills/archon-workflow/SKILL.md
```

### Documentation Files
```
~/OPENCODE_CONFIG.md            # Technical configuration
~/OPENCODE_COMPLETE_GUIDE.md   # All options guide
~/OPENCODE_ALL_OPTIONS.md       # Detailed analysis
~/OPENCODE_MASTER.md            # This file
```

---

## Next Steps

### Immediate Actions (5 minutes each)

1. **Set Brave API Key**
   ```bash
   export BRAVE_API_KEY=your_key
   ```
   Get free key at: https://brave.com/search/api/

2. **Test GitHub MCP**
   ```bash
   opencode
   # Try: "list my GitHub repositories"
   ```

3. **Test Custom Skill**
   ```bash
   cd python
   opencode
   # Try: "using archon-workflow skill, explain the API structure"
   ```

### Optional Enhancements

- Add more MCP servers (PostgreSQL, Puppeteer)
- Create additional custom skills
- Configure project-specific models
- Set up team sharing

---

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| Bun crash on Windows | Edit config files directly, use TUI mode |
| MCP not connecting | Check npm installation, verify args |
| Skills not loading | Check `~/.agents/skills/` directory |
| API key errors | Verify environment variables |
| Permission denied | Check security.json settings |

### Support

- **Issues:** https://github.com/sst/opencode/issues
- **Docs:** https://opencode.ai
- **Bun Bugs:** https://bun.report

---

## Changelog

### 2025-03-21 - Initial Configuration

**Added:**
- 6 MCP servers (filesystem, memory, context7, github, brave-search, fetch)
- 5 custom agents (security-auditor, test-generator, code-reviewer, documenter, devops)
- 1 custom skill (archon-workflow)
- 2 project configs (Archon backend + frontend)
- Security configuration
- 4 documentation files

**Configured:**
- 15 API providers
- 270 skills loaded
- Multi-model strategy
- oh-my-opencode plugin

---

*This documentation is auto-generated. Do not edit manually.*
*For updates, re-run the configuration process.*