✅ COMPLIANCE — this document and its companion script `INDEX_DELTA_RECURSIVE.py` are ADDITIVE ONLY. They do NOT modify, replace, or delete any tracked master index, master report, prior script, or any file under any `DISK_ANCHORS` directory. They refuse any path under Rule #8 (Documents, Downloads, Pictures, Videos, Music, Desktop, OneDrive, ARCHIVE_OLD) and write only to `INDEX_DELTA_RECURSIVE.log`.

# INDEX_DELTA_RECURSIVE.py — companion explainer

## 1. Purpose

The recursive depth-scanner that surfaces **WHERE INSIDE** the disk tree the master-index divergence happens. Companion to `INDEX_DELTA_SCANNER.py` — that tool tells you "234 names are claimed, 8 of them exist, 909 disk entries are unmentioned at top level". This tool tells you "the names that DO match — are they sitting in shallow subdirs, or buried deep inside huge repos where no human would ever find them?".

Specifically: walks each `DISK_ANCHORS` directory via `os.walk` up to a configurable `--max-depth` (default 2, range 1..4), and emits one per-directory delta row using the **same closed 6-element `DELTA_STATUS_ENUM`** as the non-recursive scanner. No new statuses are introduced at the leaf level — only the run summary gains a `by_depth` histogram.

## 2. Re-declared closed sets (manual sync required if either side changes)

The closed-set constants from `INDEX_DELTA_SCANNER.py` are **re-declared verbatim** in `INDEX_DELTA_RECURSIVE.py`. This is duplication, not import — there is no shared module today. **If any of these constants changes in `INDEX_DELTA_SCANNER.py`, the change MUST be mirrored here, or the two scanners will silently diverge.**

| Set | Size | Origin |
|---|---|---|
| `PERSONAL_FOLDERS`     | 8 (ends `ARCHIVE_OLD`) | re-declared from `INDEX_DELTA_SCANNER.py` |
| `TRACKED_INDEX_FILES`  | 10 | re-declared from `INDEX_DELTA_SCANNER.py` |
| `DISK_ANCHORS`         | 4  | re-declared from `INDEX_DELTA_SCANNER.py` |
| `EXTRACTION_PATTERNS`  | 3  | re-declared from `INDEX_DELTA_SCANNER.py` |
| `DELTA_STATUS_ENUM`    | 6  | re-declared verbatim: (claimed_present, claimed_missing, disk_extra, refused, skipped, unverifiable) |
| `MIN_DEPTH` / `DEFAULT_DEPTH` / `MAX_DEPTH` | `1` / `2` / `4` | NEW — only defined in the recursive scanner |

The shared sets give both scanners a consistent source-of-truth shape; the duplication keeps each script independently runnable without a third `__init__.py` import surface. The trade-off is that one constant edited in `INDEX_DELTA_SCANNER.py` does NOT auto-propagate here; an editor of either should diff the other.

Future refactor (NOT done in this turn): extract `_INDEX_DELTA_LIB.py` and have both scripts `from _INDEX_DELTA_LIB import …`. That would be a 3rd new file — out of scope for the additive-only audit pattern, but worth filing as a follow-on.

## 3. Closed recursion bounds (range [1, 4])

| Constant | Value | Reason |
|---|---|---|
| `MIN_DEPTH`     | `1` | A depth of 0 is the anchor root itself; nothing meaningful to compare. |
| `DEFAULT_DEPTH` | `2` | Top-level + immediate children. Matches the non-recursive scanner's effective coverage. |
| `MAX_DEPTH`     | `4` | Hard cap. Depth 5 on `/x/GITHUBREPO` (859 immediate children, many deep) could yield hundreds of thousands of rows. The cap is a safety belt, not a recommendation. |

## 4. Reused closed status enum (6 elements)

| Status | Meaning |
|---|---|
| `claimed_present` | Directory leaf name appears in at least one extracted index claim. |
| `claimed_missing` | Reserved for top-level scans; never emitted at depth ≥ 1 here. |
| `disk_extra`      | Directory enumerated on disk but no index mentions the leaf name. |
| `refused`         | Defensive record for any Rule #8 path that the walker accidentally entered (should never happen because the walker prunes Rule #8 dirs silently). |
| `skipped`         | Empty / whitespace-only leaf name; permission / unreadable error. |
| `unverifiable`    | Reserved for top-level scans; never emitted at depth ≥ 1 here. |

