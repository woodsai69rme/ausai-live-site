# OpenCode CLI Configuration Documentation

## Overview

OpenCode CLI is a powerful AI-powered development tool with 269 specialized skills, multi-agent orchestration, and MCP (Model Context Protocol) server integration.

## Installation

```bash
npm install -g opencode-ai
```

**Current Version:** 1.2.27
**Runtime:** Bun v1.3.10 (Windows x64)

---

## Directory Structure

```
C:\Users\karma\
├── .opencode/
│   └── config.json          # Main OpenCode configuration
├── .agents/
│   └── skills/              # 269 specialized skills
│       ├── python-testing-patterns/
│       ├── azure-deploy/
│       ├── solidify-security/
│       └── ... (269 total)
├── .claude/
│   ├── CLAUDE.md           # Claude Code instructions
│   ├── agents/             # Agent configurations
│   └── commands/           # Command definitions
└── .local/
    └── share/
        └── opencode/
            ├── auth.json   # API credentials
            ├── opencode.db # SQLite database
            └── bin/        # Binaries (rg.exe, etc.)
```

---

## Configuration Files

### 1. Main Config (`~/.opencode/config.json`)

```json
{
  "plugins": ["oh-my-opencode"],
  "mcp": {
    "context7": {
      "type": "remote",
      "url": "https://mcp.context7.com/sse"
    },
    "filesystem": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "C:\\Users\\karma"]
    },
    "memory": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"]
    }
  },
  "oh-my-opencode": {
    "features": {
      "multiAgentOrchestration": true,
      "lspAstTools": true,
      "claudeCodeCompatibility": true,
      "enhancedSearch": true,
      "smartRefactor": true,
      "contextAwareCompletion": true,
      "aiPoweredDebugging": true,
      "automatedCodeReview": true,
      "intelligentTaskManagement": true
    },
    "agents": {
      "oracle": {
        "enabled": true,
        "model": "claude-sonnet-4"
      },
      "librarian": {
        "enabled": true,
        "model": "gpt-4o"
      }
    }
  }
}
```

### 2. Auth Credentials (`~/.local/share/opencode/auth.json`)

```json
{
  "opencode-go": {
    "type": "api",
    "key": "sk-MBxgBDsAgJvO8TcsRGXlhv6mCFl37WGYoTFK53m2PFa21LC3fFMuC98gaopwqVEM"
  }
}
```

---

## Environment Variables

### AI Provider API Keys

| Variable | Description |
|----------|-------------|
| `ANTHROPIC_API_KEY` | Anthropic Claude API |
| `OPENAI_API_KEY` | OpenAI GPT API |
| `OPENROUTER_API_KEY` | OpenRouter multi-model access |
| `GEMINI_API_KEY` / `GOOGLE_API_KEY` | Google Gemini API |
| `GITHUB_TOKEN` | GitHub Models & Copilot |
| `DASHSCOPE_API_KEY` / `ALIBABA_API_KEY` | Alibaba/Qwen models |
| `MOONSHOT_API_KEY` | Moonshot AI models |
| `GOOGLE_APPLICATION_CREDENTIALS` | Google Vertex AI |

### Required for MCP Servers

| Variable | Description |
|----------|-------------|
| `BRAVE_API_KEY` | Brave Search MCP (optional) |

---

## MCP Servers

### Configured Servers

| Server | Type | Purpose |
|--------|------|---------|
| **filesystem** | stdio | Filesystem read/write access |
| **memory** | stdio | Persistent memory across conversations |
| **context7** | remote | Documentation lookup service |

### Available MCP Servers (Installable)

```bash
npm install -g @modelcontextprotocol/server-filesystem
npm install -g @modelcontextprotocol/server-memory
npm install -g @modelcontextprotocol/server-sequential-thinking
npm install -g @modelcontextprotocol/server-brave-search
npm install -g @modelcontextprotocol/server-github
```

---

## Skills (269 Total)

### Categories

