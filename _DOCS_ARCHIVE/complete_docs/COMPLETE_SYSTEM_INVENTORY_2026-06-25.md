# COMPLETE SYSTEM INVENTORY — 2026-06-25

> **Every tool, app, platform, repo, script, database, service, and config file discovered across both drives.**

---

## PART 1: C:\Users\karma (Primary Workspace)

### Git Repositories (8)

| Repo | Remote | Branch | Dirty | Verdict |
|---|---|---|---|---|
| **Root (Archon V2)** | coleam00/archon.git | master | 568 | ✅ KEEP — core project |
| **ComfyUI** | comfyanonymous/ComfyUI | master | 10 | ✅ KEEP — your launcher + scripts |
| **whisper.cpp** | ggerganov/whisper.cpp | master | 0 | ✅ KEEP — transcription dep |
| **ACTIVE_PROJECTS** | woodsai69rme/Empire-Active-Labs | main | 21,566 | ⚠️ Bloated |
| **agent-zero** | agent0ai/agent-zero | main | 1 | 🗑️ DELETE — superseded |
| **ai-music-video-studio** | none | main | 2 | 🗑️ MERGE → ComfyUI |
| **aigf** | none | main | 0 | 🗑️ DELETE — unused |
| **tadpole-studio** | proximasan/tadpole-studio | master | 2 | 🗑️ DELETE — zero activity |

### Runtimes & Languages

| Tool | Version | Status |
|---|---|---|
| Python | 3.13 (pip) / 3.12 (venv) | ✅ |
| Node.js | v22.19.0 | ✅ |
| npm | 10.9.3 | ✅ |
| pnpm | 10.33.4 | ✅ |
| bun | 1.2.20 | ✅ |
| yarn | 1.22.22 | ✅ |
| uv | 0.11.21 | ✅ |
| Java | — | ❌ Not found |
| Rust | — | ❌ Not found |
| Go | — | ❌ Not found |
| .NET | — | ❌ Not found |
| Conda | — | ❌ Not found |

### Package Managers

| Manager | Status |
|---|---|
| pip | ✅ 26.0.1 |
| uv | ✅ 0.11.21 |
| npm | ✅ 10.9.3 |
| pnpm | ✅ 10.33.4 |
| bun | ✅ 1.2.20 |
| yarn | ✅ 1.22.22 |

### NPM Global Packages (50+)

**AI/LLM Coding Agents:**
- @anthropic-ai/claude-code 2.1.126
- @google/gemini-cli 0.46.0
- @openai/codex 0.121.0
- @qwen-code/qwen-code 0.14.5
- @kilocode/cli 7.3.54
- cline (latest)
- @opencode-ai/cli 1.17.10
- @augmentcode/auggie 0.13.0
- @charmland/crush 0.65.2
- @mariozechner/pi-coding-agent 0.67.68
- @genspark/cli 1.0.23
- openclaw 2026.6.6
- paperclipai 2026.427.0
- @byterover/cipher 0.2.2

**MCP Servers:**
- @modelcontextprotocol/server-brave-search 0.6.2
- @modelcontextprotocol/server-filesystem 2025.7.29
- @modelcontextprotocol/server-github 2025.4.8
- @modelcontextprotocol/server-postgres 0.6.2
- @upstash/context7-mcp v1.0.14
- @kazuph/mcp-fetch 1.5.0

**Workflow/Deploy:**
- n8n 1.104.2
- vercel 52.0.0
- netlify-cli 23.4.0
- pm2 6.0.8
- flowise 1.6.0
- @tauri-apps/cli 2.7.1
- create-react-app 5.1.0

**Dev Tools:**
- typescript 5.9.2
- vite 6.3.5
- @vscode/vsce 3.6.0
- npm-check-updates 18.0.3

