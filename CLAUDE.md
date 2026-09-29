# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Alpha Development Guidelines

**Local-only deployment** - each user runs their own instance.

### Core Principles

- **No backwards compatibility** - remove deprecated code immediately
- **Detailed errors over graceful failures** - we want to identify and fix issues fast
- **Break things to improve them** - alpha is for rapid iteration
- **Test-driven invariant discovery** - every multi-file refresh commit lands a pytest invariance test alongside it (cont.17-fup-4 precedent: the OpenRouter lockstep test caught a real routing bug in `OPENROUTER_NAMESPACE_PREFIXES` on its first run, before any user saw it). Invariant tests create a chain of "if it ever drifts, you'll know immediately" + act as machine-verified spec of the cross-file invariants.
- **Cascade-conscious .gitignore** - never blanket-DENY a top-level directory (e.g., `/ComfyUI/`) and expect per-file re-include to recover its descendants; gitignore skips excluded dirs wholesale for performance, so the only safe pattern is deny-sublists followed by per-file/per-subdir re-include (`!` negation, "last matching pattern wins") with leading `/` anchoring for predictability. The cont.17-fup-6 + cont.17-fup-7 sweeps (92 → 0 working-tree noise on `ComfyUI/`, 7 → 0 on `ComfyUI/config/`) demonstrate the canonical pattern; whenever you deviate, leave a 2-3 line inline comment explaining the cascade reasoning so future operators don't accidentally break the chain.

### Error Handling

**Core Principle**: In alpha, we need to intelligently decide when to fail hard and fast to quickly address issues, and when to allow processes to complete in critical services despite failures. Read below carefully and make intelligent decisions on a case-by-case basis.

#### When to Fail Fast and Loud (Let it Crash!)

These errors should stop execution and bubble up immediately:

- **Service startup failures** - If credentials, database, or any service can't initialize, the system should crash with a clear error
- **Missing configuration** - Missing environment variables or invalid settings should stop the system
- **Database connection failures** - Don't hide connection issues, expose them
- **Authentication/authorization failures** - Security errors must be visible and halt the operation
- **Data corruption or validation errors** - Never silently accept bad data, Pydantic should raise
- **Critical dependencies unavailable** - If a required service is down, fail immediately
- **Invalid data that would corrupt state** - Never store zero embeddings, null foreign keys, or malformed JSON

#### When to Complete but Log Detailed Errors

These operations should continue but track and report failures clearly:

- **Batch processing** - When crawling websites or processing documents, complete what you can and report detailed failures for each item
- **Background tasks** - Embedding generation, async jobs should finish the queue but log failures
- **WebSocket events** - Don't crash on a single event failure, log it and continue serving other clients
- **Optional features** - If projects/tasks are disabled, log and skip rather than crash
- **External API calls** - Retry with exponential backoff, then fail with a clear message about what service failed and why

#### Critical Nuance: Never Accept Corrupted Data

When a process should continue despite failures, it must **skip the failed item entirely** rather than storing corrupted data:

**❌ WRONG - Silent Corruption:**

```python
try:
    embedding = create_embedding(text)
except Exception as e:
    embedding = [0.0] * 1536  # NEVER DO THIS - corrupts database
    store_document(doc, embedding)
```

**✅ CORRECT - Skip Failed Items:**

```python
try:
    embedding = create_embedding(text)
    store_document(doc, embedding)  # Only store on success
except Exception as e:
    failed_items.append({'doc': doc, 'error': str(e)})
    logger.error(f"Skipping document {doc.id}: {e}")
    # Continue with next document, don't store anything
```

**✅ CORRECT - Batch Processing with Failure Tracking:**

```python
def process_batch(items):
    results = {'succeeded': [], 'failed': []}

    for item in items:
        try:
            result = process_item(item)
            results['succeeded'].append(result)
        except Exception as e:
            results['failed'].append({
                'item': item,
                'error': str(e),
                'traceback': traceback.format_exc()
            })
            logger.error(f"Failed to process {item.id}: {e}")

    # Always return both successes and failures
    return results
```

#### Error Message Guidelines

