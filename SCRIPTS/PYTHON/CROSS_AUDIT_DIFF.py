#!/usr/bin/env python3
"""
CROSS_AUDIT_DIFF.py

First concrete cross-source scanner-diff. Reads two closed sister logs
produced by `INDEX_DELTA_SCANNER.py` (top-level non-recursive walk) and
`INDEX_DELTA_RECURSIVE.py` (depth-bounded recursive walk), groups each
into its (anchor, key) pairs, and surfaces the divergence envelope:

  - keys present at the top-level scanner and absent from the recursive
    scanner at the SAME anchor
  - keys present at the recursive scanner and absent from the top-level
    scanner at the SAME anchor
  - keys present in BOTH scanners at the same anchor but with CONFLICTING
    statuses (claimed_present vs claimed_missing, etc.)
  - per-anchor per-source status histograms so the diff is auditable
    even when no divergences are found

All writes are append-only ISO-prefixed JSONL to CROSS_AUDIT_DIFF.log
(only when --run is supplied). Default is --dry-run, which writes nothing.

Rule #8 fence: PERSONAL_FOLDERS is a closed 8-tuple ending in
ARCHIVE_OLD. is_in_personal() refuses any workspace, pair-source path,
or log path that resolves underneath one of those 8 leaf names; exit 2.

Refusal matrix:
  0  success (one JSONL row per (scanner, anchor) emitted under --run)
  1  internal error (uncaught)
  2  Rule #8 path (workspace / source log / output log)
  3  no source pairs supplied or no pairs resolved on disk
  5  contradictory flags: --dry-run and --run together; or --only-anchor
     value not in closed SOURCE_SCANNER_DIRS reference list

Companion explainer: CROSS_AUDIT_DIFF.md
Sister output log: CROSS_AUDIT_DIFF.log (append under --run)

Baseline sources the diff crosses:

  INDEX_DELTA.log           (written by INDEX_DELTA_SCANNER.py)
  INDEX_DELTA_RECURSIVE.log (written by INDEX_DELTA_RECURSIVE.py)

Both sister logs are read-only on disk; this script never writes to them.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import re
import sys
from typing import Dict, FrozenSet, Iterable, List, Optional, Tuple

# ============================================================================
# Closed sets (must remain closed; if you need a new item, add it here AND
# also document it in CROSS_AUDIT_DIFF.md so the pair stays auditable).
# ============================================================================

PERSONAL_FOLDERS: Tuple[str, ...] = (
    "Documents",
    "Downloads",
    "Pictures",
    "Videos",
    "Music",
    "Desktop",
    "OneDrive",
    "ARCHIVE_OLD",
)

# The two closed sister logs the diff compares. Future sister logs must be
# additively introduced via a sibling script; do not modify this tuple.
SOURCE_PAIR: Tuple[str, ...] = (
    "INDEX_DELTA.log",
    "INDEX_DELTA_RECURSIVE.log",
)

# Closed 6-element SOURCE_DIFF_ENUM. Used for both per-row source attribution
# and for the high-level diff classification rows appended under --run.
SOURCE_DIFF_ENUM: Tuple[str, ...] = (
    "only_in_top_level",
    "only_in_recursive",
    "conflict_both_present",
    "present_both",
    "refused",
    "skipped",
)

# Reference list of scanner-known anchors. Pairs whose keys could resolve
# under any of these are subject to the diff; pairs whose claim-source path
# falls under any other location are still parsed, but rows will carry
# `anchor_is_unverifiable=True` in their detail (see compute_pair_diff).
SOURCE_SCANNER_DIRS: Tuple[str, ...] = (
    "03_PROJECTS",
    "GITHUBREPO",
    # Two architectural placeholders referenced by the audit family but
    # not in INDEX_DELTA_SCANNER's closed 4-element DISK_ANCHORS list —
    # kept here so the diff can also classify rows whose apperance under
    # these directories is suspicious without prematurely expanding the
    # non-recursive scanner's anchor list.
    "01_FOUNDATIONS",
    "02_INFRASTRUCTURE",
)

# ============================================================================
# Rule #8 fence (READ-ONLY is_in_personal checker, collapsed suffix + segment)
# ============================================================================

_WS_RE: "re.Pattern[str]" = re.compile(r"\s+")
_SUFFIX_RE: "re.Pattern[str]" = re.compile(r"\s*\([^)]*\)\s*$")


def _suffix_norm(leaf: str) -> str:
    """Strip parentheticals and trailing whitespace from a leaf name."""
    leaf = _SUFFIX_RE.sub("", leaf)
    return _WS_RE.sub(" ", leaf).strip().lower()


def _segment_norm(value: str) -> str:
    """Lowercase the whole path segment so 'My Docs', 'mydocs', 'my docs'
    collide on the same normalized form."""
    return _WS_RE.sub(" ", value).strip().lower()


def is_in_personal(path: str) -> bool:
    """Return True iff `path` resolves underneath any leaf in PERSONAL_FOLDERS.

    Closed 8-tuple, ends in ARCHIVE_OLD. Detects both collapsed-suffix
    variants ('Documents (old)') and full-segment variants ('Desktop/...').
    """
    if not path:
        return False
    parts = [_segment_norm(p) for p in re.split(r"[\\/]+", path) if p]
    suffix_targets = {_suffix_norm(p) for p in PERSONAL_FOLDERS}
    full_targets = set(parts)
    collapsed_union = suffix_targets | full_targets
    for p in parts:
        for t in collapsed_union:
            if p == t or (t and t in p):
                return True
    return False


# ============================================================================
# JSONL row composer (append-only under --run)
# ============================================================================

def _now_iso() -> str:
    return _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds")


def _columnize_statuses(by_status: Dict[str, int]) -> List[str]:
    return [f"{k}={v}" for k, v in sorted(by_status.items())]


def append_diff_row(
    log_path: str,
    source_a: str,
    source_b: str,
    anchor: Optional[str],
    diff_status: str,
    detail: str,
    keys_only_a: Iterable[str],
    keys_only_b: Iterable[str],
    keys_conflict: Iterable[str],
    by_status: Dict[str, int],
) -> None:
    """Append one ISO-prefixed JSONL row. Refuses if log_path is Rule #8."""
    if is_in_personal(log_path):
        raise RuntimeError(f"Rule #8 refusal (log path): {log_path}")
    if diff_status not in SOURCE_DIFF_ENUM:
        diff_status = "skipped"
    row = {
        "ts": _now_iso(),
        "tool": "CROSS_AUDIT_DIFF",
        "source_a": source_a,
        "source_b": source_b,
        "anchor": anchor,
        "status": diff_status,
        "detail": detail,
        "only_in_a": list(keys_only_a),
        "only_in_b": list(keys_only_b),
        "conflict": list(keys_conflict),
        "by_status": dict(by_status),
        "by_status_columns": _columnize_statuses(by_status),
    }
    line = json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n"
    with open(log_path, "a", encoding="utf-8", newline="\n") as fh:
        fh.write(line)


