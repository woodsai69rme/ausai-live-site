"""Audio analysis utilities for AI Influencer Studio.

Detects BPM and duration from audio files. Uses librosa when available,
otherwise falls back to mutagen for duration and a default BPM.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

try:
    import librosa

    # librosa uses lazy_loader, so the real (heavy) imports only happen on
    # first attribute access. Probe one here so a broken install (e.g. a
    # numpy/numba version mismatch) degrades to the mutagen fallback instead
    # of crashing at first use in analyze_audio.
    librosa.load  # noqa: B018 - force lazy submodule load
    _LIBROSA_OK = True
except ImportError:
    librosa = None  # type: ignore[assignment]
    _LIBROSA_OK = False

try:
    from mutagen import File as MutagenFile
except ImportError:
    MutagenFile = None  # type: ignore[assignment]


def analyze_audio(path: str | Path) -> dict[str, Any]:
    """Analyze an audio file and return duration and BPM.

    Returns a dict with keys:
        - duration: float or None
        - bpm: float or None
        - source: str indicating which library produced the values
    """
    audio_path = Path(path)
    if not audio_path.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    duration: float | None = None
    bpm: float | None = None
    source = "none"

    if librosa is not None:
        y, sr = librosa.load(str(audio_path), sr=None)
        duration = librosa.get_duration(y=y, sr=sr)
        tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
        bpm = float(tempo) if tempo else None
        source = "librosa"

    if duration is None and MutagenFile is not None:
        audio = MutagenFile(str(audio_path))
        if audio is not None and audio.info is not None:
            duration = float(audio.info.length)
            source = "mutagen"

    if bpm is None:
        bpm = 120.0
        if source == "mutagen":
            source = "mutagen+default_bpm"
        elif source == "none":
            source = "default"

    return {
        "duration": duration,
        "bpm": bpm,
        "source": source,
    }
