# 🎙️ VOICE PA SYSTEM — Master Index

> **AI Voice Personal Assistant — local-first voice capture, STT, intent classification, and cross-system dispatch bridge.**
>
> Built: 2025–2026 | Status: **Design complete, runtime ready** | Files: 8

---

## 🏗️ Architecture

```
Voice Input (mic/file)
    │
    ▼
┌─────────────────────────────┐
│  ai_voice_pa.py             │  ← Core runtime
│  • Capture / STT / Intent   │
│  • Append-only audit log    │
│  • Rule #8 fence            │
└──────────┬──────────────────┘
           │ intent=dispatch
           ▼
┌─────────────────────────────┐
│  VOICE_PA_BRIDGE.py         │  ← Cross-system correlation
│  • Reads voice + footclan   │
│     dispatch logs           │
│  • Iso-minute matcher       │
│  • Bridge log output        │
└──────────┬──────────────────┘
           │ matched rows
           ▼
┌─────────────────────────────┐
│  FOOTCLAN_EXECUTOR.py       │  ← Agent dispatch (operator-triggered;
│                             │     Voice PA never auto-executes)
└─────────────────────────────┘

BROWSER MODE (alternative path):
┌─────────────────────────────┐
│  omni_voice_browser_agent   │  ← Voice-controlled browser
│  • Speech recognition       │
│  • browser-use Agent        │
│  • OpenRouter LLM           │
└─────────────────────────────┘
```

---

## 📁 File Inventory

### Core Design Docs

| File | Size | Purpose |
|---|---|---|
| `AI_VOICE_PA_DESIGN.md` | 7.1 KB | Complete design spec — CLI surface, intent enum, refusal matrix, audit log shape, compatibility |
| `AI_VOICE_PA.md` | 5.6 KB | Companion explainer — defaults, closed intent enum, refusal triggers, acceptance tests |
| `VOICE_PA_BRIDGE.md` | 6.1 KB | Bridge design — cross-system correlation, iso-minute matcher, bridge log format |

### Runtimes

| File | Size | Purpose |
|---|---|---|
| `ai_voice_pa.py` | 8.0 KB | Core runtime — `--source mic:N|file:path`, STT stub, intent classification, 4-row audit |
| `VOICE_PA_BRIDGE.py` | 9.8 KB | Bridge runtime — reads voice + footclan logs, iso-minute matching, bridge rows |
| `AI_VOICE_ASSISTANT/omni_voice_browser_agent.py` | 2.4 KB | Voice-controlled browser agent — speech recognition + browser-use Agent |

### Config & Integration

| File | Size | Purpose |
|---|---|---|
| `AI_VOICE_ASSISTANT/config.json` | 202 B | Activation phrase, voice settings, browser/computer control toggles |
| `voice_command_workflow.json` | 998 B | n8n webhook workflow — receives voice commands → AI Army backend |

---

## 🔧 CLI Quick Reference

### Core Runtime (`ai_voice_pa.py`)

```bash
# Dry-run (default) — prints plan, writes nothing
python ai_voice_pa.py --source file:transcript.txt

# Real run — appends 4 audit rows
python ai_voice_pa.py --source file:transcript.txt --run

# Mic capture (max 30s)
python ai_voice_pa.py --source mic:10 --run

# Cloud STT (requires explicit credentials flag)
python ai_voice_pa.py --source mic:15 --stt cloud --i-have-credentials --run
```

### Bridge (`VOICE_PA_BRIDGE.py`)

```bash
# Dry-run
python voice_pa_bridge.py --voice-log AI_VOICE_PA_AUDIT.log --dispatch-log FOOTCLAN_DISPATCH.log

# Real run — writes bridge rows
python voice_pa_bridge.py --voice-log AI_VOICE_PA_AUDIT.log --dispatch-log FOOTCLAN_DISPATCH.log --run
```

### Browser Agent (`omni_voice_browser_agent.py`)