**Other:**
- claude-code-router 1.0.39
- claude-flow 2.0.0-alpha.88
- claude-conductor 1.1.2
- superclaude 1.0.3
- composio-core 0.5.39
- freebuff 0.0.107
- octofriend 0.0.25
- @lobehub/market-cli 0.0.28

### Python Packages (600+ installed)

**Key categories:**

| Category | Packages |
|---|---|
| AI/LLM | openai, anthropic, langchain (full suite), pydantic-ai, crewai, autogen, google-generativeai, groq, mistralai, together, litellm, cohere |
| ML/DL | torch 2.11.0, tensorflow 2.20.0, transformers 4.57.3, keras 3.11.2, scikit-learn 1.8.0, numpy, pandas, scipy |
| Computer Vision | opencv-python 4.12.0, pillow, kornia, mediapipe, torchvision |
| Audio | librosa, soundfile, pydub, edge-tts, piper-tts, faster-whisper, openai-whisper, SpeechRecognition, torchaudio |
| Web/Scraping | playwright, selenium, beautifulsoup4, httpx, requests, Crawl4AI, firecrawl-py, browser-use |
| Database | supabase, psycopg, asyncpg, sqlalchemy, chromadb, lancedb, qdrant-client, redis |
| Web Framework | fastapi, flask, django, streamlit, uvicorn, gunicorn |
| Crypto | web3, ccxt, python-binance, bitcoinlib, solana, eth-* |
| ComfyUI | comfyui-embedded-docs, comfyui_workflow_templates (7 sub-packages), comfy-kitchen, comfy-aimdo |
| Video | moviepy, opencv-python, imageio-ffmpeg, av, yt-dlp, pytube |
| Observability | logfire, opentelemetry-* (full suite), loguru, structlog |
| Testing | pytest, pytest-asyncio, pytest-cov, pytest-mock, ruff, mypy, black, flake8, bandit |
| Agents | pydantic-ai, openai-agents, agno, praisonaiagents, mcp, mcp-agent |
| Memory | mem0ai, chromadb, lancedb, sentence-transformers |

### ComfyUI Custom Nodes

- ComfyUI-AnimateDiff-Evolved (video generation)
- ComfyUI-Florence2 (image understanding)
- ComfyUI-Manager (node management)
- ComfyUI-IPAdapter_plus (style transfer)
- + more custom workflows

### Ollama Models

- Running on port 11434
- 14 models installed (gemma4:26b confirmed active)

### LM Studio Models

- jacobcarajo/ — model repo
- janhq/ — model repo
- lmstudio-community/ — model repo
- mradermacher/ — model repo

### Services Running

| Service | Port | Status |
|---|---|---|
| Ollama | 11434 | ✅ Running |
| PostgreSQL | 5432 | ✅ Running |
| n8n | 8080 | ✅ Running |
| Unknown | 1234 | ⚠️ Running |

### Docker

| Item | Status |
|---|---|
| Docker Desktop | ✅ Installed (v29.5.3) |
| Docker Compose | ✅ Installed (v5.1.4) |
| Running containers | ❌ None (daemon may be off) |

### Cloud CLIs & Deploy

| Tool | Status |
|---|---|
| GitHub CLI (gh) | ✅ Installed |
| Vercel | ✅ Installed (v52.0.0) |
| Netlify | ✅ Installed (v23.4.0) |
| AWS CLI | ❌ Not found |
| gcloud | ❌ Not found |
| Azure CLI | ❌ Not found |
| Terraform | ❌ Not found |
| kubectl | ❌ Not found |
| Helm | ❌ Not found |

### Config & API Key Files

| File | Status |
|---|---|
| .env | ✅ Present |
| .env.example | ✅ Present |
| .env.openrouter.backup | ✅ Present |
| API_KEY_REGISTRY.json | ✅ Present |
| .openrouter/ | ✅ Present (3 items) |
| .aws/ | ✅ Present (1 item) |
| .kube/ | ✅ Present (1 item) |

### Script Files at Root