# ============================================================================
# Sister-log reader (read-only; tolerates malformed lines)
# ============================================================================

def iter_log_rows(log_path: str) -> Iterable[Dict[str, object]]:
    if not os.path.isfile(log_path):
        return iter([])
    def _gen() -> Iterable[Dict[str, object]]:
        # Tolerated shape drift: rows may or may not start with an ISO
        # timestamp; either way, we treat any plain JSON object as a
        # valid sibling-row record. Malformed JSON lines are skipped.
        with open(log_path, "r", encoding="utf-8", newline="\n") as fh:
            for raw in fh:
                s = raw.strip()
                if not s:
                    continue
                try:
                    obj = json.loads(s)
                except json.JSONDecodeError:
                    continue
                yield obj if isinstance(obj, dict) else {}
    return _gen()


# ============================================================================
# Diff computation
# ============================================================================

def _bucket_key(row: Dict[str, object]) -> Tuple[Optional[str], Optional[str]]:
    """Reduce a sister log row to (anchor, leaf_key). Tolerates shape drift
    between INDEX_DELTA (anchor + key) and INDEX_DELTA_RECURSIVE (anchor +
    key + depth)."""
    anchor = row.get("anchor")
    key = row.get("key") or row.get("name") or row.get("claim")
    if anchor is not None and not isinstance(anchor, str):
        anchor = str(anchor)
    if key is not None and not isinstance(key, str):
        key = str(key)
    return (anchor, key)


def _status_for_row(row: Dict[str, object]) -> Optional[str]:
    s = row.get("status")
    if s is None:
        s = row.get("outcome")
    if isinstance(s, str):
        return s
    return None


def gather_pairs(rows: Iterable[Dict[str, object]]) -> Dict[Tuple[Optional[str], Optional[str]], Dict[str, int]]:
    """Group rows by (anchor, key) and tabulate by_status counts."""
    out: Dict[Tuple[Optional[str], Optional[str]], Dict[str, int]] = {}
    for row in rows:
        key = _bucket_key(row)
        if key == (None, None):
            continue
        status = _status_for_row(row)
        if status is None:
            continue
        bucket = out.setdefault(key, {})
        bucket[status] = bucket.get(status, 0) + 1
    return out


