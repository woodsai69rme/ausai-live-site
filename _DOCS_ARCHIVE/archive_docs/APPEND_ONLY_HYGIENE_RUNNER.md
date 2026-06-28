# 🧪 Append-only Hygiene Runner — companion explainer

> **First concrete daily append-only hygiene checker.** Reads a closed set of script-emitted log files (FOOTCLAN_*, AI_VOICE_PA_*, MCP_*, BACKUP_*, ENV_*, REVENUE_*, PHASE_F_TEST_*, SELF_TEST_*, REVENUE_SUMMARY.md), asserts each one is **monotone-growing** between two consecutive runs, and appends ONE markdown-table section per invocation to `APPEND_ONLY_HYGIENE.md`. **Default `--dry-run`**. Personal-folder guard rigid.

---

## ✅ COMPLIANCE — this document and its companion script are ADDITIVE ONLY.

- ✔ Adds: NEW `append_only_hygiene_runner.py` + NEW `APPEND_ONLY_HYGIENE_RUNNER.md`. Nothing modified.
- ✔ Honors: every prior artifact listed in §6 untouched.
- ✦ Does NOT touch Documents, Downloads, Pictures, Videos, Music, Desktop, OneDrive, Downloads\ARCHIVE_OLD.
- ✦ Does NOT propose replacing or relabelling any prior runner.

---

## 1. Defaults

The runner is **dry-run by default**. To actually emit a section, add `--run`.

```
python3 append_only_hygiene_runner.py
# (dry-run; prints plan; writes nothing; exit 0)
```

```
python3 append_only_hygiene_runner.py --run
# (writes one section to APPEND_ONLY_HYGIENE.md)
```

---

## 2. Closed TRACKED_LOGS list

| Log                          | Current writer(s)                                    |
| ---------------------------- | ----------------------------------------------------- |
| `FOOTCLAN_DISPATCH.log`      | `footclan_squad_dispatch.py`                          |
| `FOOTCLAN_EXECUTION.log`     | `footclan_executor.py`                                |
| `AI_VOICE_PA_AUDIT.log`      | `ai_voice_pa.py`                                      |
| `MCP_QUERY_AUDIT.log`        | `MCP_REMOTE_QUERY.ps1`                                |
| `MCP_HOST_HEALTH.log`        | `MCP_HOST_CONNECTOR.ps1`                              |
| `BACKUP_AUDIT.log`           | `verify_backups.ps1`                                  |
| `ENV_AUDIT.log`              | `EnvironmentSanitizer.ps1`                            |
| `VOICE_FOOTCLAN_BRIDGE.log`  | `voice_pa_bridge.py`                                  |
| `REVENUE_LEDGER.jsonl`       | `Append-RevenueEvent.ps1`                             |
| `PHASE_F_TEST_RESULTS.log`   | `SELF_TEST_RUN.ps1`                                   |
| `SELF_TEST_RESULTS.log`      | future-self-test scripts (deferred)                   |
| `REVENUE_SUMMARY.md`         | `Append-RevenueAggregator.ps1`                        |

> The list is closed; future artifact additions are deliberate `TRACKED_LOGS` updates.

---

## 3. Hygiene status enum

`HYGIENE_STATUS = ("ok", "size_regression", "ts_regression", "missing_iso_prefix", "unreadable")` — closed 5 values.

| Status                | What it means                                          |
| --------------------- | ------------------------------------------------------ |
| `ok`                  | size grew (or stayed) AND ts not earlier AND ISO-prefix present |
| `size_regression`     | current size < prior size (someone truncated)          |
| `ts_regression`       | current last-line ts is earlier than prior             |
| `missing_iso_prefix`  | last line lacks ISO8601 prefix (subsumed in `unreadable` paths today) |
| `unreadable`          | cannot read (path missing or unreadable)               |

---

## 4. Refusal matrix

| Trigger                                              | Exit      |
| ---------------------------------------------------- | --------- |
| `--logs-root` inside a Rule #8 personal folder       | 1         |
| `--report` inside a Rule #8 personal folder          | 1         |
| a tracked log resolves inside a Rule #8 folder       | per-log `refused_in_personal` row (NOT a hard refusal) |

