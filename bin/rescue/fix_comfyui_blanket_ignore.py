#!/usr/bin/env python3
"""bin/rescue/fix_comfyui_blanket_ignore.py

Surgical .gitignore fix for: a vendored dependency (e.g. ComfyUI) whose
subtree is BLANKET-IGNORED at the repo root, but you need to track a specific
source file inside it.

WHY this exists: cont.17-fup-3 rescue (2026-07-11) discovered that ComfyUI/
was blanket-ignored at the repo root -- definitely the right policy for the
heavy-weight ``models/`` checkpoints (GB), but accidentally blocked the
operator-useful source files ``music_video_studio.py`` and
``openrouter_free_models.txt`` from being tracked.

This script strips the blanket rule and replaces it with PER-SUBDIR ignores
for just the heavy-weight / generated dirs:
  - /ComfyUI/models/        (GB-weight checkpoints, clip, vae, controlnet,
                             embeddings, lora, upscale_models, animatediff_models,
                             ipadapter; transitively covers all model subdirs)
  - /ComfyUI/custom_nodes/  (ComfyUI node source code; several GB)
  - /ComfyUI/output/        (generated media -- MP4/GIF/PNG produced by runs)
  - /ComfyUI/input/         (input media uploaded via ComfyUI UI)
  - /ComfyUI/.git/          (nested-repo git bookkeeping -- see bin/rescue/README.md)

After: lightweight source files (e.g. ``tools/music_video_studio.py``,
``config/openrouter_free_models.txt``) can be tracked.

Idempotent: re-running is a no-op if already in the precise state.

Run from repo root:
    cd /path/to/repo
    python bin/rescue/fix_comfyui_blanket_ignore.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

# Resolve .gitignore from the script's own location: repository root is 3 levels
# up from bin/rescue/<script>.py. Avoids CWD-fragility (works from any subdir).
# REPO_ROOT = bin/rescue/<script>.py -> bin/rescue/ -> bin/ -> repo-root
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
GITIGNORE = REPO_ROOT / ".gitignore"

# The 5 subdirs we want to ignore (heavy weights + generated + nested git).
SUBDIR_IGNORES: tuple[str, ...] = (
    "/ComfyUI/models/",
    "/ComfyUI/custom_nodes/",
    "/ComfyUI/output/",
    "/ComfyUI/input/",
    "/ComfyUI/.git/",
)

# Strip blanket rules: ``/ComfyUI/`` or ``ComfyUI/`` alone on a line (with
# optional trailing whitespace + inline comment). Covers the most common forms.
BLANKET_RE = re.compile(r"^[ \t]*ComfyUI[ \t]*/?[ \t]*(?:#.*)?$\n", re.MULTILINE)


def main() -> int:
    if not GITIGNORE.exists():
        print(f"ERROR: {GITIGNORE} not found", file=sys.stderr)
        return 2

    content = GITIGNORE.read_text(encoding="utf-8")
    original = content

    # Strip blanket lines.
    blanket_hits = BLANKET_RE.findall(content)
    content = BLANKET_RE.sub("", content)

    # Append per-subdir ignores that aren't already present.
    existing = {ln.strip() for ln in content.splitlines()}
    to_add = [ign for ign in SUBDIR_IGNORES if ign not in existing]

    if blanket_hits or to_add:
        if not content.endswith("\n"):
            content += "\n"
        if to_add:
            comment_block = (
                "\n# ComfyUI source files (TRACK -- never blanket-ignored anymore):\n"
                "# - ComfyUI/tools/music_video_studio.py (operator-discoverable source)\n"
                "# - ComfyUI/config/openrouter_free_models.txt (operator-discovery file)\n"
                "# Heavy-weight / generated subdirs remain excluded.\n"
                + "\n".join(to_add)
                + "\n"
            )
            content += comment_block
        GITIGNORE.write_text(content, encoding="utf-8")
        print(
            f"GITIGNORE_CHANGED: stripped {len(blanket_hits)} blanket line(s); "
            f"appended {len(to_add)} new subdir ignore(s); "
            f"size {len(original)} -> {len(content)} bytes"
        )
    else:
        print("GITIGNORE_NO_OP: no changes needed (already-precise state)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