| Type | Count | Notable |
|---|---|---|
| .py | 30+ | OMNI_*.py, AETHER_*.py, BUILD_*.py, STABILIZE*.py |
| .bat | 5+ | START-ALL-AI-TOOLS.bat, run_fastapi.bat, run_http.bat |
| .ps1 | 20+ | Audit scripts, backup scripts, scanner scripts |
| .sh | 1 | _harness_recipe_check.sh |
| .md | 239 | Planning graveyard |
| .json | 15+ | Config files, reports |
| .html | 5+ | Dashboards |

### 122 Dotdirectories (by category)

**AI/LLM Tool Caches (50+):**
.ollama, .lmstudio, .qwen, .gemini, .claude, .codex, .cline, .cursor, .kilo, .kilocode, .kiro, .trae, .monica-code, .crush, .hermes, .openclaw, .verdent, .vibe, .pochi, .serena, .antigravity, .antigravity-ide, .antigravity_cockpit, .aitk (427 items!), .cagent, .codeartsdoer, .codebuddy, .codemaker, .codestudio, .codetogether, .commandcode, .continue, .convex, .factory, .flow-nexus, .forge, .genspark-tool-cli, .gk, .husky, .icube-remote-ssh, .kilo, .kilocode, .kiro, .kode, .lingma, .mem0, .openclaw, .openhands, .openjfx, .pi, .pinokio, .pm2, .pnpm-store, .pochi, .preferences, .profiles, .pyenv, .pytest_cache, .qoder, .qodo, .qwen, .redhat, .reposort, .rustup, .search_index, .serena, .ssh, .streamlit, .templateengine, .trae, .trae-aicc, .ultimate_ai_system, .unified-ai, .universal-transfer-hub, .venv, .vercel, .verdent, .vibe, .vibe-log, .voice_orchestrator, .void-editor, .vs, .wdm, .zen-mcp, .zencoder

**Dev/Build Tools (20+):**
.cache, .config, .local, .npm, .bun, .pnpm-store, .conda, .pyenv, .rustup, .dotnet, .vs, .vscode, .devcontainer

**Cloud/Infra (10+):**
.aws, .azure, .docker, .kube, .vercel, .pm2, .mutagen

---

## PART 2: X:\GITHUBREPO (Secondary Storage)

### Security Concerns

| Item | Type | Concern |
|---|---|---|
| encryption.key | File | Exposed encryption key |
| .env* files | Files | API keys potentially exposed |
| api_keys.json | File | API keys file |
| CLAUDE_ACCESS_PERMANENTLY_BLOCKED.lock | File | Stale lock file |
| CLAUDE_EMERGENCY_ACTIVE.txt | File | Emergency state file |
| CLAUDE_PROTECTION_ACTIVE.lock | File | Stale lock file |
| COST_PROTECTION_ACTIVE.lock | File | Stale lock file |
| EMERGENCY_BACKUP/ | Dir | Emergency backup |
| EMERGENCY_PROTECTION_MAXIMUM.lock | File | Stale lock file |
| EMERGENCY_RESPONSE_ACTIVATED.txt | File | Emergency state file |
| OPENROUTER_ONLY_MODE.lock | File | Stale lock file |

### AI Agents & Orchestrators (10+)

| Directory | Purpose |
|---|---|
| foot_clan/ | Foot Clan agent system |
| footclan-ultimate-os/ | Foot Clan OS variant |
| FOOTCLAN_OS/ | Another Foot Clan variant |
| aiarmy/ | AI Army system |
| aiarmy_backup_20260217/ | Backup of AI Army |
| aether-flow-orchestrator/ | Aether flow orchestrator |
| multi_agent_core/ | Multi-agent core system |
| modular_agents/ | Modular agents |
| openrouter_multi_agent/ | OpenRouter multi-agent |

### Crypto/Trading (30+)

