#!/usr/bin/env python3
"""
MASTER_INDEX_RECONCILER.py

Purpose
-------
First concrete consolidation tool for the audit-runner family. Reads the three
closed-source sister-tool JSONL logs (REALITY_VS_CLAIM_AUDIT.log, INDEX_DELTA.log,
INDEX_DELTA_RECURSIVE.log), parses each into status histograms, and emits one
ISO-prefixed row per source log to MASTER_INDEX_RECONCILER.log.

This tool is the natural next step after the three audit runners: now that
each runner produces append-only JSONL evidence, this tool aggregates them
into a single ground-truth view of master-index-vs-disk divergence.

Contract
--------
* ADDITIVE ONLY: never deletes, never replaces, never rewrites any prior file.
* Reads ONLY the closed 3-element SOURCE_LOG_FILES tuple. No other log path
  is ever read.
* Emits ONLY statuses from the closed 6-element OUTCOME_ENUM.
* Refuses any path under the closed 8-item PERSONAL_FOLDERS tuple (Rule #8).
* Refuses contradictory flags.
* Default behavior is --dry-run: parse, summarises to stdout, writes nothing.
* --run requires explicit confirmation; persists one row per source log to
  MASTER_INDEX_RECONCILER.log.
* --emit-summary (only valid with --run) appends a human-readable
  MASTER_INDEX_RECONCILED.md summarising the same rows.

Exit codes
----------
  0  success
  2  Rule #8 refusal (workspace, source log, or summary target)
  3  no SOURCE_LOG_FILES present in workspace (nothing to reconcile)
  4  --emit-summary target refused
  5  --dry-run and --run together, or other contradictory flags
"""

# =============================================================================
# COMPLIANCE: ADDITIVE ONLY.
# This tool never deletes, replaces, or rewrites any existing artifact.
# It reads only the closed SOURCE_LOG_FILES tuple and appends only to the
# single MASTER_INDEX_RECONCILER.log file. Never touches Rule #8 folders.
# =============================================================================

import argparse
import datetime as _dt
import json
import os
import re
import sys


# ---- Closed sets (do not extend at runtime) ---------------------------------

# 8-item PERSONAL_FOLDERS tuple ending in ARCHIVE_OLD (Rule #8).
# Self-protection fence: any path matching these segments is rejected.
PERSONAL_FOLDERS = (
    "Documents", "Downloads", "Pictures", "Videos", "Music", "Desktop",
    "OneDrive", "ARCHIVE_OLD",
)

# Closed 3-element SOURCE_LOG_FILES tuple. These are the ONLY logs this tool
# ever reads. Adding a new sister runner requires updating this tuple AND its
# own tool file (no implicit expansion).
SOURCE_LOG_FILES = (
    "REALITY_VS_CLAIM_AUDIT.log",
    "INDEX_DELTA.log",
    "INDEX_DELTA_RECURSIVE.log",
)

# Closed 6-element OUTCOME_ENUM tuple. Every emitted row's "outcome" field
# MUST be one of these six strings. Defensive status clamping guarantees it.
OUTCOME_ENUM = (
    "reconciled",         # only positive statuses in the source log
    "partly_reconciled",  # both positive and negative statuses present
    "unreconciled",       # only negative statuses in the source log
    "refused",            # source log contained at least one refused row
    "skipped",            # source log missing or empty; nothing to read
    "unverifiable",       # source log rows had no parseable status field
)

# Statuses treated as "positive" by the reconciler.
_POSITIVE_STATUSES = frozenset({"verified_match", "claimed_present"})

# Statuses treated as "negative" by the reconciler.
_NEGATIVE_STATUSES = frozenset({
    "verified_mismatch", "claimed_missing", "disk_extra",
    "verified_partial", "unverifiable",
})


# ---- Hardcoded safe roots --------------------------------------------------

WORKSPACE_ROOT = r"C:\Users\karma"
LOG_FILENAME = "MASTER_INDEX_RECONCILER.log"
SUMMARY_FILENAME = "MASTER_INDEX_RECONCILED.md"