- Include context about what was being attempted when the error occurred
- Preserve full stack traces with `exc_info=True` in Python logging
- Use specific exception types, not generic Exception catching
- Include relevant IDs, URLs, or data that helps debug the issue
- Never return None/null to indicate failure - raise an exception with details
- For batch operations, always report both success count and detailed failure list

### Code Quality

- Remove dead code immediately rather than maintaining it - no backward compatibility or legacy functions
- Prioritize functionality over production-ready patterns
- Focus on user experience and feature completeness
- When updating code, don't reference what is changing (avoid keywords like LEGACY, CHANGED, REMOVED), instead focus on comments that document just the functionality of the code

## Architecture Overview

Archon V2 Alpha is a microservices-based knowledge management system with MCP (Model Context Protocol) integration:

- **Frontend (port 3737)**: React + TypeScript + Vite + TailwindCSS
- **Main Server (port 8181)**: FastAPI + Socket.IO for real-time updates
- **MCP Server (port 8051)**: Lightweight HTTP-based MCP protocol server
- **Agents Service (port 8052)**: PydanticAI agents for AI/ML operations
- **Database**: Supabase (PostgreSQL + pgvector for embeddings)

## Development Commands

### Frontend (archon-ui-main/)

```bash
npm run dev              # Start development server on port 3737
npm run build            # Build for production
npm run lint             # Run ESLint
npm run test             # Run Vitest tests
npm run test:coverage    # Run tests with coverage report
```

### Backend (python/)

```bash
# Using uv package manager
uv sync                  # Install/update dependencies
uv run pytest            # Run tests
uv run python -m src.server.main  # Run server locally

# With Docker
docker-compose up --build -d       # Start all services
docker-compose logs -f             # View logs
docker-compose restart              # Restart services
```

### Testing

```bash
# Frontend tests (from archon-ui-main/)
npm run test:coverage:stream       # Run with streaming output
npm run test:ui                    # Run with Vitest UI

# Backend tests (from python/)
uv run pytest tests/test_api_essentials.py -v
uv run pytest tests/test_service_integration.py -v
```

## Key API Endpoints

### Knowledge Base

- `POST /api/knowledge/crawl` - Crawl a website
- `POST /api/knowledge/upload` - Upload documents (PDF, DOCX, MD)
- `GET /api/knowledge/items` - List knowledge items
- `POST /api/knowledge/search` - RAG search

### MCP Integration

- `GET /api/mcp/health` - MCP server status
- `POST /api/mcp/tools/{tool_name}` - Execute MCP tool
- `GET /api/mcp/tools` - List available tools

### Projects & Tasks (when enabled)

- `GET /api/projects` - List projects
- `POST /api/projects` - Create project
- `GET /api/projects/{id}/tasks` - Get project tasks
- `POST /api/projects/{id}/tasks` - Create task

## Socket.IO Events

Real-time updates via Socket.IO on port 8181:

- `crawl_progress` - Website crawling progress
- `project_creation_progress` - Project setup progress
- `task_update` - Task status changes
- `knowledge_update` - Knowledge base changes

## Environment Variables

Required in `.env`:

```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your-service-key-here
```

Required for AI operations:

```bash
OPENROUTER_API_KEY=your-openrouter-key  # ONLY AI provider - routes all models
```

Optional:

```bash
LOGFIRE_TOKEN=your-logfire-token      # For observability
LOG_LEVEL=INFO                         # DEBUG, INFO, WARNING, ERROR
```

**⚠️ IMPORTANT: Use ONLY OpenRouter for all AI requests. Do not set direct provider keys like OPENAI_API_KEY, ANTHROPIC_API_KEY, etc.**

## File Organization

### Frontend Structure

- `src/components/` - Reusable UI components
- `src/pages/` - Main application pages
- `src/services/` - API communication and business logic
- `src/hooks/` - Custom React hooks
- `src/contexts/` - React context providers

### Backend Structure

- `src/server/` - Main FastAPI application
- `src/server/api_routes/` - API route handlers
- `src/server/services/` - Business logic services
- `src/mcp/` - MCP server implementation
- `src/agents/` - PydanticAI agent implementations