def compute_pair_diff(
    pairs_a: Dict[Tuple[Optional[str], Optional[str]], Dict[str, int]],
    pairs_b: Dict[Tuple[Optional[str], Optional[str]], Dict[str, int]],
    only_anchor: Optional[str],
) -> List[Dict[str, object]]:
    """Return one diff row per (anchor, key) over the union of both maps."""
    diffs: List[Dict[str, object]] = []
    all_keys = set(pairs_a.keys()) | set(pairs_b.keys())
    for key in all_keys:
        anchor, leaf = key
        if only_anchor is not None and anchor != only_anchor:
            continue
        bucket_a = pairs_a.get(key, {})
        bucket_b = pairs_b.get(key, {})
        status_a = sorted(bucket_a.keys())
        status_b = sorted(bucket_b.keys())
        if not bucket_a and bucket_b:
            diff_status = "only_in_recursive"
            detail = "absent from top-level scanner; present in recursive scanner"
        elif bucket_a and not bucket_b:
            diff_status = "only_in_top_level"
            detail = "absent from recursive scanner; present in top-level scanner"
        elif status_a == status_b:
            diff_status = "present_both"
            detail = f"statuses agree: {status_a}"
        else:
            diff_status = "conflict_both_present"
            detail = f"top-level calls {status_a}; recursive calls {status_b}"
        anchor_is_unverifiable = (
            anchor is not None
            and not any(part == anchor for part in SOURCE_SCANNER_DIRS)
        )
        if anchor_is_unverifiable:
            detail = f"{detail}; anchor not in SOURCE_SCANNER_DIRS"
        diffs.append({
            "anchor": anchor,
            "key": leaf,
            "status": diff_status,
            "detail": detail,
            "by_status_a": bucket_a,
            "by_status_b": bucket_b,
        })
    diffs.sort(key=lambda d: (d["anchor"] or "", d["key"] or "", d["status"]))
    return diffs


# ============================================================================
# Driver
# ============================================================================

def _resolve_pair_paths(workspace: str) -> Tuple[str, str]:
    """Resolve the two SOURCE_PAIR filenames under `workspace`. Returns
    (path_a, path_b). Each is checked for Rule #8 individually."""
    if is_in_personal(workspace):
        raise RuntimeError(f"Rule #8 refusal (workspace): {workspace}")
    a = os.path.join(workspace, SOURCE_PAIR[0])
    b = os.path.join(workspace, SOURCE_PAIR[1])
    for p in (a, b):
        if is_in_personal(p):
            raise RuntimeError(f"Rule #8 refusal (source log): {p}")
    return (a, b)


