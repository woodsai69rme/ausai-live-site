# SLEEP_TRIPLE — Three Aud-Earning Systems That Run While You Sleep

> **Scope:** Three independent systems that earn AUD with **ZERO approvals** — no ABN, no LLC, no platform Partner Programs, no human reviews. All three default to **dry-run**, observe the user's Rule #8 personal-folder fence rigidly, and write to existing append-only audit logs.

---

## Quickstart

```bash
cd C:/Users/karma/SLEEP_TRIPLE

# Dry-run, all three options (default safe mode)
python sleep_orchestrator.py

# Dry-run, single option
python opt_a_digital_factory.py --dry-run
python opt_b_faceless_shorts.py --dry-run
python opt_c_crypto_yield.py --dry-run

# Live operations (REQUIRES opt-in per option)
python opt_a_digital_factory.py --run --publish staged
python opt_b_faceless_shorts.py --run --publish
python opt_c_crypto_yield.py --run

# List today's atomic-state-machine audit log
python sleep_orchestrator.py --list
```

---

## The Three Systems

### Option A — AI Digital Product Factory (`opt_a_digital_factory.py`)

| | |
|---|---|
| **What it does** | Generates AI prompt packs, code snippets, and design assets using your local Ollama model (`qwen2.5-coder`). Stages them as Gumroad drafts. |
| **Monetization** | Gumroad instant shop (no approval). PayPal pays you in AUD. Free tier pays no fees. |
| **Capital** | $0 |
| **Defaults** | `--dry-run` writes into `./outbox/a_digital_factory/` but does NOT upload. |
| **Closed enums** | `EXEC_STATUS = (started, ok, skipped, refused, noop, failed)` · `PRODUCT_KIND = (ai_prompts, code_snippets, design_assets)` · `PUBLISH_MODE = (draft_only, staged, published)` |
| **Ledger event** | `deploy_published` (via `Append-RevenueEvent.ps1`) |

### Option B — Faceless YouTube Shorts + Affiliate Funnel (`opt_b_faceless_shorts.py`)

| | |
|---|---|
| **What it does** | Reads trending topics, drafts a 30-second voice-over script via Ollama, renders via ComfyUI, dry-run uploads via YouTube API, injects instant-approval affiliate links (Binance, Kraken, Hostinger, Persona, Ledger). |
| **Monetization** | Affiliate commissions — no human approval. YouTube monetization requires YPP (separate path) but is not required. |
| **Capital** | $0 |
| **Defaults** | `--dry-run` writes script + description, never uploads. |
| **Closed enums** | `EXEC_STATUS` · `SUB_TASKS = (harvest_topics, write_script, generate_video, upload_short, inject_links)` |
| **Ledger event** | `creative_published` |

### Option C — Crypto Yield Automation (`opt_c_crypto_yield.py`)

| | |
|---|---|
| **What it does** | Snapshots stablecoin spreads across AU/global exchanges, emits `signal_emitted` rows to your existing `REVENUE_LEDGER.jsonl`. |
| **Monetization** | Arbitrage / yield farming **after** you wire in your own exchange API keys. |
| **Capital** | Starts at `$0` — observation-only. Set `opt_c_config.json: max_capital_aud` to enable live trade. |
| **Defaults** | `--dry-run` snapshots AND writes a `signal_emitted` row of `$0` to the ledger (proper pipeline plumbing without risk). |
| **Closed enums** | `EXEC_STATUS` · `SUB_TASKS = (scan_rates, auto_compound, arbitrage)` · `EXCHANGE_ENUM = (coinspot, kraken, independentreserve, binance)` · `SIGNAL_TIER = (none, observed, actionable, executed, refused)` |
| **Ledger event** | `signal_emitted` |

---

## Design Decisions

1. **Sequential execution** — not parallel. Parallel risks GPU OOM (Ollama + ComfyUI concurrent), file-lock collisions on `REVENUE_LEDGER.jsonl`, and complicates idempotency state tracking.
2. **Idempotent by date** — orchestrator checks `SLEEP_TRIPLE_AUDIT.jsonl` for today's `(date, slug, status=ok)`. If found, emits `noop` and skips.
3. **`--dry-run` default everywhere** — mirrors the Footclan/Voice-PA runner pattern. Nothing is live until you explicitly pass `--run` (and per-option flags).
4. **Rule #8 fence rigid** — refuses with exit 2 if any path component matches `Documents, Downloads, Pictures, Videos, Music, Desktop, OneDrive, ARCHIVE_OLD`.
5. **Time-window gate** — orchestrator refuses (exit 3) outside `sleep_window` unless `--force-window`.
6. **Closed enums** — every `status`, `kind`, `task`, `mode` is from a fixed tuple. Off-list values are refused at parse time.
7. **Append-only audit logs** — `SLEEP_TRIPLE_AUDIT.jsonl` (this system) + the existing `REVENUE_LEDGER.jsonl` (reused via `Append-RevenueEvent.ps1`).
8. **No background processes** — orchestrator runs to completion then exits. Use Windows Task Scheduler / a `cron`-style trampoline to invoke at the configured sleep window.

---

## Files

```
C:\Users\karma\SLEEP_TRIPLE\
├── sleep_orchestrator.py              ← Master controller (runs all three)
├── sleep_config.json                  ← Master config (sleep window, ledger path)
├── opt_a_digital_factory.py           ← Option A
├── opt_a_config.json                  ← A's per-option config
├── opt_b_faceless_shorts.py           ← Option B
├── opt_b_config.json                  ← B's per-option config
├── opt_c_crypto_yield.py              ← Option C
├── opt_c_config.json                  ← C's per-option config
├── SLEEP_TRIPLE_AUDIT.jsonl           ← Append-only audit log (created on first run)
├── outbox/                            ← Generated artifacts (NOT published in dry-run)
│   ├── a_digital_factory/
│   └── b_faceless_shorts/
└── README.md                          ← This file
```

---

## What This Does NOT Do (honest scope)

| Thing | Status |
|---|---|
| Run as a service | Out of scope — use Windows Task Scheduler |
| Tax reporting (ABN, GST) | Out of scope — read the ATO hobby-income guidance yourself once you earn $0.5K+ |
| Auto-list on Gumroad via real OAuth | Stubbed. You must create the Gumroad API token + put it in `api_key_vault.json`. |
| Auto-trade on real exchanges | Stubbed. Wire your own exchange API keys + flip `max_capital_aud > 0`. |
| Voice-over TTS | Stubbed. Plug in `kokoro` or `piper` when you want real narration. |

---

## Real Audit Logs Path

`C:\Users\karma\REVENUE_LEDGER.jsonl` — existing append-only ledger, schema `ts,event,amount_aud,note`. Reused unchanged.

`C:\Users\karma\SLEEP_TRIPLE\SLEEP_TRIPLE_AUDIT.jsonl` — new audit log created on first run.

---

## Roll-Foward Plan

1. **Tonight (dry-run):** validate orchestrator + each option emits rows in expected order.
2. **Next:** drop in real Gumroad API token + flip `--publish staged`.
3. **Then:** wire exchange API keys + flip `max_capital_aud` if you want live crypto.
4. **Then:** wire Windows Task Scheduler to fire `--run` nightly.
5. **Then:** install a tiny dashboard that reads `SLEEP_TRIPLE_AUDIT.jsonl` + `REVENUE_LEDGER.jsonl` for a morning briefing.
