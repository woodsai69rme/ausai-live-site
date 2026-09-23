"""Beat-grid assembly for AI Influencer Studio.

Song plans already align scenes to the measured track (duration + BPM come from
``audio_analysis``) and tag every scene with a ``suggested_clip``. This module
turns that into an actual cut plan: scene boundaries are snapped to the musical
beat grid (hard-cut-on-beat, matching the scene ``transition`` field), and an
``ffmpeg`` concat command is built that trims each suggested clip to its scene
segment and muxes the original audio.

The command builder is pure (testable without ffmpeg); :func:`assemble` runs it
when ffmpeg is available. Per-scene segments assume each suggested clip is at
least as long as its segment — for longer scenes generate one clip per scene
with ``generation_mode=clip_only`` first.
"""

from __future__ import annotations

import re
import shutil
import subprocess
from collections.abc import Mapping
from pathlib import Path
from typing import Any


def beat_times(bpm: float, duration: float) -> list[float]:
    """Absolute beat timestamps from 0 up to (but not including) ``duration``.

    60 BPM yields one beat per second; 120 BPM two per second. Empty when either
    input is non-positive.
    """
    if bpm <= 0 or duration <= 0:
        return []
    interval = 60.0 / bpm
    times: list[float] = []
    t = 0.0
    while t < duration - 1e-6:
        times.append(round(t, 3))
        t += interval
    return times


def snap_to_beat(cut_time: float, beats: list[float]) -> float:
    """Snap a cut to the nearest beat timestamp; unmodified when no beats exist."""
    if not beats:
        return cut_time
    return min(beats, key=lambda beat: abs(beat - cut_time))


def snap_cut_times(cuts: list[float], bpm: float, duration: float) -> list[float]:
    """Snap every cut point to the nearest beat in a BPM grid."""
    beats = beat_times(bpm, duration)
    return [snap_to_beat(cut, beats) for cut in cuts]


def scene_cut_points(song: Mapping[str, Any], *, beat_snap: bool = True) -> list[float]:
    """Derive the cut points between scenes from a SongPlan dict.

    Uses each scene's ``end_time`` (already aligned to the measured track) and,
    when ``beat_snap`` is enabled and the plan has a BPM, snaps those cuts to the
    nearest beat. The last scene's end is the track duration and is not a cut.
    """
    scenes = song.get("scenes") or []
    if not scenes:
        duration = float(song.get("duration") or 0.0)
        return [duration] if beat_snap else []
    cuts = [float(scene["end_time"]) for scene in scenes[:-1]]
    if beat_snap:
        bpm = song.get("bpm")
        duration = float(song.get("duration") or (scenes[-1]["end_time"] if scenes else 0.0))
        if isinstance(bpm, int | float) and bpm > 0:
            return snap_cut_times(cuts, float(bpm), duration)
    return cuts


def scene_clip_sources(song: Mapping[str, Any]) -> list[str]:
    """Per-scene ``suggested_clip`` paths (scene 0 -> N). Missing scenes raise."""
    scenes = song.get("scenes") or []
    sources: list[str] = []
    for index, scene in enumerate(scenes):
        clip = scene.get("suggested_clip") or ""
        if not clip:
            raise ValueError(f"Scene {index + 1} has no suggested_clip; run music-video plan with a staging root first")
        sources.append(str(clip))
    return sources


def find_ffmpeg() -> str:
    """Locate an ffmpeg executable (PATH first, then imageio-ffmpeg)."""
    on_path = shutil.which("ffmpeg")
    if on_path:
        return on_path
    try:
        import imageio_ffmpeg

        return imageio_ffmpeg.get_ffmpeg_exe()
    except (ImportError, RuntimeError):
        pass
    raise RuntimeError(
        "ffmpeg not found; install it (e.g. 'winget install FFmpeg.FFmpeg') or pip install imageio-ffmpeg"
    )


def _probe_dimensions(ffmpeg_exe: str, video_path: str | Path) -> tuple[int, int] | None:
    """Return (width, height) of a video by parsing ffmpeg's stderr header.

    Uses the plain ``-i`` probe (no ffprobe needed). Returns None when the
    probe fails so callers can fall back to a default canvas.
    """
    try:
        result = subprocess.run(
            [ffmpeg_exe, "-hide_banner", "-i", str(video_path)],
            capture_output=True,
            text=True,
            timeout=60,
        )
    except Exception:
        return None
    text = result.stderr or ""
    match = re.search(r"Stream #[0-9]+:[0-9]+.*?, (\d{2,5})x(\d{2,5})", text)
    if not match:
        return None
    return int(match.group(1)), int(match.group(2))


DEFAULT_CANVAS: tuple[int, int] = (1280, 720)