These six values are closed. The script does not introduce new statuses at the row level.

## 5. Refusal matrix (exit codes)

| Exit | Trigger |
|---|---|
| `0` | Success — dry-run preview printed OR `--run` wrote rows + summary. |
| `2` | Workspace, anchor, or log path resolves under a Rule #8 personal folder. |
| `3` | No `DISK_ANCHORS` resolved on this machine. |
| `4` | `--max-depth` outside the closed range `[1, 4]`. |
| `5` | `--dry-run` and `--run` both passed, OR `--only-anchor` value not on the closed `DISK_ANCHORS` list. |

Targets missing / unreadable are recorded in the summary (and in `anchors_missing`); the tool still exits `0`.

## 6. Append discipline

- **Output**: `INDEX_DELTA_RECURSIVE.log` in the workspace root, opened with `"a"` (append) and `encoding="utf-8"`, never `"w"`. **Separate log file from `INDEX_DELTA.log`** so the two runs can be independently re-audited.
- **One row per visited directory** (depth ≥ 1). Each row carries the walker path, depth, normalized leaf key, status (closed enum), and detail string.
- **One `# run_complete` summary row** at the end of each real run (`WROTE` mode). Includes the by_status histogram AND a `by_depth` histogram (per-depth row counts).
- **Read-only on every master index**. No `os.walk` entry is mutated, created, or removed — `os.walk` only enumerates.
- **Default dry-run**: invoking the script without `--run` prints the histogram and writes nothing.

## 7. What the walker does NOT do

- **Does not follow symlinks** (`os.walk(..., followlinks=False)`).
- **Does not descend into Rule #8 directories** (`os.walk` is pruned in-place).
- **Does not enumerate files** — every row is per-directory; the file count is implicit in the directory count.
- **Does not walk recursively past `--max-depth`** — the in-place prune stops `os.walk` from descent.
- **Does not emit per-file rows.** A 859-child × 100-files-per-child anchor at depth 2 would be 85,900 file rows; the file count is left as a per-depth aggregate in the run summary if needed in the future.
- **Does not change any other artifact on disk.** Only writes `INDEX_DELTA_RECURSIVE.log`.

## 8. Companion surface

| File | Role |
|---|---|
| `INDEX_DELTA_RECURSIVE.py` | The script (closed sets used verbatim, capped recursion, append-only writer). |
| `INDEX_DELTA_RECURSIVE.md` | This document. |
| `INDEX_DELTA_RECURSIVE.log` | Append-only JSONL delta log (one row per visited directory + one summary per real run). |
| `INDEX_DELTA.log` | Sister log written by the non-recursive scanner. The two logs coexist; one run should NOT clobber the other. |
| `TODO_TRACKER.md` | Receives an append-only "Update logged (this turn)" block for the new artifact pair. |

## 9. Untouched prior artifacts

- Every file in `TRACKED_INDEX_FILES` is **read-only** here.
- Every directory under any `DISK_ANCHORS` entry is **read-only** here.
- All prior audit / delta runners (`BACKUP_AUDIT_RUN.ps1`, `ENV_AUDIT_RUN.ps1`, `MCP_QUERY_AUDIT_RUN.py`, `MCP_HOST_HEALTH_RUN.py`, `REALITY_VS_CLAIM_AUDIT.py`, `GAL_INTEGRITY_VERIFY.py`, `INDEX_DELTA_SCANNER.py` + `.md`) are untouched.
- This tool does not generate, replace, or rewrite any prior artifact. It only adds a new pair (`.py` + `.md`) and (on `--run`) appends to one new log.

## 10. How to use

```bash
# 1. Dry-run preview, depth = 2 (default)
python INDEX_DELTA_RECURSIVE.py

# 2. Depth = 3 (deeper walk; row count may grow dramatically)
python INDEX_DELTA_RECURSIVE.py --max-depth 3

# 3. Real run on all 4 anchors at depth 2
python INDEX_DELTA_RECURSIVE.py --run

# 4. Real run on just X:\GITHUBREPO at depth 3
python INDEX_DELTA_RECURSIVE.py --only-anchor "X:\\GITHUBREPO" --max-depth 3 --run
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

No path under any of these folders is read, written, enumerated, traversed, or implied. The list is closed and ordered.
