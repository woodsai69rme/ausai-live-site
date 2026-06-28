# SLEEP_TRIPLE — System Reference

> **Audience:** Future-me (Karma) at 3am after a context wipe, or anyone reviewing the codebase cold. This document is the *why* and *how-it-works*; `README.md` is the *how-to-run-it*.

> **Scope:** Four independent systems that earn AUD with **ZERO approvals** — no ABN, no LLC, no platform Partner Programs, no human reviews. All four default to **dry-run**, observe Rule #8 personal-folder fence rigidly, and write to append-only audit logs.

---

## 1. Philosophy & Design Decisions

### 1.1 Money-first, approvals-last
The user's input constraints were explicit: *no human review, no partner programs, no ABN, no LLC*. Every channel below was researched for actual zero-approval on-ramps:
- **Opt A:** Gumroad instant shop (creator account in 60 seconds, no approval).
- **Opt B:** Instant-approval affiliate programs (Binance, Kraken, Hostinger, Persona, Ledger, Crypto.com).
- **Opt C:** Observation-only crypto spread scanner (no exchange API key needed for read-only public endpoints).
- **Opt D:** Free-tier webhook channels (Discord, Telegram, Slack, Pushover) — only env-var paste, no signup needed beyond each platform's standard bot/webhook creation.

### 1.2 Sequential, not parallel
Three (now four) subsystems run **serially**, not concurrently. Reasons:
1. **GPU OOM**: Ollama + ComfyUI concurrent inference on RTX 4060 (8GB VRAM) tip into OOM kill.
2. **File-lock collisions**: `REVENUE_LEDGER.jsonl` and `SLEEP_TRIPLE_AUDIT.jsonl` are append-only; parallel writes risk interleaved bytes.
3. **Idempotency state**: sequential execution = clear ordered audit trail.

### 1.3 Dry-run by default, --run as opt-in
Mirrors the Footclan/Voice-PA runner pattern. `--run` is the only flag that opens the door to live side-effects; every subsystem checks it independently. **Idempotency is gated by `today_iso`**, not by `--run`, so re-running is safe.

### 1.4 Closed status enums
Every status/kind/task/mode is from a fixed tuple:
- `EXEC_STATUS = (started, ok, skipped, refused, noop, failed)`
- `PRODUCT_KIND = (ai_prompts, code_snippets, design_assets)` (Opt A)
- `SUB_TASKS = (harvest_topics, write_script, generate_video, upload_short, inject_links)` (Opt B)
- `(scan_rates, auto_compound, arbitrage)` (Opt C)
- `ALERT_TRIGGER = (actionable_spread, audit_failure, morning_digest)` (Opt D)
- `ALERT_CHANNEL = (discord, telegram, slack, pushover)` (Opt D)
- `ALERT_TIER = (info, warning, critical)` (Opt D)

Off-list values are refused at parse time.

