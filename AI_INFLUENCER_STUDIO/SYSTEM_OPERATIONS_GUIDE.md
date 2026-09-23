# AI Influencer Studio — System Operations Guide

**Updated:** 2026-08-07  
**Scope:** CLI, web dashboard, content adapters, scheduler, model routing, music-video lab, safe computer use, file indexer, testing, and operations.

## 1. Purpose and operating model

AI Influencer Studio is a local-first Python application for creating, organizing, repurposing, scheduling, and publishing AI-assisted social content. It intentionally separates:

- **Generation** — content, video, music-video planning, and repurposing adapters.
- **State** — SQLite databases and JSON plans/catalogs under the configured data directory.
- **Automation** — scheduled publishing and external n8n/Postiz/Mixpost hooks.
- **Research** — YouTube trend retrieval, generator cataloging, and reusable-asset analysis.
- **Safety** — isolated browser/Windows UI automation with observe → propose → approve → execute gates.
- **Local organization** — a dry-run multimodal file indexer with a human review queue.

Default storage is `~/.ai_influencer_studio`. The project is local-only by default; external services are opt-in and require operator credentials.

## 2. Quick-start workflow

```bash
cd AI_INFLUENCER_STUDIO
python -m pip install -e ".[dev]"
aisocial config

# Start the dashboard
aisocial web

# Generate and schedule content
aisocial create --type post --topic "AI automation" --platform twitter
aisocial schedule --platform twitter --content "Draft" --when "2026-08-08T09:00:00"
aisocial daemon
```

Use `aisocial --help` and each subcommand’s `--help` as the authoritative CLI reference.

## 3. Architecture map

```text
src/ai_influencer_studio/
├── cli.py                     CLI and safety gates
├── config.py                  JSON + environment configuration
├── database.py                Scheduled posts and generated-content state
├── model_registry.py          Ollama/OpenRouter discovery and LiteLLM output
├── file_indexer.py            Local multimodal scan/review/apply workflow
├── music_video_researcher.py  Generator research, trends, assets, plans
├── youtube_client.py          YouTube API / best-effort trend client
├── repurposer.py              FFmpeg vertical video cuts
├── adapters/
│   ├── content.py             Existing content pipeline bridge
│   ├── video.py               Existing factory/ComfyUI bridge
│   ├── automation.py          Social scheduling/publishing bridge
│   └── platforms/             Platform-specific adapters
├── core/scheduler.py           Retry-aware publishing daemon
├── safe_use/
│   ├── engine.py              Observe/propose/approve/execute orchestration
│   ├── policy.py              Domain/app/action allowlists
│   ├── browser.py              Playwright adapter
│   ├── windows_ui.py           Windows UI Automation adapter
│   ├── mcp_server.py            Policy-enforcing MCP wrapper
│   └── audit.py                Redacted JSONL audit log
├── web/                        FastAPI dashboard and API routes
└── templates/                  Jinja2 pages
```

## 4. Configuration and secrets

`StudioConfig` loads JSON from `~/.ai_influencer_studio/config.json`, then applies environment overrides for provider keys. Do not commit config files or secrets.

Important variables:

| Variable | Purpose |
|---|---|
| `OPENROUTER_API_KEY` | OpenRouter model catalog and hosted inference |
| `YOUTUBE_API_KEY` | Optional YouTube Data API trend retrieval |
| `AISTUDIO_API_KEY` | Optional local web-dashboard authentication |
| `LITELLM_MASTER_KEY` | Required before exposing LiteLLM beyond localhost |
| `OPENAI_API_KEY` | Legacy configuration field only; OpenRouter is the sole approved hosted AI provider for new requests |

Security rules:

- Generated LiteLLM YAML contains environment references, never raw keys.
- Catalog snapshots contain sanitized provider errors.
- Audit logs redact credential-like values.
- Keep dashboard and LiteLLM bound to localhost unless authentication and network controls are deliberately configured.

## 5. Live model registry and routing

The registry discovers local Ollama models and OpenRouter’s published `/api/v1/models` catalog. It stores pricing, modalities, context, tools, license, catalog availability, provenance, provider status, freshness, and errors.