## Database Schema

Key tables in Supabase:

- `sources` - Crawled websites and uploaded documents
- `documents` - Processed document chunks with embeddings
- `projects` - Project management (optional feature)
- `tasks` - Task tracking linked to projects
- `code_examples` - Extracted code snippets

## Common Development Tasks

### Add a new API endpoint

1. Create route handler in `python/src/server/api_routes/`
2. Add service logic in `python/src/server/services/`
3. Include router in `python/src/server/main.py`
4. Update frontend service in `archon-ui-main/src/services/`

### Add a new UI component

1. Create component in `archon-ui-main/src/components/`
2. Add to page in `archon-ui-main/src/pages/`
3. Include any new API calls in services
4. Add tests in `archon-ui-main/test/`

### Debug MCP connection issues

1. Check MCP health: `curl http://localhost:8051/health`
2. View MCP logs: `docker-compose logs archon-mcp`
3. Test tool execution via UI MCP page
4. Verify Supabase connection and credentials

## Code Quality Standards

We enforce code quality through automated linting and type checking:

- **Python 3.12** with 120 character line length
- **Ruff** for linting - checks for errors, warnings, unused imports, and code style
- **Mypy** for type checking - ensures type safety across the codebase
- **Auto-formatting** on save in IDEs to maintain consistent style
- Run `uv run ruff check` and `uv run mypy src/` locally before committing

## MCP Tools Available

When connected to Cursor/Windsurf:

- `archon:perform_rag_query` - Search knowledge base
- `archon:search_code_examples` - Find code snippets
- `archon:manage_project` - Project operations
- `archon:manage_task` - Task management
- `archon:get_available_sources` - List knowledge sources

## Important Notes

- Projects feature is optional - toggle in Settings UI
- All services communicate via HTTP, not gRPC
- Socket.IO handles all real-time updates
- Frontend uses Vite proxy for API calls in development
- Python backend uses `uv` for dependency management
- Docker Compose handles service orchestration

ADDITIONAL CONTEXT FOR SPECIFICALLY HOW TO USE ARCHON ITSELF:
@CLAUDE-ARCHON.md

## Phone Recovery / Mobile Tools (NEW 2026-07-12)

Single-page dashboard **`UNIFIED_MASTER_DASHBOARD.html`** (project root) brings together:
- **Empire** — 12 AI-empire links + live search filter
- **Recovery Suite** — all 18 `RECOVERY_SUITE.bat` options as cards, category filter (All / Android / iPhone / Oppo / Utilities / Diagnostics)
- **Diagnostics** — ADB status + 4 diagnostic buttons that display formatted ADB commands for the user's PC (carrier lock / SIM state / APN / full)
- **Carrier Unlock** — complete Australian guide: Telstra (TEL), Optus (OPP/OPS), Vodafone (VAU/VA) + 6 MVNOs (Boost, TPG/iiNet/Internode, Felix, Woolworths, ALDI, Belong) + Samsung-specific tips

Two new tools live in **`COMPLETED_PROJECTS/mobile_backup/`**:
- **`phone_diagnostics.py`** — auto SIM/network diagnosis via ADB. 10 checks with per-failure exit codes. Run on the user's PC (no ADB on this server).
- **`iphone_pro_drfone_alt.py`** — modern Dr. Fone alternative at `http://localhost:8455`, run with `python -X utf8`.

Documentation: `C:\Users\karma\Downloads\PHONE_FIXING_SKILLS.md` (master, 21 KB) + `PHONE_HELP.md` (synced copy).

Master menu: `COMPLETED_PROJECTS\mobile_backup\RECOVERY_SUITE.bat` (19 options: L D 1–9 P G W T M I U X).

Pre-edit guard for the dashboard: `COMPLETED_PROJECTS\mobile_backup\verify_dashboard.py` — runs `node --check` on the extracted inline JS before any future edits.

---

## Dashboard Architecture (NEW 2026-07-12)

Two self-contained HTML dashboards at project root share a glassmorphic dark-theme design pattern, modal system, and accessibility standards. Full reference: **`DASHBOARD_ARCHITECTURE.md`** at project root.

