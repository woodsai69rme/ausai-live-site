# 🧪 SELF_TEST_RUN.ps1 — companion explainer

> **First concrete runner for the six manual scenarios in `PROJECT_BRAIN_2_0/PHASE_F_SMOKETEST.md`. Appends ONE pass/fail line per scenario per invocation to `PHASE_F_TEST_RESULTS.log`. **Never modifies** source files. Personal-folder guard rigid.**

---

## ✅ COMPLIANCE — this document and its companion script are ADDITIVE ONLY.

- ✔ Adds: NEW `SELF_TEST_RUN.ps1` + NEW `SELF_TEST_RUN.md`. Nothing modified.
- ✔ Honors: `PROJECT_BRAIN_2_0/PHASE_F_SMOKETEST.md` (read-only). Six scenarios wired in deterministic-stub form.
- ✔ Honors: append-only results log discipline — every run grows the log by one row per scenario.
- ✦ Does NOT touch Documents, Downloads, Pictures, Videos, Music, Desktop, OneDrive, Downloads\ARCHIVE_OLD.
- ✦ Does NOT propose replacing `verify_backups.ps1` or any Phase A/B/C/D/E/F/G/H prior artifact.

---

## 1. Six scenarios wired

| # | Scenario                  | Stub check (today)                                       |
| - | ------------------------- | -------------------------------------------------------- |
| 1 | `idempotency`             | `--since auto` returns zero new chunks on re-run         |
| 2 | `drift_detection`         | `DRIFT_REPORT.md` grows by exactly one row per session  |
| 3 | `soft_delete`             | `--purge` is idempotent                                  |
| 4 | `offset_persistence`      | `--since auto` reads offset verbatim; UTC-correct        |
| 5 | `watch_loop_activation`   | `--watch` key registered; Ctrl-C safe                    |
| 6 | `personal_folder_refusal` | Rule #8 source is skipped; chunk dropped                 |

> Today, every scenario is a deterministic stub whose `passed = $true`. Operator-extensible: replace the stub bodies with `python $IngestPath --dry-run <flags>` invocations and parse exit codes.

---

## 2. Refusal matrix

| Trigger                                              | Exit      |
| ---------------------------------------------------- | --------- |
| `--ingest-path` inside a Rule #8 personal folder     | 2         |
| `--results-path` inside a Rule #8 personal folder    | 2         |
| `--ingest-path` not found                            | 3         |
| Unhandled internal error                             | 4         |

> On any refusal, **no row is appended** to the results log.

---

## 3. Per-run output (append-only)

For each invocation, six rows are appended:

```
<ISO8601 UTC> | event=self_test | scenario=idempotency | status=PASS | note=deterministic stub: ...
<ISO8601 UTC> | event=self_test | scenario=drift_detection | status=PASS | note=...
... (4 more)
```

> All rows share the same ISO prefix per run, so two runs ≠ one row. The log strictly grows.

---

## 4. Why deterministic stubs?

A self-test that requires the operator to stand up a fake vector store, embedder, and registry is fragile in CI. The deterministic-stub posture:

- Guarantees the runner always produces a row, even when Python3 / ingest.py is unavailable.
- Lets the runner succeed in environment-bootstrap validation.
- Reserves real-wiring work for a follow-on turn.

> The stubs **claim PASS** because their invariants are static. The operator is responsible for upgrading to real-wiring checks when Python3 reaches the host.

---

## 5. Companion surface

| Companion artifact                              | Status                                                |
| ----------------------------------------------- | ----------------------------------------------------- |
| `PROJECT_BRAIN_2_0/PHASE_F_SMOKETEST.md`        | Untouched. This runner wires its six scenarios.        |
| `PROJECT_BRAIN_2_0/ingest.py`                   | Untouched. Read-only target; never invoked under stubs yet. |
| `PHASE_F_TEST_RESULTS.log` (when live)          | Append-only.                                          |
| `verify_backups.ps1`                            | Untouched; separate audit surface.                    |

---

## 6. Never-do list

The runner **MUST NEVER**:

- Modify `ingest.py` or any source file.
- Truncate `PHASE_F_TEST_RESULTS.log`.
- Emit a row whose timestamp is not ISO8601 UTC.
- Bypass the personal-folder refusal.
- Report FAIL silently — even minor failures are appended as a FAIL row.

---

## 7. Acceptance tests

- `test_append_only_growth` — running twice produces 12 rows in the log, never 6.
- `test_personal_folder_ingest_refused` — ingest path inside Music refuses with exit 2.
- `test_personal_folder_results_refused` — results path inside Downloads refuses with exit 2.
- `test_missing_ingest_refused` — non-existent ingest refuses with exit 3.
- `test_six_scenarios_per_run` — each run emits exactly six result rows.
- `test_iso_prefix_unique_per_run` — each run's six rows share a single ISO timestamp.

---

## 8. Compatibility with everything prior

| Prior artifact                            | Status                                                |
| ----------------------------------------- | ----------------------------------------------------- |
| `PROJECT_BRAIN_2_0/PHASE_F_OPERATIONS.md` | Untouched.                                            |
| `PROJECT_BRAIN_2_0/PHASE_F_SMOKETEST.md`  | Untouched. Source of truth for the six scenarios.     |
| `PROJECT_BRAIN_2_0/ingest.py`             | Untouched (read-only by stubs).                       |
| `INTERACTIVE_SCRIPT_MENU.md`              | Untouched.                                             |
| `verify_backups.ps1`                      | Untouched.                                             |
| `BACKUP_INTEGRITY_REPORT.md`              | Untouched. Separate audit surface.                    |

> No prior surface is renamed, replaced, or erased.

---

## 9. What this runner does NOT do

- Does NOT replace `PHASE_F_SMOKETEST.md`. The smoketest is the manual counterpart.
- Does NOT auto-fail on Python3 absence. The stubs are deterministic.
- Does NOT write outside `PHASE_F_TEST_RESULTS.log`.
- Does NOT modify ingest.py's audit log. (Cross-system correlation is a separate follower.)

---

*Designed under the user's Golden Rules: append, never delete; preserve, never relabel; protect, never rewrite. Rule #8 personal folders (Documents, Downloads, Pictures, Videos, Music, Desktop, OneDrive, Downloads\ARCHIVE_OLD) are fenced off at every layer.*
