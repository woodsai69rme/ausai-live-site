# AI Influencer Studio

A unified CLI + web dashboard for AI influencer content creation and social media management.

## Features

- **Content generation**: posts, captions, video scripts, image prompts
- **Asset pipeline**: TTS, image generation, video assembly (via existing ComfyUI/tools)
- **Music video lab**: research generators, plan songs with character locks, run clip-first pipelines
- **Repurposing**: auto-cut vertical Shorts/Reels/TikToks with safe zones and captions (`aisocial repurpose`)
- **Scheduling**: SQLite-backed queue with cron-like scheduling + n8n/Postiz/Mixpost hooks (`POST /api/scheduler/{scheduler}/push`)
- **Offline voiceover**: optional Kokoro ONNX backend via `pip install -e ".[kokoro]"`
- **Publishing**: platform adapters for YouTube, TikTok, Instagram, X/Twitter, Facebook
- **Web dashboard**: FastAPI + Jinja2 for visual management

## Quick start

```bash
# Install
pip install -e ".[dev]"

# Configure
aisocial config

# Check dependencies without installing or changing anything
aisocial doctor

# Check local operational state without network calls
aisocial health

# Generate a post
aisocial create --type post --topic "AI automation" --platform twitter

# Schedule it
aisocial schedule --content "AI is changing everything..." --platform twitter --when "2026-07-17T09:00:00"

# Start web dashboard
aisocial web

# Start the background scheduler (publishes due posts)
aisocial daemon
```

## Live model registry and routing

The studio can discover local Ollama models and the current OpenRouter model catalogue, then emit a secret-free LiteLLM proxy configuration with local-first aliases and hosted free fallbacks.

```bash
# Refresh live provider metadata and generate routing files
# Defaults: Ollama http://localhost:11434 and OpenRouter https://openrouter.ai/api/v1
aisocial model-registry refresh

# Daily-safe refresh: skip a fresh catalog and retain last-known-good data on outages
aisocial model-registry refresh --daily

# Inspect freshness and verification without network calls
aisocial model-registry status

# Opt-in probe of selected local models; catalog availability remains unchanged
aisocial model-registry probe --model-ref ollama::qwen2.5:latest

# Inspect the saved registry without making network calls
aisocial model-registry list

# Export an offline Markdown report from the saved snapshot
aisocial model-registry export-docs

# Run the generated LiteLLM proxy (install LiteLLM separately)
litellm --config ~/.ai_influencer_studio/litellm.generated.yaml --port 4000
```

The refresh writes:

- `~/.ai_influencer_studio/model_registry.json` — verified catalog snapshot with pricing, modalities, context, tools, published license, catalog availability, field provenance, freshness, and provider errors.
- `~/.ai_influencer_studio/litellm.generated.yaml` — generated routing config; credentials remain environment variables.
- `~/.ai_influencer_studio/model_registry_report.md` — offline Markdown report generated from the snapshot.

Local Ollama models are preferred for privacy and latency. OpenRouter models are used only when discovered and advertised as zero-priced. OpenRouter's `/models` response is treated as authoritative for published metadata; missing license fields remain `unknown`, and its `listed`/`unlisted` state is catalog availability—not a live inference-health probe. A provider outage is recorded as an error while last-known-good records remain available and disappeared models are retained as `unlisted` for auditability. For Windows Task Scheduler, review and run `scripts\\install_model_catalog_task.bat` once as the intended user; it registers the daily 03:00 task and invokes `scripts\\refresh_model_catalog_daily.bat`. The installer is never run automatically.

Set `LITELLM_MASTER_KEY` before exposing LiteLLM beyond localhost. Keep `OPENROUTER_API_KEY` in the environment, never in the generated YAML. OpenRouter is the sole approved hosted AI provider for new AI requests; the `openai_api_key` configuration field exists only for legacy adapter compatibility and must not be introduced into new routing.

## Authentication

The web dashboard is local-only by default. To protect it, set an API key:

```bash
# Environment variable
export AISTUDIO_API_KEY="your-secret-key"

# Or add to config.json
aisocial config
```

When `AISTUDIO_API_KEY` is set, every request must include the header:

```
X-API-Key: your-secret-key
```

## Scheduler daemon

The scheduler polls the SQLite database for due posts and publishes them through the configured platform adapters.

```bash
# Run in the foreground
aisocial daemon

# Stop
Ctrl+C
```

### Run as a systemd service (Linux)

A templated unit file is provided in `scripts/aisocial@.service`. It assumes `aisocial` is installed at `~/.local/bin/aisocial` (e.g., via `pip install --user`). Adjust `ExecStart` if you installed it elsewhere. Enable it for your user:

```bash
sudo cp scripts/aisocial@.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable aisocial@$USER.service
sudo systemctl start aisocial@$USER.service
```

Create `/etc/default/aisocial` and set any environment variables the scheduler needs:

```bash
AISTUDIO_API_KEY=your-secret-key
```

### Run as a Windows service