# ---- Path safety helpers ----------------------------------------------------

def is_in_personal(raw_path: str) -> bool:
    """True iff raw_path resolves into any PERSONAL_FOLDERS directory.

    Uses a collapsed suffix / segment matcher so it catches both child
    directories and segments whose name ends in a personal-folder token.
    Handles C:\\, X:\\, /x/, /c/ forms.
    """
    if not raw_path:
        return False
    s = raw_path.replace("/", os.sep).replace("\\", os.sep)
    s_lower = s.lower()
    parts = [p for p in s_lower.split(os.sep) if p]
    for f in PERSONAL_FOLDERS:
        f_lower = f.lower()
        for p in parts:
            if p == f_lower or p.endswith(f_lower):
                return True
    return False


def normalize_path(raw_path: str) -> str:
    """Best-effort path normalisation. Handles C:\\, X:\\, /x/, /c/ forms."""
    if not raw_path:
        return raw_path
    s = raw_path.strip().strip('"').strip("'")
    m = re.match(r"^/x/(.*)$", s)
    if m:
        return os.path.join("X:\\", m.group(1).replace("/", os.sep))
    m = re.match(r"^/c/(.*)$", s)
    if m:
        return os.path.join("C:\\", m.group(1).replace("/", os.sep))
    return s


# ---- Log parsing helpers ----------------------------------------------------

_ISO_PREFIX_RE = re.compile(r"^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\s*\|\s*)(.*)$")


def parse_iso_prefix(line: str) -> str:
    """Strips the leading 'YYYY-MM-DDTHH:MM:SS | ' ISO prefix if present."""
    m = _ISO_PREFIX_RE.match(line)
    if m:
        return m.group(2)
    return line


def read_log_rows(path: str):
    """Reads a JSONL audit log defensively.

    Returns a list of dicts (parsed rows). Returns [] if missing or unreadable.
    Malformed JSONL lines are counted in 'malformed_count' but excluded from
    the returned list; the caller decides how to surface that.
    """
    result = {"rows": [], "malformed_count": 0}
    if not path or not os.path.isfile(path):
        return result
    try:
        with open(path, "r", encoding="utf-8") as fh:
            for line in fh:
                stripped = parse_iso_prefix(line.strip())
                if not stripped:
                    continue
                try:
                    obj = json.loads(stripped)
                    if isinstance(obj, dict):
                        result["rows"].append(obj)
                except json.JSONDecodeError:
                    result["malformed_count"] += 1
    except OSError:
        result["rows"] = []
    return result


# ---- Reconciliation logic --------------------------------------------------

def compute_reconciliation(log_filename: str, parsed):
    """Computes a reconciliation dict for one source log.

    Returns: { log_file, row_count, outcome, by_status, evidence,
               malformed_count }. 'outcome' is a closed OUTCOME_ENUM value.
    """
    rows = parsed["rows"]
    malformed = parsed["malformed_count"]

    by_status = {}
    for r in rows:
        s = r.get("status", "<missing>")
        by_status[s] = by_status.get(s, 0) + 1

    row_count = len(rows)

    if row_count == 0 and malformed == 0:
        outcome = "skipped"
        evidence = "log missing or empty"
    elif row_count == 0 and malformed > 0:
        outcome = "unverifiable"
        evidence = f"all {malformed} rows malformed"
    elif "refused" in by_status:
        outcome = "refused"
        evidence = (
            f"{by_status['refused']} refused rows present; lockout signal"
        )
    else:
        positives = sum(v for k, v in by_status.items() if k in _POSITIVE_STATUSES)
        negatives = sum(v for k, v in by_status.items() if k in _NEGATIVE_STATUSES)
        if positives > 0 and negatives == 0:
            outcome = "reconciled"
            evidence = f"{positives} positive / 0 negative"
        elif positives > 0 and negatives > 0:
            outcome = "partly_reconciled"
            evidence = f"{positives} positive / {negatives} negative"
        elif positives == 0 and negatives > 0:
            outcome = "unreconciled"
            evidence = f"0 positive / {negatives} negative"
        elif "skipped" in by_status:
            # source log had rows, but every row's status was skipped
            # (no positive or negative data). Treat as `skipped`, not
            # `unverifiable` — the upstream tools DID write, just with
            # benign status. (Refusal of genuine unrecognised vocab still
            # falls through to `unverifiable` below.)
            outcome = "skipped"
            evidence = (
                f"{by_status['skipped']} skipped rows "
                f"(no positive/negative data)"
            )
        else:
            # statuses present but none matched the positive/negative vocab
            # AND none were `skipped` — genuinely unrecognised vocab.
            outcome = "unverifiable"
            evidence = f"unrecognised statuses only: {sorted(by_status.keys())}"

    return {
        "log_file": log_filename,
        "row_count": row_count,
        "outcome": outcome,
        "by_status": by_status,
        "evidence": evidence,
        "malformed_count": malformed,
    }


