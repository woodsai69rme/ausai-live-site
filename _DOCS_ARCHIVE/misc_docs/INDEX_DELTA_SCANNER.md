✅ COMPLIANCE — this document and its companion script `INDEX_DELTA_SCANNER.py` are ADDITIVE ONLY. They do NOT modify, replace, or delete any tracked master index, master report, or prior script. They refuse any path under Rule #8 (Documents, Downloads, Pictures, Videos, Music, Desktop, OneDrive, ARCHIVE_OLD) and write only to `INDEX_DELTA.log`.

# INDEX_DELTA_SCANNER.py — companion explainer

## 1. Purpose

Surf the **delta** between what the project's master indexes *say* exists and what the disk *actually contains*. This is the cross-reference automation that closes the gap named in `COMPREHENSIVE_PROJECT_REPORT.md`:

> the master indexes claim dozens of repos and projects that are not on disk, while the disk contains dozens of entries the indexes never mention.

The tool emits one ISO-prefixed JSONL row per (claim, anchor) pair expressed as `claimed_present` or `claimed_missing`, plus one row per (disk_entry, anchor) pair expressed as `disk_extra`. The result is a permanently auditable list of divergences.

## 2. Closed delta status enum (6 elements)

| Status | Meaning |
|---|---|
| `claimed_present` | A name appears in at least one tracked index AND at least one disk anchor. |
| `claimed_missing` | A name appears in at least one tracked index but exists under NONE of the disk anchors. |
| `disk_extra`      | A name appears under a disk anchor but is NOT mentioned in any tracked index. |
| `refused`         | Either the claim or the disk entry resolves under Rule #8. Recorded but not written past personal folders. |
| `skipped`         | Empty / whitespace-only leaf name; non-numeric; malformed. |
| `unverifiable`    | No `DISK_ANCHORS` path resolves on this machine for the claim. |

These six values are closed. The script does not emit ad-hoc statuses at runtime.

## 3. Closed disk-anchor set (4 elements)

The tools scans the **immediate children** of each anchor (non-recursive one-level walk):

- `X:\GITHUBREPO`
- `X:\githrepo`
- `X:\03_PROJECTS`
- `C:\Users\karma\03_PROJECTS`

Each anchor is reported in the run summary as either `anchors_resolved` (exists and was enumerated) or `anchors_missing` (does not exist on this machine).

## 4. Closed extraction-regex set (3 elements)

For each tracked index, three regex patterns feed the candidate-name extractor:

| Pattern label     | Shape |
|---|---|
| `backticked_name` | `` `some-repo` `` |
| `bullet_listed_name` | `- Some Project (description)` at line start (multiline, optional parenthetical or em-dash tail) |
| `keyed_name`      | `Repository: foo-bar` / `Project: baz` / case-insensitive `repo: ...` |

Names are then run through `normalize_name` (whitespace collapsed, parenthetical suffixes stripped, last path-component taken, comparison key is lowercased). This makes the matcher case-insensitive and forgiving of trailing punctuation.

## 5. Refusal matrix (exit codes)

| Exit | Trigger |
|---|---|
| `0` | Success — dry-run preview printed OR `--run` wrote delta rows + summary. |
| `2` | Workspace, anchor, or log path resolves under Rule #8. |
| `3` | A tracked index file is missing on disk (counted in summary; does NOT exit non-zero). |
| `4` | A tracked index file is unreadable (counted in summary; does NOT exit non-zero). |
| `5` | `--dry-run` and `--run` both passed, OR `--only` value not on the closed `TRACKED_INDEX_FILES` list. |

Targets missing / unreadable are recorded in the summary; the tool exits `0` because that's normal data-quality signal, not a runner error.

## 6. Append discipline

- **Output**: `INDEX_DELTA.log` in the workspace root, opened with `"a"` (append) and `encoding="utf-8"`, never `"w"`. Newline is `"\n"` (Windows-friendly).
- **One row per (claim, anchor) AND one row per (disk_entry, anchor)**. Each row carries the side (`claim` vs `disk`), the normalized comparison key, the source index (claim-side) or anchor (disk-side), and the closed status.
- **One `# run_complete` summary row** at the end of each real run (`WROTE` mode). Includes the by_status histogram and the personal-folder refusal count.
- **Read-only on every master index** (`"r"` mode). Read-only enumeration on every disk anchor (`os.listdir`). No files anywhere in `TRACKED_INDEX_FILES` or `DISK_ANCHORS` are modified.
- **Default dry-run**: invoking the script without `--run` prints the histogram and writes nothing.

## 7. Companion surface

| File | Role |
|---|---|
| `INDEX_DELTA_SCANNER.py` | The script (closed target list, closed anchor list, closed enums, additive writer). |
| `INDEX_DELTA_SCANNER.md` | This document. |
| `INDEX_DELTA.log` | Append-only JSONL delta log (one row per divergence + one summary per real run). |
| `TODO_TRACKER.md` | Receives an append-only "Update logged (this turn)" block for the new artifact pair. |

## 8. Untouched prior artifacts

- Every file in `TRACKED_INDEX_FILES` is **read-only** here. The script NEVER writes to any of these.
- All prior audit / delta runners (`BACKUP_AUDIT_RUN.ps1`, `ENV_AUDIT_RUN.ps1`, `MCP_QUERY_AUDIT_RUN.py`, `MCP_HOST_HEALTH_RUN.py`, `REALITY_VS_CLAIM_AUDIT.py`, `GAL_INTEGRITY_VERIFY.py`) are untouched.
- This tool does not generate, replace, or rewrite any prior artifact. It only adds a new pair (`.py` + `.md`) and (on `--run`) appends to one log.

## 9. What this tool does NOT verify

- **Counts of repos/projects** (those are numeric summaries; that gap is closed by `REALITY_VS_CLAIM_AUDIT.py`).
- **Dollar valuations or hours** (no on-disk artifact can prove those).
- **Recursive tree walk** — the delta scanner deliberately checks ONE level under each anchor. Recursive walks would conflate "this folder exists" with "this repo IS the folder", and the false-positive rate would explode.
- **Repository health** — a name can match on disk while the underlying git clone is corrupt. That's a separate check (`GAL_INTEGRITY_VERIFY.py` walks `.gal` archives; a separate repo-integrity runner could cover this if needed).
- **Symlinks / shortcuts** — these are NOT followed. The walker reads `os.listdir` directly; entries whose names match are checked `os.path.isdir` only.

## 10. How to use

```bash
# 1. Dry-run preview (no log write)
python INDEX_DELTA_SCANNER.py

# 2. Real run on one master index only
python INDEX_DELTA_SCANNER.py --only MASTER_INDEX.md --run

# 3. Real run on all 10 tracked indexes
python INDEX_DELTA_SCANNER.py --run

# 4. From a different workspace
python INDEX_DELTA_SCANNER.py --workspace D:\\some\\other\\root --run
```

## 11. Rule #8 footer

This tool and its log refuse any path under any of the following closed 8-item list:

1. `Documents`
2. `Downloads`
3. `Pictures`
4. `Videos`
5. `Music`
6. `Desktop`
7. `OneDrive`
8. `Downloads\ARCHIVE_OLD` (the `ARCHIVE_OLD` segment terminates the list)

No path under any of these folders is read, written, enumerated, audited, or implied. The list is closed and ordered.
