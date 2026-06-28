# CROSS_TOOL_AGGREGATOR — companion explainer

✅ **COMPLIANCE — ADDITIVE ONLY.** This document describes a *new* tool that
reads pre-existing audit logs in read-only mode. It does not modify, delete,
or replace any prior artifact. Every prior audit-family script + companion
doc + log + TODO_TRACKER row is left untouched.

This is the top-of-family aggregator for the 5-log audit family. Where the
prior tools each consumed ONE source and emitted ONE log, this tool consumes
ALL FIVE of the family's expected logs and emits a single fly-eye view of the
whole family.

## What this tool does

For each of the 5 expected family logs (closed `FAMILY_LOG_FILES` tuple):

1. Opens the log in read-only mode (`"r"` encoding).
2. Parses every JSONL row.
3. Classifies the rows into a single one of the closed 6-element
   `VERDICT_ENUM`:
   - `clean` — only positive statuses, no negatives, no refused
   - `partial` — mix of positives and negatives
   - `divergent` — only negatives, no positives, no refused
   - `refused` — any `refused` rows present (early-exit, highest precedence)
   - `empty` — zero rows (tool ran but wrote nothing)
   - `unverifiable` — only neutral / `unverifiable` / `skipped` rows
4. Emits one ISO-prefixed JSONL row per family log to
   `CROSS_TOOL_AGGREGATOR.log` (with `--run`; default is `--dry-run`).
5. With `--emit-summary` (requires `--run`), also appends a single
   `CROSS_TOOL_AGGREGATOR.md` human-readable digest containing the verdict
   histogram + per-section rollup + Rule #8 footer.

## Closed sets (the only numbers that matter)

| Constant | Members | Cardinality |
|---|---|---|
| `PERSONAL_FOLDERS` | Documents, Downloads, Pictures, Videos, Music, Desktop, OneDrive, ARCHIVE_OLD | **8** (must end `ARCHIVE_OLD`) |
| `FAMILY_LOG_FILES` | REALITY_VS_CLAIM_AUDIT.log, INDEX_DELTA.log, INDEX_DELTA_RECURSIVE.log, MASTER_INDEX_RECONCILER.log, GAL_INTEGRITY_VERIFY.log | **5** |
| `SECTION_ENUM` | reality_vs_claim, index_delta_scanner, index_delta_recursive, master_index_reconciler, gal_integrity | **5** |
| `VERDICT_ENUM` | clean, partial, divergent, refused, empty, unverifiable | **6** |
| `_POSITIVE_BY_TOOL` | tool-aware frozensets (verbatim from upstream enums) | 5 entries × variable |
| `_NEGATIVE_BY_TOOL` | tool-aware frozensets (verbatim from upstream enums) | 5 entries × variable |
| `_NEUTRAL_BY_TOOL` | tool-aware frozensets (verbatim from upstream enums) | 5 entries × variable |

The `_POSITIVE_BY_TOOL`/`_NEGATIVE_BY_TOOL`/`_NEUTRAL_BY_TOOL` dictionaries
re-declare each upstream tool's closed enum VERBATIM so this aggregator can
classify rows without an import dependency. **Manual sync required if any
upstream enum changes.** Future refactor: extract `_AUDIT_LIB.py` and have
all tools import from it.

A non-exhaustive mapping of upstream enums to this tool's vocab (see the
script source for the canonical definition):

| Upstream tool | Upstream enum | → positive | → negative | → neutral |
|---|---|---|---|---|
| `REALITY_VS_CLAIM_AUDIT` | `VERIFICATION_ENUM` | `verified_match` | `verified_mismatch`, `verified_partial` | `unverifiable`, `skipped` |
| `INDEX_DELTA_SCANNER` | `DELTA_STATUS_ENUM` | `claimed_present` | `claimed_missing`, `disk_extra` | `unverifiable`, `skipped` |
| `INDEX_DELTA_RECURSIVE` | `DELTA_STATUS_ENUM` (re-declared) | `claimed_present` | `claimed_missing`, `disk_extra` | `unverifiable`, `skipped` |
| `MASTER_INDEX_RECONCILER` | `OUTCOME_ENUM` | `reconciled` | `unreconciled`, `partly_reconciled` | `unverifiable`, `skipped` |
| `GAL_INTEGRITY_VERIFY` | `GAL_STATUS_ENUM` (canonical 7-element tuple from `GAL_INTEGRITY_VERIFY.py`) | `header_ok`, `footer_ok` | `header_mismatch`, `footer_mismatch`, `too_small`, `structure_corrupt` | `skipped` |

## Verdict cascade (precedence top → bottom)

Entries are uniquely labelled so a reader skimming the list can tell them apart
without reading the prose:

1. **`refused`** — if any row has `status="refused"`, short-circuit; this
   verdict fires regardless of positives/negatives counts.
2. **`clean`** — `positives > 0` AND `negatives == 0` AND `refused == 0`.
3. **`partial`** — `positives > 0` AND `negatives > 0`.
4. **`divergent`** — `positives == 0` AND `negatives > 0`.
5. **`empty`** — `row_count == 0`; early-exit BEFORE the cascade. Source log
   file was absent or unreadable, or contained only blank lines.
6. **`unverifiable(malformed-only)`** — every row was tagged `_malformed=True`
   (no parseable status reached `by_status`). Source log was non-empty but
   every JSONL line failed JSON-decode.
7. **`unverifiable(neutral-only)`** — `neutral_c > 0` (no positives,
   negatives, or refused).
8. **`unverifiable(unrecognised-vocab-fallthrough)`** — statuses present but
   none matched any positive/negative/neutral vocab; which means the upstream
   emitted a status we don't know about.

## Refusal matrix

| Exit | Meaning |
|---|---|
| `0` | Success (including `--dry-run` with no writes) |
| `2` | Rule #8 path touched — workspace, expected log path, output path, or any log path resolved to a closed `PERSONAL_FOLDERS` entry |
| `3` | Zero `FAMILY_LOG_FILES` resolved on disk under `--workspace` |
| `4` | Reserved for symmetric enforcement of `--only-section` off-list (current `argparse(choices=...)` guard already enforces this at parse time) |
| `5` | `--dry-run` + `--run` together, or `--emit-summary` without `--run` |

## Output schema (`CROSS_TOOL_AGGREGATOR.log`, one JSONL row per family log)

```json
{
  "ts": "<ISO-8601 UTC timestamp>",
  "tool_id": "CROSS_TOOL_AGGREGATOR",
  "section": "<one of SECTION_ENUM>",
  "source_log": "<FAMILY_LOG_FILES entry>",
  "verdict": "<one of VERDICT_ENUM>",
  "row_count": <int>,
  "malformed_count": <int>,
  "by_status": {"<status>": <count>, ...},
  "detail": "<human-readable reason>",
  "mode": "--run"
}
```

## Compliance footer

🚨 **ADDITIVE ONLY.** Family tool #5+1.

🚨 **Rule #8 — Closed PersonalFolders (8 items, must end with `ARCHIVE_OLD`):**

- Documents
- Downloads
- Pictures
- Videos
- Music
- Desktop
- OneDrive
- ARCHIVE_OLD
