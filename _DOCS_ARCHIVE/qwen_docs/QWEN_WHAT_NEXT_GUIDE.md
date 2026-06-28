# 🎯 Qwen Code: What Should I Do Next?

**Interactive Decision Guide** | **250+ Skills** | **4 MCP Servers** | **4 Subagents**

---

## 🚀 Quick Decision Tree

### "I want to..."

```
┌─────────────────────────────────────────────────────────────┐
│  What do you want to accomplish today?                      │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
   ┌─────────┐        ┌─────────┐        ┌─────────┐
   │  BUILD  │        │  FIX    │        │ LEARN   │
   │  Something│       │  Something│       │ Something│
   └────┬────┘        └────┬────┘        └────┬────┘
        │                   │                   │
        ▼                   ▼                   ▼
   Web App?             Bug?              New Tech?
   API?                 Slow?             Best Practices?
   Mobile?              Test failing?     Documentation?
   AI feature?          Security issue?   Skill mastery?
```

---

## 📋 By Goal: Immediate Actions

### I Want To Build...

| Goal | Skills to Use | MCP | Example Prompt |
|------|---------------|-----|----------------|
| **Web Application** | `next-best-practices` → `react-state-management` → `frontend-design` | filesystem | "Build a Next.js dashboard with real-time data" |
| **REST API** | `api-design-principles` → `nodejs-backend-patterns` → `openapi-spec-generation` | filesystem | "Create a REST API with proper documentation" |
| **AI Feature** | `rag-implementation` → `embedding-strategies` → `llm-evaluation` | memory | "Add RAG-based search to my app" |
| **Mobile App** | `building-native-ui` → `expo-deployment` → `native-data-fetching` | filesystem | "Build a cross-platform mobile app" |
| **Data Pipeline** | `airflow-dag-patterns` → `dbt-transformation-patterns` → `data-quality-frameworks` | sequential-thinking | "Create an ETL pipeline with monitoring" |
| **Azure Deployment** | `azure-prepare` → `azure-validate` → `azure-deploy` | sequential-thinking | "Deploy my app to Azure Container Apps" |
| **Authentication** | `create-auth-skill` → `better-auth-best-practices` → `two-factor-authentication` | filesystem | "Add secure authentication with 2FA" |
| **Document Processing** | `pdf` → `xlsx` → `internal-comms` | filesystem | "Process these PDFs and create a summary report" |

### I Want To Fix...

| Problem | Skills to Use | MCP | Example Prompt |
|---------|---------------|-----|----------------|
| **Bug in Code** | `systematic-debugging` → `python-testing-patterns` or `javascript-testing-patterns` | sequential-thinking | "Use systematic-debugging to find why this test fails" |
| **Slow Performance** | `python-performance-optimization` or `sql-optimization-patterns` | memory | "Profile and optimize this slow function" |
| **Failing Tests** | `test-driven-development` → `e2e-testing-patterns` → `webapp-testing` | puppeteer | "Fix these failing E2E tests" |
| **Security Vulnerability** | `stride-analysis-patterns` → `sast-configuration` → `threat-mitigation-mapping` | sequential-thinking | "Audit this code for security issues" |
| **Production Issue** | `azure-diagnostics` → `incident-runbook-templates` → `postmortem-writing` | memory | "Investigate this production error" |
| **Code Quality** | `code-review-excellence` → `python-code-style` or `vercel-react-best-practices` | filesystem | "Review this code for best practices" |

### I Want To Learn...

| Topic | Skills to Use | Example Prompt |
|-------|---------------|----------------|
| **New Framework** | `next-best-practices` or `react-modernization` | "Teach me Next.js 14 App Router patterns" |
| **Best Practices** | `vercel-react-best-practices` or `python-design-patterns` | "Show me React best practices for 2026" |
| **Architecture** | `architecture-patterns` → `microservices-patterns` → `event-store-design` | "Explain microservices architecture with examples" |
| **Security** | `stride-analysis-patterns` → `solidity-security` or `auth-implementation-patterns` | "Teach me threat modeling with STRIDE" |
| **DevOps** | `gitops-workflow` → `helm-chart-scaffolding` → `k8s-manifest-generator` | "Explain GitOps deployment workflow" |
| **AI/ML** | `rag-implementation` → `langchain-architecture` → `prompt-engineering-patterns` | "Teach me RAG implementation patterns" |