| Dashboard | Tabs | Card count |
|---|---|---|
| `UNIFIED_MASTER_DASHBOARD.html` (~1013 lines) | Empire / Recovery Suite / Diagnostics / Carrier Unlock | 12 + 18 + 4 + 6 MVNOs |
| `AI_TOOLS_DASHBOARD.html` v2.2 polished (~700 lines) | Coding Assistants / Local Models / Quick Links / Active Projects | 14 + 6 + 6 + 3 |

**Shared pattern:** CSS variables (`--primary`, `--secondary`, `--surface`, etc.), radial-gradient backgrounds, glassmorphic cards, `.tabs > .tab` switching, modal system.

**Modal safety:** use DOM-based `showCardDetail(card)` (creates elements + sets `textContent`) for user-derived content. The legacy `openModal(title, content)` uses `innerHTML` and is XSS-prone — it's kept only for callers passing hardcoded literal HTML (e.g., the Recovery Suite modal descriptions built from a fixed string map).

**Verification:** `python COMPLETED_PROJECTS\mobile_backup\verify_dashboard.py [path]` validates any dashboard. Exit 0 = OK, 1 = missing file/arg, 2 = JS syntax error. Run before every dashboard edit. Pre-commit hook at `.git/hooks/pre-commit` (chmod 0o755) runs it automatically on every commit.

**Accessibility standards in both:**
- Decorative `<i class="fas fa-...">` icons all have `aria-hidden="true"`
- Modal: `role="dialog" aria-modal="true" aria-labelledby="modalTitle"` + close button `aria-label="Close dialog"`
- Tab focus trap inside modal, focus restoration on close, Escape closes, background-click closes

**Validate dashboards from the project root:**
```bash
node --check <(python -c "import re; s=open('UNIFIED_MASTER_DASHBOARD.html').read(); m=re.search(r'<script>([\s\S]*?)</script>', s); print(m.group(1))")
node --check <(python -c "import re; s=open('AI_TOOLS_DASHBOARD.html').read(); m=re.search(r'<script>([\s\S]*?)</script>', s); print(m.group(1))")
```
Or use the dedicated guard: `python COMPLETED_PROJECTS\mobile_backup\verify_dashboard.py`.

---

## Local ComfyUI Music Video Studio

The local ComfyUI media studio is installed under:

```text
C:\Users\karma\ComfyUI
```

### Launcher

```text
C:\Users\karma\ComfyUI\launch_music_video_studio.bat
```

21-option menu covering: ComfyUI launch (3 modes), audio (transcribe, BPM analysis, batch), video (analyze, batch), creative (brainstorm, wizard), tools (config, models, check, remote, update), local AI assistant (chat, converse, browse, review, more).

### music_video_studio.py subcommands

| Command | Purpose |
|---|---|
| `transcribe` | Whisper MP3→lyrics TXT+SRT |
| `batch-transcribe` | All audio in input/audios |
| `analyze-audio` | BPM, beats, onset, spectral (librosa) |
| `analyze-video` | Frame extraction + BLIP captioning |
| `batch-analyze` | All videos in input/reference_videos |
| `brainstorm` | Full concept via OpenRouter (uses BPM if mp3 given) |
| `wizard` | Interactive guided workflow |
| `config --show` / `--set key=val` | Persisted defaults |
| `check` | GPU, CUDA, nodes, VRAM budget estimator |
| `list-free-models` | OpenRouter free model IDs |

### local_ai_assistant.py subcommands

| Command | Purpose |
|---|---|
| `chat` | Single question to Ollama |
| `converse` | Multi-turn with `/save` history |
| `browse` | Headless Chromium + page analysis |
| `summarize` | File summarization |
| `explain-error` | Error explanation with optional file context |
| `plan` | Implementation plan generation |
| `review` | Python code review (CRITICAL/MAJOR/MINOR) |
| `check` | List installed Ollama models |

### Workflow templates

```text
C:\Users\karma\ComfyUI\workflow_templates\workflow_recipes.md
```

7 proven ComfyUI workflows for RTX 4060 8GB with VRAM budgets.

### Docs

