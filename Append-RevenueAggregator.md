# 💵 Append-RevenueAggregator.ps1 — companion explainer

> **Sister to `Append-RevenueEvent.ps1`. Reads `REVENUE_LEDGER.jsonl` (read-only) and appends ONE aggregated section per run to `REVENUE_SUMMARY.md`. Grouped by `(event, month)`. Always additive. Never destructive. Personal-folder guard rigid.**

---

## ✅ COMPLIANCE — this document and its companion script are ADDITIVE ONLY.

- ✔ Adds: NEW `Append-RevenueAggregator.ps1` + NEW `Append-RevenueAggregator.md`. Nothing modified.
- ✔ Honors: `REVENUE_TRACKING_DESIGN.md` and `Append-RevenueEvent.ps1` (read-only).
- ✔ Honors: append-only summary discipline — every run grows `REVENUE_SUMMARY.md` by exactly one section.
- ✦ Does NOT touch Documents, Downloads, Pictures, Videos, Music, Desktop, OneDrive, Downloads\ARCHIVE_OLD.
- ✦ Does NOT propose replacing `Append-RevenueEvent.ps1`, the ledger, or the readiness report.

---

## 1. What the aggregator emits

For each invocation, one section is appended:

```
## Run <run-id> @ <ISO8601 UTC>

Aggregated <N> lines (<M> malformed skipped).

| event                | month   | count | sum (USD) | source sample         |
| ---                  | ---     | ---   | ---       | ---                   |
| deploy_published     | 2026-03 | 4     | 0.0000    | pipeline:marketplace  |
| signal_emitted       | 2026-03 | 12    | 0.0000    | pipeline:crypto-sentiment |
| notify_dispatched    | 2026-03 | 7     | 0.0000    | pipeline:notify       |
```

> `-` in `sum (USD)` means amounts were all `null`; otherwise the column value is the realized sum.

---

## 2. Grouping rules

- **Key**: `event|YYYY-MM` (month derived from `ts` prefix).
- **count**: total lines matching the key.
- **sum**: realized `amount_usd` total; `null` amounts are not aggregated (the cell shows `0.0000` only if all amounts in the group are null).
- **source sample**: the first non-empty `source` for the group.

> Sub-month buckets are not produced. Sub-event-kind string semantics are preserved verbatim.

---

## 3. Refusal matrix

| Trigger                                              | Exit      |
| ---------------------------------------------------- | --------- |
| `--ledger-path` inside a Rule #8 personal folder     | 2         |
| `--summary-path` inside a Rule #8 personal folder    | 2         |
| `--ledger-path` not found                            | 3         |
| Unhandled internal error (e.g. read I/O failure)     | 4         |

> On any refusal, **no section is appended** to the summary.

Per-line malformed JSON in the ledger is **not** a refusal — it's counted in the `<M> malformed skipped` tally and skipped without halting the run.

---

## 4. Append discipline

For each successful call:

- **Exactly one section** is appended to `REVENUE_SUMMARY.md`.
- The first line of the section is `## Run <run-id> @ <ISO8601 UTC>`.
- Prior sections are **never** rewritten, reordered, or re-timed.

> The script never truncates, never rewrites, never reflows.

---

## 5. Companion surface

| Companion script             | Surface (read-mostly downstream)             |
| ---------------------------- | -------------------------------------------- |
| `Append-RevenueEvent.ps1`    | First writer; this aggregator is downstream. |
| `REVENUE_LEDGER.jsonl`       | Read-only source.                            |
| `REVENUE_SUMMARY.md`         | Append-only target.                           |

---

## 6. Never-do list (carried forward)

The aggregator **MUST NEVER**:

- DELETE the ledger or summary.
- REWRITE a prior section.
- MERGE multiple run sections into one.
- ACCEPT a path inside a Rule #8 personal folder.
- EMIT a section without `<ISO8601 UTC> timestamp.

---

## 7. Acceptance tests

- `test_append_one_section` — happy path appends exactly one section.
- `test_personal_folder_ledger_refused` — exit 2 on ledger under Music.
- `test_personal_folder_summary_refused` — exit 2 on summary under Downloads.
- `test_missing_ledger_refused` — exit 3 on a non-existent ledger path.
- `test_malformed_skipped` — a malformed ledger line is counted as skipped, not fatal.
- `test_summary_append_only` — running twice produces two append-only sections; never shrinks.
- `test_grouping_by_event_month` — events with same kind / different months end up in different buckets.
- `test_idempotent_under_no_new_rows` — running twice on an idempotent ledger produces two sections of identical content (idempotent up to timestamp + run-id).

---

## 8. Compatibility with everything prior

| Prior artifact                        | Status                                                |
| ------------------------------------- | ----------------------------------------------------- |
| `Append-RevenueEvent.ps1` / `.md`     | Untouched. This aggregator inherits its ledger contract. |
| `REVENUE_TRACKING_DESIGN.md`          | Untouched.                                             |
| `REVENUE_LEDGER.jsonl` (when live)    | Read-only.                                             |
| `REVENUE_SUMMARY.md` (when live)      | Append-only.                                           |
| `REVENUE_READINESS_REPORT.md`         | Untouched.                                             |
| `GITLEAKS_REPORT.md`                  | Untouched.                                             |

> No prior surface is renamed, replaced, or erased.

---

## 9. What this aggregator does NOT do

- Does NOT mutate the ledger.
- Does NOT compute taxes or net amounts.
- Does NOT enforce monetary correctness.
- Does NOT trigger events. The aggregator observes only.

---

*Designed under the user's Golden Rules: append, never delete; preserve, never relabel; protect, never rewrite. Rule #8 personal folders (Documents, Downloads, Pictures, Videos, Music, Desktop, OneDrive, Downloads\ARCHIVE_OLD) are fenced off at every layer.*
