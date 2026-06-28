✅ COMPLIANCE — this document and its companion script `REALITY_VS_CLAIM_AUDIT.py` are ADDITIVE ONLY. They do NOT modify, replace, or delete any tracked master index, master report, or prior script. They refuse any path under Rule #8 (Documents, Downloads, Pictures, Videos, Music, Desktop, OneDrive, ARCHIVE_OLD).

# REALITY_VS_CLAIM_AUDIT.py — companion explainer

## 1. Purpose

Cross-reference numeric / path / repo **claims** found in the project's master-index markdown files against **real on-disk state**, then emit an append-only audit log so the gap between *claim* and *reality* is permanently recorded.

This is the automation that closes the gap identified in `COMPREHENSIVE_PROJECT_REPORT.md`: the headline figures ("277 GitHub repos", "96 ACTIVE_PROJECTS", "500+ projects", "$20M+ ecosystem") were documented but never machine-checked against disk. This tool reads each master index, extracts the claims, resolves them against the filesystem, and emits a JSONL row per claim.

## 2. Closed verification status enum

| Element | Meaning |
|---|---|
| `verified_match`    | Claim resolves to a concrete on-disk artifact that matches (counts equal, file exists). |
| `verified_mismatch` | Claim resolves to an artifact on disk that does NOT match (count differs, file missing). |
| `verified_partial`  | Claim resolves to a partial match — the figure is within ±20% of reality. |
| `unverifiable`      | No on-disk anchor can resolve the claim (no dollar value can be machine-verified). |
| `skipped`           | Pattern matched but value was non-numeric / malformed. |
| `refused`           | Resolved path was under Rule #8 personal folder. Not written to log; counted only. |

These six values are closed. The script does not introduce new statuses at runtime.

## 3. Refusal matrix (exit codes)

| Exit | Trigger |
|---|---|
| `0` | Success — dry-run preview printed OR `--run` wrote rows + summary. |
| `2` | Workspace, an index path, or the log path resolves under Rule #8. |
| `3` | A tracked master index file is missing on disk. Recorded in run summary. |
| `4` | A tracked master index file is unreadable (permission / encoding error). |
| `5` | `--dry-run` and `--run` both passed (mutually exclusive). |

The summary at the bottom of the run distinguishes **targets_scanned**, **targets_missing**, and **targets_unreadable** without ever exiting non-zero for missing/unreadable — those are normal data-quality signals, not runner errors.

## 4. Append discipline

- **Output**: `REALITY_VS_CLAIM_AUDIT.log` in the workspace root, opened with `"a"` (append) and `encoding="utf-8"`, never `"w"`.
- **One row per claim** — the ISO-8601 UTC timestamp prefixes every JSON line; rows are sorted-stable so reruns compose cleanly.
- **One `# run_complete` summary row** at the end of each real run. The summary includes the tool, the mode (`DRY-RUN` vs `WROTE`), the by_status histogram, and the personal-folder refusal count.
- **Read-only on every master index**: `open(path, "r", encoding="utf-8")`. No file outside `REALITY_VS_CLAIM_AUDIT.log` is written.
- **Default dry-run**: invoking the script without `--run` prints the histogram to stdout and writes nothing. This protects against accidental bulk-writes during exploration.

## 5. Companion surface

| File | Role |
|---|---|
| `REALITY_VS_CLAIM_AUDIT.py` | The script (closed target list, closed enums, additive writer). |
| `REALITY_VS_CLAIM_AUDIT.md` | This document. |
| `REALITY_VS_CLAIM_AUDIT.log` | Append-only JSONL audit log (one row per claim + one summary per real run). |
| `TODO_TRACKER.md` | Receives an append-only "Update logged (this turn)" block for the new artifact pair. |

## 6. Untouched prior artifacts

- Every file in `TRACKED_INDEX_FILES` (10 master indexes) is **read-only** here.
- All prior audit runners (`BACKUP_AUDIT_RUN.ps1`, `ENV_AUDIT_RUN.ps1`, `MCP_QUERY_AUDIT_RUN.py`, `MCP_HOST_HEALTH_RUN.py`, etc.) are untouched.
- This tool does not generate, replace, or rewrite any prior artifact. It only adds a new pair (`.py` + `.md`) and (on `--run`) appends to one log.

## 7. What this tool does NOT verify

- **Dollar figures** (`$35K–$65K AUD`, `$20M+`) — recorded as `unverifiable`. No on-disk artifact can prove a dollar amount; that requires the user's time tracker, client billing data, or comparable sales receipts.
- **Effort hours** (500–700 hours) — same reason as dollar figures. There is no timer-log on disk.
- **Testimony / claims about ChatGPT chat history** — there's no `conversations.json` on disk; ChatGPT exports would need to be dropped into the workspace.
- **Intent / motivation / what was supposed to happen** — those live in plan docs and are not verifiable from disk state.

What it CAN verify: file existence, directory entry counts (with anchor-based matching), and path spellings found in markdown. That's a smaller scope than the headlines imply, and is exactly what's needed to break the documentation-overload loop.

## 8. How to use

```bash
# 1. Preview (no log write)
python REALITY_VS_CLAIM_AUDIT.py

# 2. Real run on one master index only
python REALITY_VS_CLAIM_AUDIT.py --only MASTER_INDEX.md --run

# 3. Real run on all 10 tracked indexes
python REALITY_VS_CLAIM_AUDIT.py --run

# 4. From a different workspace
python REALITY_VS_CLAIM_AUDIT.py --workspace D:\some\other\root --run
```

## 9. Rule #8 footer

This tool and its log refuse any path under any of the following closed 8-item list:

1. `Documents`
2. `Downloads`
3. `Pictures`
4. `Videos`
5. `Music`
6. `Desktop`
7. `OneDrive`
8. `Downloads\ARCHIVE_OLD` (the `ARCHIVE_OLD` segment terminates the list)

No path under any of these folders is read, written, counted, audited, or implied. The list is closed and ordered.