# ---- I/O helpers (append-only) ----------------------------------------------

def now_iso() -> str:
    """Returns YYYY-MM-DDTHH:MM:SS timestamp."""
    return _dt.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")


def append_audit_row(log_path: str, row):
    """Append-only writer. Raises on Rule #8 path.

    Always uses open(path, \"a\", encoding=\"utf-8\", newline=\"\\n\").
    Each emitted line is prefixed with now_iso() and the JSON-serialised row.
    """
    if is_in_personal(log_path):
        raise PermissionError(
            f"Rule #8 refusal: refusing to write log under personal folder: "
            f"{log_path}"
        )
    parent = os.path.dirname(log_path)
    if parent and is_in_personal(parent):
        raise PermissionError(
            f"Rule #8 refusal: refusing to create log under personal folder: "
            f"{parent}"
        )
    with open(log_path, "a", encoding="utf-8", newline="\n") as fh:
        fh.write(
            f"{now_iso()} | "
            f"{json.dumps(row, ensure_ascii=False, sort_keys=True)}\n"
        )


def emit_summary_md(reconciliations, target_path: str):
    """Appends a single human-readable MASTER_INDEX_RECONCILED.md summary.

    Refuses to write under Rule #8 path. Always appends — never truncates.
    """
    if is_in_personal(target_path):
        raise PermissionError(
            f"Rule #8 refusal: refusing summary under personal folder: "
            f"{target_path}"
        )
    with open(target_path, "a", encoding="utf-8", newline="\n") as fh:
        fh.write(f"# MASTER_INDEX_RECONCILER summary\n\n")
        fh.write(f"Generated {now_iso()}\n")
        fh.write(f"Workspace: {WORKSPACE_ROOT}\n")
        fh.write(f"Source logs analysed (closed 3-element SOURCE_LOG_FILES): "
                 f"{', '.join(SOURCE_LOG_FILES)}\n\n")
        for r in reconciliations:
            fh.write(f"## {r['log_file']}\n\n")
            fh.write(f"- outcome: `{r['outcome']}`\n")
            fh.write(f"- row_count: `{r['row_count']}`\n")
            fh.write(f"- malformed_count: `{r['malformed_count']}`\n")
            fh.write(f"- evidence: {r['evidence']}\n\n")
            if r["by_status"]:
                fh.write("| status | count |\n|---|---|\n")
                for k, v in sorted(r["by_status"].items()):
                    fh.write(f"| `{k}` | {v} |\n")
                fh.write("\n")
            else:
                fh.write("(no parseable rows)\n\n")
        fh.write("---\n\n")


# ---- Main runner ------------------------------------------------------------

def _check_paths():
    """Returns 2 if any required path would land under Rule #8; else None."""
    if is_in_personal(WORKSPACE_ROOT):
        return 2
    for log_name in SOURCE_LOG_FILES:
        full = os.path.join(WORKSPACE_ROOT, log_name)
        if is_in_personal(full):
            return 2
    summary_target = os.path.join(WORKSPACE_ROOT, SUMMARY_FILENAME)
    if is_in_personal(summary_target):
        return 2
    return None