| Directory | Purpose |
|---|---|
| crypto-ai-hivemind/ | Crypto AI hivemind |
| crypto-ai-nexus-dashboard/ | Crypto dashboard |
| crypto-automa-pilot/ | Crypto automation |
| crypto-beacon-fusion-hub/ | Crypto beacon |
| crypto-beacon-trader-hub/ | Crypto trader |
| crypto-dream-trade-sim/ | Trade simulator |
| crypto-forge-master/ | Crypto forge |
| crypto-fusion-nexus-flow/ | Crypto fusion |
| crypto-lovable-trader/ | Crypto trader |
| crypto-nexus-automator/ | Crypto automator |
| crypto-nexus-compass/ | Crypto compass |
| crypto-nexus-fusion/ | Crypto fusion |
| crypto-vision-suite/ | Crypto vision |
| crypto-woods-alpha/ | Woods alpha crypto |
| crypto-woods-ulitmate-26/ | Woods ultimate crypto |
| cryptoai-trade-commander/ | AI trade commander |
| cryptoai-trade-forge/ | AI trade forge |
| cryptoai-tradeflow-nexus/ | AI trade flow |
| cryptonaut-ai-terminal/ | Crypto terminal |
| solana-trading-bot-v2/ | Solana trading bot |
| freecrypto/ | Free crypto |
| coin-alchemy-ai/ | Coin alchemy |
| awesome-coins/ | Awesome coins |
| fusion-trading-vision/ | Fusion trading |
| trading-insight-sphere/ | Trading insight |
| trading-strategy-nexus/ | Trading strategy |
| trading_platform/ | Trading platform |
| ultimate-trading-platform/ | Ultimate trading |
| bot-bloom-capital/ | Bot bloom capital |
| phantom-profit-platform/ | Phantom profit |
| spare-change-futures/ | Spare change futures |
| quant-alpha-nexus/ | Quant alpha |
| marvel-ai-trading-hub/ | Marvel AI trading |
| digital-trading-flow/ | Digital trading |
| crypto-dream-voyage-sim/ | Dream voyage sim |

### Dashboards (15+)

| Directory | Purpose |
|---|---|
| AI-Dashboard-Suite/ | AI dashboard suite |
| ALL_DASHBOARDS_COMPLETE/ | All dashboards |
| DASHBOARDS_COMPLETE/ | Dashboards complete |
| DEV-DASHBOARD/ | Dev dashboard |
| GEMDASH/ | Gemini dashboard |
| GEMDASH2/ | Gemini dashboard v2 |
| SOLODASH/ | Solo dashboard |
| SOLOQA/ | Solo QA |
| SOLOQA2/ | Solo QA v2 |
| TMPDASH/ | Temp dashboard |
| archon-dashboards/ | Archon dashboards |
| dashboards_and_links/ | Dashboard links |
| favorite-flow-dashboard/ | Flow dashboard |
| project-dashboard/ | Project dashboard |
| project-heartbeat-dashboard/ | Heartbeat dashboard |
| project-pal-dashboard-hub/ | Pal dashboard |
| dashboard-deploy/ | Dashboard deploy |
| dashboard_deployment/ | Dashboard deployment |

### Code Agents / Claude Clone Army (15+)

| Directory | Purpose |
|---|---|
| CLAUCODER/ | ClauCoder |
| CLAUDASH/ | Claude Dashboard |
| CLAUDEOPEN/ | Claude Open |
| ClaraVerse/ | ClaraVerse |
| Claudable/ | Claudable |
| SuperClaude/ | SuperClaude |
| claude-code-complete-backup/ | Claude Code backup |
| claude-code-otel/ | Claude Code OTEL |
| claude-code-router/ | Claude Code Router |
| claude-code-subagents/ | Claude Code Subagents |
| claude-conductor/ | Claude Conductor |
| claude-ecosystem/ | Claude Ecosystem |
| claude-flow*/ | Claude Flow (multiple) |
| claude-task-master/ | Claude Task Master |
| claudia/ | Claudia |
| awesome-claude-agents/ | Awesome Claude Agents |
| awesome-claude-code/ | Awesome Claude Code |
| awesome-claude-code-agents/ | Awesome Claude Code Agents |

