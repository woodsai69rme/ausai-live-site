#!/usr/bin/env python3
"""
_doc_drift_check.py — guards SLEEP_TRIPLE/DOCUMENTATION.md section 9 against
commit-log drift.

Quick problem this solves: when commits pile up locally and the docs aren't
updated, future-me reading DOCUMENTATION.md has no idea which commit it
corresponds to. Drift = trust = repo rot. This script catches that.

What it checks (after stripping leading doc-update commits from BOTH sides):
  1. The most recent (non-doc-update) commit hash in section 9's commit table
     matches the most recent (non-doc-update) commit in `git log` that touches
     ``SLEEP_TRIPLE/`` or ``Append-Revenue*``.
  2. Every commit hash in the table exists in the repo (no stale references).
  3. Each live commit hash is listed in section 9 (no orphans in git that
     the table forgot).

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
# §9 table row: `| `HASH` | SUBJECT |`. Hash is 7-8 hex chars; subject is
# captured lazily up to the final `|` on the line. Anchored at end-of-line
# so trailing whitespace does not eat a boundary.
SECTION9_ROW_RE = re.compile(r"\|\s*`([0-9a-f]{7,8})`\s*\|\s*(.+?)\s*\|\s*$")

# Recognised doc-update subject signals (case-insensitive):
#   - Anchored conventional prefixes: docs:, docs(, docs(*):, chore:,
#     chore(*):, doc: (rare).
#   - Whole-word substrings anywhere: doc, docs, drift, readme.
# Word boundaries (``\b``) keep substring matches narrow: ``doc`` won't
# match ``decoder`` / ``docker`` / ``decode``.
DOC_UPDATE_RE = re.compile(
    r"\A(?:docs?|chore)(?:\([^)]+\))?:\b|\b(?:docs?|drift|readme)\b",
    re.IGNORECASE,
)


def _strip_leading_doc_updates(
    rows: list[tuple[str, str]],
) -> tuple[list[tuple[str, str]], int]:
    """Skip entries at the head of ``rows`` whose subject matches
    ``DOC_UPDATE_RE``. Once a non-doc-update entry is appended, every
    subsequent (older) entry is kept regardless of subject.

    Used symmetrically by the doc-side (caller parses §9) and the live-side
    (caller parses ``git log``). The function is a pure state machine on a
    list, so it can be re-applied to either side without losing meaning.
    """
    out: list[tuple[str, str]] = []
    skipped = 0
    for h, subj in rows:
        if not out and DOC_UPDATE_RE.search(subj):
            skipped += 1
            continue
        out.append((h, subj))
    return out, skipped


def _git_log_sleep_commits_with_subjects() -> tuple[list[tuple[str, str]], int]:
    """Return ``(rows, skipped_from_head)`` where ``rows`` is a
    most-recent-first list of ``(hash, subject)`` tuples for commits
    touching ``SLEEP_TRIPLE/`` or ``Append-Revenue*`` on HEAD, with LEADING
    doc-updates already stripped via ``_strip_leading_doc_updates``.

    The leading-strip is the amend-loop break: a fix to this very file (or
    any docs-update commit) lands as a new hash that can't yet appear in
    §9's table, so without the strip the check would perpetually fail after
    every amend. The same strip is applied to the doc side in ``main()``.
    """
    r = subprocess.run(
        ["git", "log", "--pretty=format:%h\t%s", "HEAD",
         "--", "SLEEP_TRIPLE/*", "Append-Revenue*"],
        capture_output=True, text=True, cwd=str(ROOT.parent),
    )
    if r.returncode != 0:
        return [], 0
    raw: list[tuple[str, str]] = []
    for line in r.stdout.splitlines():
        if not line.strip():
            continue
        parts = line.split("\t", 1)
        if len(parts) != 2:
            continue
        raw.append((parts[0].strip(), parts[1].strip()))
    return _strip_leading_doc_updates(raw)


def _section_h9_rows(doc_text: str) -> list[tuple[str, str]]:
    """Return ``(hash, subject)`` tuples parsed from §9 commit-history table
    rows. Each row in §9 has the form ``| `HASH` | SUBJECT |``.

    Robust to:
      * Heading variations like ``## 9. Commit History (local, awaiting push)``.
      * Lines outside §9 (header table at §5, R3/R4 tables at §8b, etc.).
      * The trailing push-status warning paragraph and ``---`` separator.
    """
    lines = doc_text.splitlines()
    in_h9 = False
    rows: list[tuple[str, str]] = []
    for line in lines:
        if HEADER_RE.match(line):
            m = re.match(r"^##\s+(\d+)\b", line)
            if not m:
                continue
            num = m.group(1)
            if in_h9 and num != "9":
                break  # next numbered section, leave.
            if num == "9":
                in_h9 = True
                continue
        if not in_h9:
            continue
        m = SECTION9_ROW_RE.match(line)
        if not m:
            continue
        rows.append((m.group(1).strip(), m.group(2).strip()))
    return rows


def _hash_exists(short: str) -> bool:
    """Verify a short hash resolves to a real commit in the repo."""
    r = subprocess.run(
        ["git", "cat-file", "-t", short],
        capture_output=True, text=True, cwd=str(ROOT.parent),
    )
    return r.returncode == 0 and r.stdout.strip() == "commit"


def _count_unstripped_live() -> int:
    """How many entries would ``git log`` return WITHOUT the DOC_UPDATE_RE
    strip? Used to disambiguate "no commits in repo" vs "every commit is a
    doc-update and got stripped" in the failure message."""
    r = subprocess.run(
        ["git", "log", "--pretty=format:%h", "HEAD",
         "--", "SLEEP_TRIPLE/*", "Append-Revenue*"],
        capture_output=True, text=True, cwd=str(ROOT.parent),
    )
    if r.returncode != 0:
        return 0
    return sum(1 for l in r.stdout.splitlines() if l.strip())


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--quiet", action="store_true",
                    help="print nothing on PASS (only on FAIL)")
    args = ap.parse_args()

    if not DOC.exists():
        print(f"[doc-drift] FAIL: {DOC} not found", file=sys.stderr)
        return 1

    text = DOC.read_text(encoding="utf-8")
    doc_rows_raw = _section_h9_rows(text)
    if not doc_rows_raw:
        print(f"[doc-drift] FAIL: no commits found in section 9 of {DOC}",
              file=sys.stderr)
        return 1
    doc_stripped, doc_skipped = _strip_leading_doc_updates(doc_rows_raw)

    live_rows, live_skipped = _git_log_sleep_commits_with_subjects()
    if not live_rows:
        # Disambiguate the empty-after-strip case from the empty-repo case.
        raw_count = _count_unstripped_live()
        if raw_count == 0:
            print("[doc-drift] FAIL: no SLEEP_TRIPLE/ or Append-Revenue/ "
                  "commits in git history", file=sys.stderr)
        else:
            print(f"[doc-drift] FAIL: all {raw_count} SLEEP_TRIPLE/ commits "
                  f"match DOC_UPDATE_RE — every commit is a doc-update and "
                  f"§9 has nothing to anchor against", file=sys.stderr)
        return 1

    failures: list[str] = []

    # 1. Every doc hash resolves in git. Catches typos and stale entries
    #    left behind by previous §9 versions.
    for h, _ in doc_rows_raw:
        if not _hash_exists(h):
            failures.append(f"stale or bogus commit hash in section 9: `{h}`")

    # 2. §9 must have at least one non-doc-update row to anchor against.
    if not doc_stripped:
        failures.append(
            "section 9 contains ONLY doc-update commits after stripping "
            "leading rows — no real trailblazer remains to anchor against")

    # 3. Latest non-doc-update commit must match between doc and git.
    if doc_stripped:
        doc_top = doc_stripped[0][0]
        live_top = live_rows[0][0]
        if doc_top != live_top:
            failures.append(
                f"latest commit hash mismatch after stripping leading "
                f"doc-updates: section 9 top=`{doc_top}` but git top=`{live_top}` "
                f"(live skipped {live_skipped}, doc skipped {doc_skipped})")

    # 4. No orphans: every stripped-live hash must appear in stripped-doc set.
    if doc_stripped:
        doc_hashes = {h for h, _ in doc_stripped}
        missing = [h for h, _ in live_rows if h not in doc_hashes]
        if missing:
            failures.append(
                f"section 9 missing {len(missing)} commit hash(es): "
                f"{', '.join(missing[:5])}"
                f"{'...' if len(missing) > 5 else ''}")

    if failures:
        print("[doc-drift] FAIL:", file=sys.stderr)
        for f in failures:
            print(f"  - {f}", file=sys.stderr)
        print(f"[doc-drift] doc_rows_raw={len(doc_rows_raw)} live_rows={len(live_rows)} "
              f"doc_stripped={len(doc_stripped)} live_skipped={live_skipped} "
              f"doc_skipped={doc_skipped}",
              file=sys.stderr)
        return 1

    if not args.quiet:
        top = doc_stripped[0][0] if doc_stripped else "?"
        print(
            f"[doc-drift] GREEN: section 9 in sync (top=`{top}`, "
            f"{len(doc_stripped)} commits recorded, "
            f"{live_skipped + doc_skipped} leading doc-updates stripped)"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
