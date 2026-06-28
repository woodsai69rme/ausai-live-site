#!/usr/bin/env python3
"""
CROSS_TOOL_AGGREGATOR.py — top-of-family audit aggregator.

First concrete single-digest consolidator for the 5-log audit family.
Reads each of these logs (closed 5-tuple FAMILY_LOG_FILES):
    - REALITY_VS_CLAIM_AUDIT.log
    - INDEX_DELTA.log
    - INDEX_DELTA_RECURSIVE.log
    - MASTER_INDEX_RECONCILER.log
    - GAL_INTEGRITY_VERIFY.log

For each, classifies the rows into a single one of the closed 6-element
VERDICT_ENUM = (clean, partial, divergent, refused, empty, unverifiable)
using a tool-aware positive/negative/neutral status vocabulary.

Appends one ISO-prefixed JSONL row per family log to CROSS_TOOL_AGGREGATOR.log
(--run only; --dry-run is the default and never writes).
With --emit-summary, additionally appends a CROSS_TOOL_AGGREGATOR.md
human-readable digest.

Refusal matrix:
    0  - success (incl. dry-run)
    2  - Rule #8 path touched (workspace, expected log, or output path)
    3  - no FAMILY_LOG_FILES resolved on disk
    4  - --only-section value not on closed list (defensive only; choices=
         argparse guard already enforces this for us, kept here for symmetry)
    5  - contradictory flags (--dry-run + --run, or --emit-summary without --run)

🚨 ADDITIVE ONLY.  Never delete. Never replace. Never rewrite prior scripts.
   Closed sets + closed refusal matrix are documented in CROSS_TOOL_AGGREGATOR.md.
"""
from __future__ import annotations

import argparse
import datetime
import json
import os
import sys


# =====================================================================
# CLOSED SETS  (the only numbers that matter — see companion doc)
# =====================================================================

PERSONAL_FOLDERS = (
    "Documents", "Downloads", "Pictures", "Videos", "Music", "Desktop",
    "OneDrive", "ARCHIVE_OLD",
)
# 8 items MUST end with ARCHIVE_OLD. Rule #8 fence.

FAMILY_LOG_FILES = (
    "REALITY_VS_CLAIM_AUDIT.log",
    "INDEX_DELTA.log",
    "INDEX_DELTA_RECURSIVE.log",
    "MASTER_INDEX_RECONCILER.log",
    "GAL_INTEGRITY_VERIFY.log",
)
# 5 items - closed list of expected family logs.

SECTION_ENUM = (
    "reality_vs_claim",
    "index_delta_scanner",
    "index_delta_recursive",
    "master_index_reconciler",
    "gal_integrity",
)
# 5 items - one per family log.

VERDICT_ENUM = (
    "clean", "partial", "divergent", "refused", "empty", "unverifiable",
)
# 6 items - closed verdict set.

# Cross-walk: which family log belongs to which section.
_LOG_TO_SECTION = {
    "REALITY_VS_CLAIM_AUDIT.log":    "reality_vs_claim",
    "INDEX_DELTA.log":                "index_delta_scanner",
    "INDEX_DELTA_RECURSIVE.log":      "index_delta_recursive",
    "MASTER_INDEX_RECONCILER.log":    "master_index_reconciler",
    "GAL_INTEGRITY_VERIFY.log":       "gal_integrity",
}

