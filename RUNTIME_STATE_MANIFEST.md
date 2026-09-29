# RUNTIME_STATE_MANIFEST.md — Machine-Regenerated Runtime State Files
**Created:** 2026-09-24
**Purpose:** Registry of files that are now **git-untracked but permanent on disk** (Golden Rules #1, #2, #5 — nothing deleted, nothing excluded from disk, nothing obsolete).

---

## What happened (2026-09-24)

Machine-regenerated runtime state files (crypto daemon state, empire health probes) were
**untracked from git only** via `git rm --cached` and added to `.gitignore`. **Every file
remains on disk, byte-identical, and continues to be rewritten by its runtime processes.**
Only git's tracking was relaxed — the files' history remains fully preserved in prior commits
(v3.0 master release `bb9e96a09`), and pre-untrack snapshots were archived under
`BACKUPS/runtime_state_untrack_2026-09-24/` per Rule #5.

## Registered runtime state files (untracked, permanent, daemon-written)

| File (permanent on disk) | Writer | Write cadence | Why untracked |
|---|---|---|---|
| `EMPIRE_HEALTH_SNAPSHOT.json` | Empire health-probe script (TCP/HTTP port scans) | minutes | machine-regenerated telemetry snapshot |
| `CRYPTO_SUITE_DATA/crypto_master_state.json` | Crypto master daemon (whale autocopy engine) | continuous | live daemon state (followers, seen whale txids, autocopy counters) |
| `CRYPTO_SUITE_DATA/realtime_transactions_stream.json` | Crypto master daemon | continuous | rolling tx stream buffer |
| `CRYPTO_SUITE_DATA/whale_events_stream.json` | Crypto master daemon | continuous | rolling whale-event buffer |
| `CRYPTO_SUITE_DATA/coinbase_live_orders.json` | Crypto daemon (Coinbase simulation) | continuous | live order book simulation state |
| `CRYPTO_SUITE_DATA/writer_heartbeats.json` | Daemon heartbeat file (updated per write cycle) | continuous | transient liveness file |
| `CRYPTO_SUITE_DATA/copy_trade_portfolio.json` | Crypto daemon (copy-trade engine) | continuous | live portfolio simulation state |
| `CRYPTO_SUITE_DATA/vip_telegram_signals_history.json` | Telegram signal collector daemon | continuous | append/roll signal history |
| `CRYPTO_MANIFEST.md` | Session documentation | n/a | session log, not runtime state |

All other `CRYPTO_SUITE_DATA/*.json` (e.g. `executive_audit_report.json`,
`whale_crawler_discoveries.json`) and `SETUP_STATUS.json` remain tracked as reports.

## How to re-track any of these (escape hatch — additive)

```bash
git add -f EMPIRE_HEALTH_SNAPSHOT.json
```

Force-add overrides the ignore rule; the file becomes tracked again and future changes show
in `git status` again. To re-track permanently, remove its line from the ignore block below
(or add a negation pattern `!path` in `.gitignore`).

## Verification snapshot (2026-09-24)

- All files verified present on disk after untrack (`git status` showed them as ignored, not deleted).
- `git check-ignore -v` confirms the new block matches only these files.
- Backups archived under `BACKUPS/runtime_state_untrack_2026-09-24/`.

*Golden Rules: append, preserve, protect. Nothing deleted, nothing lost — git tracking only relaxed; history fully retained in earlier commits.*
