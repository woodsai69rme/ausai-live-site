#!/usr/bin/env python3
"""
INDEX_DELTA_SCANNER.py
======================

First concrete master-index-vs-disk **delta** scanner.

Purpose
-------
Compare the *named* repo / project claims found in the project's master-index
markdown files against the *actually-present* entries under a closed set of
disk anchors, then emit an append-only delta report. This is the automation
that closes the cross-reference gap named in
``COMPREHENSIVE_PROJECT_REPORT.md``: the master indexes claim dozens of repos
and projects that are not on disk, while the disk contains dozens of entries
the indexes never mention.

What it actually does
---------------------
1. Reads each declared ``TRACKED_INDEX_FILES`` entry via
   ``open(path, "r", encoding="utf-8")`` -- read-only. Refuses any path under
   Rule #8.
2. Walks each ``DISK_ANCHORS`` directory via a non-recursive one-level list
   of immediate children (asymmetric: indexes describe projects/repos at
   folder level, not inside).
3. Extracts candidate leaf names from each index using a closed regex set
   (``EXTRACTION_PATTERNS``):
     - ``backticked_name``     -- ``some-repo``
     - ``bullet_listed_name``  -- "- Some Project (description)"
     - ``keyed_name``          -- "Repository: foo-bar" / "Project: baz"
4. For each ``(claim, anchor)`` pair, attempts a case-insensitive existence
   check on disk (anchored at the anchor's parent + ``\\<claim>``).
5. For each ``(disk_entry, anchor)`` pair, searches the closed
   ``TRACKED_INDEX_FILES`` list for the leaf name; if no index mentions it,
   it is recorded as ``disk_extra``.
6. Emits one ISO-prefixed JSONL row per ``(claim, anchor)`` pair AND one
   row per ``(disk_entry, anchor)`` pair to ``INDEX_DELTA.log``
   (append-only, ``"a"``, UTF-8).
7. Refuses any path under Rule #8 with exit 2.

Output delta categories (closed, 6 elements)
---------------------------------------------
- ``claimed_present``   -- name appears in an index AND on disk under anchor
- ``claimed_missing``   -- name appears in an index BUT NOT on disk
- ``disk_extra``        -- name appears on disk BUT not in any tracked index
- ``refused``           -- claim / disk_entry resolves under Rule #8
- ``skipped``           -- non-numeric / malformed / unreadable
- ``unverifiable``      -- no anchor resolvable for the claim

CLI
---
    # default = dry-run (preview histogram, do not write)
    python INDEX_DELTA_SCANNER.py
    # write INDEX_DELTA.log
    python INDEX_DELTA_SCANNER.py --run
    # scan only one master index
    python INDEX_DELTA_SCANNER.py --only MASTER_INDEX.md

Refusal matrix (exit codes)
---------------------------
- 0   success (dry-run preview OR --run wrote rows + summary)
- 2   workspace, anchor, or log path resolves under Rule #8
- 3   a tracked index file is missing on disk (counted in summary)
- 4   a tracked index file is unreadable (counted in summary)
- 5   --dry-run and --run both passed

Disclaimer
----------
This is a *name-level* cross-reference. It is intentionally a closed,
greedy, and slightly noisy heuristic -- it over-reports in both directions
rather than risk missing a real delta. It is not a substitute for an exact
declarative manifest; it is the audit that surfaces the gap before anyone
goes to the trouble of building a manifest.

Compliance
-----------
ADDITIVE ONLY. Does NOT modify, replace, or delete any tracked master index,
master report, or prior script. Writes only ``INDEX_DELTA.log``. Refuses any
path under Rule #8 (Documents, Downloads, Pictures, Videos, Music, Desktop,
OneDrive, ARCHIVE_OLD).
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import re
import sys
from collections.abc import Iterator

# ============================================================================
# Rule #8 -- Personal folder fence (8-item closed list, ending ARCHIVE_OLD)
# ============================================================================
PERSONAL_FOLDERS = (
    "Documents",
    "Downloads",
    "Pictures",
    "Videos",
    "Music",
    "Desktop",
    "OneDrive",
    "ARCHIVE_OLD",
)

# ============================================================================
# Closed target set: master indexes whose contents we audit
# ============================================================================
TRACKED_INDEX_FILES = (
    "MASTER_INDEX.md",
    "MASTER_PROJECT_CATALOG_2026.md",
    "IMPERIAL_PROJECT_INDEX.md",
    "THE_OMNI_PORT_AND_TOOL_REGISTER_2026.md",
    "ULTIMATE_KNOWLEDGE_AND_QA_CODEX.md",
    "MASTER_ROOT_INDEX.md",
    "GRAND_INDEX_2026.md",
    "MASTER_ENCYCLOPEDIA_AI_2026.md",
    "MASTER_SYSTEM_RECORD_2026.md",
    "MASTER_GUIDE_EVERY_OPTION_ULTRA_DETAILED.md",
)

# ============================================================================
# Closed disk-anchor set: directories whose immediate children we check
# ============================================================================
DISK_ANCHORS = (
    r"X:\GITHUBREPO",
    r"X:\githrepo",
    r"X:\03_PROJECTS",
    r"C:\Users\karma\03_PROJECTS",
)

# ============================================================================
# Closed extraction-regex set (3-element)
#   Each regex captures the leaf name into group 1.
# ============================================================================
EXTRACTION_PATTERNS = (
    (re.compile(r"`([A-Za-z0-9._\-]{2,64})`"), "backticked_name"),
    (re.compile(r"^\s*[-*]\s+([A-Za-z0-9._\- ]{2,80})(?:\s*[\(:\u2014\-].*)?$",
                re.MULTILINE), "bullet_listed_name"),
    (re.compile(r"(?i)(?:repository|project|repo)\s*:\s*([A-Za-z0-9._\-]{2,64})"),
     "keyed_name"),
)

# Canonical leaf-name normalizer (strip whitespace, take last path component,
# drop parentheticals, lowercase for compare-only).
_NAME_TRIM_RE = re.compile(r"\s*[\(:].*$")
_WS_RE = re.compile(r"\s+")

# ============================================================================
# Closed delta status enum (6 elements)
# ============================================================================
DELTA_STATUS_ENUM = (
    "claimed_present",
    "claimed_missing",
    "disk_extra",
    "refused",
    "skipped",
    "unverifiable",
)

# ============================================================================
# Paths produced by this tool (additive only)
# ============================================================================
THIS_TOOL = "INDEX_DELTA_SCANNER.py"
LOG_FILE_NAME = "INDEX_DELTA.log"


# ============================================================================
# Rule #8 fence (collapsed suffix + segment pattern)
# ============================================================================
def is_in_personal(path: str) -> bool:
    """Return True iff *path* falls under any of the 8 Rule #8 folders."""
    norm = path.replace("\\", "/").rstrip("/")
    for pf in PERSONAL_FOLDERS:
        suffix = "/" + pf
        if norm.endswith(suffix) or (norm + "/").__contains__(suffix + "/"):
            return True
    return False