# Per-tool positive / negative / neutral status vocab for verdict
# classification. Re-declared VERBATIM from each upstream tool's own enum
# (manual sync required if any upstream enum changes).
_POSITIVE_BY_TOOL = {
    "REALITY_VS_CLAIM_AUDIT.log":     frozenset({"verified_match"}),
    "INDEX_DELTA.log":                 frozenset({"claimed_present"}),
    "INDEX_DELTA_RECURSIVE.log":      frozenset({"claimed_present"}),
    "MASTER_INDEX_RECONCILER.log":     frozenset({"reconciled"}),
    # GAL_STATUS_ENUM is the canonical 7-element tuple from GAL_INTEGRITY_VERIFY.py:
    # header_ok / footer_ok -- the header/footer probes matched; positive.
    "GAL_INTEGRITY_VERIFY.log":        frozenset({"header_ok", "footer_ok"}),
}
_NEGATIVE_BY_TOOL = {
    "REALITY_VS_CLAIM_AUDIT.log":     frozenset({"verified_mismatch", "verified_partial"}),
    "INDEX_DELTA.log":                 frozenset({"claimed_missing", "disk_extra"}),
    "INDEX_DELTA_RECURSIVE.log":      frozenset({"claimed_missing", "disk_extra"}),
    "MASTER_INDEX_RECONCILER.log":     frozenset({"unreconciled", "partly_reconciled"}),
    # GAL_STATUS_ENUM is the canonical 7-element tuple from GAL_INTEGRITY_VERIFY.py:
    # header_mismatch / footer_mismatch -- probe failures;
    # too_small -- archive below MIN_BYTES (likely truncated or stub);
    # structure_corrupt -- length-prefix walk hit an impossible offset.
    "GAL_INTEGRITY_VERIFY.log":        frozenset({
        "header_mismatch", "footer_mismatch", "too_small", "structure_corrupt",
    }),
}
_NEUTRAL_BY_TOOL = {
    "REALITY_VS_CLAIM_AUDIT.log":     frozenset({"unverifiable", "skipped"}),
    "INDEX_DELTA.log":                 frozenset({"unverifiable", "skipped"}),
    "INDEX_DELTA_RECURSIVE.log":      frozenset({"unverifiable", "skipped"}),
    "MASTER_INDEX_RECONCILER.log":     frozenset({"unverifiable", "skipped"}),
    # GAL_STATUS_ENUM uses "skipped" only; "unverifiable" is not part of the
    # canonical GAL enum, so the neutral set for GAL is just {"skipped"}.
    "GAL_INTEGRITY_VERIFY.log":        frozenset({"skipped"}),
}

OUTPUT_LOG = "CROSS_TOOL_AGGREGATOR.log"
SUMMARY_MD = "CROSS_TOOL_AGGREGATOR.md"


# =====================================================================
# RULE #8 -- personal-folder refusal
# =====================================================================

def is_in_personal(path: str) -> bool:
    """True iff `path` lives under (or is itself) any PERSONAL_FOLDERS name.

    Collapsed suffix / segment pattern: any segment of the normalised
    (forward-slash, upper-case) path matching a closed folder name matches.
    """
    if not path:
        return False
    abs_norm = path.replace("\\", "/").upper()
    segments_norm = set(abs_norm.split("/"))
    for fol in PERSONAL_FOLDERS:
        if fol.upper() in segments_norm:
            return True
    for fol in PERSONAL_FOLDERS:
        if abs_norm.endswith("/" + fol.upper()):
            return True
    return False


# =====================================================================
# LOG READING (read-only on existing master logs)
# =====================================================================

