# Verified Daily OpenRouter Model Catalog

**Project:** AI Influencer Studio  
**Implemented:** 2026-08-06  
**Status:** Complete and validated

## Purpose

AI Influencer Studio maintains a local, persistent catalog of OpenRouter and Ollama models. The catalog is designed for routing decisions, model selection, auditing, and daily refreshes without placing secrets in generated configuration files.

The OpenRouter `/api/v1/models` response is the authoritative source for published OpenRouter model metadata. The catalog does **not** claim that a listed model is currently healthy or that every provider endpoint is serving traffic.

## Captured OpenRouter fields

For each listed OpenRouter model, the catalog records:

- Model ID and display name
- Context length
- Input and output modalities
- Pricing for prompts and completions
- Cost class (`hosted_free`, `hosted_paid`, or `unknown`)
- Supported parameters and tool support
- Published license, when supplied
- Catalog availability (`listed`, `expired`, `unavailable`, or `unknown`)
- Timestamp for availability observation
- Per-field provenance (`openrouter-models`, `ollama-tags`, `model-name-heuristic`, or `unknown`)
- Additional upstream metadata such as canonical slug, release date, expiration date, top provider, and architecture

Missing or ambiguous license information remains `unknown`; it is never treated as permissive.

## Snapshot verification

Snapshots are JSON files with schema version 2 metadata:

- `checked_at` — refresh timestamp
- `fresh_until` — 24-hour freshness deadline
- `verification_status` — `verified` or `degraded`
- `verified` — boolean convenience flag
- `provider_status` — per-provider `verified`, `stale`, or `failed`
- `source_urls` — upstream catalog URLs
- `refresh_mode` — `manual` or `daily`
- `errors` — sanitized provider errors

A snapshot is fresh only when it has a valid future `fresh_until` and `verification_status == "verified"`.

## Failure and change behavior

### Provider outage

When a provider request fails during a refresh:

1. The failure is recorded with credentials and query strings redacted.
2. The previous provider records are retained when a prior snapshot exists.
3. Retained records are marked `stale` and excluded from routing aliases.
4. The snapshot becomes `degraded` rather than silently pretending to be current.

### Model disappearance

When a refreshed provider no longer lists a previously known model:

1. The previous record is retained as `unlisted` for auditability.
2. It is excluded from routing aliases.
3. It is not deleted from the snapshot history.

Only providers included in the current refresh are eligible for disappearance reconciliation; intentionally skipped providers are left untouched.

### Routing safety

Aliases exclude records marked:

- `unlisted`
- `unavailable`
- `stale`
- `expired`
- `unknown`

Legacy `ModelRecord` construction remains compatible: records created by existing callers default to `listed` unless the caller explicitly supplies another state.

## CLI usage

From `AI_INFLUENCER_STUDIO`:

```bash
# Manual live refresh
aisocial model-registry refresh

# Daily-safe refresh; skips a fresh verified snapshot
aisocial model-registry refresh --daily

# Force the daily refresh immediately
aisocial model-registry refresh --daily --force

# Inspect freshness and verification without network access
aisocial model-registry status

# Print the saved model catalog
aisocial model-registry list

# Export an offline Markdown report
aisocial model-registry export-docs
```

The actual entry point is `aisocial`; the first command above should be entered as:

```bash
aisocial model-registry refresh
```

Optional flags:

- `--snapshot PATH` — choose the JSON snapshot path
- `--litellm-config PATH` — choose the generated LiteLLM YAML path
- `--ollama-url URL` — override the Ollama endpoint
- `--openrouter-url URL` — override the OpenRouter API base
- `--no-ollama` — skip local Ollama discovery
- `--no-openrouter` — skip OpenRouter discovery

Default files:

- `~/.ai_influencer_studio/model_registry.json`
- `~/.ai_influencer_studio/litellm.generated.yaml`

## Daily Windows scheduling

The project includes two reviewed batch files:

```text
scripts/refresh_model_catalog_daily.bat
scripts/install_model_catalog_task.bat
```

Run the installer manually under the intended Windows user account. It registers a daily 03:00 task and is never executed automatically by the application.

The launcher runs:

```text
aisocial model-registry refresh --daily
```

The task requires `aisocial` to be available on `PATH`. Review the batch file before registering it in a production or shared account.

## Credentials and generated routing

- `OPENROUTER_API_KEY` is read from the environment or local config.
- API keys are never written into the model snapshot.
- Generated LiteLLM configuration references environment variables instead of embedding secrets.
- Keep `LITELLM_MASTER_KEY` configured before exposing LiteLLM beyond localhost.

## Source files

- `src/ai_influencer_studio/model_registry.py` — normalized records, refresh, persistence, freshness, fallback, and routing selection
- `src/ai_influencer_studio/cli.py` — refresh, daily, status, probe, list, export-docs, health, and doctor commands
- `tests/test_model_registry.py` — existing registry and LiteLLM regression tests
- `tests/test_model_registry_catalog.py` — verified catalog, stale fallback, freshness, disappearance, and routing safety tests
- `scripts/refresh_model_catalog_daily.bat` — daily launcher
- `scripts/install_model_catalog_task.bat` — explicit Task Scheduler installer
- `README.md` — operator-facing overview

## Validation completed

- Ruff: passed
- Python syntax compilation: passed
- Focused registry/catalog tests: **15 passed**
- Combined registry/catalog, safe-use, indexer, and scheduler regressions: **36 passed**
- Malformed daily snapshot handling: passed
- Wheel build: passed
- Wheel contents: verified for `model_registry.py` and `cli.py`

## Limitations

- OpenRouter `/models` catalog listing is not a live inference-health probe; use the opt-in `model-registry probe` command for selected models.
- Availability is therefore catalog availability, not a guarantee of successful generation.
- A Task Scheduler installer is provided but is intentionally not run automatically.
- No raw session transcript was available for the documentation pass.