#### Development & Testing
- `python-testing-patterns` - pytest, fixtures, mocking
- `test-driven-development` - TDD workflow
- `javascript-testing-patterns` - Jest, Vitest
- `e2e-testing-patterns` - Playwright, Cypress
- `code-review-excellence` - Review best practices

#### Security
- `solidity-security` - Smart contract security
- `sast-configuration` - Static analysis setup
- `auth-implementation-patterns` - Auth patterns
- `pci-compliance` - Payment security
- `gdpr-data-handling` - Privacy compliance

#### Cloud & DevOps
- `azure-deploy` - Azure deployment
- `k8s-manifest-generator` - Kubernetes manifests
- `terraform-module-library` - Infrastructure as code
- `github-actions-templates` - CI/CD workflows
- `docker-compose` - Container orchestration

#### AI & Machine Learning
- `rag-implementation` - Retrieval augmented generation
- `llm-evaluation` - LLM testing strategies
- `mcp-builder` - MCP server development
- `langchain-architecture` - LangChain patterns
- `embedding-strategies` - Vector embeddings

#### Web Development
- `next-best-practices` - Next.js patterns
- `react-state-management` - React state management
- `vercel-react-best-practices` - Vercel optimization
- `tailwind-design-system` - Tailwind CSS
- `shadcn-ui` - UI components

#### Database
- `postgresql-table-design` - PostgreSQL schema design
- `sql-optimization-patterns` - Query optimization
- `dbt-transformation-patterns` - Data transformations
- `vector-index-tuning` - Vector database optimization

#### Mobile
- `react-native-architecture` - React Native patterns
- `expo-deployment` - Expo app deployment
- `mobile-ios-design` - iOS design guidelines
- `mobile-android-design` - Android Material Design

#### Specialized Skills
- `dap-viz` - D3.js visualizations
- `algorithmic-art` - p5.js generative art
- `web-asset-generator` - Favicons, icons
- `canvas-design` - Poster/art creation

---

## Agents

### Primary Agent: `build`

System prompt and permissions configured for software development tasks.

```json
{
  "permission": "*",
  "action": "allow",
  "pattern": "*"
}
```

### Additional Agents (oh-my-opencode)

| Agent | Model | Purpose |
|-------|-------|---------|
| `oracle` | Claude Sonnet 4 | Primary reasoning |
| `librarian` | GPT-4o | Knowledge retrieval |

---

## Available AI Models

### OpenCode Go (Primary)
```
opencode-go/glm-5
opencode-go/kimi-k2.5
opencode-go/minimax-m2.5
opencode-go/minimax-m2.7
```

### Free Models
```
opencode/big-pickle
opencode/gpt-5-nano
opencode/mimo-v2-omni-free
opencode/mimo-v2-pro-free
opencode/minimax-m2.5-free
opencode/nemotron-3-super-free
```

### Alibaba/Qwen
```
alibaba/qwen-max
alibaba/qwen-plus
alibaba/qwen-turbo
alibaba/qwen3-max
alibaba/qwen3-coder-flash
alibaba/qwq-plus
```

---

## Commands

### Basic Usage
```bash
opencode                  # Start TUI in current directory
opencode <project>       # Start in specific project
opencode run <message>   # Run with message
opencode -m <model>      # Use specific model
```

### Session Management
```bash
opencode -c              # Continue last session
opencode -s <session-id># Resume specific session
opencode --fork          # Fork when continuing
```

### MCP Management
```bash
opencode mcp list        # List configured servers
opencode mcp add         # Add new server
opencode mcp auth <name> # Authenticate OAuth server
```

### Provider Management
```bash
opencode providers list  # List configured providers
opencode models          # List available models
opencode models <provider> # Models for specific provider
```

### GitHub Integration
```bash
opencode github          # Manage GitHub agent
opencode pr <number>     # Work on PR branch
```

### Utilities
```bash
opencode stats           # Token usage statistics
opencode upgrade         # Update to latest version
opencode export <id>     # Export session as JSON
opencode import <file>   # Import session
```

---

