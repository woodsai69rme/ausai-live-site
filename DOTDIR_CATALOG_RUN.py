"""
DOTDIR_CATALOG_RUN.py

Bounded audit for dot-directories that show up at the project workspace root.

The original goal of this tool is to surface `.X/` directories that are NOT
already covered by `.gitignore` so an operator can decide which entries to add.
It also serves as a generic "what user-tooling state is sitting next to source"
cataloger for hygiene / privacy passes.

Closed architecture (do not extend without editing this header):

- WELL_KNOWN_NOISE_DIRS  frozenset -- names we know from experience are per-user
  IDE / AI-tooling state and therefore should NEVER be committed.
- CLOSED_POSSIBLY_LEGIT  frozenset -- names that look like dot-dirs but are
  legitimate project artefacts (`.git/`, `.github/`, `.vscode/`, ...). These
  MUST NOT be auto-ignored even when they match the dotdir walker.
- DOTDIR_CATALOG_ENUM    closed 6-tuple -- the only legal verdicts a row can
  carry: well_known_noise / unclassified_per_user / possibly_legit / refused /
  skipped / unverifiable. Adding verdicts requires editing this file, not
  extending data.
- RULE_8_DIRS            closed 8-tuple -- personal / user folders the walker
  refuses to descend into (CLAUDE.md Rule #8 + project Rule #8 fence).
- TRACKED_DOTDIR_LOGS    frozenset, intended-closed -- append-only log files
  this tool concludes can be emitted. Currently exactly one entry.

I/O contract:

- default `--dry-run`: walks the root, classifies every direct-child dotdir,
  prints a tabular summary to stdout, never touches disk.
- `--run`: walks the root, classifications as above, but ALSO appends one
  ISO-prefixed JSONL row per dotdir to `DOTDIR_CATALOG.log` (open(...,'a',...)).
- refuses rule-8 workspace with exit 2
- refuses `--emit-summary` without `--run` with exit 5
- refuses a workspace that does not exist with exit 4
- refuses a workspace that is not a directory with exit 6
- emits zero rows for empty workspaces (does not exit non-zero)

Closed-set sync caveat (audited, not auto-synced): WELL_KNOWN_NOISE_DIRS here
is a representative snapshot; on every dry-run, `sync_warning` reads the
`# Per-user IDE/AI-tooling` block from `.gitignore` and emits WARN lines if
either side has names the other doesn't, so drift is observable at audit time
rather than silently incorrect.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Final


# ----- closed sets (do not add new entries without editing the header) -----

WELL_KNOWN_NOISE_DIRS: Final[frozenset[str]] = frozenset({
    ".agent", ".agents", ".ai_completion",
    ".aider-desk", ".aider", ".aitk",
    ".antigravity-ide", ".antigravity", ".azad",
    ".bitcoinlib", ".bowtie", ".bun",
    ".cagent", ".charm_crush_enhanced", ".chocolatey",
    ".clara", ".claude-code-router", ".claude-flow",
    ".claude-plugin", ".claude", ".cline",
    ".codeartsdoer", ".codebuddy", ".codemaker",
    ".codestudio", ".codetogether", ".codex",
    ".commandcode", ".conda", ".config",
    ".continue", ".cursor", ".deepsource",
    ".devcontainer", ".dyad", ".flox",
    ".gemini-cli", ".gemini", ".gh-code",
    ".gitconfig-extra", ".gitkraken", ".glacier-cli",
    ".glow", ".gpt4all", ".gradle",
    ".hack", ".helix", ".hermes",
    ".husky", ".jetbrains", ".julius",
    ".jupyter", ".kilocode", ".kilocli",
    ".kiro", ".lmstudio", ".local-shellx",
    ".magic", ".marsx", ".mcp-cli",
    ".mcp_config", ".minimax-ide", ".minimax",
    ".mockflow", ".morph", ".n8n",
    ".nextflow", ".notdiamond", ".notes",
    ".octocoder", ".ollama", ".openai-coder",
    ".openclients", ".opencode", ".opencoder",
    ".openrouter-cli", ".oxcoder", ".pi-mono",
    ".pieces", ".qwen-code", ".qutebrowser",
    ".rerun", ".roo", ".scrollx",
    ".sculptor", ".shellmate", ".skill-ui",
    ".solidlts", ".soch", ".solidity",
    ".super_agent", ".symbiote", ".symphony",
    ".tactical", ".tambo", ".tea",
    ".tensordock", ".tortoise", ".trae",
    ".warp", ".windsurf", ".worktrees",
    ".zed", ".zere", ".zerepy",
    ".zsh-history", ".deepseek",
    ".morph-bench", ".morph-edit", ".morph-studio",
    ".morph-vfx", ".dynamicstudios",
})


CLOSED_POSSIBLY_LEGIT: Final[frozenset[str]] = frozenset({
    ".git",
    ".github",
    ".vscode",
    ".idea",
    ".gitignore",
    ".gitattributes",
    ".env.example",
    ".env.sample",
    ".env.template",
})


RULE_8_DIRS: Final[tuple[str, ...]] = (
    "Documents", "Downloads", "Pictures", "Videos", "Music",
    "Desktop", "OneDrive",
    os.path.join("Downloads", "ARCHIVE_OLD"),
    "ARCHIVE_OLD",
)


DOTDIR_CATALOG_ENUM: Final[tuple[str, ...]] = (
    "well_known_noise",
    "unclassified_per_user",
    "possibly_legit",
    "refused",
    "skipped",
    "unverifiable",
)


TRACKED_DOTDIR_LOGS: Final[frozenset[str]] = frozenset({
    "DOTDIR_CATALOG.log",
})


REFUSAL_EXIT_CODE_MATRIX: Final[dict[str, int]] = {
    # Single source of truth for refusal exit codes; main() MUST consume this
    # rather than hardcoding integers so the .md refusal matrix and the code
    # never drift.
    "rule_8_workspace": 2,
    "workspace_missing": 4,
    "workspace_not_a_directory": 6,
    "emit_summary_without_run": 5,
    "unreadable_workspace": 0,  # data-quality signal, not a hard failure
}


NOISE_BLOCK_HEADING: Final[str] = "Per-user IDE/AI-tooling"


# ----- helpers -----


def normalize_workspace(raw: str) -> Path:
    """Expand user / env vars and return an absolute Path."""
    return Path(os.path.expandvars(os.path.expanduser(raw))).resolve()


def is_rule_8(path: Path) -> bool:
    """True if any of path's parts (case-insensitive on win32) match RULE_8_DIRS."""
    parts_lc = frozenset(p.lower() for p in path.parts)
    return any(rule.lower() in parts_lc for rule in RULE_8_DIRS)


