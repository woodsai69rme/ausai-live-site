# Qwen Code Setup Complete ✅

**Date:** March 5, 2026  
**Qwen Version:** 0.11.1 (updated from 0.10.4)

---

## 📦 Installed Skills (104 Total)

### File Handling (anthropics/skills)
- `pdf` - PDF reading, writing, manipulation
- `docx` - Word document handling
- `pptx` - PowerPoint presentation handling
- `xlsx` - Excel spreadsheet handling

### Design & Creative (anthropics/skills)
- `frontend-design` - Production-grade frontend interfaces
- `canvas-design` - Visual art and poster creation
- `algorithmic-art` - Generative art with p5.js
- `brand-guidelines` - Anthropic brand styling
- `theme-factory` - Theme styling for artifacts
- `slack-gif-creator` - Animated GIFs for Slack
- `remotion` - Video generation from Stitch projects

### Development Workflow (obra/superpowers)
- `systematic-debugging` - Systematic bug investigation
- `test-driven-development` - TDD implementation
- `writing-plans` - Multi-step task planning
- `executing-plans` - Plan execution with checkpoints
- `verification-before-completion` - Evidence-based completion
- `using-git-worktrees` - Isolated git worktrees
- `requesting-code-review` - Code review requests
- `receiving-code-review` - Handling review feedback
- `finishing-a-development-branch` - Branch completion
- `subagent-driven-development` - Parallel task execution
- `dispatching-parallel-agents` - Independent task parallelization
- `brainstorming` - Creative exploration
- `writing-skills` - Skill creation
- `using-superpowers` - Skill discovery and usage

### React & Next.js (vercel-labs)
- `vercel-react-best-practices` - React performance optimization
- `vercel-react-native-skills` - React Native guidelines
- `vercel-composition-patterns` - Vercel composition patterns
- `web-design-guidelines` - Web interface guidelines
- `next-best-practices` - Next.js file conventions, RSC, data patterns
- `next-cache-components` - Next.js 16 caching (PPR, cache directive)
- `next-upgrade` - Next.js version upgrades

### Azure & Microsoft (microsoft/github-copilot-for-azure)
- `azure-ai` - Azure AI: Search, Speech, OpenAI, Document Intelligence
- `azure-deploy` - Azure deployments (azd, terraform, bicep)
- `azure-prepare` - App preparation for deployment
- `azure-validate` - Pre-deployment validation
- `azure-diagnostics` - Production troubleshooting
- `azure-observability` - Azure Monitor, Application Insights
- `azure-storage` - Blob, File Shares, Queue, Table, Data Lake
- `azure-cost-optimization` - Cost savings analysis
- `azure-compliance` - Security auditing, Key Vault monitoring
- `azure-resource-lookup` - List and find Azure resources
- `azure-resource-visualizer` - Mermaid architecture diagrams
- `azure-compute` - VM size recommendations
- `azure-kusto` - KQL queries for Azure Data Explorer
- `azure-messaging` - Event Hubs, Service Bus troubleshooting
- `azure-rbac` - RBAC role recommendations
- `azure-cloud-migrate` - Cross-cloud migration (AWS/GCP to Azure)
- `azure-aigateway` - API Management as AI Gateway
- `azure-hosted-copilot-sdk` - Copilot SDK apps on Azure
- `azure-validate` - Deployment readiness checks
- `entra-app-registration` - Entra ID app registration
- `microsoft-foundry` - Azure AI Foundry agent deployment
- `appinsights-instrumentation` - Application Insights telemetry

### Better Auth (better-auth/skills)
- `create-auth-skill` - Authentication scaffolding
- `better-auth-best-practices` - Server/client configuration
- `better-auth-security-best-practices` - Rate limiting, CSRF, sessions
- `email-and-password-best-practices` - Email verification, password reset
- `two-factor-authentication-best-practices` - TOTP, OTP, 2FA flows
- `organization-best-practices` - Multi-tenant orgs, RBAC

### Google Stitch (google-labs-code/stitch-skills)
- `design-md` - DESIGN.md synthesis for Stitch projects
- `enhance-prompt` - Stitch-optimized prompt enhancement
- `react-components` - Vite/React component conversion
- `shadcn-ui` - shadcn/ui component integration
- `stitch-loop` - Iterative website building with Stitch
- `remotion` - Walkthrough videos from Stitch projects

### Expo (expo/skills)
- `building-native-ui` - Expo Router UI components
- `expo-api-routes` - API routes with EAS Hosting
- `expo-deployment` - iOS/Android/web deployment
- `expo-dev-client` - Development client builds
- `expo-tailwind-setup` - Tailwind CSS v4 setup
- `native-data-fetching` - Network requests, React Query
- `use-dom` - Expo DOM components for web
- `upgrading-expo` - SDK version upgrades
- `expo-cicd-workflows` - EAS workflow YAML files