---

## 🎯 By Project Type

### 1. Full-Stack Web Application

```
Week 1: Foundation
├─ Day 1-2: architecture-patterns + api-design-principles
├─ Day 3-4: nextjs-app-router-patterns + react-state-management
└─ Day 5-7: backend setup (nodejs-backend-patterns or fastapi-templates)

Week 2: Features
├─ Authentication: create-auth-skill + two-factor-authentication
├─ Database: postgresql-table-design
└─ API: openapi-spec-generation

Week 3: Polish & Deploy
├─ Testing: test-driven-development + e2e-testing-patterns
├─ Deployment: azure-deploy or vercel-deploy
└─ Monitoring: azure-observability or prometheus-configuration
```

### 2. AI-Powered Application

```
Phase 1: Core AI
├─ rag-implementation
├─ embedding-strategies
├─ llm-evaluation
└─ prompt-engineering-patterns

Phase 2: Integration
├─ langchain-architecture
├─ hybrid-search-implementation
└─ vector-index-tuning

Phase 3: Production
├─ ml-pipeline-workflow
├─ azure-ai
└─ distributed-tracing
```

### 3. Data Engineering Pipeline

```
Step 1: Ingestion
├─ airflow-dag-patterns
└─ python-background-jobs

Step 2: Transformation
├─ dbt-transformation-patterns
├─ spark-optimization
└─ data-quality-frameworks

Step 3: Analytics
├─ kpi-dashboard-design
├─ grafana-dashboards
└─ data-storytelling
```

### 4. Mobile Application

```
Week 1: Setup
├─ building-native-ui
├─ expo-tailwind-setup
└─ native-data-fetching

Week 2: Features
├─ react-native-architecture
├─ react-state-management
└─ offline-first patterns

Week 3: Deploy
├─ expo-deployment
├─ expo-dev-client
└─ expo-cicd-workflows
```

---

## 🔌 MCP Server Decision Guide

### Which MCP Should I Use?

| Task | MCP Server | Example |
|------|------------|---------|
| Read/write project files safely | **filesystem** | "Search my projects folder for React components" |
| Remember patterns & context | **memory** | "Remember this architecture pattern for future use" |
| Complex problem solving | **sequential-thinking** | "Think through this bug step by step" |
| Browser automation | **puppeteer** | "Take a screenshot of my deployed site" |

### MCP Combinations

```
Filesystem + Memory = Context-Aware File Operations
"Read this file and remember the patterns for future projects"

Sequential-Thinking + Puppeteer = Systematic Browser Debugging
"Systematically debug why my website looks broken on mobile"

All 4 MCPs = Full Development Environment
"Build, test, and deploy a feature with full context tracking"
```

---

## 🤖 Subagent Decision Guide

### Which Subagent Should I Use?

| When You Need... | Use This Subagent |
|------------------|-------------------|
| Code quality check | `code-reviewer` |
| Documentation | `documentation-writer` |
| Test coverage | `testing-expert` |
| Research or complex task | `general-purpose` |

### Subagent + Skill Combinations

```
code-reviewer + vercel-react-best-practices
= Expert React code review

testing-expert + test-driven-development
= Comprehensive test suite creation

documentation-writer + openapi-spec-generation
= Complete API documentation

general-purpose + architecture-patterns
= Deep architectural research and recommendations
```

---

## 🎓 Learning Path Selector

### Find Your Level

**Beginner** (0-3 months with Qwen Code)
- Focus: File operations, basic web dev, simple debugging
- Skills: 10-20 core skills
- Goal: Comfortable daily use

**Intermediate** (3-6 months)
- Focus: Full-stack projects, AI integration, cloud deployment
- Skills: 50+ skills across categories
- Goal: Production-ready applications

**Advanced** (6-12 months)
- Focus: Architecture, optimization, custom skills
- Skills: 100+ skills, custom combinations
- Goal: System design and mentorship

**Expert** (12+ months)
- Focus: Creating skills, enterprise patterns, community contribution
- Skills: All 250+, custom creations
- Goal: Ecosystem contribution

### Weekly Learning Plan

