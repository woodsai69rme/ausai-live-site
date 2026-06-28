# DOCS_INDEX — Cold-start map for this repo

> **Audience:** Future-me (Karma) at 3am after a context wipe, or anyone auditing the repo cold. This file is the cold-start table of contents. README.md is *how-to-run-it*. DOCUMENTATION.md is *how-it-works*. This file is *where-do-I-go*.

---

## 0. TL;DR

- **Project name:** SLEEP_TRIPLE — three Aud-earning systems that run while you sleep (`SLEEP_TRIPLE/`)
- **Smoke entry point:** `python SLEEP_TRIPLE/_smoke_retry.py` (13 sections, last committed GREEN)
- **Most recent local commit:** see `git log --oneline -1` or §14 of `SLEEP_TRIPLE/DOCUMENTATION.md`
- **Push status:** local-only (rc=128 to `git push origin master` — no PAT on this shell)

---

## 1. Quick pointer map

| I want to… | Go to |
|---|---|
| Run the system | `SLEEP_TRIPLE/README.md` — "Quickstart" + "What This Does NOT Do" |
| Understand how it works | `SLEEP_TRIPLE/DOCUMENTATION.md` — Sections 1–13 |
| Find recent changes since docs | `SLEEP_TRIPLE/DOCUMENTATION.md` — Section 14 |
| Look at audit history | `SLEEP_TRIPLE_AUDIT.jsonl` (this CLI's state machine) |
| Look at revenue ledger | `REVENUE_LEDGER.jsonl` (existing append-only ledger) |
| Roll back a scheduled run | `REVENUE_SUMMARY.md` (weekly aggregator output) |
| See scheduled tasks | `schtasks /query /tn SLEEP_TRIPLE\\Nightly /tn SLEEP_TRIPLE\\MorningDigest /tn SLEEP_TRIPLE\\WeeklyRollup` |
| Run the smoke | `python SLEEP_TRIPLE/_smoke_retry.py` |
| Verify docs haven't drifted | `python SLEEP_TRIPLE/_doc_drift_check.py` |
| Push to origin (if you have a PAT) | `git push origin master` |

---

## 2. Module → doc section mapping

| Module | README.md section | DOCUMENTATION.md section |
|---|---|---|
| `sleep_orchestrator.py` | "Quickstart", "The Three Systems" | §3 (Subsystem Reference), §4 (Scheduling) |
| `opt_a_digital_factory.py` | "Option A" | §3.1 |
| `opt_b_faceless_shorts.py` | "Option B" | §3.2 |
| `opt_c_crypto_yield.py` | "Option C" | §3.3 |
| `opt_d_alerts.py` | (in "Three Systems" but not as a header) | §3.4 |
| `dashboard_server.py` | (mentioned in §7 cross-ref) | §7 |
| `_smoke_retry.py` | "Smoke is 12 sections now" | §8, §8b |
| `_doc_drift_check.py` | (NEW — this batch) | (NEW — to add) |
| `_ledger_writer.py` | (NEW — recent rounds) | §14.1 |
| `Append-RevenueEvent.ps1` | "Bug closeouts" | §14.2, §14.3 |
| `Append-RevenueAggregator.ps1` | (NEW — recent rounds) | §14.6 |
| `run_nightly.bat` / `run_morning_digest.bat` / `run_weekly_rollup.bat` | "Three scheduled tasks now" | §4.1, §14.6 |
| `install_scheduler.bat` / `install_aggregator_scheduler.bat` / `uninstall_aggregator_scheduler.bat` | (mentioned) | §4.1, §14.6 |

---

## 3. Failure modes at a glance

| Symptom | First check |
|---|---|
| `REFUSED: ROOT path … violates Rule #8 fence` | `Documents, Downloads, Pictures, Videos, Music, Desktop, OneDrive, ARCHIVE_OLD` |
| `schtasks /create` exit 1 | Re-run install bat elevated (admin) |
| Smoke Section 11 flapped rc=1 | Port TIME_WAIT — restart dashboard or wait |
| Smoke Section 12 rc=1 | `_ledger_writer` not wired — re-import `from _ledger_writer import append_ledger_event` |
| `git push origin master` rc=128 | No PAT on this shell. Add to credential helper. |
| `JSON.parse` rejects first byte of ledger row | UTF-8 BOM in appender — re-run `Append-RevenueEvent.ps1` BOM-fix patch |
| `_doc_drift_check.py` rc=1 | DOCUMENTATION.md §9 latest commit != filtered git-log top — re-run smoke, then regenerate §9 with the snippet in section 7 |

For thorough failure-mode reference, see DOCUMENTATION.md §13.

---

## 4. Quick command reference

```bash
# Cold start: read this file + run smoke.
python SLEEP_TRIPLE/_smoke_retry.py

# Verify docs are in sync with the commit log.
python SLEEP_TRIPLE/_doc_drift_check.py

# Dry-run the orchestrator.
python SLEEP_TRIPLE/sleep_orchestrator.py --force-window

# Dry-run a single option.
python SLEEP_TRIPLE/opt_a_digital_factory.py --dry-run
python SLEEP_TRIPLE/opt_b_faceless_shorts.py --dry-run
python SLEEP_TRIPLE/opt_c_crypto_yield.py --dry-run
python SLEEP_TRIPLE/opt_d_alerts.py --dry-run --trigger morning_digest

# Start the dashboard (read-only) on port 3144.
launch_dashboard.bat            # Windows

# Install/remove scheduled tasks (admin).
install_scheduler.bat
uninstall_scheduler.bat
install_aggregator_scheduler.bat
uninstall_aggregator_scheduler.bat

# Verify scheduled tasks.
schtasks /query /tn 'SLEEP_TRIPLE\Nightly'
schtasks /query /tn 'SLEEP_TRIPLE\MorningDigest'
schtasks /query /tn 'SLEEP_TRIPLE\WeeklyRollup'

# List today's audit log.
python SLEEP_TRIPLE/sleep_orchestrator.py --list

# Synthetic DST tests.
python SLEEP_TRIPLE/_test_dst.py

# Live webhook round-trip (real POST).
python SLEEP_TRIPLE/_live_send_test.py --channel slack
```

---

## 5. Document lineage

| File | Last committed | Subject |
|---|---|---|
| `SLEEP_TRIPLE/README.md` | `c1132ec4` | "Recent Updates" block appended |
| `SLEEP_TRIPLE/DOCUMENTATION.md` | `c1132ec4` | §14 appended (7-commit archaeology) |
| `DOCS_INDEX.md` | (NEW with this batch) | Cold-start map |
| `SLEEP_TRIPLE/_doc_drift_check.py` | (NEW with this batch) | Doc/commit-log sync guard |

Run `git log --oneline -- 'SLEEP_TRIPLE/*' 'Append-Revenue*' 'DOCS_INDEX.md'` to see live history.

---

*If you find yourself hunting through README.md and DOCUMENTATION.md for a single answer, please update this file — that's its purpose.*