### Utility Skills
- `mcp-builder` - MCP server creation
- `skill-creator` - Skill creation and optimization
- `sensei` - Skill frontmatter compliance
- `skill-authoring` - Skill writing guidelines
- `file-test-bug` - GitHub issue filing for test failures
- `markdown-token-optimizer` - Token efficiency for markdown
- `doc-coauthoring` - Documentation co-authoring
- `internal-comms` - Internal communications (status reports, FAQs)
- `web-artifacts-builder` - Multi-component HTML artifacts
- `webapp-testing` - Playwright web app testing
- `template-skill` - Skill template

### Additional Skills (Previously Installed)
- `archon-integration` - Archon AI integration
- `d3js-visualization` - D3.js visualizations
- `docker-compose` - Docker Compose configurations
- `ios-development` - iOS development guidelines
- `janitor-agent` - Janitor AI agent
- `ollama-management` - Ollama model management
- `playwright-skill` - Playwright testing
- `rag-nexus` - RAG implementation
- `revenue-pipeline` - Revenue analytics
- `search-agent` - Search agent functionality
- `supabase-db` - Supabase database patterns
- `superpowers-lab` - Superpowers lab tools
- `web-asset-generator` - Web asset generation
- `web-fuzzing` - Web fuzzing testing

---

## 🔌 MCP Servers Configured

Added to `C:\Users\karma\.qwen\settings.json`:

### 1. Filesystem MCP
```json
{
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-filesystem", "C:\\Users\\karma\\projects", "C:\\Users\\karma\\ACTIVE_PROJECTS"]
}
```
**Purpose:** Safe filesystem access to project directories

### 2. Memory MCP
```json
{
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-memory"]
}
```
**Purpose:** Knowledge graph-based memory for Claude

### 3. Sequential Thinking MCP
```json
{
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"]
}
```
**Purpose:** Step-by-step problem solving

---

## 🛠️ Built-in Subagents (Always Available)

| Subagent | Purpose |
|----------|---------|
| `code-reviewer` | Comprehensive code reviews |
| `documentation-writer` | README, API docs, user guides |
| `testing-expert` | Test suites with mocking |
| `general-purpose` | Research, code search, multi-step tasks |

---

## 📝 Usage Examples

### Using Skills
Skills are automatically available when you ask Qwen to perform related tasks:

```
"Create a PDF report from this data"  → Uses pdf skill
"Build a React component"             → Uses frontend-design, vercel-react-best-practices
"Deploy to Azure"                     → Uses azure-deploy, azure-prepare
"Add authentication"                  → Uses create-auth-skill, better-auth-best-practices
```

### Using MCP Servers
MCP servers are automatically invoked when their capabilities are needed:

```
"Search my project files"             → Uses filesystem MCP
"Remember this pattern"               → Uses memory MCP
"Think through this problem"          → Uses sequential-thinking MCP
```

### Using Subagents
Subagents are automatically delegated for complex tasks:

```
"Review this code for security"       → Uses code-reviewer subagent
"Write comprehensive tests"           → Uses testing-expert subagent
"Create API documentation"            → Uses documentation-writer subagent
"Research best practices for X"       → Uses general-purpose subagent
```

---

## 🔧 Configuration Files

### Qwen Settings
**Location:** `C:\Users\karma\.qwen\settings.json`

Key configurations:
- Model routing with fallbacks
- MCP servers enabled
- Auto-save sessions
- Cache auto-clear (weekly)
- Parallel tool calls (max 5)

### Skills Location
**Location:** `C:\Users\karma\.agents\skills\`

104 skills installed and symlinked to Qwen Code.

---

## 🚀 Quick Start

```bash
# Check Qwen version
qwen --version

# List MCP servers
qwen mcp list

# Start interactive session
qwen

# Use with prompt
qwen -p "Build a React dashboard with Azure integration"
```

---

## 📊 Summary

| Category | Count |
|----------|-------|
| **Skills Installed** | 104 |
| **MCP Servers** | 3 |
| **Built-in Subagents** | 4 |
| **Qwen Version** | 0.11.1 |

---

## ⚠️ Security Notes

Skills run with **full agent permissions**. Review skill code before use:
- Skills are located in `C:\Users\karma\.agents\skills\`
- Each skill has a `SKILL.md` file with documentation
- Security assessments were performed during installation

---

**Setup completed successfully!** 🎉