- Music Video Studio: `docs/music_video_studio.md`
- Local AI Assistant: `docs/local_ai_assistant.md`
- Workflow Recipes: `workflow_templates/workflow_recipes.md`

### Key files

| File | Purpose |
|---|---|
| `config/music_video_studio_config.json` | Persisted defaults |
| `config/openrouter_free_models.txt` | Free model IDs |
| `tools/configure_remote_stay_connected.bat` | Power/sleep tweaks |
| `tools/update_comfyui_tools.bat` | Git pull all custom nodes |
| `tools/check_gpu_stack.bat` | Quick GPU verification |
| `launch_comfyui_menu.bat` | Alternate ComfyUI-only launcher |

OpenRouter is the approved AI provider for brainstorming, lyric/concept planning, and reference-video prompt extraction. Use free OpenRouter models.
Local Ollama is available for coding/debugging/browser assistance.

### Full Reference
- `C:\Users\karma\ComfyUI\README.md` — complete system guide
- `C:\Users\karma\ComfyUI\AGENTS.md` — session memory / quick-reference`

## Reference Documentation (NEW 2026-07-09)

Workspace-level engineering docs catalogued at repo root for cross-discovery from any future session. Engineering context only — sales/launch/money/client-mgmt docs deliberately excluded from this index.

| Topic | Doc |
|---|---|
| YouTube + transcript + ComfyUI video ecosystem | `YOUTUBE_GITHUB_DEEP_RESEARCH_2026.md` |
| Laptop → display + peripherals (14 categories, 3-tier recommendation) | `HARDWARE_SHOPPING_LIST_2026.md` |
| GPU-accelerated remote desktop install (Sunshine + Moonlight) | `SUNSHINE_MOONLIGHT_SETUP.md` |
| Curated GitHub `awesome-*` lists for YouTube tooling | `AWESOME_YOUTUBE_REPOS_2026.md` |
| Single-page start-here index for the above | `REFERENCE_DOCS_INDEX.md` |
| One-page daily digest | `DAILY_REFERENCE_DIGEST_2026-07-09.md` |

`HARDWARE_SHOPPING_LIST_2026.md` is the recommended first read for any session that touches the laptop→display/peripheral stack. `SUNSHINE_MOONLIGHT_SETUP.md` documents a 6-step install for cable-free remote-desktop; the file is intentionally advisory (not auto-installed). For deeper YouTube tooling context start with `YOUTUBE_GITHUB_DEEP_RESEARCH_2026.md` then go to `AWESOME_YOUTUBE_REPOS_2026.md` for the catalog-of-catalogs view.

## Documentation Contract (MANDATORY)

When the user asks to **document**, **save**, **archive**, or **record** anything, the task is **not complete** until real files exist on disk. A chat reply alone does not count.

**Load skill:** `.grok/skills/document-this/SKILL.md` — follow its 10-step checklist every time.

| Trigger | Required action |
|---|---|
| "document this" / "make sure it's documented" | Write `.md` files + verify on disk |
| "save a copy" / "save to x:" | Write to `X:\SESSION_ARCHIVES\` **and** mirror `_DOCS_ARCHIVE\` |
| "open/show me" | `notepad` + `explorer` on saved files |
| Session or chat scope | `SESSION_DOCUMENTATION_YYYY-MM-DD.md` + `SESSION_FULL_HISTORY_YYYY-MM-DD.md` |
| Raw transcript available | Copy `updates.jsonl` to `X:\SESSION_ARCHIVES\` |

**Save locations (always both):**
- `X:\SESSION_ARCHIVES\` — user backup drive
- `C:\Users\karma\_DOCS_ARCHIVE\` — workspace mirror

**Index updates (append-only):**
- `ALL_PLANS_AND_PROJECTS_MASTER.md` → Session Work Completed table
- `X:\SESSION_ARCHIVES\README.md` → new session row

**Helper:** `DOCUMENT_SESSION.bat` (opens archive folder) · `python .grok/skills/document-this/scripts/save_session_docs.py`

**Fail loud** if X: is unavailable — write to `_DOCS_ARCHIVE\` and report the error. Never claim documentation is done without verified file paths.