def classify(name: str, on_disk: bool) -> str:
    """Map a dotdir name to a closed verdict.

    `unverifiable` is a closed-enum safety net reserved for the defensive
    fallback path. Today's worker only ever passes `on_disk=True`, so the
    value is uncommon on the happy path.
    """
    if name in WELL_KNOWN_NOISE_DIRS:
        return "well_known_noise"
    if name in CLOSED_POSSIBLY_LEGIT:
        return "possibly_legit"
    if name.startswith(".") and on_disk:
        return "unclassified_per_user"
    return "unverifiable"


def parse_gitignore_noise_block(
    gitignore_path: Path,
) -> tuple[frozenset[str], bool]:
    """Read .gitignore and extract leading-dot directories inside the
    per-user IDE/tooling block (the section heading we mark with
    `NOISE_BLOCK_HEADING`).

    Returns `(frozenset_of_names, found_block)`. `found_block=False` means the
    marker heading was not located; callers should treat that as a failed sync
    check rather than as zero drift.

    Names that appear elsewhere in `.gitignore` (e.g. `.idea/`, `.vscode/`)
    fall outside this scope; the caller subtracts `CLOSED_POSSIBLY_LEGIT`
    before diffing.

    Read-only: opens `.gitignore` in `'r'` mode only. Never writes.
    """
    if not gitignore_path.exists():
        return frozenset(), False
    names: set[str] = set()
    found_block = False
    in_target_block = False
    with open(gitignore_path, "r", encoding="utf-8") as fp:
        for raw_line in fp:
            line = raw_line.strip()
            if line.startswith("#") and NOISE_BLOCK_HEADING in line:
                in_target_block = True
                found_block = True
                continue
            # Paired close fence: a `# ===...===` line that follows the heading
            # closes the noise block. We require the line to start AND end with
            # `===` so unrelated future sub-sections with hash-prefix headings
            # do not accidentally close the block early.
            if in_target_block and line.startswith("# ===") and line.endswith("==="):
                in_target_block = False
                continue
            if not in_target_block:
                continue
            if line.startswith(".") and line.endswith("/"):
                names.add(line[:-1])
    return frozenset(names), found_block