def read_log(path: str) -> list:
    """Read JSONL rows. Returns [] on absence / Rule #8 / read error.

    Note: malformed rows (json.JSONDecodeError) are tagged with an internal-only
    sentinel dict ``{"_malformed": True}``. This sentinel is NOT upstream JSONL;
    it is set by this aggregator so ``classify_log`` can count and surface
    malformed rows distinctly in the verdict cascade. Upstream tools never emit
    rows with a ``_malformed`` key.
    """
    if not path:
        return []
    if is_in_personal(path):
        return []
    if not os.path.isfile(path):
        return []
    rows = []
    try:
        with open(path, "r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    rows.append(json.loads(line))
                except json.JSONDecodeError:
                    # Malformed row -- counted as malformed, not classified.
                    rows.append({"_malformed": True})
    except OSError:
        return []
    return rows


def classify_log(log_name: str, rows: list) -> dict:
    """Classify one log into (verdict, by_status, row_count, malformed, detail)."""
    if not rows:
        return {
            "verdict": "empty", "by_status": {},
            "row_count": 0, "malformed": 0,
            "detail": "0 rows",
        }

    malformed = 0
    by_status: dict = {}
    for row in rows:
        if row.get("_malformed"):
            malformed += 1
            continue
        st = row.get("status")
        if not isinstance(st, str):
            malformed += 1
            continue
        by_status[st] = by_status.get(st, 0) + 1

    pos_vocab = _POSITIVE_BY_TOOL.get(log_name, frozenset())
    neg_vocab = _NEGATIVE_BY_TOOL.get(log_name, frozenset())
    neutral_vocab = _NEUTRAL_BY_TOOL.get(log_name, frozenset())

    positives = sum(c for st, c in by_status.items() if st in pos_vocab)
    negatives = sum(c for st, c in by_status.items() if st in neg_vocab)
    refused_c = by_status.get("refused", 0)
    neutral_c  = sum(c for st, c in by_status.items() if st in neutral_vocab)

    # Verdict cascade (precedence top -> bottom):
    #   refused          first -- a refused row short-circuits
    #   clean            positives > 0, negatives == 0, refused == 0
    #   partial          positives > 0, negatives > 0
    #   divergent        positives == 0, negatives > 0
    #   empty            (no rows at all -- handled above)
    #   malformed_only   every row was `_malformed=True` (no parseable status)
    #   unverifiable     neutral_c > 0 (no positives, negatives, refused)
    #   unverifiable     truly-unrecognised vocab -> fallthrough
    if refused_c > 0:
        verdict = "refused"
        detail = f"{refused_c} refused statuses"
    elif positives > 0 and negatives == 0:
        verdict = "clean"
        detail = f"{positives} positive / 0 negative"
    elif positives > 0 and negatives > 0:
        verdict = "partial"
        detail = f"{positives} positive / {negatives} negative"
    elif positives == 0 and negatives > 0:
        verdict = "divergent"
        detail = f"0 positive / {negatives} negative"
    elif malformed > 0:
        # Every row was malformed; no parseable status reached by_status. This
        # is distinct from the unrecognised-vocab fall-through (which never
        # fires if by_status is empty but rows are uncountable as malformed).
        verdict = "unverifiable"
        detail = f"all {malformed} rows malformed (no parseable statuses)"
    elif neutral_c > 0:
        verdict = "unverifiable"
        detail = f"{neutral_c} unverifiable/skipped (no positive/negative data)"
    else:
        verdict = "unverifiable"
        detail = f"unrecognised statuses only: {sorted(by_status.keys())}"

    return {
        "verdict": verdict,
        "by_status": by_status,
        "row_count": len(rows),
        "malformed": malformed,
        "detail": detail,
    }


# =====================================================================
# APPEND-ONLY WRITERS
# =====================================================================

def append_aggregator_row(workspace: str, row: dict) -> None:
    """Append one ISO-prefixed JSONL row to CROSS_TOOL_AGGREGATOR.log."""
    log_path = os.path.join(workspace, OUTPUT_LOG)
    if is_in_personal(log_path):
        raise SystemExit(2)  # defense in depth
    ts = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    payload = {"ts": ts, **row}
    line = json.dumps(payload, ensure_ascii=False, sort_keys=True)
    with open(log_path, "a", encoding="utf-8", newline="\n") as fh:
        fh.write(line + "\n")


def append_summary(workspace: str, sections: list) -> None:
    """Append a CROSS_TOOL_AGGREGATOR.md human-readable digest."""
    md_path = os.path.join(workspace, SUMMARY_MD)
    if is_in_personal(md_path):
        raise SystemExit(2)

    now = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    by_verdict: dict = {}
    for sec in sections:
        v = sec["verdict"]
        by_verdict[v] = by_verdict.get(v, 0) + 1

    lines: list = []
    lines.append(f"# Cross-Tool Audit Aggregator -- digest as of {now}")
    lines.append("")
    lines.append("## Verdict histogram")
    lines.append("")
    lines.append("| verdict | count |")
    lines.append("|---|---|")
    for h in VERDICT_ENUM:
        lines.append(f"| {h} | {by_verdict.get(h, 0)} |")
    lines.append("")
    lines.append("## Section rollup")
    lines.append("")
    lines.append("| section | source_log | verdict | row_count | malformed | detail |")
    lines.append("|---|---|---|---|---|---|")
    for sec in sections:
        lines.append(
            f"| {sec['section']} | `{sec['log_name']}` | "
            f"{sec['verdict']} | {sec['row_count']} | {sec['malformed']} | "
            f"{sec['detail']} |"
        )
    lines.append("")
    lines.append("## Compliance footer")
    lines.append("")
    lines.append(
        f"Rule #8 -- closed PERSONAL_FOLDERS "
        f"({len(PERSONAL_FOLDERS)} items ending ARCHIVE_OLD):"
    )
    for fol in PERSONAL_FOLDERS:
        lines.append(f"- {fol}")
    lines.append("")

    body = "\n".join(lines)
    with open(md_path, "a", encoding="utf-8", newline="\n") as fh:
        fh.write(body + "\n")


# =====================================================================
# DRIVER
# =====================================================================

def main() -> int:
    raw_argv = sys.argv[1:]

    parser = argparse.ArgumentParser(
        description=(
            "CROSS_TOOL_AGGREGATOR -- reads 5 family logs, classifies each "
            "into a closed 6-element VERDICT_ENUM."
        )
    )
    parser.add_argument(
        "--workspace", default=".",
        help="Directory containing the family logs (default: current dir).",
    )
    parser.add_argument(
        "--dry-run", dest="dry_run", action="store_true", default=True,
        help="(default) Print classification only; never write.",
    )
    parser.add_argument(
        "--run", dest="dry_run", action="store_false",
        help="Actually append CROSS_TOOL_AGGREGATOR.log rows.",
    )
    parser.add_argument(
        "--emit-summary", action="store_true",
        help="With --run, additionally append CROSS_TOOL_AGGREGATOR.md.",
    )
    parser.add_argument(
        "--only-section", default=None, choices=SECTION_ENUM,
        help="Process only this section (one of SECTION_ENUM).",
    )
    args = parser.parse_args()

    # --- Refusal matrix -------------------------------------------------

    # 2: Rule #8 path touched.
    if is_in_personal(args.workspace):
        print(
            f"REFUSED: workspace '{args.workspace}' is a Rule #8 path (exit 2)",
            file=sys.stderr,
        )
        return 2
    if is_in_personal(OUTPUT_LOG) or is_in_personal(SUMMARY_MD):
        print("REFUSED: output path is on Rule #8 (exit 2)", file=sys.stderr)
        return 2

    # 5: contradictory flags.
    if "--dry-run" in raw_argv and "--run" in raw_argv:
        print(
            "REFUSED: --dry-run and --run are mutually exclusive (exit 5)",
            file=sys.stderr,
        )
        return 5
    if "--emit-summary" in raw_argv and "--run" not in raw_argv:
        print(
            "REFUSED: --emit-summary requires --run (exit 5)",
            file=sys.stderr,
        )
        return 5

    # --- Locate family logs ---------------------------------------------

    target_logs = list(FAMILY_LOG_FILES)
    if args.only_section:
        target_logs = [
            log_name for log_name, sec in _LOG_TO_SECTION.items()
            if sec == args.only_section
        ]

    sections = []
    for log_name in FAMILY_LOG_FILES:
        if log_name not in target_logs:
            continue
        log_path = os.path.join(args.workspace, log_name)
        sec_label = _LOG_TO_SECTION[log_name]

        if is_in_personal(log_path):
            sections.append({
                "log_name": log_name,
                "section": sec_label,
                "verdict": "refused",
                "by_status": {},
                "row_count": 0,
                "malformed": 0,
                "detail": "Rule #8 path refused",
            })
            continue

        rows = read_log(log_path)
        cls = classify_log(log_name, rows)
        sections.append({
            "log_name": log_name,
            "section": sec_label,
            **cls,
        })

    # --- 3: no source files resolved ------------------------------------

    on_disk = [
        log_name for log_name in target_logs
        if os.path.isfile(os.path.join(args.workspace, log_name))
    ]
    if not on_disk:
        print(
            f"REFUSED: no FAMILY_LOG_FILES resolved under "
            f"'{args.workspace}' (exit 3)", file=sys.stderr,
        )
        return 3

    # --- Emit (or dry-run print) ----------------------------------------

    histogram_lines = [
        f"section: {sec['section']} log: {sec['log_name']} "
        f"verdict: {sec['verdict']} rows: {sec['row_count']} "
        f"malformed: {sec['malformed']} detail: {sec['detail']}"
        for sec in sections
    ]

    if args.dry_run:
        print("CROSS_TOOL_AGGREGATOR -- DRY-RUN (no writes):")
        for line in histogram_lines:
            print(f"  {line}")
        print(
            f"  total_sections={len(sections)} "
            f"on_disk_files={len(on_disk)} "
            f"missing_files={len(target_logs) - len(on_disk)}"
        )
        return 0

    # --run: write rows + (optional) summary.
    for sec in sections:
        row = {
            "tool_id": "CROSS_TOOL_AGGREGATOR",
            "section": sec["section"],
            "source_log": sec["log_name"],
            "verdict": sec["verdict"],
            "row_count": sec["row_count"],
            "malformed_count": sec["malformed"],
            "by_status": sec["by_status"],
            "detail": sec["detail"],
            "mode": "--run",
        }
        append_aggregator_row(args.workspace, row)

    if args.emit_summary:
        append_summary(args.workspace, sections)

    for line in histogram_lines:
        print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