def build_ffmpeg_command(
    song: Mapping[str, Any],
    *,
    out_path: str | Path,
    audio_path: str | Path | None = None,
    beat_snap: bool = True,
    target_resolution: tuple[int, int] | None = None,
) -> dict[str, Any]:
    """Build an ffmpeg command that assembles the plan's clips on the beat grid.

    Returns ``{command, scene_clips, cuts, segments, duration}``. Raises
    ``FileNotFoundError`` listing any missing clip/audio inputs — nothing is run.

    ``target_resolution`` (default ``(1280, 720)``) is the output canvas every
    clip is scaled/padded to fit, so mixed-aspect staged clips (e.g. square
    Instagram cuts next to 16:9 YouTube cuts) can be concatenated.
    """
    clips = scene_clip_sources(song)
    missing = [clip for clip in clips if not Path(clip).exists()]
    if missing:
        raise FileNotFoundError(f"Missing scene clips: {missing} — generate them first")
    audio = Path(audio_path) if audio_path is not None else Path(str(song.get("audio_path") or ""))
    if audio_path is not None and not audio.exists():
        raise FileNotFoundError(f"Audio file not found: {audio}")
    has_audio = audio.exists() and str(audio) != "."

    duration = float(song.get("duration") or 0.0)
    cuts = scene_cut_points(song, beat_snap=beat_snap)
    starts = [0.0, *cuts]
    ends = [*cuts, duration]
    segments = list(zip(starts, ends, strict=True))

    canvas_w, canvas_h = target_resolution or DEFAULT_CANVAS

    input_args: list[str] = []
    for clip in clips:
        input_args += ["-i", clip]
    audio_input_index: int | None = None
    if has_audio:
        input_args += ["-i", str(audio)]
        audio_input_index = len(clips)

    # Each suggested clip is a standalone asset, so it is trimmed from its own
    # start to the scene segment length (the beat-snapped boundary determines
    # how long the cut stays on screen), then scaled/padded to the shared
    # canvas so clips of different aspect ratios can be concatenated.
    filter_parts: list[str] = []
    for index, (start, end) in enumerate(segments):
        segment_duration = max(end - start, 0.0)
        filter_parts.append(
            f"[{index}:v]trim=start=0:end={segment_duration:.3f},setpts=PTS-STARTPTS,"
            f"scale={canvas_w}:{canvas_h}:force_original_aspect_ratio=decrease,"
            f"pad={canvas_w}:{canvas_h}:(ow-iw)/2:(oh-ih)/2:color=black,setsar=1[v{index}]"
        )
    video_labels = "".join(f"[v{index}]" for index in range(len(clips)))
    filter_parts.append(f"{video_labels}concat=n={len(clips)}:v=1:a=0[outv]")
    filter_complex = ";".join(filter_parts)

    command = ["ffmpeg", *input_args, "-filter_complex", filter_complex, "-map", "[outv]"]
    if audio_input_index is not None:
        command += ["-map", f"{audio_input_index}:a", "-shortest"]
    command += [
        "-c:v", "libx264", "-preset", "fast", "-crf", "20", "-pix_fmt", "yuv420p",
        "-y", str(out_path),
    ]

    return {
        "command": command,
        "scene_clips": clips,
        "cuts": cuts,
        "segments": [[round(s, 3), round(e, 3)] for s, e in segments],
        "duration": duration,
        "audio": str(audio) if has_audio else None,
    }


def assemble(
    song: Mapping[str, Any],
    *,
    out_path: str | Path,
    audio_path: str | Path | None = None,
    beat_snap: bool = True,
    timeout_seconds: int = 1800,
) -> dict[str, Any]:
    """Build and run the ffmpeg assembly; returns the plan plus the run result.

    Requires ffmpeg (see :func:`find_ffmpeg`). Raises on non-zero exit so a bad
    assembly fails loudly instead of producing a corrupt file.
    """
    # Normalize mixed-aspect staged clips onto the first clip's canvas so a
    # square Instagram clip and a 16:9 YouTube clip can share a concat graph.
    clips = [
        str(scene.get("suggested_clip") or "")
        for scene in (song.get("scenes") or [])
        if scene.get("suggested_clip")
    ]
    executable = find_ffmpeg()
    target_resolution = _probe_dimensions(executable, clips[0]) if clips else None
    spec = build_ffmpeg_command(
        song,
        out_path=out_path,
        audio_path=audio_path,
        beat_snap=beat_snap,
        target_resolution=target_resolution,
    )
    cmd = [executable, *spec["command"][1:]]  # replace the placeholder 'ffmpeg'
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout_seconds)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg assembly failed (exit {result.returncode}): {result.stderr.strip()}")
    return {**spec, "returncode": 0, "output": str(out_path)}
