#!/usr/bin/env python3
"""bin/rescue/unblock_comfyui_case_insensitive_ignores.py

Surgical .gitignore fix for: ``git check-ignore -v <file>`` reports NOT
IGNORED, but ``git add -v <file>`` silently prints NOTHING (rc=0 but no
effect). The smoking gun is usually case-insensitive gitignore patterns
elsewhere in the rule set (Windows ``core.ignorecase=true``) that blanket-
match the file's parent directory.

WHY this exists: cont.17-fup-3 rescue (2026-07-11) discovered TWO extra
blanket ignores AFTER removing the original ``/ComfyUI/`` rule:

  - line 300: ``[C-c]onfig/`` -- a gitignore bracket expression that matches
    any directory named ``config*`` at any depth, CASE-INSENSITIVELY.
  - line 830: ``TOOLS/`` -- a no-leading-slash pattern that matches any
    directory named ``tools*`` at any depth.

On Windows where ``core.ignorecase=true``, both still blanket-match
``/ComfyUI/config/`` and ``/ComfyUI/tools/`` despite the prior fix.

This script appends SURGICAL NEGATION rules to .gitignore that re-include
ONLY ``/ComfyUI/tools/`` and ``/ComfyUI/config/``, leaving the offending
blanket rules in place so they still cover ``Tools/`` and ``Config/``
directories elsewhere in the repo.

Why negation vs blanket removal:
  - Removing the offender would unblock ALL ``config/`` / ``tools/``
    directories in the workspace (potentially leaking secrets, build
    artifacts, etc.).
  - Append-only negation is reversible in one ``str_replace``.
  - Aligns with the CLAUDE.md alpha principle "detailed errors over
    graceful failures" -- log WHICH rule was the offender, not silently
    unblock everything.

Idempotent: re-running is a no-op if both negation lines already present.

Run from repo root:
    cd /path/to/repo
    python bin/rescue/unblock_comfyui_case_insensitive_ignores.py
"""
from __future__ import annotations

import sys
from pathlib import Path

# Resolve .gitignore from the script's own location: repository root is 3 levels
# up from bin/rescue/<script>.py. Avoids CWD-fragility (works from any subdir).
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
GITIGNORE = REPO_ROOT / ".gitignore"

NEGATION_RULES: tuple[str, ...] = (
    "# Surgical unblock (cont.17-fup-3 rescue): negation for the blanket\n"
    "# TOOLS/ (line 830) and [Cc]onfig/ (line 300) rules, which -- on Windows\n"
    "# with core.ignorecase=true -- would otherwise block /ComfyUI/tools/ and\n"
    "# /ComfyUI/config/ source files from being tracked. These two negations\n"
    "# let the existing blanket rules still cover other TOOLS/ + Config dirs.\n"
    "!/ComfyUI/tools/\n"
    "!/ComfyUI/config/\n"
)


def main() -> int:
    if not GITIGNORE.exists():
        print(f"ERROR: {GITIGNORE} not found", file=sys.stderr)
        return 2

    text = GITIGNORE.read_text(encoding="utf-8")

    # Idempotency check
    if all(rule in text for rule in ("!/ComfyUI/tools/", "!/ComfyUI/config/")):
        print("GITIGNORE_UNBLOCK_NOOP: both negation rules already present")
        return 0

    # Append, ensuring a separator newline if the existing file didn't end in one.
    if not text.endswith("\n"):
        text += "\n"
    text += "\n" + "".join(NEGATION_RULES)  # leading blank line for readability

    GITIGNORE.write_text(text, encoding="utf-8")
    print(
        "GITIGNORE_UNBLOCK_APPLIED: appended negation rules "
        "!/ComfyUI/tools/ + !/ComfyUI/config/"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
