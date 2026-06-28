# CROSS_AUDIT_DIFF

✅ COMPLIANCE — ADDITIVE ONLY

## 1. What this artifact is

`CROSS_AUDIT_DIFF.py` is the first concrete **cross-source scanner-difference**
generator in the audit family. It reads two closed sister logs already
produced by upstream tools in this family:

| Source log            | Producer                                  | Shape offered                     |
|-----------------------|-------------------------------------------|-----------------------------------|
| `INDEX_DELTA.log`     | `INDEX_DELTA_SCANNER.py`                  | `(anchor, key, status, detail)`   |
| `INDEX_DELTA_RECURSIVE.log` | `INDEX_DELTA_RECURSIVE.py`            | `(anchor, key, depth, status, detail)` |

It groups each sister log by `(anchor, key)` and surfaces four kinds of
divergence between the two scanners over the same disk anchors:

| `SOURCE_DIFF_ENUM` value     | Meaning                                                     |
|------------------------------|-------------------------------------------------------------|
| `present_both`               | both scanners saw the (anchor, key) AND agree on statuses   |
| `conflict_both_present`      | both scanners saw it, but disagreed on status vocab         |
| `only_in_top_level`          | top-level scanner saw it, recursive scanner did not         |
| `only_in_recursive`          | recursive scanner saw it, top-level scanner did not         |
| `refused`                    | reserved (emitted when a row carries a Rule #8 refusal)     |
| `skipped`                    | reserved (emitted when input was unparseable / empty)       |

Under **`--run`**, the script appends ONE ISO-prefixed JSONL row per
`anchor` (joining on `source_b = INDEX_DELTA_RECURSIVE.log`) to
`CROSS_AUDIT_DIFF.log`, so the downstream `MASTER_INDEX_RECONCILER` can
treat this new log as a fourth closed sister log without changes to its
own `SOURCE_LOG_FILES` tuple. (Adding it to the master reconciler is the
natural follow-on; out of scope for this artifact.)

## 2. Why this artifact exists

After the non-recursive scanner and the recursive scanner both touch
the same `DISK_ANCHORS` (`03_PROJECTS`, `GITHUBREPO`, etc.) but at
different depths, the natural question becomes **"where do the two views
disagree?"** This artifact answers that question without re-walking the
disk: it reads the two JSONL outputs and computes their set difference
plus their status-conflict overlap.

## 3. Closed sets (must remain closed)

```python
PERSONAL_FOLDERS      = ("Documents", "Downloads", "Pictures", "Videos",
                         "Music", "Desktop", "OneDrive", "ARCHIVE_OLD")  # 8 items

SOURCE_PAIR           = ("INDEX_DELTA.log",
                         "INDEX_DELTA_RECURSIVE.log")                   # 2 items

SOURCE_DIFF_ENUM      = ("only_in_top_level",
                         "only_in_recursive",
                         "conflict_both_present",
                         "present_both",
                         "refused",
                         "skipped")                                     # 6 items

SOURCE_SCANNER_DIRS   = ("03_PROJECTS",
                         "GITHUBREPO",
                         "01_FOUNDATIONS",
                         "02_INFRASTRUCTURE")                          # 4 items
```

`SOURCE_SCANNER_DIRS` deliberately extends the non-recursive scanner's
own closed 4-element `DISK_ANCHORS` tuple by adding two architectural
placeholders (`01_FOUNDATIONS`, `02_INFRASTRUCTURE`); rows bearing
anchors in those two but not in the non-recursive scanner's anchors
get a `detail` suffix of `"; anchor not in SOURCE_SCANNER_DIRS"` — they
are NOT refused (per the additive-only rule), they are simply
distinguished in the diff so the divergence is visible.

## 4. Refusal matrix

| Exit | Trigger                                                            |
|------|--------------------------------------------------------------------|
| 0    | Success (always returns 0; --run or --dry-run both succeed)       |
| 1    | Internal error (uncaught)                                          |
| 2    | Rule #8 path (workspace, source log path, or output log path)      |
| 3    | No source-pair files present / both empty after parsing           |
| 5    | Contradictory flags: --dry-run + --run; or --only-anchor not in    |
|      | closed SOURCE_SCANNER_DIRS tuple                                   |

## 5. How to use it

```bash
# Default: parse + compute + print summary; no log write
python CROSS_AUDIT_DIFF.py

# Override and append rows to the default log path
python CROSS_AUDIT_DIFF.py --run

# Restrict to a single anchor (must be on closed list)
python CROSS_AUDIT_DIFF.py --run --only-anchor 03_PROJECTS

# Custom log path (anywhere outside Rule #8 folders)
python CROSS_AUDIT_DIFF.py --run --log /tmp/CROSS_AUDIT_DIFF.log
```

## 6. Output shape (under `--run`)

```
ISO_TIMESTAMP  tool=CROSS_AUDIT_DIFF
               source_a=INDEX_DELTA.log
               source_b=INDEX_DELTA_RECURSIVE.log
               anchor=03_PROJECTS (or whichever anchor)
               status=conflict_both_present | only_in_top_level | ...
               detail="..."
               only_in_a=["..."]
               only_in_b=["..."]
               conflict=["..."]
               by_status={ present_both: N, only_in_top_level: N, ... }
```

The script never writes to `INDEX_DELTA.log` or
`INDEX_DELTA_RECURSIVE.log`; it only ever appends to
`CROSS_AUDIT_DIFF.log` (and only when `--run` is passed).

## 7. Follow-ons filed elsewhere

| Follow-on ID  | Description                                                          |
|---------------|----------------------------------------------------------------------|
| ENH-H15.d.1   | Add `CROSS_AUDIT_DIFF.log` to `MASTER_INDEX_RECONCILER.SOURCE_LOG_FILES` tuple (additive audit-family expansion). |

## 8. Rule #8 footer (verbatim)

This artifact refuses to read, write, traverse, mutate, or report on any
path whose leaf name (or collapsed-suffix variant) matches any of the
following 8 closed values:

1. `Documents`
2. `Downloads`
3. `Pictures`
4. `Videos`
5. `Music`
6. `Desktop`
7. `OneDrive`
8. `ARCHIVE_OLD`

END OF DOCUMENT