## Known Issues

### Bun Runtime Crash (Windows)

**Issue:** Some commands crash with "Bun has crashed" on Windows.

```
panic(main thread): Stack overflow
panic(main thread): Illegal instruction
```

**Affected Commands:**
- `opencode mcp add`
- `opencode agent list`
- `opencode upgrade`

**Workarounds:**
1. Configure MCP servers directly in `~/.opencode/config.json`
2. Use `opencode mcp list` via TUI mode
3. Edit configuration files manually

### Disk Space

**Issue:** C: drive fills up quickly with caches.

**Recommended:** Keep at least 10GB free for normal operation.

```bash
# Clean npm cache
npm cache clean --force

# Clean bun cache
rm -rf ~/.bun/install/cache
```

---

## Performance Optimization

### Model Selection

| Use Case | Recommended Model |
|----------|-------------------|
| General coding | `opencode-go/glm-5` |
| Complex reasoning | `alibaba/qwq-plus` |
| Fast responses | `opencode/big-pickle` |
| Code generation | `alibaba/qwen3-coder-flash` |
| Multi-modal | `alibaba/qwen3-omni-flash` |

### Token Optimization

```bash
# Check usage
opencode stats

# Use streaming for long responses
opencode --streaming

# Limit context when needed
# In config: "maxTokens": 4096
```

### Skills Selection

Load only needed skills for better performance:

1. Startup/Financial: `startup-financial-modeling`, `startup-metrics-framework`
2. Web Dev: `next-best-practices`, `vercel-react-best-practices`, `shadcn-ui`
3. Security: `solidity-security`, `sast-configuration`, `auth-implementation-patterns`
4. DevOps: `azure-deploy`, `k8s-manifest-generator`, `github-actions-templates`

---

## Troubleshooting

### MCP Server Not Connecting

```bash
# Verify server is installed
npm list -g @modelcontextprotocol/server-filesystem

# Test server directly
npx -y @modelcontextprotocol/server-filesystem /path/to/dir
```

### Skills Not Loading

```bash
# Check skills directory
ls ~/.agents/skills/ | wc -l  # Should show 269

# Verify SKILL.md exists
find ~/.agents/skills -name "SKILL.md" | wc -l
```

### Auth Issues

```bash
# Re-authenticate provider
opencode providers

# Check auth file
cat ~/.local/share/opencode/auth.json
```

### Database Issues

```bash
# Backup and reset
cp ~/.local/share/opencode/opencode.db ~/.local/share/opencode/backup.db
rm ~/.local/share/opencode/opencode.db*
```

---

## Integration with Other Tools

### Claude Code

OpenCode integrates with Claude Code via the `oh-my-opencode` plugin:

- `claudeCodeCompatibility`: true
- Shares skills from `~/.agents/skills/`
- Compatible configuration format

### Cursor/Windsurf

MCP servers configured in OpenCode are accessible to Cursor and Windsurf editors.

### VS Code

Extension available: `tanishqkancharla.opencode-vscode`

---

## File Locations Summary

| File/Directory | Purpose |
|----------------|---------|
| `~/.opencode/config.json` | Main configuration |
| `~/.local/share/opencode/auth.json` | API credentials |
| `~/.local/share/opencode/opencode.db` | Session database |
| `~/.agents/skills/` | Skills library (269) |
| `~/.claude/CLAUDE.md` | Claude Code instructions |
| `~/.config/opencode-cli/config.json` | CLI configuration |

---

## Quick Reference Card

```
# Start OpenCode
opencode

# Use specific model
opencode -m opencode-go/glm-5

# Continue last session
opencode -c

# Work on GitHub PR
opencode pr 123

# Check stats
opencode stats

# List models
opencode models

# Export session
opencode export > backup.json
```

---

## Support

- **Issues:** https://github.com/sst/opencode/issues
- **Documentation:** https://opencode.ai
- **Bun Bugs:** https://bun.report

---

*Last Updated: 2025-03-20*
*Configuration Version: 1.2.27*