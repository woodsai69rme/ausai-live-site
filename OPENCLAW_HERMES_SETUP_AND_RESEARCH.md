# OpenClaw & Hermes Setup and Research

## Overview

This document describes the **OpenClaw + Hermes** agent pairing that provides
the orchestration and chat-agent backbone for the local-AI fleet at
`C:\Users\karma\`. Together they handle high-level intent routing, multi-turn
conversation, and self-improving agent loops using free OpenRouter models
with local Ollama fallback.

| Component | Role | Status |
|---|---|---|
| **OpenClaw** | Gateway / orchestrator (port 18789) | **Active** — installed, config at `.openclaw/openclaw.json` |
| **Hermes** | Self-improving chat agent (Nous Research) | **Active** — installed, config at `.hermes/config/hermes.config.json` |

The launcher (`START-ALL-AI-TOOLS.bat`) exposes them as menu options **2**
(OpenClaw) and **6** (Hermes). Three additional agent personas — Oracle,
Jarvis, and Paperclip — are documented in `ORACLE_JARVIS_PAPERCLIP_SETUP.md`
and exposed as launcher options **8, 9, 10**.

## Configuration Details

### OpenClaw Gateway

- **Config:** `C:\Users\karma\.openclaw\openclaw.json`
- **Workspace state:** `C:\Users\karma\.openclaw\workspace\` (includes
  `AGENTS.md`, `BOOTSTRAP.md`, `HEARTBEAT.md`, `IDENTITY.md`, `SOUL.md`,
  `TOOLS.md`, `USER.md`)
- **Session data:** `C:\Users\karma\.openclaw\agents\main\sessions\`
- **Internal state:** `C:\Users\karma\.openclaw\state.sqlite`

OpenClaw acts as the **entry gateway** for multi-agent routing. Its `/steer`
command allows mid-session redirection to different personas (Hermes for
conversation, Oracle for retrieval, Jarvis for code, Paperclip for admin).

When the gateway is health-checked, any downstream agent can stream terminal
output through it (port 18789), enabling a unified logging and routing layer
without direct inter-agent IPC.

### Hermes Agent

- **Config:** `C:\Users\karma\.hermes\config\hermes.config.json`
- **Identity:** `C:\Users\karma\.hermes\SOUL.md` (Nous Research persona —
  intelligent, helpful, direct; admits uncertainty; efficient investigations)
- **Entry point:** `C:\Users\karma\hermes-agent\run_agent.py`
- **Setup helper:** `C:\Users\karma\.hermes\ollama-setup.ps1`

Hermes is the **default chat persona**. It uses a three-tier model fallback:

1. **Tier 1 (Cloud via OpenRouter free):** `qwen/qwen-2.5-7b-instruct:free`
2. **Tier 2 (Cloud fallback):** OpenRouter's internal provider fallback
3. **Tier 3 (Local floor):** Ollama `qwen2.5-coder:7b` on `127.0.0.1:11434`

The local Ollama model is already provisioned — `START-ALL-AI-TOOLS.bat`
option 4 launches `ollama run qwen2.5-coder:latest` for direct chat.

## Master Launcher Integration

`START-ALL-AI-TOOLS.bat` (the unified fleet launcher at
`C:\Users\karma\`) exposes:

- **Option 2:** `openclaw agent --agent test` — launches the gateway
- **Option 6:** `uv run python run_agent.py` from `hermes-agent\` — launches
  Hermes with `uv` and the local `.local\bin` on `PATH`
- **Options 8/9/10:** Oracle, Jarvis, Paperclip — documented in
  `ORACLE_JARVIS_PAPERCLIP_SETUP.md`

## Deep Research & Routing Architecture

### Recommended delegation flow

```
User intent → OpenClaw (port 18789)
                │
                ├─ Chat / reasoning → Hermes
                ├─ Retrieval / data  → Oracle
                ├─ Code / system     → Jarvis
                └─ Admin / file-ops  → Paperclip
```

Each persona has its own model + tool allow-list (see the respective docs).
OpenClaw's `/steer` command performs the switch mid-session without dropping
context.

### Three-tier fallback (shared pattern)

Every persona in the fleet uses the same three-tier resilience model that
Hermes pioneered:

1. OpenRouter free tier (persona-specific model)
2. OpenRouter internal provider fallback
3. Local Ollama on `127.0.0.1:11434` (persona-specific model)

If all three tiers fail, the launcher prints the specific failure so the
operator can decide: swap roles, retry, or escalate to manual mode.

## Recommended Next Steps

1. **Wire OpenClaw routing layer** — connect `/steer` to the three new
   personas once they're cloned (see `ORACLE_JARVIS_PAPERCLIP_SETUP.md`
   TODO blocks for repo URLs).
2. **Unify the audit log aggregation** — OpenClaw's `workspace/` already
   tracks session state; add per-persona `.jsonl` audit logs (Oracle,
   Jarvis, Paperclip each have their own per the Oracle/Jarvis/Paperclip doc)
   and build a Mission Control roll-up that reads all four streams.
3. **Health-check dashboard** — add a `/health` endpoint to the God-Mode
   Dashboard (port 3142, launcher option 13) that polls OpenClaw, Hermes,
   and the three new personas and shows live status.
4. **Document persona-switching logic** — once routing is wired through the
   OpenClaw gateway, update this doc with concrete `/steer` examples for
   each persona handoff.