A helper batch script is provided in `scripts/install_windows_service.bat`. It requires [NSSM](https://nssm.cc/) to be on your PATH. Run it as Administrator:

```bat
scripts\install_windows_service.bat
```

If you need to set `AISTUDIO_API_KEY` afterwards, use:

```bat
nssm set AIInfluencerStudioScheduler AppEnvironmentExtra "AISTUDIO_API_KEY=your-secret-key"
```

The scheduler supports automatic retries with exponential backoff:

| Failure | Retry delay |
|--------|-------------|
| 1st    | 2 minutes   |
| 2nd    | 4 minutes   |
| 3rd    | 8 minutes   |

After 3 retries, the post is marked `failed`.

## Documentation map

- [`SYSTEM_OPERATIONS_GUIDE.md`](SYSTEM_OPERATIONS_GUIDE.md) — complete architecture, operations, safety, troubleshooting, and enhancement roadmap.
- [`OPENROUTER_MODEL_CATALOG.md`](OPENROUTER_MODEL_CATALOG.md) — verified catalog semantics and daily refresh details.
- [`MUSIC_VIDEO_RESEARCHER.md`](MUSIC_VIDEO_RESEARCHER.md) — music-video research, planning, web API, and limitations.
- `aisocial model-registry export-docs` — regenerate an offline model snapshot report without network access.
- `aisocial doctor` — inspect required/optional Python dependencies without changing the environment.
- `aisocial health` — inspect local databases, catalog freshness, and recorded model health.
- `aisocial music-video style-bible-template --output assets/style-bible.json` — create a reusable character/style template without overwriting an existing file.

## Architecture

```text
src/ai_influencer_studio/
├── cli.py                    # CLI entry point and command safety gates
├── config.py                 # JSON + environment configuration
├── database.py               # SQLite scheduled-post/generated-content state
├── model_registry.py         # Ollama/OpenRouter discovery and LiteLLM output
├── file_indexer.py           # Local multimodal scan/review/apply workflow
├── music_video_researcher.py # Generator research, trends, and plans
├── youtube_client.py         # YouTube API / best-effort trend client
├── repurposer.py             # FFmpeg vertical video cuts
├── adapters/                 # Content, video, automation, and platform bridges
├── core/                     # Background publishing scheduler
├── safe_use/                 # Browser/Windows policy, MCP, approval, audit
├── web/                      # FastAPI routes and dashboard
└── templates/                # Jinja2 HTML templates
```

## Status

The project includes the content dashboard, scheduling queue, music-video planning tools, repurposing tools, the provider-neutral live model registry, and an isolated safe browser/computer-use layer.

## Safe browser and Windows computer use

The safe-use layer is separate from the existing social/browser adapters and defaults to observation or proposal. Mutating actions require an explicit one-shot approval and pass policy checks first.

Install optional dependencies:

```bash
pip install -e ".[browser]"      # Playwright browser adapter
playwright install chromium
pip install -e ".[windows]"      # Windows UI Automation adapter
```

Generate the policy-aware Playwright MCP bridge configuration:

```bash
aisocial safe-use mcp-config --output ~/.ai_influencer_studio/playwright-mcp.json --domain example.com
```

Observe an allowlisted website without an action:

```bash
aisocial safe-use observe --target browser --url https://example.com --domain example.com
```

Validate an action without executing it:

```bash
aisocial safe-use propose --target browser --domain example.com \
  --intent '{"target":"browser","action":"click","parameters":{"selector":"button","url":"https://example.com"}}'
```

Execute one action only with explicit approval:

```bash
aisocial safe-use execute --approve --target browser --domain example.com \
  --intent '{"target":"browser","action":"click","parameters":{"selector":"button","url":"https://example.com"}}'
```

Windows actions require a specific allowlisted app name. Every event is appended to `safe-use-audit.jsonl` with credential-like values redacted. The generated MCP config points to a custom policy-enforcing FastMCP wrapper around Playwright—not Microsoft’s unrestricted `@playwright/mcp` server—so browser tools cannot bypass the local allowlist and approval flow.

## Local multimodal file indexer

The indexer handles documents, images, videos, and music entirely on the local machine. Scanning is always dry-run: it hashes files, extracts lightweight metadata, proposes category destinations, and writes a persistent SQLite review queue. It never moves or deletes files during scanning.

```bash
# Scan; no files are moved
aisocial indexer scan --source ./incoming --target ./organized

# Review queue
aisocial indexer queue --status PENDING

# Approve records without applying them
aisocial indexer approve --ids 1 2
# or: aisocial indexer approve --all

# Apply only approved records, with explicit confirmation
aisocial indexer apply --confirm
```

Destinations are grouped under `documents/`, `images/`, `videos/`, and `music/`. Optional local analysis hooks can enrich metadata (OCR, transcription, perceptual hashes, or custom classifiers) without changing the dry-run/apply safety contract; hook failures are recorded in metadata rather than aborting the scan. Hooks are trusted in-process Python callables, not sandboxed plugins, so load only code you control. Each apply operation copies to a temporary file, verifies SHA-256, atomically places the destination, and then removes the source. Duplicate hashes are marked `DUPLICATE`; collisions receive `_v2`, `_v3`, and later suffixes. Indexing metadata and operations are stored in the configured data directory, with secrets excluded from audit records.