### Web Clones / Apps (20+)

| Directory | Purpose |
|---|---|
| bolt.diy/ | Bolt.diy (open-source) |
| bolt2/ | Bolt v2 |
| boltcrypto/ | Bolt crypto |
| boltnew/ | Bolt new |
| perplexity-clone/ | Perplexity clone |
| lovable-custom-gpt/ | Lovable custom GPT |
| lovable-evolved-fusion-core/ | Lovable fusion |
| lovable-idea-nexus/ | Lovable idea |
| love-bolt-clone-magic/ | Love bolt clone |
| lovely-web-clone/ | Lovely web clone |
| loving-bolt-vortex-clone/ | Loving bolt clone |
| mimic-youware-clone/ | YouWare clone |
| open-lovable/ | Open Lovable |
| open-webui/ | Open WebUI |
| remote-desktop-webui/ | Remote desktop WebUI |
| rest-express-replit/ | Express Replit |
| pancake-frontend/ | Pancake frontend |
| tell-me-that-clone/ | Tell Me That clone |
| ui-source-gatherer/ | UI source gatherer |
| web-analyst-mirror/ | Web analyst |
| web-quadrant-viewer/ | Web quadrant viewer |
| enhanced_file_sharing_app/ | File sharing app |
| file_sharing_app/ | File sharing app |
| v0-untitled-project/ | V0 untitled project |

### AI Tools / Platforms (20+)

| Directory | Purpose |
|---|---|
| AI-TOOLS-INTEGRATION/ | AI tools integration |
| AI_TOOLS_INTEGRATION/ | AI tools integration (dup) |
| AI_TOOLS_WIKI/ | AI tools wiki |
| AI_COLLABORATION_PLATFORM/ | AI collaboration |
| ai_portal/ | AI portal |
| ai-workspace-open-source/ | AI workspace |
| ai/ | AI root |
| ai_assistants/ | AI assistants |
| ai_hub_env/ | AI hub env |
| aiworkspace/ | AI workspace |
| aigenius-toolkit/ | AI genius toolkit |
| aiittoolsbolt/ | AI tools bolt |
| aiusemaxbolt/ | AI use max bolt |
| local-ai-alchemy-lab/ | Local AI lab |
| smart-ai-buddy/ | Smart AI buddy |
| unified-ai-ecosystem/ | Unified AI ecosystem |
| zeroone-autonomy-forge/ | ZeroOne autonomy |
| zeroone-private-nexus/ | ZeroOne private |
| zeroone-toolkit/ | ZeroOne toolkit |
| zeroonebolt/ | ZeroOne bolt |
| extreme_ai/ | Extreme AI |

### Security / Pentesting (6)

| Directory | Purpose |
|---|---|
| cybersecurity-platform/ | Cybersecurity platform |
| ethical-pentesting-platform/ | Ethical pentesting |
| security-forensics-toolkit/ | Security forensics |
| bug-bounty-toolkit/ | Bug bounty toolkit |
| hackrf-ultimate-platform/ | HackRF platform |
| hackrfv0/ | HackRF v0 |

### Media / Creative (8)

| Directory | Purpose |
|---|---|
| musicmanager/ | Music manager |
| artspark-gallery-verse/ | Art gallery |
| artspark-nft-haven/ | NFT haven |
| comment-roulette-youtube/ | YouTube comment roulette |
| youtube-intelligence-suite/ | YouTube intelligence |
| youtube_intelligence/ | YouTube intelligence |
| Youtube-playlist-to-formatted-text/ | YT playlist converter |
| creativeforge-nexus-studio/ | Creative forge |

### Revenue / Business (12)