> Personal-folder logs are flagged in the report and emitted as `refused_in_personal` rows without raising the exit code. The operator can resolve by relocating the offending log.

---

## 5. Append discipline (per `--run` invocation)

For each invocation, ONE section is appended:

```
## Run <run-id> @ <ISO8601 UTC>

| log | size | last_iso_prefix | prior_size | prior_iso | status |
| --- | --- | --- | --- | --- | --- |
| FOOTCLAN_DISPATCH.log       | 1024 | 2026-03-09T23:55  | 950  | 2026-03-09T22:30 | ok |
| AUDIT lines                | ...  | ...                | ...  | ...              | ... |
```

> The runner reads the report's own most-recent section to derive `prior_size` / `prior_iso`. Two runs != overlapping rows; strictly append-only.

---

## 6. Companion surface

| Companion artifact                                 | Status                                                |
| -------------------------------------------------- | ----------------------------------------------------- |
| `verify_backups.ps1`                               | Untouched. Source of `BACKUP_AUDIT.log`.              |
| `EnvironmentSanitizer.ps1`                         | Untouched. Source of `ENV_AUDIT.log`.                 |
| `MCP_HOST_CONNECTOR.ps1` / `MCP_HOST_HEALTH.log`   | Untouched.                                            |
| `MCP_REMOTE_QUERY.ps1` / `MCP_QUERY_AUDIT.log`     | Untouched.                                            |
| `ai_voice_pa.py` / `AI_VOICE_PA_AUDIT.log`         | Untouched.                                            |
| `footclan_squad_dispatch.py` / `FOOTCLAN_DISPATCH.log` | Untouched.                                         |
| `footclan_executor.py` / `FOOTCLAN_EXECUTION.log`  | Untouched.                                            |
| `voice_pa_bridge.py` / `VOICE_FOOTCLAN_BRIDGE.log` | Untouched.                                            |
| `Append-RevenueEvent.ps1` / `REVENUE_LEDGER.jsonl` | Untouched.                                            |
| `Append-RevenueAggregator.ps1` / `REVENUE_SUMMARY.md` | Untouched.                                         |
| `SELF_TEST_RUN.ps1` / `PHASE_F_TEST_RESULTS.log`   | Untouched.                                            |
| `APPEND_ONLY_HYGIENE.md` (when live)               | Append-only target.                                   |

> No prior surface is renamed, replaced, or erased.

---

## 7. Never-do list (carried forward)

The runner **MUST NEVER**:

- DELETE or REWRITE any tracked log.
- Truncate or rewrite prior sections of `APPEND_ONLY_HYGIENE.md`.
- Emit a status outside the 5-element enum.
- Read or write inside any Rule #8 personal folder.

---

## 8. Acceptance tests

- `test_append_only_growth` — running twice produces 2 sections of `APPEND_ONLY_HYGIENE.md` (strictly growing).
- `test_personal_folder_report_refused` — exit 1 on `--report` under Music/Downloads/etc.
- `test_personal_folder_log_flagged` — `--logs-root` containing a Rule #8 log path emits `refused_in_personal` row, no exit-code raise.
- `test_size_growth_pass` — a fresh log file of size 0 → size > 0 reports `ok`.
- `test_size_regression_detected` — a log file detected at smaller-than-prior size reports `size_regression`.
- `test_ts_regression_detected` — a log file whose latest line has earlier timestamp reports `ts_regression`.
- `test_dry_run_no_write` — `--dry-run` performs zero writes; report file byte-identical (when present) or absent (when first run).
- `test_tracked_logs_closed` — the runner inspects exactly the 12 logs in §2; no rogue entries.

---

## 9. What this runner does NOT do

- Does NOT enforce hygiene. The runner observes; the operator decides.
- Does NOT modify any tracked log.
- Does NOT auto-recover from size/ts regression. Recover is operator-driven.
- Does NOT scan unseen directories. The list is closed.

---

*Designed under the user's Golden Rules: append, never delete; preserve, never relabel; protect, never rewrite. Rule #8 personal folders (Documents, Downloads, Pictures, Videos, Music, Desktop, OneDrive, Downloads\ARCHIVE_OLD) are fenced off at every layer.*
