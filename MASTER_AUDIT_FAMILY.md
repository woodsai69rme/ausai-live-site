# Master Audit Family — Cross-Tool Documentation

✅ **COMPLIANCE — ADDITIVE ONLY.** This document does not modify, delete, or
replace any prior artifact. It is a read-only cross-reference tying together
the audit family built around the master-index-vs-disk divergence problem
first surfaced in `COMPREHENSIVE_PROJECT_REPORT.md` (the 859-vs-277 gap).

This document closes the documentation gap surfaced during the family
build: each tool has a companion explainer, but the **family as a whole**
(no single document describing the data flow / closed-set dependencies /
refusal matrices for all 5+1 audit tools) had to be reconstructed from each
individual tool's README + companion doc. **This file is now the
single-source-of-truth cross-reference for the family.**

## Family inventory

| # | Tool | Companion doc | Output log | Reads | Consumed by |
|---|---|---|---|---|---|
| 1 | `REALITY_VS_CLAIM_AUDIT.py` | `REALITY_VS_CLAIM_AUDIT.md` | `REALITY_VS_CLAIM_AUDIT.log` | Closed 10-item `TRACKED_INDEX_FILES` (read-only); disk | `CROSS_TOOL_AGGREGATOR` |
| 2a | `INDEX_DELTA_SCANNER.py` | `INDEX_DELTA_SCANNER.md` | `INDEX_DELTA.log` | Same closed `TRACKED_INDEX_FILES` + closed 4-tuple `DISK_ANCHORS`; non-recursive one-level walk of each disk anchor | `MASTER_INDEX_RECONCILER`, `CROSS_TOOL_AGGREGATOR` |
| 2b | `INDEX_DELTA_RECURSIVE.py` | `INDEX_DELTA_RECURSIVE.md` | `INDEX_DELTA_RECURSIVE.log` | Same closed sets as 2a (re-declared verbatim) + new closed `[MIN_DEPTH=1, DEFAULT_DEPTH=2, MAX_DEPTH=4]` range; recursive `os.walk` pruned in place | `MASTER_INDEX_RECONCILER`, `CROSS_TOOL_AGGREGATOR` |
| 3 | `MASTER_INDEX_RECONCILER.py` | `MASTER_INDEX_RECONCILER.md` | `MASTER_INDEX_RECONCILER.log` (plus `--emit-summary` → `MASTER_INDEX_RECONCILED.md`) | Reads ONLY the closed 3-tuple `SOURCE_LOG_FILES` = (Step 1 log, Step 2a log, Step 2b log) | `CROSS_TOOL_AGGREGATOR` |
| 4 | `GAL_INTEGRITY_VERIFY.py` | `GAL_INTEGRITY_VERIFY.md` | `GAL_INTEGRITY_VERIFY.log` | Walks `X:\AETHER_CORE_SYSTEM`; closed 7-element `GAL_STATUS_ENUM`; header/footer/size/length-prefix walk probes | `CROSS_TOOL_AGGREGATOR` |
| 5 | `CROSS_TOOL_AGGREGATOR.py` | `CROSS_TOOL_AGGREGATOR.md` | `CROSS_TOOL_AGGREGATOR.log` (+`--emit-summary` → `CROSS_TOOL_AGGREGATOR.md`) | Reads ALL 5 family logs in the closed 5-tuple `FAMILY_LOG_FILES` | (top of family — terminal digest) |
| 6 | `DOTDIR_CATALOG_RUN.py` | `DOTDIR_CATALOG_RUN.md` | `DOTDIR_CATALOG.log` (+`--emit-summary` → `DOTDIR_CATALOG.md`) | Walks the workspace root one level deep; classifies each direct-child dotdir against `WELL_KNOWN_NOISE_DIRS` / `CLOSED_POSSIBLY_LEGIT`. **Not currently consumed by the family aggregator** (sibling under ENH-H15) — it produces workspace-hygiene evidence that operates upstream of the master-index-vs-disk narrative. | (sibling tool — dashboard-feed candidate only) |

## Data flow

```
┌───────────────────────────────────────────────────────────────┐
│ Sources of truth (all read-only)                              │
│  - TRACKED_INDEX_FILES  (10-item closed tuple of master idx)  │
│  - DISK_ANCHORS         (4-item closed tuple of repo roots)  │
│  - AETHER_CORE_SYSTEM   (X:\AETHER_CORE_SYSTEM, ~133 GB)      │
└───────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌───────────────────────────────────────────────────────────────┐
│ Step 1-4 audit-log producers (each emits 1 JSONL log)        │
│                                                               │
│  REALITY_VS_CLAIM_AUDIT ──► REALITY_VS_CLAIM_AUDIT.log        │
│  INDEX_DELTA_SCANNER    ──► INDEX_DELTA.log                    │
│  INDEX_DELTA_RECURSIVE  ──► INDEX_DELTA_RECURSIVE.log          │
│  MASTER_INDEX_RECONCILER──► MASTER_INDEX_RECONCILER.log        │
│                           └──► MASTER_INDEX_RECONCILED.md     │
│                              (--emit-summary)                 │
│  GAL_INTEGRITY_VERIFY   ──► GAL_INTEGRITY_VERIFY.log          │
└───────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌───────────────────────────────────────────────────────────────┐
│ Step 5 top-of-family aggregator                               │
│  CROSS_TOOL_AGGREGATOR  ──► CROSS_TOOL_AGGREGATOR.log         │
│                           └──► CROSS_TOOL_AGGREGATOR.md      │
│                              (--emit-summary)                 │
└───────────────────────────────────────────────────────────────┘
                              │
                              ▼
                  Single human-readable family digest
                  in CROSS_TOOL_AGGREGATOR.md
```

