# ✅ COMPLIANCE — ADDITIVE ONLY

`MASTER_INDEX_RECONCILER.py` is a new artifact. It NEVER deletes, replaces,
rewrites, or modifies any prior file. It reads only the closed
`SOURCE_LOG_FILES` tuple, parses JSONL rows defensively, and appends ONE row
per source log to **`MASTER_INDEX_RECONCILER.log`** (a new file). Optionally
(with `--emit-summary --run`) it appends a human-readable
**`MASTER_INDEX_RECONCILED.md`** (also new). No prior artifact is touched.

The tool closes the last concrete gap in the audit-runner family: until this
turn, each sister runner (`REALITY_VS_CLAIM_AUDIT`, `INDEX_DELTA_SCANNER`,
`INDEX_DELTA_RECURSIVE`) emitted its own JSONL log independently. There was no
single ground-truth view. This tool is `cat`-friendly: one row per source log,
one status field per row, one outcome field per row — human-glanceable.

---

## What it does

Reads each of the three closed-source sister-tool JSONL audit logs,
classifies the rows by `status`, and emits one consolidated row per source
log whose `outcome` field is a single word from the closed 6-element
`OUTCOME_ENUM`. The reconciliation vocabulary:

| source log had… | → `outcome` |
|---|---|
| only positive statuses (`verified_match`, `claimed_present`) | `reconciled` |
| both positive and negative statuses | `partly_reconciled` |
| only negative statuses | `unreconciled` |
| at least one `refused` row (Rule #8 lockout signal) | `refused` |
| file missing or empty | `skipped` |
| all rows malformed JSON | `unverifiable` |

If you ran each upstream runner with `--run` once, this tool now produces a
single ground-truth "where does the master-index-vs-disk divergence actually
stand" view.

---

## Closed sets (do not extend at runtime — manual sync required)

These are the same shape as `REALITY_VS_CLAIM_AUDIT.py`,
`INDEX_DELTA_SCANNER.py`, and `INDEX_DELTA_RECURSIVE.py`. The constants are
duplicated, not imported, because no shared module exists today (see also the
same note in `INDEX_DELTA_RECURSIVE.md` §2 — manual sync only).

| tuple | size | contents |
|---|---|---|
| `PERSONAL_FOLDERS` | 8 | `Documents`, `Downloads`, `Pictures`, `Videos`, `Music`, `Desktop`, `OneDrive`, `ARCHIVE_OLD` |
| `SOURCE_LOG_FILES` | 3 | `REALITY_VS_CLAIM_AUDIT.log`, `INDEX_DELTA.log`, `INDEX_DELTA_RECURSIVE.log` |
| `OUTCOME_ENUM` | 6 | `reconciled`, `partly_reconciled`, `unreconciled`, `refused`, `skipped`, `unverifiable` |

Adding a new sister runner requires:
1. Writing the new runner script + .md
2. Updating the `SOURCE_LOG_FILES` tuple in this script AND in any future
   `_INDEX_DELTA_LIB.py` extraction (future refactor, NOT done in this turn)

No tuple is mutated at runtime.

---

## Refusal matrix (exit codes)

| exit | reason |
|---|---|
| `0` | success — source logs parsed, summary printed, optional log row(s) appended |
| `2` | Rule #8 refusal — workspace, source log filename, or summary target resolves into a `PERSONAL_FOLDERS` segment |
| `3` | none of `SOURCE_LOG_FILES` exist on disk under the workspace; nothing to reconcile |
| `5` | contradictory flags: `--dry-run` + `--run` together, or `--emit-summary` without `--run` |

There is no exit code `4` at present — reserved for future use (e.g. if a
`--emit-summary` path is refused post-parse, distinct from exit `2`).

---

## I/O contract (append-only)

| file | mode | content |
|---|---|---|
| `MASTER_INDEX_RECONCILER.log` | append `"a"` (`encoding="utf-8"`, `newline="\n"`) | one ISO-prefixed JSONL row per source log per run |
| `MASTER_INDEX_RECONCILED.md` | append `"a"` (`encoding="utf-8"`, `newline="\n"`) | optional human-readable summary; only appended when `--emit-summary --run` is passed |

Both files start non-existent (this is the first turn that creates them).
Both are opened only with `"a"` mode and rejection-on-Rule-#8 — never `"w"`,
`"x"`, `os.remove`, `shutil.rmtree`, or `Set-Content`.

---

## Usage

```bash
# Default: parse + print only
python MASTER_INDEX_RECONCILER.py

# Default again (explicit dry-run)
python MASTER_INDEX_RECONCILER.py --dry-run

# Persist: one row per source log appended to MASTER_INDEX_RECONCILER.log
python MASTER_INDEX_RECONCILER.py --run

# Persist AND append a human-readable summary
python MASTER_INDEX_RECONCILER.py --run --emit-summary

# Any of the following exits 5 (contradictory flags):
python MASTER_INDEX_RECONCILER.py --dry-run --run
python MASTER_INDEX_RECONCILER.py --emit-summary
```

---

## Output schema (one `MASTER_INDEX_RECONCILER.log` row)

Each line is `YYYY-MM-DDTHH:MM:SS | {json}` and the JSON object is exactly:

```json
{
  "log_file": "REALITY_VS_CLAIM_AUDIT.log",
  "row_count": 234,
  "outcome": "partly_reconciled",
  "by_status": { "verified_match": 12, "verified_mismatch": 222 },
  "evidence": "12 positive / 222 negative",
  "malformed_count": 0
}
```

Field definitions:

| field | type | meaning |
|---|---|---|
| `log_file` | str | one of `SOURCE_LOG_FILES` (the source log filename) |
| `row_count` | int | number of well-formed JSONL rows parsed out of the source log |
| `outcome` | str | one of `OUTCOME_ENUM` (closed 6-element set) |
| `by_status` | dict{str: int} | status histogram over the row_count rows |
| `evidence` | str | short human-readable summary of the by_status counts |
| `malformed_count` | int | number of lines that failed JSON parsing (excluded from by_status) |

---

## Companion files

| file | role |
|---|---|
| `MASTER_INDEX_RECONCILER.py` | the runner (this file describes it) |
| `MASTER_INDEX_RECONCILER.md` | this companion explainer |
| `MASTER_INDEX_RECONCILER.log` | new append-only per-source-log reconciliation rows (created on first `--run`) |
| `MASTER_INDEX_RECONCILED.md` | new append-only human-readable summary (created on first `--run --emit-summary`) |

Existing sister tools, sister logs, master indexes, and Rule #8 artefacts
remain untouched.

---

## Future refactors (advertised, NOT done in this turn)

* Extract `_AUDIT_LIB.py` shared between `MASTER_INDEX_RECONCILER.py`,
  `INDEX_DELTA_SCANNER.py`, `INDEX_DELTA_RECURSIVE.py`,
  `REALITY_VS_CLAIM_AUDIT.py`, and `GAL_INTEGRITY_VERIFY.py`. Out of scope
  for this turn's additive-only audit pattern (it would be a 6th new file).
* Add a `--since TIMESTAMP` flag to filter rows by ISO prefix before
  reconciliation. Out of scope (new flag, new behaviour, written to logs).
* Track per-source-log `last_seen_at` so the summary can flag stale source
  logs (e.g. a source log not appended to in >24 h).

These would each require a future additive turn (new file or new flag, never
a rewrite of an existing tool).

---

## ✅ COMPLIANCE FOOTER

* This file (`MASTER_INDEX_RECONCILER.md`) is a NEW artifact. Created this turn.
* `MASTER_INDEX_RECONCILER.py` is a NEW artifact. Created this turn.
* `MASTER_INDEX_RECONCILER.log` will be a NEW append-only file on first `--run`.
* `MASTER_INDEX_RECONCILED.md` will be a NEW append-only file on first `--run --emit-summary`.
* No prior artifact was modified, replaced, or deleted.
* No path under the 8-item `PERSONAL_FOLDERS` tuple was read, written, or
  even mentioned in any code path:
  `Documents`, `Downloads`, `Pictures`, `Videos`, `Music`, `Desktop`,
  `OneDrive`, `ARCHIVE_OLD`.
* Every writer opened with `"a"` mode, `encoding="utf-8"`, `newline="\n"`.
  No `"w"`, `"x"`, `os.remove`, `shutil.rmtree`, `Set-Content`,
  `Clear-Content`, or `Remove-Item` anywhere in this tool.