def normalize_path(path: str) -> str:
    """Translate common spellings into something os.path can use."""
    p = path.strip().strip("`'\"")
    if not p:
        return p
    if re.match(r"^[A-Za-z]:[\\/]", p):
        return p.replace("/", "\\")
    m = re.match(r"^/([a-zA-Z])/(.*)$", p)
    if m:
        drive = m.group(1).upper()
        rest = m.group(2).replace("/", "\\")
        return f"{drive}:\\{rest}"
    return p


# ============================================================================
# Index file reader (read-only)
# ============================================================================
def read_index(path: str) -> str | None:
    """Return file contents (UTF-8) or None if missing / unreadable.

    Refuses to follow any path that resolves under Rule #8.
    """
    if is_in_personal(path):
        return None
    if not os.path.isfile(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return fh.read()
    except (OSError, UnicodeDecodeError):
        return None


# ============================================================================
# Name normalizer (closed logic)
# ============================================================================
def normalize_name(raw: str) -> str:
    """Collapse *raw* into a comparable leaf-name string.

    Strips whitespace, drops parenthetical suffixes, takes the last path
    component, and lowercases the result. The compare key is invariant
    under case and minor whitespace differences.
    """
    s = _WS_RE.sub(" ", raw).strip()
    s = _NAME_TRIM_RE.sub("", s)
    # Last path component (handles `a/b/c`-style names)
    if "/" in s or "\\" in s:
        s = re.split(r"[\\/]", s)[-1]
    return s.lower().strip(" ._-").rstrip(".git")


# ============================================================================
# Name extractor (closed regex set)
# ============================================================================
def extract_names(text: str, source_file: str) -> list[dict]:
    """Extract candidate names from *text* using EXTRACTION_PATTERNS."""
    out: list[dict] = []
    seen_keys: set[str] = set()
    for pattern, label in EXTRACTION_PATTERNS:
        for m in pattern.finditer(text):
            raw = m.group(1).strip()
            key = normalize_name(raw)
            if not key or key in seen_keys:
                continue
            seen_keys.add(key)
            out.append({
                "source": source_file,
                "offset": m.start(),
                "pattern_label": label,
                "raw_name": raw,
                "normalized_key": key,
            })
    return out


# ============================================================================
# Disk walker (non-recursive, one level only)
# ============================================================================
def list_anchor(anchor: str) -> list[dict]:
    """Return one record per immediate child of *anchor*.

    Records have ``normalized_key`` for fast comparison with extracted names.
    """
    anchor_path = normalize_path(anchor)
    if is_in_personal(anchor_path):
        return []
    if not os.path.isdir(anchor_path):
        return []
    out: list[dict] = []
    try:
        entries = os.listdir(anchor_path)
    except (OSError, PermissionError):
        return []
    for name in entries:
        full = os.path.join(anchor_path, name)
        out.append({
            "anchor": anchor_path,
            "leaf": name,
            "full_path": full,
            "normalized_key": normalize_name(name),
            "is_dir": os.path.isdir(full),
        })
    return out


# ============================================================================
# Delta computer (closed logic)
# ============================================================================
def compute_deltas(extracted: list[dict], disk: list[dict]) -> list[dict]:
    """Return per-row records for every (claim, anchor) and
    every (disk_entry, anchor) pair."""
    rows: list[dict] = []

    # Group disk entries by anchor
    by_anchor: dict[str, list[dict]] = {}
    for d in disk:
        by_anchor.setdefault(d["anchor"], []).append(d)

    # Build a per-anchor lookup set for fast claimed_present / claimed_missing
    # classification. Disk entries are case-insensitive.
    present_index: dict[str, set[str]] = {}
    for anchor, entries in by_anchor.items():
        present_index[anchor] = {e["normalized_key"] for e in entries if e["normalized_key"]}

    # 1) For every extracted claim, classify against each anchor
    for claim in extracted:
        key = claim["normalized_key"]
        if any(is_in_personal(os.path.join(a, key)) for a in by_anchor):
            rows.append({
                "source": claim["source"],
                "side": "claim",
                "anchor": "",
                "name": claim["raw_name"],
                "normalized_key": key,
                "status": "refused",
                "detail": "claim resolves under Rule #8",
            })
            continue
        any_anchor_present = False
        any_anchor_used = False
        for anchor in by_anchor:
            any_anchor_used = True
            if key in present_index[anchor]:
                any_anchor_present = True
                rows.append({
                    "source": claim["source"],
                    "side": "claim",
                    "anchor": anchor,
                    "name": claim["raw_name"],
                    "normalized_key": key,
                    "status": "claimed_present",
                    "detail": f"present at {anchor}\\{key}",
                })
        if any_anchor_used and not any_anchor_present:
            # Only emit ONE claimed_missing row per (claim, name), not one
            # per anchor -- that is the symmetric counterpart to a single
            # disk_extra row below.
            rows.append({
                "source": claim["source"],
                "side": "claim",
                "anchor": "",
                "name": claim["raw_name"],
                "normalized_key": key,
                "status": "claimed_missing",
                "detail": ("present in index but absent from every tracked disk anchor; "
                           f"checked {len(by_anchor)} anchors"),
            })
        if not any_anchor_used:
            rows.append({
                "source": claim["source"],
                "side": "claim",
                "anchor": "",
                "name": claim["raw_name"],
                "normalized_key": key,
                "status": "unverifiable",
                "detail": "no DISK_ANCHORS path resolves on this machine",
            })

    # 2) For every disk entry, classify against every index
    # Build a per-name set of which indexes mention it.
    mentioned_in: dict[str, set[str]] = {}
    for claim in extracted:
        mentioned_in.setdefault(claim["normalized_key"], set()).add(claim["source"])

    for anchor, entries in by_anchor.items():
        for entry in entries:
            key = entry["normalized_key"]
            if not key:
                rows.append({
                    "source": "",
                    "side": "disk",
                    "anchor": anchor,
                    "name": entry["leaf"],
                    "normalized_key": key,
                    "status": "skipped",
                    "detail": "empty / whitespace-only leaf name",
                })
                continue
            if is_in_personal(entry["full_path"]):
                rows.append({
                    "source": "",
                    "side": "disk",
                    "anchor": anchor,
                    "name": entry["leaf"],
                    "normalized_key": key,
                    "status": "refused",
                    "detail": "disk entry resolves under Rule #8",
                })
                continue
            if key not in mentioned_in:
                rows.append({
                    "source": "",
                    "side": "disk",
                    "anchor": anchor,
                    "name": entry["leaf"],
                    "normalized_key": key,
                    "status": "disk_extra",
                    "detail": "on disk but not mentioned in any tracked index",
                })
    return rows


# ============================================================================
# Audit-row writer (append-only)
# ============================================================================
def append_audit_row(log_path: str, row: dict) -> None:
    """Append one ISO-prefixed JSON line to *log_path*."""
    if is_in_personal(log_path):
        raise RuntimeError(f"refusing Rule #8 path for log: {log_path}")
    line = json.dumps(row, ensure_ascii=False, sort_keys=True)
    with open(log_path, "a", encoding="utf-8", newline="\n") as fh:
        fh.write(_dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds") + " ")
        fh.write(line + "\n")
        fh.flush()


# ============================================================================
# Runner
# ============================================================================
def run(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog=THIS_TOOL,
        description="Compute master-index vs disk delta (additive only)",
    )
    parser.add_argument("--dry-run", action="store_true",
                        help="Preview histogram without writing (DEFAULT if --run absent)")
    parser.add_argument("--run", action="store_true",
                        help="Append rows to INDEX_DELTA.log")
    parser.add_argument("--only", default=None,
                        help="Audit only this one master index file")
    parser.add_argument("--workspace", default=os.getcwd(),
                        help="Workspace root for resolving relative paths")
    args = parser.parse_args(argv)

    workspace = os.path.abspath(args.workspace)
    if is_in_personal(workspace):
        print(f"REFUSED: workspace {workspace} is under a Rule #8 folder", file=sys.stderr)
        return 2

    targets = list(TRACKED_INDEX_FILES)
    if args.only:
        if args.only not in TRACKED_INDEX_FILES:
            print(f"REFUSED: {args.only} is not on the closed TRACKED_INDEX_FILES list",
                  file=sys.stderr)
            return 5
        targets = [args.only]

    if args.dry_run and args.run:
        print("REFUSED: --dry-run and --run are mutually exclusive", file=sys.stderr)
        return 5

    # Resolve anchors and refuse any Rule #8 anchor early
    resolved_anchors: list[str] = []
    for a in DISK_ANCHORS:
        np = normalize_path(a)
        if is_in_personal(np):
            print(f"REFUSED: anchor {np} is under a Rule #8 folder", file=sys.stderr)
            return 2
        resolved_anchors.append(np)

    log_path = os.path.join(workspace, LOG_FILE_NAME)
    if is_in_personal(log_path):
        print(f"REFUSED: log path {log_path} is under a Rule #8 folder", file=sys.stderr)
        return 2

    summary = {
        "tool": THIS_TOOL,
        "started_utc": _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds"),
        "mode": "WROTE" if args.run else "DRY-RUN",
        "targets_scanned": [],
        "targets_missing": [],
        "targets_unreadable": [],
        "anchors_resolved": [],
        "anchors_missing": [],
        "names_extracted": 0,
        "disk_entries_observed": 0,
        "by_status": {s: 0 for s in DELTA_STATUS_ENUM},
        "personal_folder_refusals": 0,
        "exited_cleanly": True,
    }

    # 1) Read each index, run extraction
    extracted: list[dict] = []
    for name in targets:
        full = os.path.join(workspace, name)
        if is_in_personal(full):
            print(f"REFUSED: {name} resolves under Rule #8 ({full})", file=sys.stderr)
            return 2
        if not os.path.isfile(full):
            summary["targets_missing"].append(name)
            continue
        text = read_index(full)
        if text is None:
            summary["targets_unreadable"].append(name)
            continue
        summary["targets_scanned"].append(name)
        names = extract_names(text, name)
        extracted.extend(names)

    summary["names_extracted"] = len(extracted)

    # 2) List each disk anchor
    disk: list[dict] = []
    for anchor in resolved_anchors:
        entries = list_anchor(anchor)
        if entries:
            summary["anchors_resolved"].append(anchor)
        else:
            summary["anchors_missing"].append(anchor)
        disk.extend(entries)
    summary["disk_entries_observed"] = len(disk)

    # 3) Compute deltas
    rows = compute_deltas(extracted, disk)
    for r in rows:
        status = r["status"]
        if status not in DELTA_STATUS_ENUM:
            status = "skipped"
        summary["by_status"][status] += 1
        if status == "refused":
            summary["personal_folder_refusals"] += 1

    print(f"# {THIS_TOOL} -- mode: {summary['mode']}")
    print(f"# workspace: {workspace}")
    print(f"# targets scanned: {len(summary['targets_scanned'])}")
    print(f"# targets missing: {len(summary['targets_missing'])}")
    print(f"# targets unreadable: {len(summary['targets_unreadable'])}")
    print(f"# anchors resolved: {len(summary['anchors_resolved'])}")
    print(f"# anchors missing: {len(summary['anchors_missing'])}")
    print(f"# names extracted: {summary['names_extracted']}")
    print(f"# disk entries observed: {summary['disk_entries_observed']}")
    for s in DELTA_STATUS_ENUM:
        print(f"# by_status[{s}]: {summary['by_status'][s]}")
    print(f"# personal_folder_refusals: {summary['personal_folder_refusals']}")

    if args.run:
        for row in rows:
            append_audit_row(log_path, row)
        summary["finished_utc"] = _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds")
        append_audit_row(log_path, {"event": "run_complete", **summary})
        print(f"# wrote {len(rows)} delta rows + 1 run_complete summary to {log_path}")
    else:
        print("# dry-run: nothing written. Pass --run to append delta rows.")

    return 0


if __name__ == "__main__":
    sys.exit(run())