```bash
# Interactive voice-controlled browser (requires Playwright)
python AI_VOICE_ASSISTANT/omni_voice_browser_agent.py
# Say "nexus search for X" or "nexus go to example.com"
```

---

## 🛡️ Security Boundaries

### Rule #8 Fence (NEVER accessed)

| Protected Folder | Guarded By |
|---|---|
| Documents | ai_voice_pa.py, VOICE_PA_BRIDGE.py |
| Downloads | ai_voice_pa.py, VOICE_PA_BRIDGE.py |
| Pictures / Videos / Music | ai_voice_pa.py, VOICE_PA_BRIDGE.py |
| Desktop / OneDrive | ai_voice_pa.py, VOICE_PA_BRIDGE.py |
| Downloads\ARCHIVE_OLD | ai_voice_pa.py, VOICE_PA_BRIDGE.py |

### Refusal Matrix

| Trigger | Exit Code | Runtime |
|---|---|---|
| `--source` in Rule #8 folder | 1 | ai_voice_pa.py |
| `--audit-out` in Rule #8 folder | 1 | ai_voice_pa.py |
| `--stt cloud` without `--i-have-credentials` | 1 | ai_voice_pa.py |
| Intent outside closed enum | 1 | ai_voice_pa.py |
| Mic duration > 30s | 1 | ai_voice_pa.py |
| Bridge log path in Rule #8 folder | 1 | VOICE_PA_BRIDGE.py |
| Input logs not found | 1 | VOICE_PA_BRIDGE.py |

---

## 🎯 Closed Intent Enum (5 values)

| Intent | Action | Audit Row |
|---|---|---|
| `transcribe` | Save text only | `intent=transcribe` |
| `summarize` | Summarize transcript | `intent=summarize` |
| `dispatch` | Log for Footclan handoff | `intent=dispatch` |
| `pause` | Operator timeout / empty text | `intent=pause` |
| `noop` | Unrecognized input | `intent=noop` |

---

## 📋 Audit Log Format

Each `--run` invocation appends **4 rows** sharing one ISO timestamp:

```
<ISO8601> | event=capture | source=file:path | duration_s=0
<ISO8601> | event=stt | backend=local-stub | chars=200 | status=ok
<ISO8601> | event=intent_dispatch | intent=summarize | conf=0.5000
<ISO8601> | event=run_complete | intent=summarize | chars=200 | duration_s=0
```

Two runs = 8 rows, never overlapping.

---

## 🔗 Cross-References

| Related System | File |
|---|---|
| Agent Registry (2,793 agents) | `AGENT_REGISTRY.md` |
| AI Agent Inventory | `AI_AGENT_INVENTORY.md` |
| Footclan Squad Design | `FOOTCLAN_SQUAD_DESIGN.md` |
| Footclan Executor | `FOOTCLAN_EXECUTOR.py` |
| AI Army | `AI_ARMY/` |
| Aether Core System | `AETHER_CORE_SYSTEM/`, `AETHER_SYNC_BRIDGE.py` |

---

## 🧪 Acceptance Tests (from design)

| Test | What It Verifies |
|---|---|
| `test_append_only_growth` | 2 runs → 8 rows, never 4 |
| `test_personal_folder_source_refused` | Music path → exit 1 |
| `test_cloud_stt_refused` | Cloud without creds → exit 1 |
| `test_intent_enum_closed` | Unknown intent → exit 1 |
| `test_dry_run_no_write` | Dry-run → file unchanged |
| `test_four_rows_per_run` | Every run = exactly 4 rows |
| `test_iso_minute_match` | Same-minute pairs → matched |

---

## 📌 What the Voice PA Does NOT Do

- ❌ Auto-listen (requires explicit `--source mic:N`)
- ❌ Upload voice off-host without `--i-have-credentials`
- ❌ Execute Footclan soldiers (dispatch is logged; operator runs separately)
- ❌ Touch Rule #8 personal folders
- ❌ Rewrite or delete any audit log

---

**Last update:** 2026-06-28 — System index created. 8 files catalogued across design, runtime, config, and integration layers.