## Closed-set matrix

Every tool declares its closed enumerations at module level. Cross-tool
dependencies (e.g. `_LOG_TO_SECTION`, `_POSITIVE_BY_TOOL`,
`_NEGATIVE_BY_TOOL`, `_NEUTRAL_BY_TOOL` in `CROSS_TOOL_AGGREGATOR`)
**re-declare each upstream enum VERBATIM with a manual-sync-required
marker.** Future refactor (out of scope for the additive-only audit
pattern): extract a shared `_AUDIT_LIB.py` module and have all tools
`from _AUDIT_LIB import …` so a single change propagates everywhere.

| Tool | Closed sets | Cardinalities |
|---|---|---|
| `REALITY_VS_CLAIM_AUDIT` | `PERSONAL_FOLDERS` / `TRACKED_INDEX_FILES` / `CLAIM_PATTERNS` / `VERIFICATION_ENUM` | 8 / 10 / 4 / 6 |
| `INDEX_DELTA_SCANNER` | `PERSONAL_FOLDERS` / `TRACKED_INDEX_FILES` / `DISK_ANCHORS` / `EXTRACTION_PATTERNS` / `DELTA_STATUS_ENUM` | 8 / 10 / 4 / 3 / 6 |
| `INDEX_DELTA_RECURSIVE` | (same 5 sets as `INDEX_DELTA_SCANNER`, re-declared verbatim) + new closed `[MIN_DEPTH=1, DEFAULT_DEPTH=2, MAX_DEPTH=4]` triple | 8 / 10 / 4 / 3 / 6 / 3 (depth triple) |
| `MASTER_INDEX_RECONCILER` | `PERSONAL_FOLDERS` / `SOURCE_LOG_FILES` / `OUTCOME_ENUM` | 8 / 3 / 6 |
| `GAL_INTEGRITY_VERIFY` | `PERSONAL_FOLDERS` / `GAL_STATUS_ENUM` / `[HEADER_LEN, FOOTER_LEN]` size constants | 8 / 7 / 2 |
| `CROSS_TOOL_AGGREGATOR` | `PERSONAL_FOLDERS` / `FAMILY_LOG_FILES` / `SECTION_ENUM` / `VERDICT_ENUM` | 8 / 5 / 5 / 6 |
| `DOTDIR_CATALOG_RUN` | `RULE_8_DIRS` / `WELL_KNOWN_NOISE_DIRS` / `CLOSED_POSSIBLY_LEGIT` / `DOTDIR_CATALOG_ENUM` / `TRACKED_DOTDIR_LOGS` / `NOISE_BLOCK_HEADING` / `REFUSAL_EXIT_CODE_MATRIX` | 8 / ~191 (re-declared verbatim) / 9 / 6 / 1 / 1 / 5 | Rhyming sister-tool closed-set shape: `PERSONAL_FOLDERS`-shaped fence (`RULE_8_DIRS`), `WELL_KNOWN_NOISE_DIRS` instead of `TRACKED_INDEX_FILES`, 6-element verdict enum, refusal-matrix is a 5-key dict rather than free-standing booleans. See `DOTDIR_CATALOG_RUN.md` §4.1/§4.2 for the two by-design deviations from the audit-family strict-`.gitignore` pattern. |

## Refusal matrix (collapsed across the family)

Every tool refuses a tightly bounded set of conditions with a fixed exit code.

| Exit | Meaning | Tools that emit |
|---|---|---|
| `0` | Success (incl. `--dry-run` with no writes) | All |
| `2` | Rule #8 path touched (workspace, source, output) | All (PERSONAL_FOLDERS 8-item fence) |
| `3` | No source inputs resolved on disk under `--workspace` | `MASTER_INDEX_RECONCILER`, `CROSS_TOOL_AGGREGATOR` |
| `4` | `--max-depth` outside `[1, 4]` (`INDEX_DELTA_RECURSIVE`-specific) | `INDEX_DELTA_RECURSIVE` |
| `4` | Defensive reservation for off-list `--only-*` (currently `argparse` guard handles it at parse time) | reserved |
| `5` | `--dry-run` + `--run` together, or `--emit-summary` without `--run`, or `--only-*` value not on the closed list | All (except `INDEX_DELTA_RECURSIVE` which uses `4` for depth-bound violations, `5` for `--only-anchor` off-list) |

