"""Validate the repository security documentation and workflow guardrails.

This command is dependency-light and safe to run locally or in CI. It checks
only repository metadata and documentation; it does not contact providers,
rotate credentials, rewrite history, or mutate append-only logs.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover - exercised only in minimal environments
    yaml = None

ROOT = Path(__file__).resolve().parents[1]
DOC_FILES = [
    ROOT / "DOCS_INDEX.md",
    ROOT / "SECURITY" / "README.md",
    ROOT / "SECURITY" / "INCIDENT_RESPONSE.md",
    ROOT / "SECURITY" / "ROTATION_CHECKLIST.md",
    ROOT / "SECURITY" / "AUDIT_REMEDIATION_STATUS_2026-08-23.md",
    ROOT / "SECURITY" / "EXTERNAL_ACTION_HANDOFF_2026-08-24.md",
    ROOT / "SECURITY" / "DOCUMENTATION_MANIFEST_2026-08-24.md",
    ROOT / "SECURITY" / "REWRITE_READINESS_2026-08-24.md",
    ROOT / "SECURITY" / "FORENSIC_ARCHIVE_AND_WORKTREE_EXPORT_PLAN_2026-08-24.md",
    ROOT / "SECURITY" / "REWRITE_REF_SCOPE_2026-08-24.md",
]
WORKFLOW_DIR = ROOT / ".github" / "workflows"
REPOSITORY_REF = re.compile(r"(?<![A-Za-z0-9_./-])((?:SECURITY|SLEEP_TRIPLE|tests)/[A-Za-z0-9_./-]+)")
ACTION_REF = re.compile(r"uses:\s*[^\s@]+@([^\s#]+)")
SHA = re.compile(r"^[0-9a-fA-F]{40}$")


def _load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def check_document_files() -> list[str]:
    errors: list[str] = []
    for path in DOC_FILES:
        if not path.is_file():
            errors.append(f"missing documentation file: {path.relative_to(ROOT).as_posix()}")
            continue
        for reference in REPOSITORY_REF.findall(_load_text(path)):
            candidate = ROOT / reference.rstrip(".,:)")
            if candidate.suffix and not candidate.exists():
                errors.append(
                    f"{path.relative_to(ROOT).as_posix()}: missing reference {candidate.relative_to(ROOT).as_posix()}"
                )
    return errors


def check_workflows() -> list[str]:
    errors: list[str] = []
    if yaml is None:
        return ["PyYAML is required to validate workflow YAML"]
    for path in sorted(WORKFLOW_DIR.glob("*.yml")):
        try:
            yaml.safe_load(_load_text(path))
        except yaml.YAMLError as exc:
            errors.append(f"{path.relative_to(ROOT).as_posix()}: invalid YAML: {exc}")
        for reference in ACTION_REF.findall(_load_text(path)):
            if not SHA.fullmatch(reference):
                errors.append(
                    f"{path.relative_to(ROOT).as_posix()}: mutable or invalid action reference {reference}"
                )
    return errors


def check_security_docs() -> list[str]:
    errors: list[str] = []
    scanner = ROOT / "SECURITY" / "secret_scan.py"
    if not scanner.is_file():
        errors.append("missing SECURITY/secret_scan.py")
    else:
        # Keep the validation script from silently becoming a secret source.
        try:
            from SECURITY.secret_scan import scan_paths
        except ModuleNotFoundError:  # direct `python SECURITY/validate_security_docs.py`
            from secret_scan import scan_paths

        findings, scan_errors = scan_paths([str(path.relative_to(ROOT)) for path in DOC_FILES], ROOT)
        errors.extend(
            f"security documentation finding: {finding.path}:{finding.line} ({finding.pattern})"
            for finding in findings
        )
        errors.extend(f"security documentation read error: {error.path} ({error.error})" for error in scan_errors)
    return errors


def validate() -> list[str]:
    return check_document_files() + check_workflows() + check_security_docs()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Emit a machine-readable validation result")
    args = parser.parse_args(argv)
    errors = validate()
    result: dict[str, Any] = {"ok": not errors, "errors": errors}
    if args.json:
        print(json.dumps(result, sort_keys=True))
    else:
        if errors:
            print("Security documentation validation failed:")
            for error in errors:
                print(f"- {error}")
        else:
            print(f"Security documentation validation passed: {len(DOC_FILES)} docs and {len(list(WORKFLOW_DIR.glob('*.yml')))} workflows checked.")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
