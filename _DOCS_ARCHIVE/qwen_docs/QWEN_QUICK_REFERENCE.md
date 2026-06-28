# Qwen Code Quick Reference Card

**Version:** 0.11.1 | **Skills:** 104 | **MCP:** 3 | **Subagents:** 4

---

## 🚀 Essential Commands

```bash
qwen --version              # Check version
qwen                        # Start interactive mode
qwen -p "your prompt"       # Run with prompt
qwen -i "prompt"            # Interactive mode after prompt
qwen mcp list               # List MCP servers
qwen extensions list        # List extensions
```

---

## 📁 File Locations

```
Qwen Settings:    C:\Users\karma\.qwen\settings.json
Skills:           C:\Users\karma\.agents\skills\
Documentation:    C:\Users\karma\QWEN_CODE_SETUP_DOCUMENTATION.md
Recommendations:  C:\Users\karma\QWEN_RECOMMENDATIONS.md
```

---

## 🎯 Skill Categories (104 Total)

| Category | Count | Top Skills |
|----------|-------|------------|
| **File Handling** | 4 | pdf, docx, pptx, xlsx |
| **Web Development** | 20 | frontend-design, vercel-react-best-practices, next-best-practices, shadcn-ui |
| **Azure/Cloud** | 25 | azure-deploy, azure-ai, azure-storage, azure-compliance |
| **Dev Workflow** | 14 | systematic-debugging, test-driven-development, writing-plans |
| **Mobile (Expo)** | 9 | building-native-ui, expo-deployment, native-data-fetching |
| **Authentication** | 6 | create-auth-skill, two-factor-authentication-best-practices |
| **Creative** | 8 | canvas-design, algorithmic-art, remotion, slack-gif-creator |
| **Utilities** | 18 | mcp-builder, skill-creator, webapp-testing, internal-comms |

---

## 🔌 MCP Servers (3 Configured)

| Server | Purpose | Command |
|--------|---------|---------|
| **filesystem** | Safe file access | `npx -y @modelcontextprotocol/server-filesystem` |
| **memory** | Knowledge graph | `npx -y @modelcontextprotocol/server-memory` |
| **sequential-thinking** | Problem solving | `npx -y @modelcontextprotocol/server-sequential-thinking` |

---

## 🤖 Built-in Subagents

| Subagent | When It's Used |
|----------|----------------|
| `code-reviewer` | Code reviews, security audits |
| `documentation-writer` | README, API docs, guides |
| `testing-expert` | Test suites, mocking |
| `general-purpose` | Research, multi-step tasks |

---

## 💬 Prompt Templates

### File Operations
```
"Convert this PDF to a Word document"
"Extract data from this Excel file and create a summary"
"Create a PowerPoint presentation from this report"
```

### Web Development
```
"Build a React component with TypeScript for [feature]"
"Create a Next.js page with server-side rendering"
"Style this component using Tailwind CSS"
```

### Azure Deployment
```
"Deploy this application to Azure Container Apps"
"Set up Azure Key Vault for secrets management"
"Create infrastructure as code using Bicep"
```

### Debugging
```
"Use systematic-debugging to find why this test fails"
"Debug this production issue using azure-diagnostics"
```

### Planning
```
"Use writing-plans to break down this feature"
"Execute this plan using executing-plans skill"
"Verify completion using verification-before-completion"
```

---

## 🔄 Common Workflows

### New Feature Development
```
1. brainstorming → 2. writing-plans → 3. executing-plans → 
4. test-driven-development → 5. verification-before-completion → 
6. requesting-code-review
```

### Bug Fix
```
1. systematic-debugging → 2. read_file/grep_search → 
3. edit/write_file → 4. webapp-testing → 
5. verification-before-completion
```

### Azure Deployment
```
1. azure-prepare → 2. azure-validate → 3. azure-deploy → 
4. azure-observability → 5. azure-diagnostics (if needed)
```

### Document Processing
```
1. pdf/docx/xlsx → 2. internal-comms (for summary) → 
3. doc-coauthoring (for refinement)
```

---

## ⚡ Quick Fixes

### Skill Not Loading
```bash
# Restart terminal
# Check skill exists
dir C:\Users\karma\.agents\skills\[skill-name]
```

### MCP Server Error
```bash
# Test server manually
npx -y @modelcontextprotocol/server-filesystem C:\Users\karma\projects
```

### Slow Performance
```json
// Reduce in settings.json
"maxConcurrentTools": 3
```

---

## 🛡️ Security Checklist

- [ ] API keys in environment variables (not settings.json)
- [ ] Review skill code before first use
- [ ] Limit filesystem MCP to project directories
- [ ] Regular settings.json backup
- [ ] Keep Qwen updated: `npm install -g @qwen-code/qwen-code@latest`

---

## 📊 Skill Usage Tracker

Copy this to track your usage:

```markdown
### This Week
| Skill | Uses | Notes |
|-------|------|-------|
|       |      |       |

### Favorites (Top 5)
1. 
2. 
3. 
4. 
5. 
```

---

## 🆘 Emergency Commands

```bash
# Reset skills
npx skills add anthropics/skills --yes

# Update Qwen
npm install -g @qwen-code/qwen-code@latest

# Clear cache
npm cache clean --force

# Check settings
cat C:\Users\karma\.qwen\settings.json
```

---

## 📞 Support

- **Docs:** `C:\Users\karma\QWEN_CODE_SETUP_DOCUMENTATION.md`
- **Recommendations:** `C:\Users\karma\QWEN_RECOMMENDATIONS.md`
- **GitHub:** https://github.com/anthropics/qwen-code
- **Skills:** https://skills.sh

---

**Print this card and keep it at your desk!** 📌
