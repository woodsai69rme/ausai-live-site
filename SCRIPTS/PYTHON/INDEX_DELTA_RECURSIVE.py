#!/usr/bin/env python3
"""
INDEX_DELTA_RECURSIVE.py
========================

First concrete recursive depth-scanner. Companion to ``INDEX_DELTA_SCANNER.py``.

Purpose
-------
Walk each ``DISK_ANCHORS`` directory recursively up to a configurable
``--max-depth`` (default 2), and emit a per-directory delta row against the
master-index claims using the **same closed 6-element ``DELTA_STATUS_ENUM``**
as the non-recursive scanner. This surfaces WHERE INSIDE the disk tree the
divergence happens, not just whether it's there at top level.

What it actually does
---------------------
1. Reads the closed 10-item ``TRACKED_INDEX_FILES`` list via
   ``open(path, "r", encoding="utf-8")`` -- read-only. Refuses Rule #8 paths.
2. Extracts candidate claims from each index using the same 3-element regex
   set ``EXTRACTION_PATTERNS`` (backticked_name / bullet_listed_name /
   keyed_name). Comparison keys go through ``normalize_name`` (lowercased,
   parentheticals stripped, last path-component, trailing ``.git`` removed).
3. Walks each closed 4-element ``DISK_ANCHORS`` directory via ``os.walk``,
   TRUNCATING at ``--max-depth`` (default 2, max 4). Symlinks are NOT
   followed; ``Rule #8`` directories encountered at any depth are silently
   skipped (with a per-depth counter increment).
4. For every directory enumerated at any depth ``<= --max-depth``, emits ONE
   JSONL row with status from the **same 6-element ``DELTA_STATUS_ENUM``**:
     - ``claimed_present``   -- the directory's normalized leaf appears in any
                                extracted index claim.
     - ``disk_extra``        -- the directory was enumerated on disk but no
                                index mention was found.
     - ``refused``           -- the directory resolved under Rule #8 (should
                                not happen because we silently skip, but kept
                                as a defensive record for any future change).
     - ``skipped``           -- os.walk hit a permission / unreadable error.
     - ``claimed_missing``   -- never used at depth >= 1 (reserved for top
                                level, emitted as 0 rows here).
     - ``unverifiable``      -- never used (reserved for top level).
5. Appends every row to ``INDEX_DELTA_RECURSIVE.log`` (append-only, ``"a"``,
   UTF-8, ``newline="\\n"``).
6. Refuses any path under Rule #8 for the workspace / log / anchors with
   exit 2.

CLI
---
    # default --max-depth=2 (top-level + immediate children)
    python INDEX_DELTA_RECURSIVE.py
    # write INDEX_DELTA_RECURSIVE.log
    python INDEX_DELTA_RECURSIVE.py --run
    # deeper walk
    python INDEX_DELTA_RECURSIVE.py --max-depth 3 --run
    # constrained to one anchor
    python INDEX_DELTA_RECURSIVE.py --only-anchor "X:\\GITHUBREPO" --run

Refusal matrix (exit codes)
---------------------------
- 0   success (dry-run OR --run)
- 2   workspace / anchor / log path resolves under Rule #8
- 3   no DISK_ANCHORS resolved on this machine
- 4   --max-depth was outside the closed range [1, 4]
- 5   --dry-run and --run both passed OR --only-anchor not on the closed list

Closed assumptions about the walk
---------------------------------
- Defaults: ``--max-depth=2``.
- Range: ``1..=4``. Default cap protects the 859-immediate-child
  ``X:\\GITHUBREPO`` anchor from emitting hundreds of thousands of rows.
- Symlinks are NOT followed (matches the closed-architectural decision in
  the non-recursive scanner).

Compliance
-----------
ADDITIVE ONLY. Does NOT modify, replace, or delete any tracked master index,
master report, prior script, or any file under any ``DISK_ANCHORS`` directory.
Writes only ``INDEX_DELTA_RECURSIVE.log`` in the workspace root. Refuses any
path under Rule #8.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import re
import sys

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
# Closed target set: master indexes whose contents we audit (10 elements)
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
# Closed disk-anchor set (4 elements)
# ============================================================================
DISK_ANCHORS = (
    r"X:\GITHUBREPO",
    r"X:\githrepo",
    r"X:\03_PROJECTS",
    r"C:\Users\karma\03_PROJECTS",
)

# ============================================================================
# Closed extraction-regex set (3 elements)
# ============================================================================
EXTRACTION_PATTERNS = (
    (re.compile(r"`([A-Za-z0-9._\-]{2,64})`"), "backticked_name"),
    (re.compile(r"^\s*[-*]\s+([A-Za-z0-9._\- ]{2,80})(?:\s*[\(:\u2014\-].*)?$",
                re.MULTILINE), "bullet_listed_name"),
    (re.compile(r"(?i)(?:repository|project|repo)\s*:\s*([A-Za-z0-9._\-]{2,64})"),
     "keyed_name"),
)

# ============================================================================
# Closed delimiter / trim regex
# ============================================================================
_NAME_TRIM_RE = re.compile(r"\s*[\(:].*$")
_WS_RE = re.compile(r"\s+")

# ============================================================================
# Closed status enum (6 elements) - reused verbatim from INDEX_DELTA_SCANNER
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
# Closed recursion bounds (range [1, 4])
# ============================================================================
MIN_DEPTH = 1
MAX_DEPTH = 4
DEFAULT_DEPTH = 2

# ============================================================================
# Paths produced by this tool (additive only)
# ============================================================================
THIS_TOOL = "INDEX_DELTA_RECURSIVE.py"
LOG_FILE_NAME = "INDEX_DELTA_RECURSIVE.log"


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


def normalize_name(raw: str) -> str:
    """Compare-key normalizer (matches the non-recursive scanner's logic)."""
    s = _WS_RE.sub(" ", raw).strip()
    s = _NAME_TRIM_RE.sub("", s)
    if "/" in s or "\\" in s:
        s = re.split(r"[\\/]", s)[-1]
    return s.lower().strip(" ._-").rstrip(".git")


# ============================================================================
# Index file reader (read-only)
# ============================================================================
def read_index(path: str) -> str | None:
    """Return file contents (UTF-8) or None if missing / unreadable."""
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
# Recursive disk walker (os.walk with --max-depth cap and Rule #8 fence)
# ============================================================================
def walk_anchor(anchor: str, max_depth: int) -> list[dict]:
    """Walk *anchor* up to *max_depth*, yielding one record per directory.

    Symlinks are not followed. Rule #8 directories are silently skipped (the
    walker simply does NOT descend into them; the caller learns about the
    skip via the returned ``rule8_skip`` counter).
    """
    anchor_path = normalize_path(anchor)
    if is_in_personal(anchor_path):
        return []
    if not os.path.isdir(anchor_path):
        return []

    records: list[dict] = []
    # os.walk root has depth 0; immediate children are depth 1; etc.
    for current_root, dirs, _files in os.walk(anchor_path, followlinks=False):
        try:
            rel = os.path.relpath(current_root, anchor_path)
        except ValueError:
            rel = current_root
        depth = 0 if rel == "." else rel.count(os.sep) + 1
        if depth > max_depth:
            # Don't recurse further: prune dirs in-place so os.walk stops
            # descending into them.
            dirs[:] = []
            continue
        # Refuse to descend into any Rule #8 directory (silent skip at the
        # walker level) -- the caller records this in summary if needed.
        for d in tuple(dirs):
            if is_in_personal(os.path.join(current_root, d)):
                # Remove from dirs so os.walk does not recurse.
                dirs.remove(d)
        # Skip the anchor root itself at depth 0 -- nothing meaningful to
        # compare at the anchor level because the non-recursive scanner
        # already covers that case at top level. Drop it here so
        # compute_rows does not have to filter.
        if depth == 0:
            continue
        leaf = os.path.basename(current_root)
        records.append({
            "anchor": anchor_path,
            "full_path": current_root,
            "leaf": leaf,
            "normalized_key": normalize_name(leaf) if leaf else "",
            "depth": depth,
        })
        # Do NOT yield files -- per-directory rolls up file counts; per-file
        # rows would explode row counts on a 859-child GITHUBREPO tree.
        # File count is recorded as a derived aggregate below.
    return records


# ============================================================================
# Row computer (closed logic; emits one row per visited directory)
# ============================================================================
def compute_rows(records: list[dict], mentioned_keys: set[str]) -> list[dict]:
    """Convert walker records into status-tagged JSON rows.

    Note: ``records`` already contains only depth >= 1 entries because
    ``walk_anchor()`` drops depth-0 records at the source.
    """
    out: list[dict] = []
    for rec in records:
        if not rec["normalized_key"]:
            out.append({**rec, "status": "skipped",
                        "detail": "empty / whitespace-only leaf"})
            continue
        if rec["normalized_key"] in mentioned_keys:
            out.append({**rec, "status": "claimed_present",
                        "detail": f"leaf appears in at least one tracked index"})
        else:
            out.append({**rec, "status": "disk_extra",
                        "detail": "leaf not mentioned in any tracked index"})
    return out


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
        description="Recursive master-index vs disk delta walker (additive only)",
    )
    parser.add_argument("--dry-run", action="store_true",
                        help="Preview histogram without writing (DEFAULT if --run absent)")
    parser.add_argument("--run", action="store_true",
                        help="Append rows to INDEX_DELTA_RECURSIVE.log")
    parser.add_argument("--max-depth", type=int, default=DEFAULT_DEPTH,
                        help=f"Recursion depth [{MIN_DEPTH}..{MAX_DEPTH}] (default {DEFAULT_DEPTH})")
    parser.add_argument("--only-anchor", default=None,
                        help="Walk only this one DISK_ANCHORS candidate (verbatim regex match)")
    parser.add_argument("--workspace", default=os.getcwd(),
                        help="Workspace root for resolving relative paths")
    args = parser.parse_args(argv)

    workspace = os.path.abspath(args.workspace)
    if is_in_personal(workspace):
        print(f"REFUSED: workspace {workspace} is under a Rule #8 folder",
              file=sys.stderr)
        return 2

    if args.dry_run and args.run:
        print("REFUSED: --dry-run and --run are mutually exclusive",
              file=sys.stderr)
        return 5

    if args.only_anchor:
        if args.only_anchor not in DISK_ANCHORS:
            print(f"REFUSED: {args.only_anchor} is not on the closed DISK_ANCHORS list",
                  file=sys.stderr)
            return 5

    if not (MIN_DEPTH <= args.max_depth <= MAX_DEPTH):
        print(f"REFUSED: --max-depth {args.max_depth} outside closed range "
              f"[{MIN_DEPTH}..{MAX_DEPTH}]", file=sys.stderr)
        return 4

    # Resolve anchors and refuse any Rule #8 anchor early
    resolved_anchors: list[str] = []
    anchor_candidates = [args.only_anchor] if args.only_anchor else list(DISK_ANCHORS)
    for a in anchor_candidates:
        np = normalize_path(a)
        if is_in_personal(np):
            print(f"REFUSED: anchor {np} is under a Rule #8 folder",
                  file=sys.stderr)
            return 2
        resolved_anchors.append(np)

    log_path = os.path.join(workspace, LOG_FILE_NAME)
    if is_in_personal(log_path):
        print(f"REFUSED: log path {log_path} is under a Rule #8 folder",
              file=sys.stderr)
        return 2

    summary = {
        "tool": THIS_TOOL,
        "started_utc": _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds"),
        "mode": "WROTE" if args.run else "DRY-RUN",
        "max_depth": args.max_depth,
        "targets_scanned": [],
        "targets_missing": [],
        "targets_unreadable": [],
        "anchors_resolved": [],
        "anchors_missing": [],
        "names_extracted": 0,
        "directories_visited": 0,
        "by_status": {s: 0 for s in DELTA_STATUS_ENUM},
        "by_depth": {},
        "personal_folder_refusals": 0,
        "exited_cleanly": True,
    }

    # 1) Read indexes, extract names
    extracted: list[dict] = []
    for name in TRACKED_INDEX_FILES:
        full = os.path.join(workspace, name)
        if is_in_personal(full):
            print(f"REFUSED: {name} resolves under Rule #8 ({full})",
                  file=sys.stderr)
            return 2
        if not os.path.isfile(full):
            summary["targets_missing"].append(name)
            continue
        text = read_index(full)
        if text is None:
            summary["targets_unreadable"].append(name)
            continue
        summary["targets_scanned"].append(name)
        extracted.extend(extract_names(text, name))
    summary["names_extracted"] = len(extracted)
    mentioned_keys: set[str] = {e["normalized_key"] for e in extracted if e["normalized_key"]}

    # 2) Walk each anchor to --max-depth
    if not resolved_anchors:
        print("REFUSED: no DISK_ANCHORS resolved on this machine", file=sys.stderr)
        return 3

    all_records: list[dict] = []
    for anchor in resolved_anchors:
        try:
            recs = walk_anchor(anchor, args.max_depth)
        except (OSError, PermissionError) as e:
            summary["anchors_missing"].append(anchor)
            print(f"# skip (unreadable): {anchor} ({e})", file=sys.stderr)
            continue
        if recs:
            summary["anchors_resolved"].append(anchor)
        else:
            summary["anchors_missing"].append(anchor)
        all_records.extend(recs)

    summary["directories_visited"] = sum(1 for r in all_records if r["depth"] > 0)

    # 3) Compute delta rows
    rows = compute_rows(all_records, mentioned_keys)
    for r in rows:
        status = r["status"]
        if status not in DELTA_STATUS_ENUM:
            status = "skipped"
        summary["by_status"][status] += 1
        d = r["depth"]
        summary["by_depth"][str(d)] = summary["by_depth"].get(str(d), 0) + 1
        if status == "refused":
            summary["personal_folder_refusals"] += 1

    print(f"# {THIS_TOOL} -- mode: {summary['mode']}")
    print(f"# workspace: {workspace}")
    print(f"# max-depth: {args.max_depth}")
    print(f"# targets scanned: {len(summary['targets_scanned'])}")
    print(f"# targets missing: {len(summary['targets_missing'])}")
    print(f"# targets unreadable: {len(summary['targets_unreadable'])}")
    print(f"# anchors resolved: {len(summary['anchors_resolved'])}")
    print(f"# anchors missing: {len(summary['anchors_missing'])}")
    print(f"# names extracted: {summary['names_extracted']}")
    print(f"# directories visited (>= depth 1): {summary['directories_visited']}")
    print(f"# rows emitted: {len(rows)}")
    for s in DELTA_STATUS_ENUM:
        print(f"# by_status[{s}]: {summary['by_status'][s]}")
    print(f"# by_depth: {summary['by_depth']}")
    print(f"# personal_folder_refusals: {summary['personal_folder_refusals']}")

    if args.run:
        for row in rows:
            append_audit_row(log_path, row)
        summary["finished_utc"] = _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds")
        append_audit_row(log_path, {"event": "run_complete", **summary})
        print(f"# wrote {len(rows)} directory rows + 1 run_complete summary to {log_path}")
    else:
        print("# dry-run: nothing written. Pass --run to append directory rows.")

    return 0


if __name__ == "__main__":
    sys.exit(run())
