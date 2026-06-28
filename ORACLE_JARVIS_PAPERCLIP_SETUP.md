# Oracle, Jarvis & Paperclip Setup

## Overview

This document is the companion to `OPENCLAW_HERMES_SETUP_AND_RESEARCH.md`. The
OpenClaw/Hermes pair already covers the orchestration + chat-agent persona
(free OpenRouter models with Ollama fallback). This file describes the
**three additional agent personas** that round out the local-AI fleet at
`C:\Users\karma\`:

| Agent | Role | Status |
|---|---|---|
| **Oracle** | RAG / Data / Long-context retrieval | **TODO** -- repo URL not yet pasted |
| **Jarvis** | System commands / Coding / Automation | **TODO** -- repo URL not yet pasted |
| **Paperclip** | Admin / File ops / Glue work | **TODO** -- repo URL not yet pasted |

All three are intended to run as sibling processes alongside Hermes and
OpenClaw. The launcher (`START-ALL-AI-TOOLS.bat`) already exposes them as
menu options **8, 9, 10**; pressing them now prints a `TODO` summary until the
matching repo is cloned.

## Configuration Details

### 1. Oracle Agent (RAG / Data persona)

- **Files (planned):**
  - `C:\Users\karma\oracle-agent\` *(cloned from repo URL -- see TODO below)*
  - `C:\Users\karma\.oracle\oracle.config.json`

- **TODO (paste here when ready):**
  - `git clone <TODO: oracle repo URL> C:\Users\karma\oracle-agent`
  - `cd C:\Users\karma\oracle-agent && uv sync`

- **Model mapping (filled):**
  - Cloud (OpenRouter free): `qwen/qwen3-next-80b-a3b-instruct:free`
  - Local fallback (Ollama): `qwen2.5-coder:7b` (already on disk per
    `START-ALL-AI-TOOLS.bat` option 4)

- **Role-specific config sketch:**
  - Long-context window: dynamic; start with `8k`, scale up only when the
    running persona actually needs it (free-tier providers cap at ~32k
    context and bill by token above that).
  - Vector-store adapter: Supabase (port 8181) or local `chromadb`
  - Tool allow-list: `rag_query`, `code_search`, `retrieve_doc`

  **Config (`oracle.config.json`) — already filled:**
  ```json
  {
    "cloud_model_id": "qwen/qwen3-next-80b-a3b-instruct:free",
    "local_model_id": "qwen2.5-coder:7b",
    "context_window": 8192,
    "vector_store": "chromadb",
    "tool_allowlist": ["rag_query", "code_search", "retrieve_doc"],
    "audit_log": ".oracle/logs/oracle.actions.jsonl"
  }
  ```

### 2. Jarvis Agent (System / Coding persona)

- **Files (planned):**
  - `C:\Users\karma\jarvis-agent\` *(cloned from repo URL -- see TODO below)*
  - `C:\Users\karma\.jarvis\jarvis.config.json`

- **TODO (paste here when ready):**
  - `git clone <TODO: jarvis repo URL> C:\Users\karma\jarvis-agent`
  - `cd C:\Users\karma\jarvis-agent && uv sync`

- **Model mapping (filled):**
  - Cloud (OpenRouter free): `qwen/qwen3-next-80b-a3b-instruct:free`
  - Local fallback (Ollama): `qwen2.5-coder:7b`

- **Role-specific config sketch:**
  - File-system sandbox: only operate inside `C:\Users\karma\<workspaces>`
  - Terminal proxy: stream via OpenClaw gateway (port 18789 if running)
  - Tool allow-list: `bash`, `read_file`, `write_file`, `git`

  **Config (`jarvis.config.json`) — already filled:**
  ```json
  {
    "cloud_model_id": "qwen/qwen3-next-80b-a3b-instruct:free",
    "local_model_id": "qwen2.5-coder:7b",
    "file_sandbox": "C:/Users/karma/workspaces",
    "terminal_proxy": "http://127.0.0.1:18789",
    "tool_allowlist": ["bash", "read_file", "write_file", "git"],
    "audit_log": ".jarvis/logs/jarvis.actions.jsonl"
  }
  ```

### 3. Paperclip Agent (Admin / File-ops persona)

- **Files (planned):**
  - `C:\Users\karma\paperclip-agent\` *(cloned from repo URL -- see TODO below)*
  - `C:\Users\karma\.paperclip\paperclip.config.json`

- **TODO (paste here when ready):**
  - `git clone <TODO: paperclip repo URL> C:\Users\karma\paperclip-agent`
  - `cd C:\Users\karma\paperclip-agent && uv sync`

- **Model mapping (filled):**
  - Cloud (OpenRouter free): `meta-llama/llama-3.3-70b-instruct:free`
  - Local fallback (Ollama): `phi3:latest` (already on disk per option 5)

- **Role-specific config sketch:**
  - Concurrency 1 (no parallel writes to the same dir)
  - Audit log: append every action to
    `C:\Users\karma\.paperclip\logs\paperclip.actions.jsonl`
  - Tool allow-list: `move_file`, `copy_file`, `delete_file`, `archive`

  **Config (`paperclip.config.json`) — already filled:**
  ```json
  {
    "cloud_model_id": "meta-llama/llama-3.3-70b-instruct:free",
    "local_model_id": "phi3:latest",
    "concurrency": 1,
    "tool_allowlist": ["move_file", "copy_file", "delete_file", "archive"],
    "audit_log": ".paperclip/logs/paperclip.actions.jsonl"
  }
  ```

## Master Launcher Integration

`START-ALL-AI-TOOLS.bat` now exposes the trio as options **8, 9, 10** (the
utility entries List-models / List-skills / Open-docs have beenshifted to **14, 15, 16**). Each entry uses the same `IF EXIST` launcher pattern as
Hermes: if the local clone exists the bat `cd`s in and `uv run`s the agent;
if not, it prints the clone command + links to this file so the operator
knows exactly which slot to fill in.
The prompt was widened from `Enter choice (0-9)` to `Enter choice (0-16)` to
accommodate the shifted utility entries.

Note: `OPENCLAW_HERMES_SETUP_AND_RESEARCH.md` (line 25) used to reference a
non-existent `START_EVERYTHING_HERMES_OPENROUTER.bat`. That reference was
corrected to point at the real `START-ALL-AI-TOOLS.bat`.

**Entry-point flexibility:** the launcher currently defaults to
`uv run python main.py` for all three personas (Hermes-style). When
you paste the specific repo URLs, if any of them ships a non-standard
entry-point (`python -m <pkg>`, `python src/server.py`, etc.), update
the matching `:oracle` / `:jarvis` / `:paperclip` block in
`START-ALL-AI-TOOLS.bat` to match. The launcher prints the actual
command it's about to run before launching, so misconfigured entry-points
fail fast with a clear stack trace instead of silently hanging.

## Deep Research & Recommended Enhancements

### Routing between the three personas

The recommended pattern is **staged task delegation** via OpenClaw:

1. **OpenClaw** receives the high-level intent.
2. **Hermes** routes to the appropriate persona based on the request:
   - Read-only / data questions -> **Oracle**
   - Code / system ops -> **Jarvis**
   - File movement / admin -> **Paperclip**
3. **Each persona** has its own model + tool allow-list (above).

### Failure-mode tolerance

Each persona MUST have its own three-tier fallback (matching Hermes):

- Tier 1 (Cloud via OpenRouter free): persona-specific model listed above.
- Tier 2 (Cloud fallback): OpenRouter's internal provider fallback.
- Tier 3 (Local floor): Ollama persona-specific model on `127.0.0.1:11434`.

If any persona cannot reach either cloud or local, the bat menu print
includes the specific failure so the operator can decide whether to swap
roles or escalate to Hermes.

### Auditability

Each persona has its OWN append-only audit log so the streams stay
isolated and easy to grep per-role:

- Oracle:        `C:\Users\karma\.oracle\logs\oracle.actions.jsonl`
- Jarvis:        `C:\Users\karma\.jarvis\logs\jarvis.actions.jsonl`
- Paperclip:     `C:\Users\karma\.paperclip\logs\paperclip.actions.jsonl`

Every tool call MUST log `(ts_iso, persona, tool_name, args_hash, exit_code)`
to the persona's own file. Roll-up dashboards (e.g. a Mission-Control UI)
should aggregate by reading all three files in parallel.

## Recommended Next Steps

1. **Paste the three specific repo URLs** under the TODO blocks above, then
   clone into `oracle-agent/`, `jarvis-agent/`, `paperclip-agent/`.
   The launcher will pick them up on the next `.bat` run automatically.
2. **Smoke-test each persona** by pressing the new menu options (8, 9, 10) in
   `START-ALL-AI-TOOLS.bat` and verifying the clone -> launch flow works
   end-to-end before enabling in production runtime.
3. **Document the persona-switching logic** in
   `OPENCLAW_HERMES_SETUP_AND_RESEARCH.md` once the routing layer is wired
   through the OpenClaw gateway.
4. **Split Oracle/Jarvis models** when more Qwen free variants appear on
   OpenRouter to avoid shared rate limits.

## Verified-free model reference

Source-of-truth list:
`C:\Users\karma\ComfyUI\config\openrouter_free_models.txt` (free-tier
catalog, regenerated by `music_video_studio.py list-free-models`).

| Persona | Model ID (`cloud_model_id`) | Source |
|---|---|---|
| Oracle | `qwen/qwen3-next-80b-a3b-instruct:free` | `ComfyUI/config/openrouter_free_models.txt` |
| Jarvis | `qwen/qwen3-next-80b-a3b-instruct:free` | `ComfyUI/config/openrouter_free_models.txt` |
| Paperclip | `meta-llama/llama-3.3-70b-instruct:free` | `ComfyUI/config/openrouter_free_models.txt` |

> **Note:** Oracle and Jarvis share the same Qwen model (only Qwen free model available). They are differentiated by tool allowlists and persona configs. If more Qwen free variants appear, split them to avoid shared rate limits (20 req/min, 200 req/day free tier).

The swap is written into the **`cloud_model_id` field of each persona's
config JSON** (`oracle.config.json`, `jarvis.config.json`,
`paperclip.config.json`). The schema was sketched under *Configuration
Details* above -- the field name is unchanged across all three so the
swap-in is mechanically identical.

Never paste a 32B / 70B specific ID unless you have explicit confirmation
it is currently free-tier -- the verification list above is the only
authoritative source.
