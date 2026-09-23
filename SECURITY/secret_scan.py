"""Fail-closed scan for high-confidence credentials in repository files.

The scanner reports paths, line numbers, and pattern classes only. It is a
preventive guardrail, not a replacement for provider rotation or Git-history
scrubbing. It never prints matched credential values.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

PATTERNS = (
    ("private-key", re.compile(r"-----BEGIN (?:RSA|OPENSSH|EC|DSA|PGP) PRIVATE KEY-----")),
    ("github-token", re.compile(r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9_]{20,}\b")),
    ("github-pat", re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b")),
    ("openai-key", re.compile(r"\bsk-[A-Za-z0-9]{20,}\b")),
    ("google-key", re.compile(r"\bAIza[0-9A-Za-z_-]{30,}\b")),
    ("slack-token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{20,}\b")),
    ("discord-webhook", re.compile(r"https?://discord(?:app)?\.com/api/webhooks/\d+/[^\s\"']+")),
)

# Only explicit template syntax is ignored. Generic words such as "example"
# must not suppress a real credential-shaped value on the same line.
EXAMPLE_LINE_PATTERNS = (
    re.compile(r"<[^>]+>"),
    re.compile(r"\$\{[^}]+\}"),
    re.compile(r"\b(?:YOUR|REPLACE|CHANGE|REDACTED|PLACEHOLDER)(?:[_ -][A-Z0-9_-]+)*\b"),
)
IGNORED_PATHS = {"SECURITY/secret_scan.py", "tests/test_security_controls.py"}


@dataclass(frozen=True)
class Finding:
    path: str
    line: int
    pattern: str


@dataclass(frozen=True)
class ScanError:
    path: str
    error: str


def repository_root() -> Path:
    """Return the Git worktree root, or the current directory outside Git."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        return Path(result.stdout.strip()).resolve()
    except (OSError, subprocess.CalledProcessError):
        return Path.cwd().resolve()


def tracked_files() -> list[str]:
    result = subprocess.run(
        ["git", "ls-files"],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return [line for line in result.stdout.splitlines() if line]


def _without_template_markers(line: str) -> str:
    """Remove only explicit placeholders before testing credential patterns."""
    cleaned = line
    for pattern in EXAMPLE_LINE_PATTERNS:
        cleaned = pattern.sub("", cleaned)
    return cleaned


def scan_file(path: Path) -> list[tuple[int, str]]:
    """Scan one file incrementally so large archives cannot exhaust RAM."""
    findings: list[tuple[int, str]] = []
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        for line_number, line in enumerate(handle, 1):
            candidate = _without_template_markers(line)
            for label, pattern in PATTERNS:
                if pattern.search(candidate):
                    findings.append((line_number, label))
    return findings


def _relative_path(raw_path: str, root: Path) -> tuple[str, Path] | None:
    """Resolve a path and reject symlink/path traversal outside the worktree."""
    candidate = Path(raw_path)
    if not candidate.is_absolute():
        candidate = root / candidate
    resolved = candidate.resolve(strict=False)
    try:
        relative = resolved.relative_to(root)
    except ValueError:
        return None
    normalized = relative.as_posix()
    return normalized, resolved


def scan_paths(paths: Iterable[str], root: Path | None = None) -> tuple[list[Finding], list[ScanError]]:
    """Scan repository-relative paths and return findings plus fail-closed errors."""
    root = (root or repository_root()).resolve()
    findings: list[Finding] = []
    errors: list[ScanError] = []
    seen: set[str] = set()

    for raw_path in paths:
        normalized = _relative_path(str(raw_path), root)
        if normalized is None:
            errors.append(ScanError(str(raw_path), "path resolves outside repository root"))
            continue
        relative, path = normalized
        if relative in seen:
            continue
        seen.add(relative)
        if relative in IGNORED_PATHS:
            continue
        if not path.is_file():
            errors.append(ScanError(relative, "file does not exist or is not a regular file"))
            continue
        try:
            for line, pattern in scan_file(path):
                findings.append(Finding(relative, line, pattern))
        except (OSError, UnicodeError) as exc:
            errors.append(ScanError(relative, f"unable to read file: {exc}"))
    return findings, errors


def _paths_from_args(args: argparse.Namespace) -> list[str]:
    if args.paths_file and args.paths:
        raise ValueError("use either --paths-file or direct paths, not both")
    if args.tracked_only and (args.paths_file or args.paths):
        raise ValueError("--tracked-only cannot be combined with explicit paths")
    if args.tracked_only or not args.paths_file and not args.paths:
        return tracked_files()
    if args.paths_file:
        return [line.strip() for line in args.paths_file.read_text(encoding="utf-8").splitlines() if line.strip()]
    return list(args.paths)


def _print_text(findings: list[Finding], errors: list[ScanError], checked: int) -> None:
    if findings or errors:
        print(
            f"Secret scan failed: {len(findings)} finding(s), {len(errors)} path error(s).",
            file=sys.stderr,
        )
        for finding in findings:
            print(
                f"::error file={finding.path},line={finding.line}::{finding.pattern} detected; "
                "rotate and remove from history",
                file=sys.stderr,
            )
        for error in errors:
            print(f"::error file={error.path}::{error.error}", file=sys.stderr)
        return
    print(f"Secret scan passed: {checked} repository path(s) checked.")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--tracked-only",
        action="store_true",
        help="Scan all Git-tracked files; explicit incident-audit mode",
    )
    parser.add_argument("--paths-file", type=Path, help="Scan repository-relative paths listed in this file")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable findings and errors")
    parser.add_argument("paths", nargs="*", help="Repository-relative paths to scan directly")
    args = parser.parse_args(argv)

    try:
        paths = _paths_from_args(args)
    except (OSError, UnicodeError, ValueError) as exc:
        parser.error(str(exc))

    findings, errors = scan_paths(paths)
    if args.json:
        print(
            json.dumps(
                {
                    "ok": not findings and not errors,
                    "checked_paths": len(paths),
                    "findings": [asdict(finding) for finding in findings],
                    "errors": [asdict(error) for error in errors],
                },
                sort_keys=True,
            )
        )
    else:
        _print_text(findings, errors, len(paths))
    return 1 if findings or errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
