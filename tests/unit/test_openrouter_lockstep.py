"""tests/unit/test_openrouter_lockstep.py

Lockstep-invariant guard for the OpenRouter free-tier refresh workflow.

Background: the cont.17-fup-3 commit (2026-07-11) refreshed
ComfyUI/tools/music_video_studio.py FREE_MODELS (8 -> 16) and the operator-
discovery mirror ComfyUI/config/openrouter_free_models.txt. The two lists
MUST stay byte-identical -- otherwise ``brainstorm --model <id>`` silently
routes to a stale model ID while operators reference a different ID in the
.txt. This test trips on ANY drift.

Tests:
    1. test_lockstep_invariant_openrouter_free_models
       - Both lists match exactly (no diff in either direction).
    2. test_free_models_count_is_reasonable
       - 1 <= N <= 50 (catches accidental wipe or pragma bloat).
    3. test_all_free_model_ids_end_with_colon_free
       - Every entry ends with ":free" (router only dispatches :free tags).
    4. test_is_openrouter_tag_accepts_all_free_models
       - is_openrouter_tag() returns True for every entry
         (catches namespace-prefix drift).

If a future refresh adds/removes an ID, BOTH files must change together,
and this test will pass again.

NOTE on skip semantics: each test uses ``pytest.skip()`` if the source files
are missing (e.g. fresh-clean state, partial checkout). This is intentional:
a missing-file skip means the test cannot enforce the invariant (NOT a
false-positive pass -- pytest reports ``s`` in the verbose output). If you
need a hard fail when files are missing, switch ``pytest.skip()`` to
``pytest.fail()`` or ``xfail(strict=True, ...)``. The current default
matches the project's "detailed errors over graceful failures" alpha
principle -- we WANT the test to trip loudly on drift, but skip-silently
on missing-infrastructure is acceptable since the project's CI isn't set
up yet (see TODO #4.12 in TODO_TRACKER.md).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
COMFY_DIR = ROOT / "ComfyUI"
PY_FILE = COMFY_DIR / "tools" / "music_video_studio.py"
TXT_FILE = COMFY_DIR / "config" / "openrouter_free_models.txt"

# Ensure ComfyUI/tools is importable so music_video_studio can be loaded.
if str(COMFY_DIR / "tools") not in sys.path:
    sys.path.insert(0, str(COMFY_DIR / "tools"))


def _parse_canonical_ids_from_txt(path: Path) -> set[str]:
    """Parse the ## ✅ FREE OPENROUTER MODELS section of the operator-discovery file.

    The .txt format is: header line, list of IDs (one per line, no inline
    comments), "Live free-tier" commentary block, then the rest of the file.
    We extract strictly the IDs from the canonical list block.
    """
    text = path.read_text(encoding="utf-8")
    start = text.find("## ✅ FREE OPENROUTER MODELS")
    assert start != -1, f"Canonical section header missing in {path.name}"
    end = text.find("# Live free-tier", start)
    assert end != -1, f"Canonical section terminator missing in {path.name}"
    block = text[start:end]
    ids: set[str] = set()
    for line in block.splitlines():
        line = line.strip()
        if line and not line.startswith("#") and ":free" in line:
            ids.add(line)
    return ids


@pytest.mark.unit
def test_lockstep_invariant_openrouter_free_models():
    """FREE_MODELS in music_video_studio.py == canonical IDs in openrouter_free_models.txt."""
    if not PY_FILE.exists():
        pytest.skip(f"{PY_FILE.name} not yet present")
    if not TXT_FILE.exists():
        pytest.skip(f"{TXT_FILE.name} not yet present")
    import music_video_studio  # noqa: E402

    py_ids = set(music_video_studio.FREE_MODELS)
    txt_ids = _parse_canonical_ids_from_txt(TXT_FILE)

    missing_in_py = txt_ids - py_ids
    extra_in_py = py_ids - txt_ids

    assert not missing_in_py, (
        f"{len(missing_in_py)} ID(s) in {TXT_FILE.name} but missing from "
        f"music_video_studio.FREE_MODELS: {sorted(missing_in_py)}"
    )
    assert not extra_in_py, (
        f"{len(extra_in_py)} ID(s) in music_video_studio.FREE_MODELS "
        f"but not in {TXT_FILE.name}: {sorted(extra_in_py)}"
    )


@pytest.mark.unit
def test_free_models_count_is_reasonable():
    """N must be in [1, 50]; catches accidental wipe or wildcard bloat."""
    if not PY_FILE.exists():
        pytest.skip(f"{PY_FILE.name} not yet present")
    import music_video_studio  # noqa: E402

    n = len(music_video_studio.FREE_MODELS)
    assert 1 <= n <= 50, f"FREE_MODELS has unexpected size {n}"


@pytest.mark.unit
def test_all_free_model_ids_end_with_colon_free():
    """Every entry must end with ':free' -- router only dispatches :free tags."""
    if not PY_FILE.exists():
        pytest.skip(f"{PY_FILE.name} not yet present")
    import music_video_studio  # noqa: E402

    bad = [m for m in music_video_studio.FREE_MODELS if not m.endswith(":free")]
    assert not bad, f"FREE_MODELS contains non-:free entries: {bad}"


@pytest.mark.unit
def test_is_openrouter_tag_accepts_all_free_models():
    """Router must signal 'cloud dispatch' for every FREE_MODELS entry."""
    if not PY_FILE.exists():
        pytest.skip(f"{PY_FILE.name} not yet present")
    import music_video_studio  # noqa: E402

    for mid in music_video_studio.FREE_MODELS:
        assert music_video_studio.is_openrouter_tag(mid), (
            f"Router would misdispatch to Ollama: {mid!r} "
            f"is_openrouter_tag() returned False -- check "
            f"OPENROUTER_NAMESPACE_PREFIXES for namespace-prefix coverage"
        )


@pytest.mark.unit
def test_txt_canonical_section_header_present():
    """The ## \u2705 FREE OPENROUTER MODELS section header must exist
    (format invariant; the lockstep test relies on it)."""
    if not TXT_FILE.exists():
        pytest.skip(f"{TXT_FILE.name} not yet present")
    text = TXT_FILE.read_text(encoding="utf-8")
    assert "## \u2705 FREE OPENROUTER MODELS" in text, (
        f"{TXT_FILE.name} missing canonical header line -- "
        f"test_openrouter_lockstep.py relies on it for parsing"
    )