```
Week 1-2: Core Skills
├─ pdf, docx, xlsx (file operations)
├─ frontend-design (web dev)
├─ systematic-debugging (debugging)
└─ test-driven-development (testing)

Week 3-4: Backend & API
├─ api-design-principles
├─ nodejs-backend-patterns or fastapi-templates
├─ postgresql-table-design
└─ openapi-spec-generation

Week 5-6: Cloud & DevOps
├─ azure-deploy (or your cloud of choice)
├─ gitops-workflow
├─ github-actions-templates
└─ prometheus-configuration

Week 7-8: AI & Advanced
├─ rag-implementation
├─ embedding-strategies
├─ llm-evaluation
└─ ml-pipeline-workflow
```

---

## 🛠️ Advanced Integration Patterns

### Pattern 1: Complete Feature Development

```
1. brainstorming (generate ideas)
    ↓
2. writing-plans (create implementation plan)
    ↓
3. architecture-patterns (design architecture)
    ↓
4. executing-plans (implement)
    ↓
5. test-driven-development (write tests)
    ↓
6. verification-before-completion (verify)
    ↓
7. requesting-code-review (get review)
```

### Pattern 2: Bug Resolution

```
1. systematic-debugging (investigate)
    ↓
2. parallel-debugging (multiple hypotheses)
    ↓
3. Fix the issue
    ↓
4. python-testing-patterns or javascript-testing-patterns (test fix)
    ↓
5. verification-before-completion (confirm fix)
```

### Pattern 3: Security Audit

```
1. stride-analysis-patterns (identify threats)
    ↓
2. attack-tree-construction (visualize attacks)
    ↓
3. sast-configuration (automated scanning)
    ↓
4. security-requirement-extraction (define requirements)
    ↓
5. threat-mitigation-mapping (create fixes)
```

### Pattern 4: AI Feature Build

```
1. rag-implementation (core RAG)
    ↓
2. embedding-strategies (optimize embeddings)
    ↓
3. hybrid-search-implementation (add keyword search)
    ↓
4. vector-index-tuning (optimize performance)
    ↓
5. llm-evaluation (test quality)
```

---

## 📊 Skill Discovery Matrix

### By Technology Stack

| Stack | Essential Skills | Nice to Have |
|-------|-----------------|--------------|
| **React/Next.js** | next-best-practices, vercel-react-best-practices, react-state-management | next-cache-components, next-upgrade |
| **Python** | python-testing-patterns, python-performance-optimization, fastapi-templates | python-packaging, python-observability |
| **Node.js** | nodejs-backend-patterns, javascript-testing-patterns, modern-javascript-patterns | monorepo-management, turborepo-caching |
| **Azure** | azure-deploy, azure-ai, azure-storage | All 25 Azure skills |
| **Mobile** | building-native-ui, expo-deployment, native-data-fetching | expo-tailwind-setup, expo-api-routes |
| **AI/ML** | rag-implementation, embedding-strategies, llm-evaluation | langchain-architecture, prompt-engineering-patterns |

### By Use Case

| Use Case | Top 5 Skills |
|----------|--------------|
| **Startup MVP** | fastapi-templates or nodejs-backend-patterns, frontend-design, azure-deploy, test-driven-development, stripe-integration |
| **Enterprise App** | architecture-patterns, microservices-patterns, azure-deploy, gitops-workflow, distributed-tracing |
| **Data Product** | airflow-dag-patterns, dbt-transformation-patterns, data-quality-frameworks, grafana-dashboards, data-storytelling |
| **AI Startup** | rag-implementation, embedding-strategies, llm-evaluation, azure-ai, ml-pipeline-workflow |

---

## 🎯 30-Day Challenge Calendar

### Week 1: Foundation
- [ ] Day 1: Set up skill tracking spreadsheet
- [ ] Day 2: Master pdf, docx, xlsx skills
- [ ] Day 3: Build something with frontend-design
- [ ] Day 4: Use systematic-debugging on a real bug
- [ ] Day 5: Implement test-driven-development
- [ ] Day 6-7: Mini-project using Week 1 skills

### Week 2: Backend & API
- [ ] Day 8: Learn api-design-principles
- [ ] Day 9: Build API with nodejs-backend-patterns
- [ ] Day 10: Design database with postgresql-table-design
- [ ] Day 11: Document with openapi-spec-generation
- [ ] Day 12: Test with javascript-testing-patterns
- [ ] Day 13-14: Mini-project: Complete API