def sync_warning(gitignore_path: Path) -> list[str]:
    """Return a list of human-readable sync warnings (caller prints them).

    Compares WELL_KNOWN_NOISE_DIRS against the per-user IDE/tooling block
    inside `.gitignore` (subtracting `CLOSED_POSSIBLY_LEGIT` so legitimate
    project dot-dirs are not flagged).

    Failure modes emit explicit warnings so the operator can correct them:

    - `.gitignore` not on disk: silent (operator evidently doesn't use one).
    - `.gitignore` exists but the noise-block heading is missing: WARN printed
      so the operator can correct the heading and have the sync check actually
      run. Without this, a renamed/missing marker would look like a clean sync.
    - Diff mismatch: WARN listing each side.

    Empty list strictly means "block found and in sync".
    """
    on_disk, found_block = parse_gitignore_noise_block(gitignore_path)
    warnings: list[str] = []
    if not found_block:
        warnings.append(
            f"WARN: noise-block marker '{NOISE_BLOCK_HEADING}' not found in "
            f"{gitignore_path} -- sync check did not run. Empty well-known set "
            f"also produces no warning; check manually."
        )
        return warnings
    only_in_python = WELL_KNOWN_NOISE_DIRS - on_disk
    only_in_gitignore = on_disk - WELL_KNOWN_NOISE_DIRS - CLOSED_POSSIBLY_LEGIT
    if only_in_python:
        warnings.append(
            "WARN: in WELL_KNOWN_NOISE_DIRS but missing from .gitignore noise block: "
            f"{sorted(only_in_python)}"
        )
    if only_in_gitignore:
        warnings.append(
            "WARN: in .gitignore noise block but missing from WELL_KNOWN_NOISE_DIRS: "
            f"{sorted(only_in_gitignore)}"
        )
    return warnings


def iter_direct_dotdirs(root: Path) -> list[tuple[str, Path, int]]:
    """Enumerate direct-child dotdirs of `root` (one level only, no recursion)."""
    out: list[tuple[str, Path, int]] = []
    try:
        children = sorted(os.listdir(root))
    except (PermissionError, OSError) as exc:
        raise OSError(f"cannot list workspace: {exc}") from exc

    for child in children:
        if not child.startswith("."):
            continue
        abs_path = root / child
        if not abs_path.is_dir():
            continue
        try:
            count = sum(1 for _ in abs_path.iterdir())
        except (PermissionError, OSError):
            count = -1
        out.append((child, abs_path, count))
    return out


def emit_row(
    workspace: Path,
    name: str,
    abs_path: Path,
    item_count: int,
    verdict: str,
    detail: str,
) -> dict[str, object]:
    """Build one append-only JSONL row."""
    return {
        "ts_iso": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "workspace": str(workspace),
        "dotdir_name": name,
        "abs_path": str(abs_path),
        "item_count": item_count,
        "verdict": verdict,
        "gitignore_match": verdict == "well_known_noise",
        "detail": detail,
    }


