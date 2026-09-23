"""Regression tests for repository security guardrails."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from SECURITY.secret_scan import Finding, ScanError, scan_paths
from SECURITY.validate_security_docs import validate

ROOT = Path(__file__).resolve().parents[1]


def test_scanner_detects_real_credential_without_printing_value(tmp_path: Path) -> None:
    path = tmp_path / "config.txt"
    path.write_text("OPENAI_KEY=sk-abcdefghijklmnopqrstuvwxyz123456\n", encoding="utf-8")

    findings, errors = scan_paths([str(path)], tmp_path)

    assert errors == []
    assert findings == [Finding("config.txt", 1, "openai-key")]
    assert "abcdefghijklmnopqrstuvwxyz" not in json.dumps([finding.__dict__ for finding in findings])


def test_scanner_allows_explicit_placeholder_without_suppressing_other_content(tmp_path: Path) -> None:
    path = tmp_path / "example.env"
    path.write_text(
        "OPENAI_KEY=<your-key-here>\n"
        "OTHER_KEY=sk-abcdefghijklmnopqrstuvwxyz123456\n",
        encoding="utf-8",
    )

    findings, errors = scan_paths([str(path)], tmp_path)

    assert errors == []
    assert findings == [Finding("example.env", 2, "openai-key")]


def test_scanner_rejects_paths_outside_repository(tmp_path: Path) -> None:
    inside = tmp_path / "inside.txt"
    outside = tmp_path.parent / "outside.txt"
    inside.write_text("safe\n", encoding="utf-8")
    outside.write_text("sk-abcdefghijklmnopqrstuvwxyz123456\n", encoding="utf-8")

    findings, errors = scan_paths([str(inside), str(outside)], tmp_path)

    assert findings == []
    assert errors == [ScanError(str(outside), "path resolves outside repository root")]


def test_scanner_reports_missing_paths_instead_of_skipping_them(tmp_path: Path) -> None:
    findings, errors = scan_paths(["missing.txt"], tmp_path)

    assert findings == []
    assert len(errors) == 1
    assert errors[0].path == "missing.txt"
    assert "does not exist" in errors[0].error


def test_security_documentation_validation_passes() -> None:
    assert validate() == []


@pytest.mark.parametrize(
    "relative_path",
    [
        "SECURITY/README.md",
        "SECURITY/INCIDENT_RESPONSE.md",
        "SECURITY/ROTATION_CHECKLIST.md",
        "SECURITY/AUDIT_REMEDIATION_STATUS_2026-08-23.md",
    ],
)
def test_security_documentation_exists(relative_path: str) -> None:
    assert (ROOT / relative_path).is_file()