### Week 3: Cloud & DevOps
- [ ] Day 15: Learn azure-deploy or your cloud
- [ ] Day 16: Set up CI/CD with github-actions-templates
- [ ] Day 17: Implement gitops-workflow
- [ ] Day 18: Configure monitoring with prometheus-configuration
- [ ] Day 19: Create dashboards with grafana-dashboards
- [ ] Day 20-21: Deploy Week 2 project

### Week 4: AI & Advanced
- [ ] Day 22: Learn rag-implementation
- [ ] Day 23: Implement embedding-strategies
- [ ] Day 24: Add hybrid-search-implementation
- [ ] Day 25: Evaluate with llm-evaluation
- [ ] Day 26: Optimize with vector-index-tuning
- [ ] Day 27-28: Capstone project
- [ ] Day 29-30: Document and share learnings

---

## 💡 Idea Generator

### Random Project Ideas

Pick one from each column:

| Type | Domain | Technology | Challenge |
|------|--------|------------|-----------|
| Web App | Finance | Next.js + Azure | Real-time updates |
| Mobile App | Health | Expo + Python | Offline-first |
| API Service | Education | FastAPI + RAG | Multi-tenant |
| Data Pipeline | E-commerce | Airflow + dbt | ML predictions |
| AI Tool | Productivity | LangChain + Vector DB | Voice interface |
| Dashboard | Analytics | React + Grafana | Sub-second latency |

### Skill Combination Challenges

```
Challenge 1: Build something using exactly these 5 skills:
- frontend-design
- api-design-principles
- postgresql-table-design
- test-driven-development
- azure-deploy

Challenge 2: Create a skill chain for your workflow:
- Identify 5 skills you use together
- Document the pattern
- Share with community

Challenge 3: MCP + Skill Integration:
- Use puppeteer MCP with webapp-testing
- Use memory MCP with rag-implementation
- Use filesystem MCP with skill-creator
```

---

## 📈 Progress Tracking Template

Copy this to track your journey:

```markdown
## My Qwen Code Journey

### Skills Mastered (add as you go)
- [ ] pdf, docx, xlsx
- [ ] frontend-design
- [ ] systematic-debugging
- [ ] test-driven-development
- [ ] api-design-principles
- [ ] nodejs-backend-patterns
- [ ] postgresql-table-design
- [ ] azure-deploy
- [ ] rag-implementation
- [ ] (add more...)

### Projects Built
1. [Project Name] - [Date] - Skills Used: [list]
2. [Project Name] - [Date] - Skills Used: [list]
3. [Project Name] - [Date] - Skills Used: [list]

### Favorite Skills (Top 10)
1.
2.
3.
4.
5.
6.
7.
8.
9.
10.

### Goals
- 30-day: [goal]
- 60-day: [goal]
- 90-day: [goal]
```

---

## 🆘 When You're Stuck

### "I don't know what to build"
→ Use `brainstorming` skill + `competitive-landscape` + `market-sizing-analysis`

### "I'm overwhelmed by 250+ skills"
→ Focus on 10 core skills for your stack (see Skill Discovery Matrix)

### "I keep forgetting how to use skills"
→ Use `memory` MCP to remember patterns + create personal cheat sheet

### "My setup isn't working"
→ Check `QWEN_QUICK_REFERENCE.md` troubleshooting section

### "I want to contribute but don't know how"
→ Start with bug reports → improve documentation → create simple skill

---

## ✅ Daily Quick Check

**Morning Planning:**
```
Today I will:
[ ] Use 1 new skill
[ ] Practice 1 familiar skill
[ ] Build something (even small)
[ ] Document what I learned
```

**Evening Reflection:**
```
Today I:
[ ] Learned: _______________
[ ] Built: _________________
[ ] Skills used: ___________
[ ] Tomorrow: _____________
```

---

## 🎁 Bonus: Skill of the Day

Generate daily challenges:

```
Day 1: Use `algorithmic-art` to create generative art
Day 2: Use `slack-gif-creator` to make an animated GIF
Day 3: Use `canvas-design` to design a poster
Day 4: Use `remotion` to create a video
Day 5: Use `internal-comms` to write a status report
Day 6: Use `data-storytelling` for a presentation
Day 7: Use `theme-factory` to style something
```

---

**Remember:** The goal isn't to use all 250+ skills, but to master the ones that matter for YOUR workflow. Start small, build gradually, and focus on high-impact capabilities first.

**Pick ONE thing from this document and start today!** 🚀