def run(args):
    """Main runner. Closed-set, refusal matrix, append-only."""
    refusal = _check_paths()
    if refusal is not None:
        print(
            f"refusing Rule #8 path under PERSONAL_FOLDERS: {WORKSPACE_ROOT}",
            file=sys.stderr,
        )
        return 2

    # ---- 5: contradictory flags ----------------------------------------
    if args.dry_run and args.run:
        print(
            "contradictory flags: --dry-run and --run are mutually exclusive",
            file=sys.stderr,
        )
        return 5
    if args.emit_summary and args.dry_run:
        print(
            "contradictory flags: --emit-summary requires --run; add --run or "
            "drop --emit-summary",
            file=sys.stderr,
        )
        return 5
    if args.emit_summary and not args.run:
        print(
            "contradictory flags: --emit-summary requires --run",
            file=sys.stderr,
        )
        return 5

    should_write = args.run and not args.dry_run
    emit_summary = args.emit_summary and should_write

    # ---- 3: no SOURCE_LOG_FILES present ---------------------------------
    any_present = any(
        os.path.isfile(os.path.join(WORKSPACE_ROOT, n)) for n in SOURCE_LOG_FILES
    )
    if not any_present:
        print(
            f"no SOURCE_LOG_FILES present in {WORKSPACE_ROOT}; expected any of: "
            f"{', '.join(SOURCE_LOG_FILES)}. Run the upstream runners with "
            f"--run first.",
            file=sys.stderr,
        )
        return 3

    # ---- Main loop: per source log --------------------------------------
    reconciliations = []
    for log_name in SOURCE_LOG_FILES:
        full = os.path.join(WORKSPACE_ROOT, log_name)
        parsed = read_log_rows(full)
        recon = compute_reconciliation(log_name, parsed)
        reconciliations.append(recon)

    # ---- Always print human summary to stdout --------------------------
    print(f"MASTER_INDEX_RECONCILER — {now_iso()}")
    print(f"workspace: {WORKSPACE_ROOT}")
    print(
        f"{len(reconciliations)} source logs analysed "
        f"(closed 3-element SOURCE_LOG_FILES)\n"
    )
    for r in reconciliations:
        print(
            f"[{r['outcome']}] {r['log_file']}: "
            f"{r['row_count']} rows; malformed={r['malformed_count']}"
        )
        print(f"  evidence: {r['evidence']}")
        if r["by_status"]:
            bs_str = ", ".join(
                f"{k}={v}" for k, v in sorted(r["by_status"].items())
            )
            print(f"  by_status: {{{bs_str}}}")
        print()

    # ---- Optionally persist --------------------------------------------
    if should_write:
        log_path = os.path.join(WORKSPACE_ROOT, LOG_FILENAME)
        for r in reconciliations:
            append_audit_row(log_path, r)
        print(f"wrote append-only log: {log_path}")
        if emit_summary:
            summary_target = os.path.join(WORKSPACE_ROOT, SUMMARY_FILENAME)
            emit_summary_md(reconciliations, summary_target)
            print(f"appended human-readable summary: {summary_target}")
    else:
        print(
            "dry-run: no files written. re-run with --run to persist. "
            "add --emit-summary (requires --run) to also append a "
            "MASTER_INDEX_RECONCILED.md."
        )

    return 0


def main():
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument(
        "--dry-run", action="store_true",
        help="Default. Parse source logs and print summary; write nothing.",
    )
    p.add_argument(
        "--run", action="store_true",
        help="Persist one row per source log to MASTER_INDEX_RECONCILER.log.",
    )
    p.add_argument(
        "--emit-summary", action="store_true",
        help="Also append a human-readable MASTER_INDEX_RECONCILED.md "
             "(requires --run).",
    )
    args = p.parse_args()
    sys.exit(run(args))


if __name__ == "__main__":
    main()