def run(args: argparse.Namespace) -> int:
    log_path = os.path.abspath(args.log)
    if is_in_personal(log_path):
        print(f"Refusing: log path resolves under Rule #8 personal folder: {log_path}", file=sys.stderr)
        return 2

    workspace = os.path.abspath(args.workspace)
    if is_in_personal(workspace):
        print(f"Refusing: workspace resolves under Rule #8 personal folder: {workspace}", file=sys.stderr)
        return 2

    path_a, path_b = _resolve_pair_paths(workspace)

    only_anchor = args.only_anchor
    if only_anchor is not None and only_anchor not in SOURCE_SCANNER_DIRS:
        print(
            f"Refusing: --only-anchor={only_anchor!r} is not in closed "
            f"SOURCE_SCANNER_DIRS tuple ({SOURCE_SCANNER_DIRS}).",
            file=sys.stderr,
        )
        return 5

    if not (os.path.isfile(path_a) or os.path.isfile(path_b)):
        print(
            "Refusing: neither SOURCE_PAIR file is present at workspace. "
            f"Expected: {path_a} and/or {path_b}; run the upstream scanners "
            "first (INDEX_DELTA_SCANNER.py / INDEX_DELTA_RECURSIVE.py --run).",
            file=sys.stderr,
        )
        return 3

    rows_a = list(iter_log_rows(path_a))
    rows_b = list(iter_log_rows(path_b))
    if not rows_a and not rows_b:
        print(
            "Refusing: sister logs present but contain zero parseable rows.",
            file=sys.stderr,
        )
        return 3

    pairs_a = gather_pairs(rows_a)
    pairs_b = gather_pairs(rows_b)
    diffs = compute_pair_diff(pairs_a, pairs_b, only_anchor)

    histogram: Dict[str, int] = {k: 0 for k in SOURCE_DIFF_ENUM}
    for d in diffs:
        histogram[d["status"]] = histogram.get(d["status"], 0) + 1

    print(f"=== CROSS_AUDIT_DIFF summary (workspace={workspace}) ===")
    print(f"  source_a rows parsed:        {len(rows_a)}  ({path_a})")
    print(f"  source_b rows parsed:        {len(rows_b)}  ({path_b})")
    print(f"  (anchor,key) buckets in a:   {len(pairs_a)}")
    print(f"  (anchor,key) buckets in b:   {len(pairs_b)}")
    print(f"  diff rows computed:          {len(diffs)}")
    if only_anchor is not None:
        print(f"  only_anchor filter:          {only_anchor}")
    print(f"  source_diff_enum histogram: {dict(sorted(histogram.items()))}")
    print(f"  run mode: {'WRITE' if args.run else 'DRY-RUN (no log write)'}")

    if not args.run:
        return 0

    # Per-(scanner, anchor) summary row: anchors that appear in EITHER
    # side of the pair get a row carrying the scope-level view of the
    # diff histogram so the reconciler can later join on (source_b, anchor).
    anchor_set: set = set()
    for key in set(pairs_a.keys()) | set(pairs_b.keys()):
        anchor_set.add(key[0])
    for anchor in sorted(a for a in anchor_set if a is not None):
        per_anchor = {"present_both": 0, "only_in_top_level": 0,
                      "only_in_recursive": 0, "conflict_both_present": 0,
                      "refused": 0, "skipped": 0}
        for d in diffs:
            if d["anchor"] == anchor:
                per_anchor[d["status"]] = per_anchor.get(d["status"], 0) + 1
        # Emit one row per anchor (representative of `source_b` for join
        # compatibility with MASTER_INDEX_RECONCILER's SOURCE_LOG_FILES list).
        append_diff_row(
            log_path=log_path,
            source_a=SOURCE_PAIR[0],
            source_b=SOURCE_PAIR[1],
            anchor=anchor,
            diff_status=_classify_anchor_view(per_anchor),
            detail=f"per-anchor summary for {anchor}",
            keys_only_a=[d["key"] for d in diffs if d["anchor"] == anchor and d["status"] == "only_in_top_level"],
            keys_only_b=[d["key"] for d in diffs if d["anchor"] == anchor and d["status"] == "only_in_recursive"],
            keys_conflict=[d["key"] for d in diffs if d["anchor"] == anchor and d["status"] == "conflict_both_present"],
            by_status=per_anchor,
        )
    return 0


def _classify_anchor_view(per_anchor: Dict[str, int]) -> str:
    if per_anchor["conflict_both_present"] > 0:
        return "conflict_both_present"
    if per_anchor["only_in_top_level"] > 0 and per_anchor["only_in_recursive"] > 0:
        return "conflict_both_present"
    if per_anchor["only_in_recursive"] > 0 and per_anchor["only_in_top_level"] == 0 and per_anchor["present_both"] == 0:
        return "only_in_recursive"
    if per_anchor["only_in_top_level"] > 0 and per_anchor["only_in_recursive"] == 0 and per_anchor["present_both"] == 0:
        return "only_in_top_level"
    if per_anchor["present_both"] > 0:
        return "present_both"
    return "skipped"


# ============================================================================
# CLI
# ============================================================================

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="CROSS_AUDIT_DIFF",
        description=(
            "First concrete cross-source scanner-diff: "
            f"compares [{SOURCE_PAIR[0]}, {SOURCE_PAIR[1]}] per anchor. "
            "Default --dry-run (writes nothing); --run appends ISO-prefixed "
            "JSONL rows to CROSS_AUDIT_DIFF.log (one per anchor under "
            "the second source for downstream-reconciler join compatibility)."
        ),
    )
    p.add_argument("--workspace", default=".",
                   help="Directory holding INDEX_DELTA.log + INDEX_DELTA_RECURSIVE.log "
                        "(defaults to current working directory).")
    p.add_argument("--log", default="CROSS_AUDIT_DIFF.log",
                   help="Append-only output log path (default: CROSS_AUDIT_DIFF.log).")
    p.add_argument("--dry-run", action="store_true",
                   help="Explicit dry-run signal; default mode is also dry-run.")
    p.add_argument("--run", action="store_true",
                   help="Opt into write mode and emit JSONL rows to --log.")
    p.add_argument("--only-anchor", default=None,
                   help="Restrict the diff to a single anchor; value MUST be "
                        f"in closed SOURCE_SCANNER_DIRS tuple: {SOURCE_SCANNER_DIRS}.")
    return p


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)

    if args.dry_run and args.run:
        print("Refusing: --dry-run and --run together (contradictory).", file=sys.stderr)
        return 5

    try:
        return run(args)
    except RuntimeError as exc:
        print(f"Refusing: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:  # pragma: no cover - defensive catch-all
        print(f"Internal error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