| Directory | Purpose |
|---|---|
| ENTERPRISE_SALES/ | Enterprise sales |
| REVENUE_ACTIVATION/ | Revenue activation |
| revenue_systems/ | Revenue systems |
| saas_launch/ | SaaS launch |
| MARKETING_LAUNCH/ | Marketing launch |
| marketing/ | Marketing |
| consulting_services/ | Consulting services |
| business_sale/ | Business sale |
| GUMROAD_PRODUCTS/ | Gumroad products |
| creator_brand/ | Creator brand |
| InstantCoder/ | InstantCoder |
| TaskFlow_AI_Manager/ | TaskFlow AI |

### Dev Tools / MCP (10)

| Directory | Purpose |
|---|---|
| mcp/ | MCP root |
| mcp-servers/ | MCP servers |
| mcp_servers/ | MCP servers (dup) |
| mcp-crawl4ai-rag/ | Crawl4AI RAG MCP |
| context7/ | Context7 |
| context7-mcp/ | Context7 MCP |
| metamcp/ | Meta MCP |
| awesome-mcp-servers/ | Awesome MCP servers |

### SQLite Databases (39 orphaned)

agent_registry.db, ai_collaboration_platform.db, ai_ecosystem_memory.db, ai_hub.db, apex_enterprise.db, audit_agent_registry.db, conversations.db, crypto_analysis.db, crypto_test_results.db, deep_security_audit.db, documentation_generation.db, enterprise_hub.db, enterprise_revenue.db, enhanced_security_monitoring.db, github_repo_manager.db, hackrf_platform.db, hackrf_ultimate_complete.db, hackrf_ultimate_sessions.db, integration_coordination.db, integration_system.db, market_domination_analytics.db, marketplace.db, master_audit.db, models.db, monitoring_data.db, openrouter.db, openrouter_analysis.db, openrouter_revenue.db, performance_optimization.db, project_management.db, quality_assurance.db, research_data.db, revenue_customers.db, revenue_marketplace.db, security_analysis.db, security_platform.db, search_index.db, ultimate_crypto_platform.db, ultimate_revenue_system.db, unified_crypto_platform.db

### Backup Duplicates (4x OpenRouter backups within 3 minutes)

- OPENROUTER_COMPLETE_BACKUP_20250811_170045/
- OPENROUTER_COMPLETE_BACKUP_20250811_170207/
- OPENROUTER_COMPLETE_BACKUP_20250811_170242/
- OPENROUTER_COMPLETE_BACKUP_20250811_170310/

### Android / Mobile (4)

- UltimateAndroidToolkit_Portable/
- UltimateAndroidToolkit_v3.0_Professional/
- woods-android-recovery-kit/
- woodsandroidv2/

---

## PART 3: Combined Summary

### Total Counts

| Category | C:\Users\karma | X:\GITHUBREPO | Total |
|---|---|---|---|
| Git repos | 8 | 100+ | 108+ |
| Python packages | 600+ | — | 600+ |
| NPM global packages | 50+ | — | 50+ |
| Dotdirectories | 122 | — | 122 |
| SQLite databases | 0 | 39 | 39 |
| Markdown files | 239 | 50+ | 289+ |
| Script files | 56+ | 100+ | 156+ |
| Config files | 15+ | 50+ | 65+ |
| Lock/state files | 0 | 8+ | 8+ |
| Security risks | 0 | 3+ | 3+ |

### What's Actually Useful

| Drive | Keep | Delete/Archive | % Useful |
|---|---|---|---|
| C:\Users\karma | ~15 repos, 14 Ollama models, 7 tools | 5 dead repos, 239 orphan .md | ~30% |
| X:\GITHUBREPO | ~10-15 projects | 200+ directories, 39 databases | ~5% |

### Key Finding

**~90% of X:\GITHUBREPO is dead weight** — duplicate projects, orphaned databases, stale logs, and lock files from previous AI agent sessions. The ~10-15 actually useful projects are buried under 200+ directories of abandoned work.