# ----- main -----


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="DOTDIR_CATALOG_RUN",
        description="Catalog root dot-directories and classify them for .gitignore decisions.",
    )
    parser.add_argument("--workspace", default=".", help="Workspace root (default: cwd)")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--dry-run", dest="mode", action="store_const", const="dry_run",
        help="Walk + classify + print summary; default; never writes a log.",
    )
    mode.add_argument(
        "--run", dest="mode", action="store_const", const="run",
        help="Walk + classify + APPEND JSONL rows to DOTDIR_CATALOG.log.",
    )
    parser.add_argument(
        "--emit-summary", dest="emit_summary", action="store_true",
        help="With --run only: also append a markdown summary to DOTDIR_CATALOG.md.",
    )
    parser.set_defaults(mode="dry_run")
    args = parser.parse_args(argv)

    if args.emit_summary and args.mode != "run":
        print(
            f"REFUSED: --emit-summary requires --run (got mode={args.mode!r}).",
            file=sys.stderr,
        )
        return REFUSAL_EXIT_CODE_MATRIX["emit_summary_without_run"]

    workspace = normalize_workspace(args.workspace)
    if is_rule_8(workspace):
        print(f"REFUSED: workspace '{workspace}' falls under Rule #8 fence.", file=sys.stderr)
        return REFUSAL_EXIT_CODE_MATRIX["rule_8_workspace"]
    if not workspace.exists():
        print(f"REFUSED: workspace '{workspace}' does not exist.", file=sys.stderr)
        return REFUSAL_EXIT_CODE_MATRIX["workspace_missing"]
    if not workspace.is_dir():
        print(f"REFUSED: workspace '{workspace}' is not a directory.", file=sys.stderr)
        return REFUSAL_EXIT_CODE_MATRIX["workspace_not_a_directory"]

    dry_run = args.mode == "dry_run"
    print(
        f"# DOTDIR_CATALOG_RUN | workspace={workspace} | mode={args.mode} "
        f"| emit_summary={args.emit_summary and args.mode == 'run'}"
    )

    # Closed-set sync check: WELL_KNOWN_NOISE_DIRS vs .gitignore noise block.
    # Emits warnings on stderr if the block is missing or if either set has
    # members the other doesn't. Empty list means strict in-sync.
    for warning in sync_warning(workspace / ".gitignore"):
        print(warning, file=sys.stderr)

    try:
        dotdirs = iter_direct_dotdirs(workspace)
    except OSError as exc:
        print(f"SKIPPED: {exc}", file=sys.stderr)
        return REFUSAL_EXIT_CODE_MATRIX["unreadable_workspace"]

    by_verdict: dict[str, list[tuple[str, Path, int]]] = {v: [] for v in DOTDIR_CATALOG_ENUM}
    for name, p, cnt in dotdirs:
        verdict = classify(name, on_disk=True)
        by_verdict[verdict].append((name, p, cnt))

    for verdict in DOTDIR_CATALOG_ENUM:
        rows = by_verdict[verdict]
        if not rows:
            continue
        print(f"## verdict={verdict} count={len(rows)}")
        for name, p, cnt in rows:
            note = "" if cnt >= 0 else "  [unreadable]"
            print(f"  {name:<32} {cnt:>5}{note}  ({p})")

    total = sum(len(v) for v in by_verdict.values())
    print(f"## TOTAL direct-child dotdirs: {total}")
    print(
        f"## well_known_noise: {len(by_verdict['well_known_noise'])} | "
        f"unclassified_per_user: {len(by_verdict['unclassified_per_user'])} | "
        f"possibly_legit: {len(by_verdict['possibly_legit'])} | "
        f"skipped/unverifiable/refused: "
        f"{len(by_verdict['skipped']) + len(by_verdict['unverifiable']) + len(by_verdict['refused'])}"
    )

    if dry_run:
        return 0

    # ---- writer phase (--run only) ----
    log_path = workspace / "DOTDIR_CATALOG.log"
    with open(log_path, "a", encoding="utf-8") as fp:
        for verdict in DOTDIR_CATALOG_ENUM:
            if verdict in ("refused", "skipped"):
                continue
            for name, p, cnt in by_verdict[verdict]:
                detail = (
                    "unreadable_dir_contents" if cnt < 0
                    else "in_well_known_set" if verdict == "well_known_noise"
                    else "needs_human_decision" if verdict == "unclassified_per_user"
                    else "do_not_ignore"
                )
                fp.write(json.dumps(
                    emit_row(workspace, name, p, cnt, verdict, detail),
                    ensure_ascii=False,
                ) + "\n")
    print(f"## appended JSONL rows to {log_path}")

    if args.emit_summary:
        md_path = workspace / "DOTDIR_CATALOG.md"
        with open(md_path, "a", encoding="utf-8") as fp:
            fp.write(
                f"# DOTDIR_CATALOG summary "
                f"{datetime.now(timezone.utc).isoformat(timespec='seconds')}\n\n"
            )
            fp.write(f"Workspace: `{workspace}`\n\n")
            for verdict in DOTDIR_CATALOG_ENUM:
                rows = by_verdict[verdict]
                if not rows:
                    continue
                fp.write(f"## {verdict} ({len(rows)})\n\n")
                for name, p, cnt in rows:
                    fp.write(f"- `{name}` (items={cnt}, path=`{p}`)\n")
                fp.write("\n")
        print(f"## appended summary to {md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