```bash
aisocial model-registry refresh
iaisocial model-registry refresh --daily
iaisocial model-registry refresh --daily --force
aisocial model-registry status
aisocial model-registry list
aisocial model-registry export-docs
```

Outputs:

- `model_registry.json` — normalized snapshot.
- `litellm.generated.yaml` — local-first aliases and hosted-free fallbacks.
- `model_registry_report.md` — offline Markdown report generated from a snapshot.
- `aisocial doctor` — dependency diagnostics with no installation side effects.
- `aisocial health` — local operational health report with no provider calls.
- `source_urls` — provider-specific catalog endpoints used for the snapshot.

Routing safety:

- Local Ollama models are preferred.
- Hosted OpenRouter records enter aliases only when advertised as zero-priced.
- `stale`, `expired`, `unavailable`, `unknown`, and `unlisted` records never enter aliases.
- A catalog listing is not a live inference-health guarantee.
- Provider outages retain last-known-good records for auditability but mark the snapshot degraded.

### Opt-in model health probes

Catalog listing and runtime health are separate. Use a targeted probe only when you explicitly want a minimal local or hosted request:

```bash
aisocial model-registry probe --model-ref ollama::qwen2.5:latest
# Hosted probes require explicit opt-in:
aisocial model-registry probe --include-hosted --model-ref openrouter::provider/model
```

Probe results are stored as `health_status`, `health_checked_at`, `health_latency_ms`, and `health_error`. They never overwrite `availability_status` or routing aliases.

Local Ollama probes use `POST /api/show` (metadata read) rather than `/api/generate`. This keeps the probe fast and works for every model type, including embedding models that reject generation; it does not load model weights into memory. Localhost Ollama requests bypass any system-wide HTTP proxy so a misconfigured or slow local proxy cannot time out the health check.

## 6. Safe browser and Windows computer use

The safe-use layer is intentionally separate from existing social adapters:

1. **Observe** — inspect an allowlisted page or app without mutation.
2. **Propose** — validate an exact intent against policy.
3. **Approve** — issue a short-lived, intent-bound approval token.
4. **Execute** — run one approved action and consume the token.

Example:

```bash
aisocial safe-use observe --target browser --url https://example.com --domain example.com
aisocial safe-use propose --target browser --domain example.com \
  --intent '{"target":"browser","action":"click","parameters":{"selector":"button","url":"https://example.com"}}'
aisocial safe-use execute --approve --target browser --domain example.com \
  --intent '{"target":"browser","action":"click","parameters":{"selector":"button","url":"https://example.com"}}'
```

The policy requires explicit HTTP(S) domain allowlists, exact Windows app allowlists, action allowlists, current-page checks, and sensitive-field opt-in. The MCP configuration points to the local policy-enforcing wrapper, not an unrestricted external automation server.

## 7. Local multimodal file indexer

The indexer supports documents, images, videos, and music. Optional analysis hooks can add local OCR, transcription, perceptual-hash, or classifier metadata. Hooks are trusted in-process Python callables, not sandboxed plugins; load only code you control. Hook failures are recorded and do not move files or change approval semantics. Scanning is always non-destructive:

```bash
aisocial indexer scan --source ./incoming --target ./organized
aisocial indexer queue --status PENDING
aisocial indexer approve --ids 1 2
aisocial indexer apply --ids 1 2 --confirm
```

The workflow hashes files, extracts optional metadata, proposes category destinations, detects duplicates, persists a SQLite queue, writes audit events, copies to a temporary destination, verifies SHA-256, atomically places the file, and only then removes the source. Source and target roots are checked against the indexed roots before apply.

## 8. Music-video research and production

### Character/style bible

Create a starter bible without overwriting an existing file:

```bash
aisocial music-video style-bible-template --output assets/style-bible.json
```

Fill in character reference, appearance, wardrobe, continuity rules, palette, lighting, camera language, locations, and negative rules. Attach it to planning:

```bash
aisocial music-video plan \
  --style-bible assets/style-bible.json \
  --song '{"name":"Track","audio":"track.mp3"}'
```

The bible is optional and persisted inside each plan for reproducibility. It does not execute generation by itself.

The music-video lab supports:

- free/freemium generator research by VRAM budget;
- YouTube trend retrieval through API or best-effort fallback;
- local audio and reusable asset scans;
- character and style reference reuse;
- eight-scene song plans;
- full, clip-only, and assembly-only execution modes;
- ComfyUI orchestration and repurposing into platform clips.

```bash
aisocial music-video research --generators --vram 8
aisocial music-video research --trends --max-results 10
aisocial music-video plan --song '{"name":"Track","audio":"track.mp3","genre":"pop","mood":"upbeat"}'
aisocial music-video master-plan --song '{"name":"Track","audio":"track.mp3"}' --output plans/master.json
aisocial music-video execute --plan plans/master.json --song-index 0 --generation-mode clip_only
```

Review `MUSIC_VIDEO_RESEARCHER.md` for the HTTP API, data model, generator catalog, and known limitations.

## 9. Scheduling and publishing

`StudioDatabase` stores scheduled posts. `PublishScheduler` polls due records, dispatches through `AutomationAdapter`, retries failures up to three times with exponential delays, and marks exhausted records failed.

Supported operational paths:

- foreground daemon: `aisocial daemon`;
- Linux systemd template: `scripts/aisocial@.service`;
- Windows NSSM helper: `scripts/install_windows_service.bat`;
- external scheduler push hooks: n8n, Postiz, and Mixpost.

Review credentials, working directories, and service-user permissions before installing a service. Installation helpers are not run automatically.

## 10. Validation and release checks

Recommended focused checks:

```bash
python -m ruff check src tests
python -m py_compile src/ai_influencer_studio/model_registry.py src/ai_influencer_studio/music_video_researcher.py src/ai_influencer_studio/file_indexer.py src/ai_influencer_studio/cli.py src/ai_influencer_studio/web/app.py
PYTHONPATH="$PWD/src" python -m pytest tests/test_model_registry.py tests/test_model_registry_catalog.py tests/test_model_registry_cli.py tests/test_music_video_researcher.py tests/test_file_indexer.py tests/test_e2e_smoke.py tests/test_safe_use.py tests/test_scheduler.py --confcutdir=/tmp -q
python -m build --wheel
```

The full test suite may require a compatible FastAPI/Pydantic installation. If the shared `conftest.py` fails before collection, fix the environment rather than treating that import failure as an application test failure.

## 11. Troubleshooting

| Symptom | Check |
|---|---|
| Empty model catalog | Verify network, API URL, response shape, and `OPENROUTER_API_KEY`; inspect `errors` in the snapshot. |
| Models marked stale | Provider refresh failed; restore connectivity and run `--daily --force`. |
| Safe-use action denied | Confirm domain/app allowlist, current observed page, action name, and approval token. |
| Indexer refuses apply | Re-scan or pass matching source/target roots; inspect queue status and audit log. |
| Video execution fails | Confirm audio path, ComfyUI availability, FFmpeg, and orchestrator script path. |
| Scheduler does not publish | Check SQLite status, due time timezone, adapter credentials, and retry/error fields. |
| Web auth unexpectedly active | Clear `AISTUDIO_API_KEY` or send the configured `X-API-Key` header. |

## 12. Remaining enhancement backlog

The following remain intentionally separate from this pass:

1. Add provider retry/backoff with bounded delays around catalog requests.
2. Add schema-version migration diagnostics for old snapshots.
3. Add structured scheduler metrics and a dashboard health view.
4. Add built-in opt-in OCR/transcription/perceptual-hash hook packages.
5. Replace public trend scraping with authenticated YouTube Data API by default when configured.
6. Add CSV and machine-readable model-selection report exports.

Completed in this pass: opt-in model probes, local health output, dependency diagnostics, end-to-end smoke coverage, additive indexer hooks, and character/style-bible templates. The focused validation command above is the reference check for these additions.