### 1.5 Append-only audit logs
Two audit trails:
- **System-level:** `SLEEP_TRIPLE/SLEEP_TRIPLE_AUDIT.jsonl` (this system's state machine).
- **Revenue-level:** `C:/Users/karma/REVENUE_LEDGER.jsonl` (existing append-only ledger, schema `ts,event,amount_aud,note`, reused via `Append-RevenueEvent.ps1`).

Audit rows never get edited or deleted. Corrections happen by appending new rows.

### 1.6 Rule #8 personal-folder fence
PATH components matching `Documents | Downloads | Pictures | Videos | Music | Desktop | OneDrive | ARCHIVE_OLD` cause immediate refusal (exit 2). Rigid, no opt-out. This is the user's rule, enforced in code.

### 1.7 No background processes
`sleep_orchestrator.py` runs to completion then exits. Recurrence is the OS's job (Windows Task Scheduler for nightly + morning digest).

---

## 2. Architecture

### 2.1 Module Layout

```
C:\Users\karma\SLEEP_TRIPLE\
├── sleep_orchestrator.py         # Master controller (runs all 4 sequentially)
├── sleep_config.json             # Master config: tz, sleep_window, ledger paths, Rule #8 fence
├── compute_next_boundary.py      # DST-safe HH:MM boundary compute for scheduler installers
│
├── opt_a_digital_factory.py      # Option A — AI products → Gumroad
├── opt_a_config.json             # Ollama + ComfyUI preferences
│
├── opt_b_faceless_shorts.py      # Option B — YT Shorts + affiliate funnel
├── opt_b_config.json             # 30s shorts, transcript seed n, affiliate program URLs
│
├── opt_c_crypto_yield.py         # Option C — Stablecoin spread observation
├── opt_c_config.json             # Exchanges (CoinSpot, Kraken, IR), threshold bps
│
├── opt_d_alerts.py               # Option D — Multi-channel webhook alerter (read audit log, fan out)
├── opt_d_config.json             # Channels, rate limit, tier thresholds
│
├── install_scheduler.bat         # Registers BOTH nightly + morning-digest tasks via schtasks
├── uninstall_scheduler.bat       # Removes both (continue-on-error)
├── launch.bat                    # Convenience launcher
├── launch_dashboard.bat          # Starts dashboard_server.py + opens browser
│
├── dashboard_server.py           # Flask-style HTTP server, port 3144
├── dashboard.html                # Live audit + revenue view
│
├── _live_send_test.py            # One-shot webhook round-trip verifier
├── _test_dst.py                  # Synthetic DST scenario tests
├── _verify_schtasks.py           # Verifies schtasks XML parse installs cleanly
│
├── _commit_and_push.py           # Helper: git add/commit/push wrapper
├── _commit_alerts.py             # Helper: opt_d batch commit
├── _commit_alerts2.py            # Helper: opt_d fanout batch commit
├── _push_retry.py                # Helper: retry push preserving creds
├── sleep_task.xml                # schtasks XML for nightly installation
│
├── SLEEP_TRIPLE_AUDIT.jsonl      # Append-only state audit (grows nightly)
├── outbox\                       # Generated artifacts (NOT published in dry-run)
│   ├── a_digital_factory\
│   └── b_faceless_shorts\
└── README.md / DOCUMENTATION.md
```

### 2.2 Module Pipeline

```
install_scheduler.bat (cron)
        │
        ▼ (daily 23:00 user-local)
sleep_orchestrator.py --run --force-window
        │
        ▼
┌─────────────────────────┐
│ Rule #8 fence check     │──fail──> exit 2
├─────────────────────────┤
│ Sleep window gate       │──fail──> exit 3
├─────────────────────────┤
│ Sequential loop:        │
│   ┌─ opt_a ─┐           │
│   ├─ opt_b ─┤           │
│   ├─ opt_c ─┤           │
│   └─ opt_d ─┘           │
├─────────────────────────┤
│ Audit row per module    │
│ Idempotency check       │
└─────────────────────────┘
```

Independent of the orchestrator, `install_scheduler.bat` also registers `SLEEP_TRIPLE\MorningDigest` at 07:00 user-local. That task runs:

```
python opt_d_alerts.py --run --trigger morning_digest --audit-window-hours 8
```

This aggregates the night's audit rows into a single push notification.

---

## 3. Subsystem Reference

### 3.1 Option A — AI Digital Product Factory

| | |
|---|---|
| **Module** | `opt_a_digital_factory.py` |
| **Monetization** | Gumroad instant shop (no approval) |
| **Capital** | $0 |
| **Defaults** | `--dry-run` writes to `./outbox/a_digital_factory/` but does NOT upload |
| **External** | Ollama (`qwen2.5-coder:latest`), ComfyUI (`http://127.0.0.1:8188`), OpenRouter free fallback |

**Closed enums:**
- `PRODUCT_KIND = (ai_prompts, code_snippets, design_assets)`
- `PUBLISH_MODE = (draft_only, staged, published)`

**Live mode flags:** `--publish staged` (publishes to Gumroad with `PUBLISH_MODE=staged`) or `--publish published` (full live). Default `--dry-run` does not upload.

**Ledger event:** `deploy_published` (via `Append-RevenueEvent.ps1`).

### 3.2 Option B — Faceless YouTube Shorts + Affiliate Funnel

| | |
|---|---|
| **Module** | `opt_b_faceless_shorts.py` |
| **Monetization** | Affiliate commissions via instant-approval programs |
| **Capital** | $0 |
| **Defaults** | `--dry-run` writes script + description; never uploads to YouTube |

**Closed enums:** `SUB_TASKS = (harvest_topics, write_script, generate_video, upload_short, inject_links)`

**Affiliate program URLs** (config: `opt_b_config.json: instant_approval_affiliate_programs`):
- Persona, Hostinger, Crypto.com, Binance, Kraken — all zero human approval.

**Live mode flag:** `--publish` (without this, even `--run` does not upload).

### 3.3 Option C — Crypto Yield Automation

| | |
|---|---|
| **Module** | `opt_c_crypto_yield.py` |
| **Monetization** | Observation-only spread snapshots; live trade is opt-in |
| **Capital** | $0 by default; set `opt_c_config.json: max_capital_aud > 0` to enable live trade |
| **Defaults** | `--dry-run` snapshots AND writes `signal_emitted` rows of `$0` |

**Closed enums:**
- `EXCHANGE_ENUM = (coinspot, kraken, independentreserve, binance)`
- `SIGNAL_TIER = (none, observed, actionable, executed, refused)`

**Real API fetches (zero human approval):**
- CoinSpot public ticker (no API key needed)
- Kraken `Ticker?pair=X` (no API key needed)
- IndependentReserve `GetMarketSummary` (no API key needed)

**Built-in safety rails:**
- Windows Python 3.12 ships an older CA store that trips on some exchange certs — `https_get_json()` retries with `CERT_NONE` so public endpoints don't fail closed.
- `_derive_aud_per_usd()` derives AUD/USD via BTC pivot (CoinSpot BTC/AUD ÷ Kraken XBTUSD) with sanity band 1.00–2.00; refuses synthetic 1.50 hardcode.
- IR fetcher uses `CurrentHighestBidPrice` / `CurrentLowestOfferPrice` (real schema), falls back to day-range if those are null.

### 3.4 Option D — Multi-Channel Webhook Alerter

| | |
|---|---|
| **Module** | `opt_d_alerts.py` |
| **Monetization** | None (operations tool) |
| **Capital** | $0 |
| **Defaults** | `--dry-run` prints payload to stdout |

**Closed enums:**
- `ALERT_TRIGGER = (actionable_spread, audit_failure, morning_digest)`
- `ALERT_CHANNEL = (discord, telegram, slack, pushover)`
- `ALERT_TIER = (info, warning, critical)`

**Multi-channel fanout (default behavior):**

When `--channel` is NOT specified, the alerter inspects the env vars for every channel and sends to all whose `CHANNEL_ENV_REQUIREMENTS` are fully set. Required env vars:

| Channel | Required env vars |
|---|---|
| Discord | `DISCORD_WEBHOOK_URL` |
| Telegram | `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` |
| Slack | `SLACK_WEBHOOK_URL` |
| Pushover | `PUSHOVER_APP_TOKEN`, `PUSHOVER_USER_KEY` |

Auto-fanout modes:
- `auto` (default): fanout to every env-set channel.
- `always`: same as auto, ignores `--channel`.
- `single`: respects explicit `--channel=X` or falls back to `default_channel`.

**Audit schema:** both legacy flat (`channel`, `sent`, `info`, `status_code`) AND new array (`channels: [{name, sent, info, status_code}]`) are populated, depending on whether single or multi-channel is in use. Dashboard readers that look at `row['channel']` keep working.

**Per-channel rate-limit:** `rate_limit_seconds` (default 900) debounces per `(trigger, channel)` tuple. Recognizes both legacy and new schema rows when scanning for last-sent timestamp.

**Tier thresholds (config: `tier_thresholds.actionable_spread`):**
- `critical_bps`: 200
- `warning_bps`: 100
- info below 100 bps.

**Discord payload safety:** `"allowed_mentions": {"parse": []}` so the alert never accidentally pings.

**Trigger behaviors:**
- `actionable_spread`: scans audit log for `opt_c` rows with `task=arbitrage` + `actionable_pairs>0`; emits one alert with up to 5 best opportunities.
- `audit_failure`: scans for `status=failed|refused` rows across all modules (excluding `opt_d_alerts` itself to prevent loops); emits warning-tier alert.
- `morning_digest`: aggregates last-N-hrs rows by status and module; emits info-tier summary.

---

## 4. Scheduling

### 4.1 Two scheduled tasks

`install_scheduler.bat` registers BOTH tasks in a single call:

| Task | Time (user-local) | Command |
|---|---|---|
| `SLEEP_TRIPLE\Nightly` | `sleep_window[0]` (default 23:00) | `python sleep_orchestrator.py --run --force-window` |
| `SLEEP_TRIPLE\MorningDigest` | `sleep_window[1]` (default 07:00) | `python opt_d_alerts.py --run --trigger morning_digest --audit-window-hours 8` |

Both times computed via `compute_next_boundary.py --boundary=start|end`, which honours the `tz` field in `sleep_config.json` (default `Australia/Sydney`) and rounds down to local HH:MM regardless of Windows box timezone.

### 4.2 DST handling (`compute_next_boundary.py`)

**DST spring-forward gap:** if the requested wall-clock does NOT exist on the current date (e.g. 02:30 AEDT→AEST doesn't exist on first Sunday of October in `Australia/Sydney`), the script detects it via naive `datetime(y,m,d,hh,mm)` + explicit `ZoneInfo` + UTC roundtrip and returns exit code 3 (refused).

**DST autumn-fallback overlap:** if the wall-clock exists twice (e.g. 02:30 AEST→AEDT repeats on first Sunday of April), the script picks fold=1 (post-transition UTC) so the daily recurrence keeps firing at the same wall-clock after DST ends.

**Return codes (`compute_next_boundary.py`):**
- `0` — success
- `1` — sleep_config.json missing
- `2` — sleep_window[index] not parseable
- `3` — DST gap (refused)
- `4` — bad `--boundary` argument

**Synthetic tests** in `_test_dst.py` cover all three scenarios (normal, gap, overlap).

### 4.3 Verification commands
```bat
schtasks /query /tn SLEEP_TRIPLE\Nightly /fo LIST /v
schtasks /query /tn SLEEP_TRIPLE\MorningDigest /fo LIST /v
```

---

## 5. Audit Log Schema (`SLEEP_TRIPLE_AUDIT.jsonl`)

Each row is a JSON object on its own line. Common fields:

| Field | Type | Notes |
|---|---|---|
| `ts` | ISO 8601 string | tz-aware (Australia/Sydney by default) |
| `module` | enum | `orchestrator / opt_a_digital_factory / opt_b_faceless_shorts / opt_c_crypto_yield / opt_d_alerts` |
| `slug` | string | Same as module name (per-module row short name) |
| `status` | enum | `started / ok / skipped / refused / noop / failed` |
| `reason` | string | Optional context (e.g., `outside_window`, `rate_limited`) |
| `date` | YYYY-MM-DD | Australia/Sydney date, used for idempotency |
| `dry_run` | bool | Was this a dry-run? |
| `exit_code` | int | Module subprocess return code |

**Per-module additions:**
- Opt A: `task`, `product_kind`, `publish_mode`
- Opt B: `task` (one of `SUB_TASKS`), `short_id`, `affiliate_urls`
- Opt C: `task` (one of `SUB_TASKS`), `best_pair`, `best_exchange`, `best_spread_bps`, `best_data_source`, `actionable_pairs`, `real_count`, `real_derived_fx`, `real_dayrange_approx`, `synthetic_fallbacks`
- Opt D legacy (single-channel): `channel`, `trigger`, `tier`, `sent`, `info`, `status_code`, `rate_limit_seconds`
- Opt D new (multi-channel): `channels: [{name, sent, info, status_code}]`, `trigger`, `tier`, `fanout_mode`, `headline_chars`, `line_count`, `rows_scanned`

**Why append-only?** Idempotency depends on `(date, slug, status=ok)` lookup; editing past rows collapses history. Corrections happen by appending new rows pointing at the same incident.

---

## 6. Helpers

### 6.1 `_live_send_test.py`
End-to-end webhook verifier:
- Detects configured channels via mirrored `CHANNEL_ENV_REQUIREMENTS`.
- Refuses politely with setup guidance if no env vars set.
- Otherwise invokes `python opt_d_alerts.py --run --trigger morning_digest --channel CHAN`.
- Scans audit-log delta for `http=200/204` in info string.
- `0` = real POST succeeded, `1` = audit row recorded failure / refused, `2` = setup error.

### 6.2 `_test_dst.py`
Synthetic DST scenario harness — verifies gap detection (exit 3) and overlap selection (exit 0 with fold=1 chosen).

### 6.3 `_verify_schtasks.py`
Confirms `schtasks /create /xml <path>` registers cleanly. Useful before relying on `install_scheduler.bat` for the first time on a fresh host.

### 6.4 `_commit_and_push.py` / `_commit_alerts.py` / `_commit_alerts2.py` / `_push_retry.py`
Drivers that work around Git Bash's path-quoting nonsense on `git add` + `git push`.

---

## 7. Real-time Dashboard

`launch_dashboard.bat` starts `dashboard_server.py` on port 3144 in the background and opens the browser to `http://127.0.0.1:3144`. Pulls from `SLEEP_TRIPLE_AUDIT.jsonl` and `REVENUE_LEDGER.jsonl`.

**Layout:**
- Top: today's date + last-run summary.
- Middle: per-status counts (ok/skipped/failed/refused).
- Bottom: latest 30 rows, color-coded by status.

---

## 8. Smoke Test History

| Run | Files | Result |
|---|---|---|
| R1 | syntax + JSON + compute_next_boundary (start/end/json) + opt_d fanout (default fallback) + detect_set_channels + _live_send_test refusal + bat files | All 7/7 PASS |
| R1 followup | argparse `choices=(...)` regression | One FAIL: `--boundary nonsense` returned rc=2 (argparse) not rc=4 (custom). Fixed by removing the argparse constraint and relying on explicit validation. All 7 PASS after fix. |
| R2 (regression) | compute_next_boundary `--boundary start \| end \| end --json \| nonsense \| default` | All 6/6 PASS; `--boundary nonsense` correctly returns rc=4 |

---

## 9. Commit History (local, awaiting push)

| Hash | Message |
|---|---|
| `216ffba8` | feat(opt_d): multi-channel fanout + morning-digest auto-fire + live-send helper |
| `6a312cbd` | fix(opt_d): dry-run semantics + config tier thresholds + rate-limit debounce + Discord dedupe |
| `ee632c7d` | fix: DST spring-forward gap detection via naive+tzinfo+UTC roundtrip |
| `d3acd167` | feat: wire IR fetcher + live AUD/USD FX + DST-safe scheduler |
| `f0d3d735` | feat: real APIs + scheduler + dashboard |
| `45034915` | chore: untrack SLEEP_TRIPLE/__pycache__/ bytecode; gitignore it |

⚠ **Push status:** all commits are local-only. `git push origin master` returns rc=128 (no PAT on this shell). The commits will not be on `origin/master` until a credential is supplied.

---

## 10. Architecture Decisions Recap

| Decision | Rationale |
|---|---|
| Sequential not parallel | GPU OOM + file-lock collisions |
| `--dry-run` default | Mirror Footclan runner pattern; live = opt-in |
| Append-only audit | Idempotency + history preservation |
| Rule #8 fence rigid | Personal-folder protection, no opt-out |
| Closed enums | Off-list values refused at parse time; human-readable schemas |
| Public APIs only | Zero-approval; no API key onboarding |
| TLS verify-then-fallback | Windows Py 3.12 old CA store trips on some endpoints |
| Naive+tzinfo+UTC roundtrip for DST | Canonical zoneinfo idiom for detecting non-existent local time |
| Multi-channel fanout default | Missed push to one channel doesn't lose the alert |
| Per-channel rate-limit independent | Prevents one rate-limit hit from blocking all channels |
| Audit schema backward-compat | Legacy single-channel readers see flat fields; new readers see `channels[]` |
| Two scheduled tasks (nightly + morning) | Orchestrator runs at night; morning digest aggregates after wake |
| `compute_next_boundary.py --boundary=start\|end` | Single source of truth for HH:MM conversion; both tasks share DST safety |
| `_live_send_test.py` separate from opt_d | Self-contained verifier; doesn't require opt_d code changes to debug channels |

---

## 11. Known Limitations & Pending Followups

| Item | Status |
|---|---|
| PAT not on shell; push to origin/master blocked | Pending user intervention |
| Telegram bot needs `@BotFather` one-time setup | Documented; pending user action |
| Dashboard reads `REVENUE_LEDGER.jsonl` directly | Fine; no fix needed |
| Window-end compute hardcodes 8h audit-window for morning digest | User must update if sleep window changes shape |
| No retry logic for failed `--run` POSTs | The `_live_send_test.py` helper exists; production retry could be added |
| Single monitor dashboard, no PWA / mobile | Cosmetic only |
| Opt A/B image generation depends on ComfyUI being online | Falls back to Ollama text-only if ComfyUI unreachable |
| No integrated AB test between revenue channels | Could add a simple revenue-per-iteration log |

---

## 12. Quick Reference Commands

```bash
# Dry-run, all 4
python sleep_orchestrator.py --force-window

# Dry-run, single option
python opt_a_digital_factory.py --dry-run
python opt_b_faceless_shorts.py --dry-run
python opt_c_crypto_yield.py --dry-run
python opt_d_alerts.py --dry-run --trigger morning_digest --channel discord

# Force a specific alerter trigger
python opt_d_alerts.py --dry-run --trigger actionable_spread
python opt_d_alerts.py --dry-run --trigger audit_failure --audit-window-hours 72

# Compute next boundary (debug)
python compute_next_boundary.py --boundary start
python compute_next_boundary.py --boundary end
python compute_next_boundary.py --boundary end --json

# Synthetic DST tests
python _test_dst.py

# Live webhook round-trip
python _live_send_test.py                 # pick first env-set channel
python _live_send_test.py --channel slack # force a channel

# Dashboard
launch_dashboard.bat                       # opens http://127.0.0.1:3144

# Install/remove scheduled tasks (admin)
install_scheduler.bat
uninstall_scheduler.bat

# Verify schedules
schtasks /query /tn SLEEP_TRIPLE\Nightly
schtasks /query /tn SLEEP_TRIPLE\MorningDigest

# List today's audit log
python sleep_orchestrator.py --list
```

---

## 13. Failure-Mode Reference Table

| Symptom | Likely cause | First check |
|---|---|---|
| `REFUSED: ROOT path ... violates Rule #8 fence` | opt_* path contains a personal folder segment | Move installation |
| `REFUSED: not in sleep window` (exit 3) | Outside 23:00–07:00 wall-clock | Add `--force-window` |
| `schtasks /create` exit 1 | Not running as admin | Re-run elevated |
| Opt D `STATUS_FAILED` with `-1` status_code | Required env var missing | Set the env var listed in `info` |
| Opt C `synthetic_fallbacks` row count dominates | Public API down / cert issue | Check `_derive_aud_per_usd` return; see comment in code |
| Opt D second call within 900s blocked | Rate-limit debounce | Clear audit log or wait |
| Morning digest empty `rows_scanned` | Audit log truncated or not present yet | Run nightly first |
| Push to GitHub fails rc=128 | PAT missing on shell | Add to credential helper |

---

*End of DOCUMENTATION.md. For how-to-run-it, see README.md. For ops audit log, see `SLEEP_TRIPLE_AUDIT.jsonl`. For revenue events, see `REVENUE_LEDGER.jsonl`.*