The split between `4` (depth-bound for `INDEX_DELTA_RECURSIVE` only) and
`5` (off-list `--only-*` for everything else) is intentional: depth-bound
violations have unique semantics distinct from closed-list violations.

## Output paths

| File | Writer(s) | Read by |
|---|---|---|
| `REALITY_VS_CLAIM_AUDIT.log` | `REALITY_VS_CLAIM_AUDIT` (with `--run`) | `CROSS_TOOL_AGGREGATOR` |
| `INDEX_DELTA.log` | `INDEX_DELTA_SCANNER` (with `--run`) | `MASTER_INDEX_RECONCILER`, `CROSS_TOOL_AGGREGATOR` |
| `INDEX_DELTA_RECURSIVE.log` | `INDEX_DELTA_RECURSIVE` (with `--run`) | `MASTER_INDEX_RECONCILER`, `CROSS_TOOL_AGGREGATOR` |
| `MASTER_INDEX_RECONCILER.log` | `MASTER_INDEX_RECONCILER` (with `--run`) | `CROSS_TOOL_AGGREGATOR` |
| `MASTER_INDEX_RECONCILED.md` | `MASTER_INDEX_RECONCILER` (with `--run --emit-summary`) | Humans |
| `GAL_INTEGRITY_VERIFY.log` | `GAL_INTEGRITY_VERIFY` (with `--run`) | `CROSS_TOOL_AGGREGATOR` |
| `CROSS_TOOL_AGGREGATOR.log` | `CROSS_TOOL_AGGREGATOR` (with `--run`) | Terminal JSONL sink for the family |
| `CROSS_TOOL_AGGREGATOR.md` | `CROSS_TOOL_AGGREGATOR` (with `--run --emit-summary`) | Humans — top-of-family digest |
| `DOTDIR_CATALOG.log` | `DOTDIR_CATALOG_RUN` (with `--run`) | (no in-family consumer — sibling workspace-hygiene audit) |
| `DOTDIR_CATALOG.md` | `DOTDIR_CATALOG_RUN` (with `--run --emit-summary`) | Humans — workspace-hygiene digest (output of the dry-run catalog) |

## Workflow contract

To run the family end-to-end against a machine with the master indexes +
disk anchors + `X:\AETHER_CORE_SYSTEM` mounted:

```bash
# Step 0 — workspace hygiene (sibling under ENH-H15; optional pre-step)
python DOTDIR_CATALOG_RUN.py --run --emit-summary

# Step 1 (run once per index refresh)
python REALITY_VS_CLAIM_AUDIT.py --run
python INDEX_DELTA_SCANNER.py --run
python INDEX_DELTA_RECURSIVE.py --run

# Step 2 (after Steps 1, 2a, 2b have produced their logs)
python MASTER_INDEX_RECONCILER.py --run --emit-summary
python GAL_INTEGRITY_VERIFY.py --run

# Step 3 (after ALL 5 family logs exist)
python CROSS_TOOL_AGGREGATOR.py --run --emit-summary
```

> **Note on DOTDIR_CATALOG_RUN placement:** it is positioned as Step 0 because
> it operates on the workspace `C:\Users\karma` (the project root itself),
> while Steps 1–4 operate on disk anchors (`X:\GITHUBREPO` etc.) and
> `X:\AETHER_CORE_SYSTEM`. The two halves of the family have overlapping
> scope concerns but do not chain via log-file exchange; they share only the
> `PERSONAL_FOLDERS`-shaped rule-#8 fence.

**Note on `--emit-summary`:** Only `MASTER_INDEX_RECONCILER` and
`CROSS_TOOL_AGGREGATOR` support `--emit-summary` today (they each produce an
`*.md` digest in addition to the JSONL audit log). The four other family tools
are pure JSONL producers; omitting `--emit-summary` for them is correct.

Every step is **default `--dry-run`** if invoked without `--run`, so a
fresh machine where the upstream logs don't yet exist will not write
anything — instead it'll emit refusal exit `3` (no source resolved) and
print a classification histogram on stdout for human inspection.

## Compliance footer

🚨 **ADDITIVE ONLY.** This family was built one tool at a time with strict
append-only semantics. Every tool opens with `✅ COMPLIANCE — ADDITIVE ONLY`
in its companion doc and closes with the 8-item `PERSONAL_FOLDERS` Rule
#8 footer. `MASTER_AUDIT_FAMILY.md` (this doc) follows the same convention.

🚨 **Rule #8 — Closed PersonalFolders (8 items, must end with `ARCHIVE_OLD`):**

- Documents
- Downloads
- Pictures
- Videos
- Music
- Desktop
- OneDrive
- ARCHIVE_OLD
