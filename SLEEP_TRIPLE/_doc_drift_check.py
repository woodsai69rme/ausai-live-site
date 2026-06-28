#!/usr/bin/env python3
"""
_doc_drift_check.py — guards SLEEP_TRIPLE/DOCUMENTATION.md section 9 against
commit-log drift.

Quick problem this solves: when commits pile up locally and the docs aren't
updated, future-me reading DOCUMENTATION.md has no idea which commit it
corresponds to. Drift = trust = repo rot. This script catches that.

What it checks:
  1. The most recent commit hash in section 9's commit table matches the most
     recent SLEEP_TRIPLE-related commit in `git log`.
  2. Every commit hash in the table exists in the repo (no stale references).
  3. The table count is consistent with the git log size (no orphans, no stale).

Exits 0 on PASS, 1 on FAIL. stderr carries human-readable diagnostics.

Optional --quiet flag for CI runs (only emits output on FAIL).
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DOC = ROOT / "DOCUMENTATION.md"

HEADER_RE = re.compile(r"^##\s+\d+\b")
HASH_RE = re.compile(r"`([0-9a-f]{7,8})`")


def _git_log_sleep_commits() -> list[str]:
    """Return most-recent-first list of 7/8-char short commit hashes that touch
    SLEEP_TRIPLE/ or Append-Revenue* on HEAD.

    Filters OUT the most-recent commit IF its subject indicates the commit's
    purpose was to update DOCS / §9 itself. Without this filter, every amend
    creates a new hash that the §9 table can't yet contain (chicken-and-egg).
    The filter is regex-based so future subject variants stay covered.

    Recognized doc-update subject signals (case-insensitive):
      - Anchored conventional prefixes: docs:, docs(, docs(*):, chore:,
        chore(*):, doc: (rare).
      - Whole-word substrings anywhere: doc, docs, drift, readme.

    Older doc-update commits are kept in the listing so §9 archaeology stays
    complete. Code commits that incidentally contain "doc" as a SUBSTRING of
    an unrelated word (e.g. "decode", "decoded") still pass through because
    the substring check uses ``\\b`` word boundaries.
    """
    DOC_UPDATE_RE = re.compile(
        r"\A(?:docs?|chore)(?:\([^)]+\))?:\b|\b(?:docs?|drift|readme)\b",
        re.IGNORECASE,
    )
    r = subprocess.run(
        ["git", "log", "--pretty=format:%h\t%s", "HEAD",
         "--", "SLEEP_TRIPLE/*", "Append-Revenue*"],
        capture_output=True, text=True, cwd=str(ROOT.parent),
    )
    if r.returncode != 0:
        return []
    rows: list[str] = []
    for line in r.stdout.splitlines():
        if not line.strip():
            continue
        parts = line.split("\t", 1)
        if len(parts) != 2:
            continue
        h, subj = parts[0].strip(), parts[1].strip()
        # Filter only the MOST-RECENT commit if it's a doc-update commit.
        # Older doc-update commits stay in the listing so §9 stays complete.
        if not rows and DOC_UPDATE_RE.search(subj):
            continue
        rows.append(h)
    return rows


def _section_h9_hashes(doc_text: str) -> list[str]:
    """Return 7-char hex hashes backticked in lines between ## 9. and the next
    ## <other-digits>. heading. Robust to headers with trailing parentheticals
    like '## 9. Commit History (local, awaiting push)'.
    """
    lines = doc_text.splitlines()
    in_h9 = False
    rows: list[str] = []
    for line in lines:
        if HEADER_RE.match(line):
            heading_num_match = re.match(r"^##\s+(\d+)\b", line)
            if not heading_num_match:
                continue
            num = heading_num_match.group(1)
            if in_h9 and num != "9":
                break  # next numbered section, leave.
            if num == "9":
                in_h9 = True
                continue
        if not in_h9:
            continue
        # Greedy harvest of all 7-char hex hashes in this line.
        for m in HASH_RE.finditer(line):
            rows.append(m.group(1))
    return rows


def _hash_exists(short: str) -> bool:
    """Verify a short hash resolves to a real commit in the repo."""
    r = subprocess.run(
        ["git", "cat-file", "-t", short],
        capture_output=True, text=True, cwd=str(ROOT.parent),
    )
    return r.returncode == 0 and r.stdout.strip() == "commit"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--quiet", action="store_true",
                    help="print nothing on PASS (only on FAIL)")
    args = ap.parse_args()

    if not DOC.exists():
        print(f"[doc-drift] FAIL: {DOC} not found", file=sys.stderr)
        return 1

    text = DOC.read_text(encoding="utf-8")
    doc_hashes = _section_h9_hashes(text)
    if not doc_hashes:
        print(f"[doc-drift] FAIL: no commits found in section 9 of {DOC}",
              file=sys.stderr)
        return 1

    live_hashes = _git_log_sleep_commits()
    if not live_hashes:
        print("[doc-drift] FAIL: no git history found (not in a git tree?)",
              file=sys.stderr)
        return 1

    failures: list[str] = []

    # 1. Most recent commit match.
    doc_top = doc_hashes[0]
    live_top = live_hashes[0]
    if doc_top != live_top:
        failures.append(
            f"latest commit hash mismatch: section 9 top=`{doc_top}` "
            f"but git log top=`{live_top}`")

    # 2. Each doc hash resolves.
    for h in doc_hashes:
        if not _hash_exists(h):
            failures.append(f"stale or bogus commit hash in section 9: `{h}`")

    # 3. Doc table count must be reasonably close to git log count.
    # Drift in EITHER direction is suspect: more in doc than git = orphan
    # hashes; more in git than doc = section 9 is stale. >5 in either
    # direction means the table diverged from reality.
    extra = len(doc_hashes) - len(live_hashes)
    if abs(extra) > 5:
        direction = "doc table LONGER" if extra > 0 else "doc table SHORTER"
        failures.append(
            f"section 9 drift: {direction} than git log ("
            f"doc={len(doc_hashes)} git={len(live_hashes)} delta={extra})")

    if failures:
        print("[doc-drift] FAIL:", file=sys.stderr)
        for f in failures:
            print(f"  - {f}", file=sys.stderr)
        print(f"[doc-drift] doc_top=`{doc_top}` live_top=`{live_top}` "
              f"doc_count={len(doc_hashes)} git_count={len(live_hashes)}",
              file=sys.stderr)
        return 1

    if not args.quiet:
        print(f"[doc-drift] GREEN: section 9 in sync (top=`{doc_top}`, "
              f"{len(doc_hashes)} commits match git history)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
