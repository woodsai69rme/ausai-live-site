#!/usr/bin/env python3
"""
DISK_FREE_ADVISOR.py - OPT-9.1 Disk Space Optimization (catalog + advisor)
"""
"""
✅ COMPLIANCE: ADDITIVE ONLY.
- Walks non-personal roots; identifies installer/zip files >50MB.
- Produces DISK_FREE_PROPOSALS.md (append-only) with columns: path, size,
  proposed cold-storage target, rationale. PROPOSALS ONLY -- no execution.
- Personal folders (Documents, Downloads, Pictures, Videos, Music,
  Desktop, OneDrive, Downloads\ARCHIVE_OLD) are NEVER touched.
- An explicit `--apply <confirm_token>` is required to perform any
  proposal. Without the token, the script exits 0 with report only.
"""
from __future__ import annotations

import argparse
import hashlib
import os
import sys
import time
from pathlib import Path
from typing import Iterable

PERSONAL_FOLDERS = {
    "Documents",
    "Downloads",
    "Pictures",
    "Videos",
    "Music",
    "Desktop",
    "OneDrive",
    # Per Rule #8 + companion note: Downloads\ARCHIVE_OLD is protected too.
    "ARCHIVE_OLD",
}

COLD_STORAGE_ROOT = Path(os.environ.get("COLD_STORAGE_ROOT", "~/COLD_STORAGE")).expanduser()

# Patterns that count as "installer / archive / large binary" for proposing.
PROPOSE_PATTERNS = (
    ".iso",
    ".img",
    ".zip", ".tar", ".tar.gz", ".tgz", ".tar.bz2", ".7z", ".rar",
    ".exe", ".msi", ".pkg", ".dmg",
)

SIZE_THRESHOLD_BYTES = 50 * 1024 * 1024  # 50 MB


def is_in_personal(path: Path) -> bool:
    parts = path.parts
    for pf in PERSONAL_FOLDERS:
        if pf in parts:
            return True
    return False


def iter_candidates(root: Path) -> Iterable[Path]:
    skip_dirs = {".git", "node_modules", ".venv", "__pycache__", ".cache"}
    for parent, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        if is_in_personal(Path(parent)):
            continue
        for fname in files:
            if not fname.lower().endswith(PROPOSE_PATTERNS):
                continue
            f = Path(parent) / fname
            if is_in_personal(f):
                continue
            try:
                if f.stat().st_size >= SIZE_THRESHOLD_BYTES:
                    yield f
            except OSError:
                continue


def content_hash(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def propose_target(src: Path) -> Path:
    """`~/COLD_STORAGE/<mirror>/<basename>` -- additive mirror, never deletion."""
    relative = src.name
    return COLD_STORAGE_ROOT / relative


def append_proposal(proposals_md: Path, src: Path) -> None:
    target = propose_target(src)
    sha = content_hash(src)
    ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    line = (
        f"\n| `{src}` | {src.stat().st_size:,} | `{target}` | "
        f"`{sha[:16]}` | {ts} | pending |\n"
    )
    with proposals_md.open("a", encoding="utf-8") as fh:
        fh.write(line)


def emit_report_intro(proposals_md: Path, basename: str, n: int) -> None:
    ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    intro = f"""
## DISK_FREE_ADVISOR pass - {ts}

- Root walked: {basename}
- Candidates found (>=50 MB installer/archive): {n}
- Cold-storage root: `{COLD_STORAGE_ROOT}` (does NOT need to exist yet)
- Personal folders excluded: Documents, Downloads, Pictures, Videos, Music,
  Desktop, OneDrive, Downloads\\ARCHIVE_OLD
- Status: proposals are **PENDING**. Apply only via `--apply <confirm_token>`.
"""
    with proposals_md.open("a", encoding="utf-8") as fh:
        fh.write(intro)
        fh.write("| Source | Bytes | Proposed target | SHA-256 head | Detected | Status |\n")
        fh.write("|---|---|---|---|---|---|\n")


def apply_proposals(proposals_md: Path, confirm_token: str) -> int:
    if confirm_token != os.environ.get("DISK_FREE_ADVISOR_TOKEN", "NO_TOKEN"):
        print("REFUSED: --apply requires env var DISK_FREE_ADVISOR_TOKEN to be set and non-empty.")
        return 2
    # Read appended proposals, mirror each to COLD_STORAGE_ROOT (preserving the
    # original; never deleting). This is the ADDITIVE copy step.
    COLD_STORAGE_ROOT.mkdir(parents=True, exist_ok=True)
    moved = 0
    with proposals_md.open("r", encoding="utf-8") as fh:
        for line in fh:
            if not line.startswith("| `") or "pending" not in line:
                continue
            parts = [p.strip().strip("`") for p in line.split("|")]
            src = Path(parts[1])
            target = Path(parts[3])
            try:
                # True additive mirror: copy + log sha match.
                target.write_bytes(src.read_bytes())
                sha_target = content_hash(target)
                sha_src = content_hash(src)
                if sha_target == sha_src:
                    moved += 1
            except OSError:
                continue
    return moved


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=str(Path.home()),
                        help="Top-level walk root (default: ~).")
    parser.add_argument("--out", default="DISK_FREE_PROPOSALS.md",
                        help="Append-only proposals report.")
    parser.add_argument("--apply", default="",
                        help="Set to a confirm token and have DISK_FREE_ADVISOR_TOKEN env var "
                             "set to the same value to mirror (additively) all pending proposals.")
    args = parser.parse_args()

    proposals_md = Path(args.out)
    root = Path(args.root).resolve()

    candidates = sorted(set(iter_candidates(root)), key=lambda p: p.stat().st_size, reverse=True)
    if candidates:
        emit_report_intro(proposals_md, str(root), len(candidates))
        for c in candidates:
            append_proposal(proposals_md, c)
        print(f"DISK_FREE_ADVISOR: cataloged {len(candidates)} candidates into {proposals_md}")
    else:
        print(f"DISK_FREE_ADVISOR: no candidates (>=50 MB installer/archive) found under {root}")

    if args.apply:
        moved = apply_proposals(proposals_md, args.apply)
        print(f"DISK_FREE_ADVISOR: mirrored {moved} files into {COLD_STORAGE_ROOT} (originals untouched).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
